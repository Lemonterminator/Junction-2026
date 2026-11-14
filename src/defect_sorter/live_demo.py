"""Live perception demo: D415 → :func:`detect_scene` → annotated frames and JSON state over HTTP.

Run on the workstation::

	uv run sorter-live-demo --host 100.76.18.70 --port 8090

then open ``http://100.76.18.70:8090/``. Bind to the Tailscale address, not ``0.0.0.0``: the page has no auth.
"""

from __future__ import annotations

import argparse
import logging
import threading
import time
from http.server import ThreadingHTTPServer

import cv2
import numpy as np

from defect_sorter.geometry import Plane
from defect_sorter.scene import Scene, SceneConfig, detect_scene
from defect_sorter.webview import FrameBuffer, make_handler, page_html

logger = logging.getLogger(__name__)


def scene_state(scene: Scene, fps: float) -> dict:
	"""JSON-serialisable summary of a scene."""
	return {
		"t": time.time(),
		"fps": round(fps, 1),
		"table": {"dist_m": round(scene.plane.offset, 3), "inlier_frac": round(scene.plane.inlier_fraction, 2)},
		"objects": [
			{
				"px": [round(o.px[0]), round(o.px[1])],
				"bbox": list(o.bbox),
				"height_m": round(o.height_m, 3),
				"xyz_cam_m": [round(c, 3) for c in o.xyz_cam_m],
				"in_bowl": o.in_bowl,
			}
			for o in scene.objects
		],
		"bowls": [
			{
				"colour": b.colour,
				"hue": round(b.hue, 1),
				"px": [round(b.px[0]), round(b.px[1])],
				"xyz_cam_m": [round(c, 3) for c in b.xyz_cam_m],
			}
			for b in scene.bowls
		],
	}


def render(color_bgr: np.ndarray, scene: Scene, config: SceneConfig, fps: float) -> np.ndarray:
	"""Colour view with detections next to a height map."""
	h, w = scene.height_m.shape
	vis = color_bgr.copy()
	left, top, right, bottom = config.roi_margin
	cv2.rectangle(vis, (int(left * w), int(top * h)), (int((1 - right) * w), int((1 - bottom) * h)), (255, 255, 0), 1)
	for b in scene.bowls:
		cv2.ellipse(vis, b.ellipse, (255, 0, 255), 2)
		cv2.putText(
			vis, f"bowl {b.colour}", (int(b.px[0]) - 40, int(b.px[1])), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 2
		)
	for o in scene.objects:
		x, y = o.bbox[0], o.bbox[1]
		cv2.drawContours(vis, [o.contour], -1, (0, 255, 0), 2)
		label = f"object {o.height_m * 100:.1f}cm" + (f" -> in {o.in_bowl} bowl" if o.in_bowl else "")
		cv2.putText(vis, label, (x, max(15, y - 6)), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 0), 2)
	cv2.putText(
		vis,
		f"{fps:.1f} fps  table {scene.plane.offset:.2f} m",
		(10, h - 10),
		cv2.FONT_HERSHEY_SIMPLEX,
		0.55,
		(255, 255, 255),
		2,
	)

	hm = cv2.applyColorMap(np.clip(scene.height_m / 0.10 * 255, 0, 255).astype(np.uint8), cv2.COLORMAP_TURBO)
	hm[~scene.valid] = 0
	dim = scene.rim_mask & scene.valid
	hm[dim] = (hm[dim] * 0.4).astype(np.uint8)
	cv2.putText(hm, "height above table (0-10 cm)", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)
	return np.hstack([vis, hm])


class LiveScene:
	"""Background loop that reads the camera, detects the scene and publishes the annotated frame and state."""

	def __init__(self, camera, config: SceneConfig) -> None:
		self._camera = camera
		self._config = config
		self._plane: Plane | None = None
		self.refit_requested = True
		self.buffer = FrameBuffer()
		self._fps = 0.0

	def step(self) -> None:
		t0 = time.perf_counter()
		frame = self._camera.read()
		plane = None if self.refit_requested or self._plane is None else self._plane
		scene = detect_scene(frame.color_bgr, frame.depth_m, frame.intrinsics, plane=plane, config=self._config)
		self._plane, self.refit_requested = scene.plane, False
		dt = time.perf_counter() - t0
		self._fps = 0.9 * self._fps + 0.1 / dt if self._fps else 1 / dt
		ok, buf = cv2.imencode(
			".jpg", render(frame.color_bgr, scene, self._config, self._fps), [cv2.IMWRITE_JPEG_QUALITY, 80]
		)
		self.buffer.publish(buf.tobytes() if ok else None, scene_state(scene, self._fps))

	def request_refit(self) -> None:
		self.refit_requested = True

	def run_forever(self) -> None:
		while True:
			try:
				self.step()
			except Exception:
				logger.exception("perception step failed")
				time.sleep(0.5)


def main(argv: list[str] | None = None) -> None:
	"""Start the camera loop and the HTTP server."""
	parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
	parser.add_argument("--host", default="127.0.0.1", help="bind address; use the Tailscale IP, never 0.0.0.0")
	parser.add_argument("--port", type=int, default=8090)
	args = parser.parse_args(argv)
	logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

	from defect_sorter.realsense import D415Camera

	live = LiveScene(D415Camera(), SceneConfig())
	threading.Thread(target=live.run_forever, daemon=True).start()
	logger.info("serving on http://%s:%d/", args.host, args.port)
	page = page_html("Top camera: depth objects + colour bowls", {"refit": "Refit table plane"})
	ThreadingHTTPServer(
		(args.host, args.port), make_handler(live.buffer, page, {"refit": live.request_refit})
	).serve_forever()


if __name__ == "__main__":
	main()
