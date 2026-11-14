"""Share the D415 between our code and Physical AI Studio: colour and depth as two MJPEG camera streams.

Studio records the RealSense in colour only, and only one process can open the camera. The bridge owns it and
serves ``/top.mjpg`` (colour) and ``/top_depth.mjpg`` (a depth image), which Studio records as two IP cameras; the
depth image then becomes one more visual input for a policy.

Depth images, all on fixed scales (never normalised per frame, so a value means the same thing in every episode):

* ``layers`` (default): height above the table plane in three channels, as a viewer sees them: **R** fine height
  0 → ``fine_max_m`` (default 4 cm: the brick, also inside the jaws), **G** coarse height 0 → ``coarse_max_m``
  (default 30 cm: the gripper's height during approach and descent), **B** depth valid (255) or missing (0). Table
  and missing depth are both 0 in R and G; B keeps them apart, which one grey level could not survive JPEG.
* ``height``: one grey channel, height above the table 0 (grey 1) → ``max_height_m`` (255), missing 0. This is the
  encoding of dataset sort-depth-v1 (recorded at 10 cm).
* ``distance``: distance from the camera, ``near_m`` → 255 to ``far_m`` → 1, missing 0. On a tilted camera the table
  itself spans most of the range, which hides small objects.

The table plane is fitted once on the first frame and then held, so the arm or a hand over the table cannot shift
the scale mid-episode. With ``--plane FILE`` the plane is saved on first use and reused on every later start, as long
as a fresh fit agrees with it; a moved camera is refused, because it would change the encoding within a dataset.

``--crop X Y W H`` cuts the same pixel box from colour and depth, at its own size: the policy resizes its inputs to a
fixed resolution anyway, so cropping to the work area puts more of those pixels on the brick and the gripper.
JPEGs use 4:4:4 chroma so detail that differs between the depth channels is not averaged away.

	uv run sorter-depth-bridge --host <tailnet IP> --port 8092 --plane data/depth/plane.json

Then add two IP cameras in Studio: ``http://<host>:8092/top.mjpg`` and ``http://<host>:8092/top_depth.mjpg``.
``/top.jpg`` and ``/top_depth.jpg`` return a single frame for a quick look.
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import time
from collections.abc import Callable
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import cv2
import numpy as np

from defect_sorter.alignment import tilt_deg
from defect_sorter.geometry import Intrinsics, Plane, deproject, fit_table_plane, height_above
from defect_sorter.webview import FrameBuffer

logger = logging.getLogger(__name__)

STREAM_WAIT_S = 2.0
_PATH = re.compile(r"^/([a-z_]+)\.(mjpg|jpg)$")
MODES = ("layers", "height", "distance")
PLANE_TILT_TOL_DEG = 1.0
PLANE_OFFSET_TOL_M = 0.01
MIN_PLANE_INLIERS = 0.5


def colorize_depth(depth_m: np.ndarray, *, near_m: float, far_m: float) -> np.ndarray:
	"""Depth (metres) as a 3-channel grey image on a fixed scale; see the module docstring."""
	if not 0 < near_m < far_m:
		raise ValueError("depth scale needs 0 < near_m < far_m")
	d = np.asarray(depth_m, dtype=np.float32)
	valid = np.isfinite(d) & (d > 0)
	clipped = np.clip(np.where(valid, d, far_m), near_m, far_m)
	grey = np.rint(1.0 + 254.0 * (far_m - clipped) / (far_m - near_m)).astype(np.uint8)
	grey[~valid] = 0
	return np.repeat(grey[..., None], 3, axis=2)


def height_image(height_m: np.ndarray, *, max_m: float) -> np.ndarray:
	"""Height above the table as a 3-channel grey image: 0 m (or below) → 1, ``max_m`` (or above) → 255, NaN → 0."""
	if max_m <= 0:
		raise ValueError("max_m must be positive")
	h = np.asarray(height_m, dtype=np.float32)
	valid = np.isfinite(h)
	grey = np.rint(1.0 + 254.0 * np.clip(np.where(valid, h, 0.0), 0.0, max_m) / max_m).astype(np.uint8)
	grey[~valid] = 0
	return np.repeat(grey[..., None], 3, axis=2)


def layered_height_image(height_m: np.ndarray, *, fine_max_m: float, coarse_max_m: float) -> np.ndarray:
	"""Height above the table as three channels (OpenCV order B, G, R); see ``layers`` in the module docstring.

	Parameters
	----------
	height_m : numpy.ndarray
		Height above the table in metres, NaN where depth is missing; shape (H, W).
	fine_max_m, coarse_max_m : float
		Heights drawn as 255 in R and G; ``0 < fine_max_m < coarse_max_m``.

	Returns
	-------
	numpy.ndarray
		uint8 image, shape (H, W, 3).
	"""
	if not 0 < fine_max_m < coarse_max_m:
		raise ValueError("scales need 0 < fine_max_m < coarse_max_m")
	h = np.asarray(height_m, dtype=np.float64)
	valid = np.isfinite(h)
	h = np.clip(np.where(valid, h, 0.0), 0.0, None)
	out = np.empty((*h.shape, 3), np.uint8)
	out[..., 0] = np.where(valid, 255, 0)
	out[..., 1] = np.rint(255.0 * np.minimum(h / coarse_max_m, 1.0))
	out[..., 2] = np.rint(255.0 * np.minimum(h / fine_max_m, 1.0))
	return out


def fit_plane(depth_m: np.ndarray, intrinsics: Intrinsics) -> Plane:
	"""Fit the table plane to a depth frame (on a 4x subsample)."""
	d = np.asarray(depth_m, dtype=np.float32)
	i = intrinsics
	sub = deproject(d[::4, ::4], Intrinsics(i.fx / 4, i.fy / 4, i.ppx / 4, i.ppy / 4))
	return fit_table_plane(sub[sub[..., 2] > 0])


def table_heights(depth_m: np.ndarray, intrinsics: Intrinsics, plane: Plane) -> np.ndarray:
	"""Height of every pixel above ``plane`` in metres, NaN where depth is missing."""
	d = np.asarray(depth_m, dtype=np.float32)
	heights = height_above(deproject(d, intrinsics), plane)
	heights[~(np.isfinite(d) & (d > 0))] = np.nan
	return heights


def resolve_plane(
	depth_m: np.ndarray,
	intrinsics: Intrinsics,
	*,
	saved: Plane | None,
	tilt_tol_deg: float = PLANE_TILT_TOL_DEG,
	offset_tol_m: float = PLANE_OFFSET_TOL_M,
	min_inliers: float = MIN_PLANE_INLIERS,
) -> Plane:
	"""The table plane to hold for a run: ``saved`` when a fresh fit agrees with it, else the fresh fit.

	Raises
	------
	ValueError
		When the fresh fit is poor (no clear table in view) or differs from ``saved`` beyond the tolerances
		(the camera moved, which would change the encoding within a dataset).
	"""
	fresh = fit_plane(depth_m, intrinsics)
	if fresh.inlier_fraction < min_inliers:
		raise ValueError(
			f"no clear table plane: {fresh.inlier_fraction:.0%} of points on it, need {min_inliers:.0%}; clear the table"
		)
	if saved is None:
		return fresh
	tilt = tilt_deg(fresh.normal, saved.normal)
	shift = abs(fresh.offset - saved.offset)
	if tilt > tilt_tol_deg or shift > offset_tol_m:
		raise ValueError(
			f"camera moved since the plane was saved: {tilt:.1f} deg, {shift * 1000:.0f} mm "
			f"(allowed {tilt_tol_deg} deg, {offset_tol_m * 1000:.0f} mm); start a new dataset with a new plane file"
		)
	return saved


def save_plane(path: Path, plane: Plane) -> None:
	"""Write ``plane`` as JSON, creating the parent directory."""
	path.parent.mkdir(parents=True, exist_ok=True)
	data = {"normal": plane.normal.tolist(), "offset": plane.offset, "inlier_fraction": plane.inlier_fraction}
	path.write_text(json.dumps(data, indent=1))


def load_plane(path: Path) -> Plane:
	"""Read a plane written by :func:`save_plane`."""
	data = json.loads(path.read_text())
	return Plane(
		normal=np.asarray(data["normal"], dtype=np.float64),
		offset=float(data["offset"]),
		inlier_fraction=float(data["inlier_fraction"]),
	)


def crop(image: np.ndarray, box: tuple[int, int, int, int]) -> np.ndarray:
	"""Cut ``box`` = (x, y, width, height) pixels out of ``image``, at their own size."""
	x, y, w, h = box
	if x < 0 or y < 0 or w <= 0 or h <= 0 or x + w > image.shape[1] or y + h > image.shape[0]:
		raise ValueError(f"crop box {box} does not fit a {image.shape[1]}x{image.shape[0]} image")
	return image[y : y + h, x : x + w]


def make_stream_handler(buffers: dict[str, FrameBuffer]) -> type[BaseHTTPRequestHandler]:
	"""HTTP handler serving each buffer as ``/<name>.mjpg`` (multipart stream) and ``/<name>.jpg`` (one frame)."""

	class Handler(BaseHTTPRequestHandler):
		def log_message(self, format: str, *args: object) -> None:
			logger.debug(format, *args)

		def do_GET(self) -> None:
			match = _PATH.match(self.path.split("?", 1)[0])
			if not match or match.group(1) not in buffers:
				self.send_error(404)
				return
			buffer = buffers[match.group(1)]
			if match.group(2) == "jpg":
				frame = buffer.latest()
				if frame.jpeg is None:
					self.send_error(503, "no frame yet")
					return
				self.send_response(200)
				self.send_header("Content-Type", "image/jpeg")
				self.send_header("Content-Length", str(len(frame.jpeg)))
				self.send_header("Cache-Control", "no-store")
				self.end_headers()
				self.wfile.write(frame.jpeg)
				return
			self._stream(buffer)

		def _stream(self, buffer: FrameBuffer) -> None:
			self.send_response(200)
			self.send_header("Content-Type", "multipart/x-mixed-replace; boundary=frame")
			self.send_header("Cache-Control", "no-store")
			self.end_headers()
			last = 0
			try:
				while True:
					frame = buffer.wait_newer(last, STREAM_WAIT_S)
					if frame is None or frame.jpeg is None:
						continue
					last = frame.frame_id
					self.wfile.write(
						b"--frame\r\nContent-Type: image/jpeg\r\nX-Timestamp: "
						+ f"{frame.published_at:.6f}".encode()
						+ b"\r\nContent-Length: "
						+ str(len(frame.jpeg)).encode()
						+ b"\r\n\r\n"
						+ frame.jpeg
						+ b"\r\n"
					)
					self.wfile.flush()
			except (BrokenPipeError, ConnectionResetError):
				logger.debug("stream client left")

	return Handler


def encode_jpeg(image_bgr: np.ndarray, quality: int) -> bytes:
	"""JPEG with 4:4:4 chroma, so per-channel detail keeps full resolution."""
	params = [cv2.IMWRITE_JPEG_QUALITY, quality, cv2.IMWRITE_JPEG_SAMPLING_FACTOR, cv2.IMWRITE_JPEG_SAMPLING_FACTOR_444]
	ok, buf = cv2.imencode(".jpg", image_bgr, params)
	if not ok:
		raise RuntimeError("JPEG encoding failed")
	return buf.tobytes()


def run_bridge(
	read_frame: Callable[[], tuple[np.ndarray, np.ndarray, Intrinsics | None]],
	buffers: dict[str, FrameBuffer],
	*,
	mode: str = "layers",
	near_m: float = 0.40,
	far_m: float = 1.00,
	max_height_m: float = 0.10,
	fine_max_m: float = 0.04,
	coarse_max_m: float = 0.30,
	plane: Plane | None = None,
	crop_box: tuple[int, int, int, int] | None = None,
	quality: int = 90,
	stop: Callable[[], bool] = lambda: False,
) -> None:
	"""Publish colour and the depth image from ``read_frame`` (``(color_bgr, depth_m, intrinsics)``) until ``stop()``.

	The height modes use ``plane``, or the plane fitted on the first frame, for the whole run.
	"""
	if mode not in MODES:
		raise ValueError(f"mode must be one of {MODES}")
	count, since = 0, time.monotonic()
	stages = np.zeros(3)  # camera read (incl. alignment and filters), depth image, JPEG encode + publish; seconds
	while not stop():
		t0 = time.perf_counter()
		color, depth, intrinsics = read_frame()
		t1 = time.perf_counter()
		if mode == "distance":
			depth_img = colorize_depth(depth, near_m=near_m, far_m=far_m)
		else:
			if plane is None:
				plane = resolve_plane(depth, intrinsics, saved=None)
				logger.info("table plane fitted and held: %.0f%% inliers", plane.inlier_fraction * 100)
			heights = table_heights(depth, intrinsics, plane)
			if mode == "layers":
				depth_img = layered_height_image(heights, fine_max_m=fine_max_m, coarse_max_m=coarse_max_m)
			else:
				depth_img = height_image(heights, max_m=max_height_m)
		if crop_box is not None:
			color, depth_img = crop(color, crop_box), crop(depth_img, crop_box)
		t2 = time.perf_counter()
		buffers["top"].publish(encode_jpeg(color, quality), {})
		buffers["top_depth"].publish(encode_jpeg(depth_img, quality), {})
		stages += (t1 - t0, t2 - t1, time.perf_counter() - t2)
		count += 1
		if time.monotonic() - since >= 10.0:
			ms = stages / count * 1000
			logger.info(
				"bridge: %.1f fps; per frame: camera read %.1f ms, depth image %.1f ms, encode+publish %.1f ms",
				count / (time.monotonic() - since),
				*ms,
			)
			count, since, stages = 0, time.monotonic(), np.zeros(3)


def main(argv: list[str] | None = None) -> None:
	"""``sorter-depth-bridge``: own the D415 and serve colour and depth streams for Studio."""
	import threading

	from defect_sorter.realsense import FILTER_PROFILES, VISUAL_PRESETS, D415Camera

	parser = argparse.ArgumentParser(description="Serve the D415 colour and depth as MJPEG streams for Studio")
	parser.add_argument("--host", required=True, help="bind address; use the Tailscale IP, never 0.0.0.0")
	parser.add_argument("--port", type=int, default=8092)
	parser.add_argument("--size", type=int, nargs=2, default=[640, 480], metavar=("W", "H"))
	parser.add_argument("--fps", type=int, default=30)
	parser.add_argument("--mode", choices=MODES, default="layers", help="depth image kind")
	parser.add_argument("--fine-max", type=float, default=0.04, help="layers mode: metres drawn as 255 in R")
	parser.add_argument("--coarse-max", type=float, default=0.30, help="layers mode: metres drawn as 255 in G")
	parser.add_argument(
		"--max-height", type=float, default=0.10, help="height mode: metres above the table drawn white"
	)
	parser.add_argument("--near", type=float, default=0.40, help="distance mode: metres drawn as white")
	parser.add_argument("--far", type=float, default=1.00, help="distance mode: metres drawn as darkest grey")
	parser.add_argument(
		"--plane", type=Path, help="height modes: table plane file, saved on first use and checked on every later start"
	)
	parser.add_argument(
		"--crop", type=int, nargs=4, metavar=("X", "Y", "W", "H"), help="pixel box cut from colour and depth"
	)
	parser.add_argument("--filters", choices=FILTER_PROFILES, default="motion", help="camera depth filter profile")
	parser.add_argument("--preset", choices=VISUAL_PRESETS, help="D400 visual preset (default: camera setting)")
	parser.add_argument("--quality", type=int, default=90, help="JPEG quality")
	args = parser.parse_args(argv)
	logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

	with D415Camera(args.size[0], args.size[1], args.fps, filters=args.filters, preset=args.preset) as camera:

		def read() -> tuple[np.ndarray, np.ndarray, Intrinsics]:
			frame = camera.read()
			return frame.color_bgr, frame.depth_m, frame.intrinsics

		plane = None
		if args.mode != "distance":
			saved = load_plane(args.plane) if args.plane is not None and args.plane.exists() else None
			_, depth, intrinsics = read()
			try:
				plane = resolve_plane(depth, intrinsics, saved=saved)
			except ValueError as exc:
				raise SystemExit(f"sorter-depth-bridge: {exc}") from None
			if args.plane is not None and saved is None:
				save_plane(args.plane, plane)
			logger.info(
				"table plane %s: %.0f%% inliers, camera %.0f mm above it",
				f"from {args.plane}"
				if saved is not None
				else "fitted now" + (f", saved to {args.plane}" if args.plane else ""),
				plane.inlier_fraction * 100,
				plane.offset * 1000,
			)
		logger.info(
			"depth image: %s mode (fine %.2f m, coarse %.2f m, height %.2f m), crop %s, filters %s, preset %s; "
			"keep these fixed for a dataset",
			args.mode,
			args.fine_max,
			args.coarse_max,
			args.max_height,
			args.crop,
			args.filters,
			args.preset,
		)
		buffers = {"top": FrameBuffer(), "top_depth": FrameBuffer()}
		server = ThreadingHTTPServer((args.host, args.port), make_stream_handler(buffers))
		server.daemon_threads = True
		threading.Thread(target=server.serve_forever, daemon=True).start()
		logger.info("streams on http://%s:%d/top.mjpg and /top_depth.mjpg", args.host, args.port)
		try:
			run_bridge(
				read,
				buffers,
				mode=args.mode,
				near_m=args.near,
				far_m=args.far,
				max_height_m=args.max_height,
				fine_max_m=args.fine_max,
				coarse_max_m=args.coarse_max,
				plane=plane,
				crop_box=tuple(args.crop) if args.crop else None,
				quality=args.quality,
			)
		except KeyboardInterrupt:
			logger.info("stopped")
		finally:
			server.shutdown()


if __name__ == "__main__":
	main()
