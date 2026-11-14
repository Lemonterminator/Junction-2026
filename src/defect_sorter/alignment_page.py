"""Live alignment page for the top camera: camera tilt, marker poses, and drift from a saved reference.

Run on the workstation (stop the live demo first; only one process can open the D415)::

	uv run sorter-alignment --host <tailscale-ip> --port 8091

Shows the camera's tilt against the table (adjust the mount until it reads near 0), every known marker with its
position, yaw and tilt relative to the table, and, once a reference is saved, whether each marker moved.
Presentation only: detection is :mod:`defect_sorter.markers`, depth refinement and comparison are
:mod:`defect_sorter.alignment`.
"""

from __future__ import annotations

import argparse
import json
import logging
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import cv2
import numpy as np

from defect_sorter.alignment import (
	MarkerPose,
	compare_to_reference,
	load_reference,
	refine_with_depth,
	save_reference,
	tilt_deg,
)
from defect_sorter.geometry import CameraTilt, Intrinsics, Plane, camera_tilt, deproject, fit_table_plane
from defect_sorter.markers import detect_markers

logger = logging.getLogger(__name__)

REFIT_EVERY = 15  # frames between table-plane fits
DISPLAY_WIDTH = 960

PAGE = b"""<!doctype html><html><head><meta charset=utf-8><title>Cell alignment</title>
<style>body{font-family:system-ui;background:#111;color:#eee;margin:16px}img{max-width:100%;border:1px solid #333}
button{padding:6px 12px;margin:8px 8px 8px 0}pre{background:#1b1b1b;padding:12px;font-size:13px;max-height:45vh;overflow:auto}
.ok{color:#6c6}.bad{color:#f66}</style></head>
<body><h3>Cell alignment (top camera)</h3><img src="/stream"><br>
<button onclick="fetch('/reference',{method:'POST'}).then(()=>0)">Save reference</button>
<button onclick="fetch('/refit',{method:'POST'})">Refit table</button>
<pre id=s></pre>
<script>setInterval(async()=>{try{document.getElementById('s').textContent=JSON.stringify(await (await fetch('/state')).json(),null,1)}catch(e){}},700)</script>
</body></html>"""


def _fmt_tilt(t: CameraTilt) -> str:
	return (
		f"camera tilt {t.total_deg:.1f} deg (far edge: {t.far_edge}; pitch {t.pitch_deg:+.1f}, roll {t.roll_deg:+.1f})"
	)


