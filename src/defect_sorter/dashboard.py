"""Serve the dashboard and read-only host telemetry on one origin."""

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
from urllib.parse import unquote, urlsplit

from defect_sorter.system_metrics import SystemMetrics

_LOGGER = logging.getLogger(__name__)


def make_handler(
	frontend: Path, metrics: SystemMetrics, telemetry_file: Path | None = None
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
			}:
				self._send(404)
				return
			try:
				body = file.read_bytes()
			except OSError:
				self._send(404)
				return
			mime = "text/javascript" if file.suffix == ".mjs" else mimetypes.guess_type(file.name)[0]
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

		def log_message(self, format: str, *args: object) -> None:
			_LOGGER.debug(format, *args)

	return Handler


def main() -> None:
	"""Run the local dashboard server without opening cameras or robot devices."""
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument("--host", default="127.0.0.1")
	parser.add_argument("--port", type=int, default=8080)
	parser.add_argument("--frontend", type=Path, default=Path("frontend"))
	parser.add_argument("--telemetry-file", type=Path, help="Backend-written snapshot v1 JSON (read only)")
	args = parser.parse_args()
	if not (args.frontend / "index.html").is_file():
		parser.error("Frontend not found; run from the checkout root or set --frontend.")
	logging.basicConfig(level=logging.INFO)
	server = ThreadingHTTPServer(
		(args.host, args.port), make_handler(args.frontend, SystemMetrics(), args.telemetry_file)
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
