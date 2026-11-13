"""Live perception demo: D415 → :func:`detect_scene` → annotated MJPEG stream and JSON state over HTTP.

Run on the workstation::

	uv run sorter-live-demo --host 100.76.18.70 --port 8090

then open ``http://100.76.18.70:8090/``. Bind to the Tailscale address, not ``0.0.0.0``: the page has no auth.
"""

from __future__ import annotations

import argparse
import json
import logging
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import cv2
import numpy as np

from defect_sorter.geometry import Plane
from defect_sorter.scene import Scene, SceneConfig, detect_scene

logger = logging.getLogger(__name__)

PAGE = b"""<!doctype html><html><head><meta charset=utf-8><title>Scene perception</title>
<style>body{font-family:system-ui;background:#111;color:#eee;margin:16px}img{max-width:100%;border:1px solid #333}
pre{background:#1b1b1b;padding:12px;font-size:13px;max-height:40vh;overflow:auto}button{padding:6px 12px;margin:8px 0}</style></head>
<body><h3>Top camera: depth objects + colour bowls</h3><img src="/stream"><br>
<button onclick="fetch('/refit',{method:'POST'})">Refit table plane</button><pre id=s></pre>
<script>setInterval(async()=>{try{document.getElementById('s').textContent=JSON.stringify(await (await fetch('/state')).json(),null,1)}catch(e){}},500)</script>
</body></html>"""


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
	"""Background loop that reads the camera, detects the scene and keeps the latest JPEG and state."""

	def __init__(self, camera, config: SceneConfig) -> None:
		self._camera = camera
		self._config = config
		self._plane: Plane | None = None
		self._lock = threading.Lock()
		self.refit_requested = True
		self.jpeg: bytes | None = None
		self.state: dict = {}
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
		with self._lock:
			if ok:
				self.jpeg = buf.tobytes()
			self.state = scene_state(scene, self._fps)

	def snapshot(self) -> tuple[bytes | None, dict]:
		with self._lock:
			return self.jpeg, self.state

	def run_forever(self) -> None:
		while True:
			try:
				self.step()
			except Exception:
				logger.exception("perception step failed")
				time.sleep(0.5)


def make_handler(live: LiveScene) -> type[BaseHTTPRequestHandler]:
	"""HTTP handler serving the page, ``/stream`` (MJPEG), ``/state`` (JSON) and ``POST /refit``."""

	class Handler(BaseHTTPRequestHandler):
		def log_message(self, format: str, *args: object) -> None:
			logger.debug(format, *args)

		def do_GET(self) -> None:
			if self.path == "/":
				self._send(200, "text/html", PAGE)
			elif self.path == "/state":
				self._send(200, "application/json", json.dumps(live.snapshot()[1]).encode())
			elif self.path == "/stream":
				self.send_response(200)
				self.send_header("Content-Type", "multipart/x-mixed-replace; boundary=f")
				self.end_headers()
				try:
					while True:
						jpg, _ = live.snapshot()
						if jpg:
							self.wfile.write(
								b"--f\r\nContent-Type: image/jpeg\r\nContent-Length: "
								+ str(len(jpg)).encode()
								+ b"\r\n\r\n"
								+ jpg
								+ b"\r\n"
							)
						time.sleep(0.07)
				except (BrokenPipeError, ConnectionResetError):
					return
			else:
				self.send_error(404)

		def do_POST(self) -> None:
			if self.path == "/refit":
				live.refit_requested = True
				self.send_response(204)
				self.end_headers()
			else:
				self.send_error(404)

		def _send(self, code: int, content_type: str, body: bytes) -> None:
			self.send_response(code)
			self.send_header("Content-Type", content_type)
			self.end_headers()
			self.wfile.write(body)

	return Handler


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
	ThreadingHTTPServer((args.host, args.port), make_handler(live)).serve_forever()


if __name__ == "__main__":
	main()
