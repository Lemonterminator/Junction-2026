"""Serve the dashboard, host telemetry, an optional Physical AI Studio link and the cell link on one origin.

Without ``--studio-url`` and ``--bridge`` the server is read-only. With ``--studio-url``, camera previews, the
inspector and Studio's lists are proxied through :class:`~defect_sorter.studio_link.StudioHub`. With ``--bridge`` the
table is measured from the depth bridge and, with ``--hybrid-command``, the hybrid sort cycle runs under the
dashboard (:class:`~defect_sorter.cell_link.CellHub`), inspecting each show view on the ``--inspect-camera``.
Anything that moves the arm additionally needs ``--studio-control`` (Studio runs) or ``--cell-control`` (the cycle)
on the command line; the browser cannot enable them. ``POST /api/stop`` stops both.
"""

from __future__ import annotations

import argparse
import contextlib
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
	from defect_sorter.cell_link import CellHub
	from defect_sorter.studio_link import StudioHub

_LOGGER = logging.getLogger(__name__)


_MAX_BODY = 16 * 1024


class DashboardServer(ThreadingHTTPServer):
	"""The dashboard's HTTP server: a deep listen backlog and daemon request threads.

	A page load opens one connection per module, poll and image at once (HTTP/1.0, no keep-alive). The standard
	backlog of 5 makes the operating system refuse some of them, and one refused module fetch leaves a blank page
	without Live mode or its STOP button.
	"""

	request_queue_size = 128
	daemon_threads = True


def make_handler(
	frontend: Path,
	metrics: SystemMetrics,
	telemetry_file: Path | None = None,
	studio: Any = None,
	*,
	cell: Any = None,
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
	cell : CellHub or None
		Table measurement and the hybrid cycle; cell routes answer 204/404 without it.

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
			if path.startswith("/api/cell/"):
				self._cell_get(path)
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

		def _cell_get(self, path: str) -> None:
			if cell is None:
				self._send(204 if path == "/api/cell/state" else 404)
				return
			if path == "/api/cell/state":
				self._json(200, cell.state())
				return
			if path == "/api/cell/table.jpg":
				jpeg = cell.table_jpeg()
				self._send(204) if jpeg is None else self._send(200, jpeg, "image/jpeg")
				return
			match = re.fullmatch(r"/api/cell/view/(\d{1,2})\.jpg", path)
			if not match:
				self._send(404)
				return
			crop = cell.view_crop(int(match.group(1)))
			self._send(204) if crop is None else self._send(200, crop, "image/jpeg")

		def do_POST(self) -> None:
			path = unquote(urlsplit(self.path).path)
			studio_routes = {"/api/studio/run", "/api/studio/stop", "/api/studio/inspect"}
			cell_routes = {"/api/cell/cycle", "/api/cell/stop", "/api/cell/review"}
			known = (
				path == "/api/stop"
				or (studio is not None and path in studio_routes)
				or (cell is not None and path in cell_routes)
			)
			if not known:
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
			if path == "/api/stop":
				# STOP reaches everything that may hold the arm, whichever view the page is in
				stopping = [link.stop_run()["stopping"] for link in (studio,) if link is not None]
				stopping += [link.stop()["stopping"] for link in (cell,) if link is not None]
				self._json(200, {"stopping": any(stopping)})
			elif path == "/api/studio/stop":
				self._json(200, studio.stop_run())
			elif path == "/api/studio/inspect":
				self._json(*studio.inspect(str(body.get("camera_id"))))
			elif path == "/api/studio/run":
				if cell is not None and cell.active():
					self._json(409, {"error": "a hybrid cycle holds the arm; stop it first"})
				else:
					self._json(*studio.start_run(body))
			elif path == "/api/cell/cycle":
				self._json(*cell.start(body))
			elif path == "/api/cell/stop":
				self._json(200, cell.stop())
			else:
				self._json(*cell.review(body))

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
		max_frame_age_s=args.max_frame_age_s,
		evidence_ttl_s=args.evidence_ttl_s,
	)


