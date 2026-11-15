"""Serve the dashboard, host telemetry and an optional Physical AI Studio link on one origin.

Without ``--studio-url`` the server is read-only. With it, camera previews, the inspector and Studio's lists are
proxied through :class:`~defect_sorter.studio_link.StudioHub`. Runs that move the arm additionally need
``--studio-control`` on the command line; the browser cannot enable them.
"""

from __future__ import annotations

import argparse
import json
import logging
import mimetypes
import re
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import TYPE_CHECKING, Any
from urllib.parse import unquote, urlsplit

from defect_sorter.system_metrics import SystemMetrics

if TYPE_CHECKING:
	from defect_sorter.studio_link import StudioHub

_LOGGER = logging.getLogger(__name__)


_MAX_BODY = 16 * 1024


def make_handler(
	frontend: Path, metrics: SystemMetrics, telemetry_file: Path | None = None, studio: Any = None
) -> type[BaseHTTPRequestHandler]:
	"""Build a read-only handler with a shared one-second resource sample cache.

	Parameters
	----------
	frontend : Path
		Directory containing the dashboard's static files.
	metrics : SystemMetrics
		Counter sampler shared across HTTP requests.
	telemetry_file : Path or None
		Optional backend-written snapshot; the browser validates its v1 contract.
	studio : StudioHub or None
		Physical AI Studio link; Studio routes answer 204/404 without it.

	Returns
	-------
	type of BaseHTTPRequestHandler
		Handler for static files, resource samples and optional sorting snapshots.
	"""
	root = frontend.resolve()
	lock = threading.Lock()
	cached: bytes | None = None
	sampled_at = float("-inf")

	class Handler(BaseHTTPRequestHandler):
		def _send(
			self,
			status: int,
			body: bytes = b"",
			content_type: str = "application/json",
			headers: dict[str, str] | None = None,
		) -> None:
			self.send_response(status)
			self.send_header("Content-Type", content_type)
			self.send_header("Content-Length", str(len(body)))
			self.send_header("Cache-Control", "no-store")
			self.send_header("X-Content-Type-Options", "nosniff")
			for name, value in (headers or {}).items():
				self.send_header(name, value)
			self.end_headers()
			self.wfile.write(body)

		def do_GET(self) -> None:
			nonlocal cached, sampled_at
			path = unquote(urlsplit(self.path).path)
			if path == "/api/system":
				with lock:
					now = time.monotonic()
					if cached is None or now - sampled_at >= 1:
						cached = json.dumps(metrics.sample(), allow_nan=False).encode()
						sampled_at = now
					body = cached
				self._send(200, body)
				return
			if path.startswith("/api/studio/"):
				self._studio_get(path)
				return
			if path == "/api/telemetry":
				if telemetry_file is None or not telemetry_file.exists():
					self._send(204)
					return
				try:
					body = json.dumps(json.loads(telemetry_file.read_text()), allow_nan=False).encode()
				except (OSError, ValueError, UnicodeError):
					self._send(503, b'{"error":"Snapshot unavailable"}')
					return
				self._send(200, body)
				return
			file = (root / ("index.html" if path == "/" else path.lstrip("/"))).resolve()
			if not file.is_relative_to(root) or file.suffix not in {
				".html",
				".css",
				".mjs",
				".svg",
				".png",
				".webp",
				".jpg",
				".mp3",
				".wav",
				".mp4",
				".vtt",
				".woff2",
			}:
				self._send(404)
				return
			try:
				body = file.read_bytes()
			except OSError:
				self._send(404)
				return
			mime = {".mjs": "text/javascript", ".woff2": "font/woff2"}.get(file.suffix) or mimetypes.guess_type(
				file.name
			)[0]
			headers = {"Accept-Ranges": "bytes"}
			status = 200
			if requested := self.headers.get("Range"):
				match = re.fullmatch(r"bytes=(\d*)-(\d*)", requested)
				size = len(body)
				if match and any(match.groups()):
					first, last = match.groups()
					start = int(first) if first else max(0, size - int(last))
					end = min(size - 1, int(last)) if first and last else size - 1
				else:
					start, end = size, -1
				if not 0 <= start <= end < size:
					self._send(416, headers={"Content-Range": f"bytes */{size}"})
					return
				headers["Content-Range"] = f"bytes {start}-{end}/{size}"
				body = body[start : end + 1]
				status = 206
			self._send(status, body, mime or "application/octet-stream", headers)

		def _json(self, status: int, value: Any) -> None:
			self._send(status, json.dumps(value, allow_nan=False).encode())

		def _studio_get(self, path: str) -> None:
			if studio is None:
				self._send(204 if path == "/api/studio/state" else 404)
				return
			if path == "/api/studio/state":
				self._json(200, studio.state())
				return
			if path == "/api/studio/inspection/crop.jpg":
				crop = studio.crop_jpeg
				self._send(204) if crop is None else self._send(200, crop, "image/jpeg")
				return
			match = re.fullmatch(r"/api/studio/frame/([A-Za-z0-9_-]{1,64})\.jpg", path)
			if not match:
				self._send(404)
				return
			frame = studio.frame(match.group(1))
			if frame is None:
				self._send(204)
				return
			age_ms = max(0, round((time.time() - frame.received_at) * 1000))
			self._send(
				200,
				frame.jpeg,
				"image/jpeg",
				{"X-Frame-Sequence": str(frame.sequence), "X-Frame-Age-Ms": str(age_ms)},
			)

		def do_POST(self) -> None:
			path = unquote(urlsplit(self.path).path)
			routes = {"/api/studio/run", "/api/studio/stop", "/api/studio/inspect"}
			if studio is None or path not in routes:
				self._send(404)
				return
			# Commands need a JSON body and a custom header, which a cross-site page cannot send without a CORS
			# preflight this server never answers; a browser-sent Origin must also be this server.
			origin = self.headers.get("Origin")
			same_origin = origin is None or urlsplit(origin).netloc == self.headers.get("Host")
			if (
				self.headers.get("X-Armigo-Request") != "1"
				or not (self.headers.get("Content-Type") or "").startswith("application/json")
				or not same_origin
			):
				self._json(403, {"error": "commands need a same-origin JSON request from the dashboard"})
				return
			try:
				length = int(self.headers.get("Content-Length") or 0)
				if not 0 <= length <= _MAX_BODY:
					raise ValueError("body too large")
				body = json.loads(self.rfile.read(length) or b"{}")
				if not isinstance(body, dict):
					raise ValueError("body must be a JSON object")
			except (ValueError, UnicodeError) as error:
				self._json(400, {"error": str(error)})
				return
			if path == "/api/studio/stop":
				self._json(200, studio.stop_run())
			elif path == "/api/studio/inspect":
				self._json(*studio.inspect(str(body.get("camera_id"))))
			else:
				self._json(*studio.start_run(body))

		def log_message(self, format: str, *args: object) -> None:
			_LOGGER.debug(format, *args)

	return Handler