class AlignmentView:
	"""Background loop: read the camera, fit the table, detect markers, compare with the reference."""

	def __init__(self, camera, reference_path: Path) -> None:
		self._camera = camera
		self._reference_path = reference_path
		self._reference = load_reference(reference_path) if reference_path.exists() else {}
		self._plane: Plane | None = None
		self._frames = 0
		self._lock = threading.Lock()
		self._poses: dict[int, MarkerPose] = {}
		self.refit_requested = True
		self.save_requested = False
		self.jpeg: bytes | None = None
		self.state: dict = {}

	def step(self) -> None:
		frame = self._camera.read()
		if self.refit_requested or self._plane is None or self._frames % REFIT_EVERY == 0:
			pts = deproject(frame.depth_m[::4, ::4], _scaled(frame.intrinsics, 0.25))
			valid = pts[..., 2] > 0
			if valid.sum() > 1000:
				self._plane = fit_table_plane(pts[valid])
			self.refit_requested = False
		self._frames += 1

		detections = detect_markers(frame.color_bgr, frame.intrinsics)
		poses = {d.id: refine_with_depth(d, frame.depth_m, frame.intrinsics) for d in detections}
		if self.save_requested and poses:
			save_reference(self._reference_path, poses)
			self._reference = dict(poses)
			self.save_requested = False
			logger.info("saved reference with %d markers to %s", len(poses), self._reference_path)
		deltas = compare_to_reference(poses, self._reference) if self._reference else {}
		tilt = camera_tilt(self._plane) if self._plane is not None else None

		vis = frame.color_bgr.copy()
		for d in detections:
			delta = deltas.get(d.id)
			colour = (0, 200, 255) if delta is None else ((0, 0, 255) if delta.moved else (0, 220, 0))
			cv2.polylines(vis, [np.round(d.corners_px).astype(np.int32)], True, colour, 2)
			cv2.arrowedLine(
				vis,
				tuple(np.round(d.corners_px.mean(0)).astype(int)),
				tuple(np.round((d.corners_px[1] + d.corners_px[2]) / 2).astype(int)),
				colour,
				2,
			)
			cv2.putText(
				vis,
				f"{d.id} {d.use}",
				tuple(np.round(d.corners_px[0] + (0, -8)).astype(int)),
				cv2.FONT_HERSHEY_SIMPLEX,
				0.6,
				colour,
				2,
			)
		lines = [_fmt_tilt(tilt) if tilt else "camera tilt: no table depth yet"]
		lines.append(f"reference: {len(self._reference)} markers" if self._reference else "reference: none saved")
		for i, text in enumerate(lines):
			cv2.putText(vis, text, (12, 30 + 30 * i), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 4)
			cv2.putText(vis, text, (12, 30 + 30 * i), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
		scale = DISPLAY_WIDTH / vis.shape[1]
		ok, buf = cv2.imencode(".jpg", cv2.resize(vis, None, fx=scale, fy=scale), [cv2.IMWRITE_JPEG_QUALITY, 80])

		state = {
			"t": time.time(),
			"camera_tilt": None
			if tilt is None
			else {
				"total_deg": round(tilt.total_deg, 2),
				"pitch_deg": round(tilt.pitch_deg, 2),
				"roll_deg": round(tilt.roll_deg, 2),
				"far_edge": tilt.far_edge,
			},
			"table_distance_m": None if self._plane is None else round(self._plane.offset, 4),
			"markers": [
				{
					"id": p.id,
					"use": p.use,
					"position_mm": [round(v * 1000, 1) for v in p.position_m],
					"yaw_deg": round(p.yaw_deg, 2),
					"tilt_vs_table_deg": None
					if self._plane is None
					else round(tilt_deg(p.normal, self._plane.normal), 2),
					"source": p.source,
					"delta": None
					if p.id not in deltas
					else {
						"moved": deltas[p.id].moved,
						"shift_mm": round(deltas[p.id].shift_mm, 1),
						"yaw_deg": round(deltas[p.id].yaw_deg, 2),
					},
				}
				for p in poses.values()
			],
			"missing_from_reference": [d.id for d in deltas.values() if d.missing],
		}
		with self._lock:
			if ok:
				self.jpeg = buf.tobytes()
			self.state = state
			self._poses = poses

	def snapshot(self) -> tuple[bytes | None, dict]:
		with self._lock:
			return self.jpeg, self.state

	def run_forever(self) -> None:
		while True:
			try:
				self.step()
			except Exception:
				logger.exception("alignment step failed")
				time.sleep(0.5)


def _scaled(intr: Intrinsics, factor: float) -> Intrinsics:
	return Intrinsics(fx=intr.fx * factor, fy=intr.fy * factor, ppx=intr.ppx * factor, ppy=intr.ppy * factor)


def make_handler(view: AlignmentView) -> type[BaseHTTPRequestHandler]:
	"""HTTP handler: page, ``/stream`` (MJPEG), ``/state`` (JSON), ``POST /reference`` and ``POST /refit``."""

	class Handler(BaseHTTPRequestHandler):
		def log_message(self, format: str, *args: object) -> None:
			logger.debug(format, *args)

		def do_GET(self) -> None:
			if self.path == "/":
				self._send(200, "text/html", PAGE)
			elif self.path == "/state":
				self._send(200, "application/json", json.dumps(view.snapshot()[1]).encode())
			elif self.path == "/stream":
				self.send_response(200)
				self.send_header("Content-Type", "multipart/x-mixed-replace; boundary=f")
				self.end_headers()
				try:
					while True:
						jpg, _ = view.snapshot()
						if jpg:
							self.wfile.write(
								b"--f\r\nContent-Type: image/jpeg\r\nContent-Length: "
								+ str(len(jpg)).encode()
								+ b"\r\n\r\n"
								+ jpg
								+ b"\r\n"
							)
						time.sleep(0.1)
				except (BrokenPipeError, ConnectionResetError):
					return
			else:
				self.send_error(404)

		def do_POST(self) -> None:
			if self.path == "/reference":
				view.save_requested = True
			elif self.path == "/refit":
				view.refit_requested = True
			else:
				self.send_error(404)
				return
			self.send_response(204)
			self.end_headers()

		def _send(self, code: int, content_type: str, body: bytes) -> None:
			self.send_response(code)
			self.send_header("Content-Type", content_type)
			self.end_headers()
			self.wfile.write(body)

	return Handler


def main(argv: list[str] | None = None) -> None:
	"""Start the camera loop and the HTTP server."""
	parser = argparse.ArgumentParser(description="Live alignment page for the top camera")
	parser.add_argument("--host", default="127.0.0.1", help="bind address; use the Tailscale IP, never 0.0.0.0")
	parser.add_argument("--port", type=int, default=8091)
	parser.add_argument("--reference", type=Path, default=Path("data/alignment/reference.json"))
	args = parser.parse_args(argv)
	logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

	from defect_sorter.realsense import D415Camera

	view = AlignmentView(D415Camera(1280, 720, 15, depth_size=(640, 480)), args.reference)
	threading.Thread(target=view.run_forever, daemon=True).start()
	logger.info("serving on http://%s:%d/", args.host, args.port)
	ThreadingHTTPServer((args.host, args.port), make_handler(view)).serve_forever()


if __name__ == "__main__":
	main()