VIEW_SETTLE_S = 0.5
"""A show view is scored on a frame received this long after the arm reported it still (camera latency, settling)."""


def _cell_hub(args: argparse.Namespace, studio: StudioHub | None) -> CellHub | None:
	"""Build the table watcher and the hybrid cycle supervisor from the command line."""
	if not (args.bridge or args.hybrid_command):
		return None
	import functools
	import shlex

	from defect_sorter.cell_link import CellHub, TableWatcher, measure_frame

	table = None
	if args.bridge:
		from defect_sorter.depth_bridge import fetch_raw

		base_xy = base_mm = None
		if args.calibration is not None and args.calibration.is_file():
			from defect_sorter.robot_pose import load_calibration

			base = load_calibration(args.calibration).base_position_m
			base_xy, base_mm = base[:2], [round(float(v) * 1000, 1) for v in base]
		measure = functools.partial(
			measure_frame, frame_file=args.frame_file, exclude_xy_m=base_xy, robot_base_mm=base_mm
		)
		table = TableWatcher(functools.partial(fetch_raw, args.bridge), measure)
		table.start()

	inspect_view = keepalive = info = None
	if studio is not None and args.inspect_models:
		from defect_sorter.live_inspection import CameraModelInspector, load_camera_models

		models = load_camera_models(args.inspect_models, args.inspect_device)
		names = dict(entry.split("=", 1) for entry in args.camera_map)
		view_inspector = CameraModelInspector(
			models, device=args.inspect_device, model=f"{args.inspect_models.parent.name} ({', '.join(models)})"
		)
		info = {"model": view_inspector.model, "device": args.inspect_device, "thresholds": view_inspector.thresholds}

		def view_cameras() -> dict[str, str | None]:
			return {key: studio.camera_id(names.get(key, key)) for key in models}

		def inspect_view(name: str) -> dict[str, Any]:
			newer = time.time() + VIEW_SETTLE_S
			frames: dict[str, list[bytes]] = {}
			for key, camera_id in view_cameras().items():
				found = (
					[]
					if camera_id is None
					else studio.fresh_frames(camera_id, newer_than=newer, count=args.view_frames, timeout_s=6.0)
				)
				frames[key] = [f.jpeg for f in found]
			return view_inspector.inspect(frames)

		def keepalive() -> None:
			for camera_id in view_cameras().values():
				if camera_id is not None:
					studio.frame(camera_id)

	elif studio is not None and studio.inspector is not None:
		live = studio.inspector
		info = {
			"model": getattr(live, "model", None),
			"device": getattr(live, "device", None),
			"thresholds": {"normal_below": live.threshold - live.band, "defective_above": live.threshold + live.band},
		}

		def camera() -> str:
			camera_id = studio.camera_id(args.inspect_camera)
			if camera_id is None:
				raise OSError(f"Studio has no camera named {args.inspect_camera!r} (set --inspect-camera)")
			return camera_id

		def inspect_view(name: str) -> dict[str, Any]:
			status, body = studio.inspect_fresh(camera(), newer_than=time.time() + VIEW_SETTLE_S, timeout_s=6.0)
			if status != 200:
				raise OSError(body.get("error", f"inspection refused ({status})"))
			return body | {"crop_jpeg": studio.crop_jpeg}

		def keepalive() -> None:
			with contextlib.suppress(OSError):
				studio.frame(camera())

	if args.cell_control:
		_LOGGER.warning("Arm control is ON: the dashboard can start hybrid sort cycles (sorter-hybrid --go).")
	return CellHub(
		hybrid_command=shlex.split(args.hybrid_command) if args.hybrid_command else None,
		control_enabled=args.cell_control,
		table=table,
		inspect_view=inspect_view,
		busy=(lambda: studio.run_active()) if studio is not None else (lambda: False),
		keepalive=keepalive,
		inspector_info=info,
		unsure_bowl=None if args.unsure_to == "ask" else args.unsure_to,
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
	studio.add_argument(
		"--max-frame-age-s", type=float, default=1.0, help="Oldest camera frame accepted as inspection evidence"
	)
	studio.add_argument(
		"--evidence-ttl-s",
		type=float,
		default=2.0,
		help="Inspect-then-sort holds the arm if its session frame is older than this when control would start",
	)
	inspect = parser.add_argument_group("Live inspection")
	inspect.add_argument("--anomaly-model", type=Path, help="Anomalib OpenVINO export (model.xml)")
	inspect.add_argument("--anomaly-device", default="CPU", help="OpenVINO device: CPU, GPU or NPU")
	inspect.add_argument("--purity", action="store_true", help="Use the colour-purity baseline instead of a model")
	inspect.add_argument("--threshold", type=float, default=0.5, help="Defect threshold of the live inspector")
	inspect.add_argument("--band", type=float, default=0.0, help="Half-width of the uncertain band")
	cell = parser.add_argument_group("Cell (depth bridge and hybrid sort cycle)")
	cell.add_argument("--bridge", metavar="URL", help="running sorter-depth-bridge, http://host:port (read only)")
	cell.add_argument(
		"--frame-file", type=Path, default=Path("data/depth/table-frame.json"), help="held table frame (read only)"
	)
	cell.add_argument(
		"--calibration",
		type=Path,
		default=Path("data/calibration/robot.json"),
		help="robot calibration: the base is drawn on the map and never taken for a brick (optional)",
	)
	cell.add_argument(
		"--hybrid-command",
		help="the sorter-hybrid command without --go/--bowl/--control (quoted), e.g. "
		"'docker exec -i <studio container> python -m defect_sorter.hybrid --port ... --bridge ... --model ...'",
	)
	cell.add_argument(
		"--cell-control",
		action="store_true",
		help="Allow the dashboard to run the hybrid cycle with --go, which MOVES THE ARM (operator present)",
	)
	cell.add_argument(
		"--inspect-models",
		type=Path,
		help="per-camera anomaly models for the show views: a training summary.json "
		'({"cameras": {"front": {"export": ..., "threshold": ...}, ...}}); needs the anomaly extra',
	)
	cell.add_argument("--inspect-device", default="CPU", help="OpenVINO device of --inspect-models: CPU, GPU or NPU")
	cell.add_argument(
		"--camera-map",
		nargs="*",
		default=[],
		metavar="KEY=NAME",
		help="Studio camera name for a model's camera key when they differ, e.g. front=Webcam",
	)
	cell.add_argument("--view-frames", type=int, default=3, help="frames per camera scored in each show view")
	cell.add_argument(
		"--inspect-camera",
		default="front",
		help="without --inspect-models: the Studio camera (name or id) the live inspector scores in each show view",
	)
	cell.add_argument(
		"--unsure-to",
		choices=("ask", "pink"),
		default="ask",
		help="an unsure brick waits for a person (ask) or goes to the reject bowl (pink); never to green",
	)
	args = parser.parse_args()
	if not (args.frontend / "index.html").is_file():
		parser.error("Frontend not found; run from the checkout root or set --frontend.")
	if args.hybrid_command and " -i " not in f" {args.hybrid_command} " and args.hybrid_command.startswith("docker"):
		parser.error("--hybrid-command through docker exec needs -i, or STOP cannot reach the cycle")
	if any("=" not in entry for entry in args.camera_map):
		parser.error("--camera-map takes KEY=NAME pairs")
	logging.basicConfig(level=logging.INFO)
	studio_hub = _studio_hub(args)
	server = DashboardServer(
		(args.host, args.port),
		make_handler(args.frontend, SystemMetrics(), args.telemetry_file, studio_hub, cell=_cell_hub(args, studio_hub)),
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