def _studio_hub(args: argparse.Namespace) -> StudioHub | None:
	"""Build the Studio link and the optional live inspector from the command line."""
	if not args.studio_url:
		return None
	from defect_sorter.studio_link import StudioClient, StudioHub

	inspector = None
	if args.anomaly_model or args.purity:
		from defect_sorter.live_inspection import LiveInspector, purity_scorer

		if args.anomaly_model:
			from defect_sorter.inspection import OpenVinoScorer

			scorer = OpenVinoScorer(args.anomaly_model, args.anomaly_device)
			inspector = LiveInspector(scorer, args.threshold, args.band, device=args.anomaly_device, model=scorer.name)
		else:
			inspector = LiveInspector(purity_scorer(), args.threshold, args.band, device="CPU", model="colour-purity")
	if args.studio_control:
		_LOGGER.warning("Arm control is ON: the dashboard can start Studio policy runs (limit %s s).", args.max_run_s)
	return StudioHub(
		StudioClient(args.studio_url),
		args.studio_project,
		control_enabled=args.studio_control,
		inspector=inspector,
		max_run_s=args.max_run_s,
		hz=args.run_hz,
	)


def main() -> None:
	"""Run the local dashboard server without opening cameras or robot devices."""
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument("--host", default="127.0.0.1")
	parser.add_argument("--port", type=int, default=8080)
	parser.add_argument("--frontend", type=Path, default=Path("frontend"))
	parser.add_argument("--telemetry-file", type=Path, help="Backend-written snapshot v1 JSON (read only)")
	studio = parser.add_argument_group("Physical AI Studio")
	studio.add_argument("--studio-url", help="Studio base URL, for example http://127.0.0.1:7860")
	studio.add_argument("--studio-project", help="Studio project id (default: the first project)")
	studio.add_argument(
		"--studio-control",
		action="store_true",
		help="Allow the dashboard to start policy runs that MOVE THE ARM (operator present at the cell)",
	)
	studio.add_argument("--max-run-s", type=float, default=60, help="Each run holds the arm after this many seconds")
	studio.add_argument("--run-hz", type=float, default=30, help="Action rate of a run")
	inspect = parser.add_argument_group("Live inspection")
	inspect.add_argument("--anomaly-model", type=Path, help="Anomalib OpenVINO export (model.xml)")
	inspect.add_argument("--anomaly-device", default="CPU", help="OpenVINO device: CPU, GPU or NPU")
	inspect.add_argument("--purity", action="store_true", help="Use the colour-purity baseline instead of a model")
	inspect.add_argument("--threshold", type=float, default=0.5, help="Defect threshold of the live inspector")
	inspect.add_argument("--band", type=float, default=0.0, help="Half-width of the uncertain band")
	args = parser.parse_args()
	if not (args.frontend / "index.html").is_file():
		parser.error("Frontend not found; run from the checkout root or set --frontend.")
	logging.basicConfig(level=logging.INFO)
	server = ThreadingHTTPServer(
		(args.host, args.port), make_handler(args.frontend, SystemMetrics(), args.telemetry_file, _studio_hub(args))
	)
	_LOGGER.info("Dashboard: http://%s:%s/", args.host, args.port)
	try:
		server.serve_forever()
	except KeyboardInterrupt:
		pass
	finally:
		server.server_close()


if __name__ == "__main__":
	main()
