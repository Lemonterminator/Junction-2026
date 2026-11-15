"""Read Physical AI Studio's cameras and sessions, and run one fixed sorting task through a Studio runtime session.

The dashboard talks to Studio over Studio's own HTTP and websocket API, so Studio stays the only owner of the arm
and the cameras:

* :class:`CameraRelay` watches one camera through ``/api/cameras/ws`` (the preview Studio's own UI uses) and keeps
  the newest JPEG. It connects only while someone is looking and releases the camera after ``idle_s``. Studio refuses
  the preview while a runtime session holds the camera; the relay reports that error instead of retrying fast.
* :class:`PolicyRun` opens one runtime session (``/api/projects/<id>/runtime/ws``), loads a saved environment and a
  model export, and sets model control with one of the fixed task texts the policy was trained on
  (:func:`task_for_action`). It stops on a request, on its time limit, or on any failed component, and it then sets
  control to ``None`` (Studio holds the arm where it is). It never retries motion.

:class:`WebSocket` is a small RFC 6455 client (``ws://`` and ``wss://``) so the default install needs no extra
dependency. Every network-facing class takes a connect factory, so tests replace the socket with a script.
"""

from __future__ import annotations

import base64
import contextlib
import hashlib
import json
import logging
import os
import select
import socket
import ssl
import struct
import threading
import time
import urllib.request
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, Protocol
from urllib.parse import quote, urlsplit

from defect_sorter.closed_loop import DEFAULT_TASKS

logger = logging.getLogger(__name__)

_GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
_MAX_MESSAGE = 64 * 1024 * 1024
ACTIONS: dict[str, str] = {"SORT_GREEN": "normal", "SORT_PINK": "defective"}
"""Prompt actions that may move the arm, mapped to the defect label whose fixed task they run."""


class WebSocketClosedError(ConnectionError):
	"""The server closed the websocket."""


class MessageSocket(Protocol):
	"""What relays and runs need from a websocket; :class:`WebSocket` and test scripts implement it."""

	def recv(self, timeout: float | None = None) -> tuple[bool, bytes] | None: ...

	def send_text(self, text: str) -> None: ...

	def close(self) -> None: ...


class WebSocket:
	"""Blocking websocket client: whole messages in, masked text frames out, pings answered.

	Parameters
	----------
	sock : socket.socket
		Connected socket after a successful upgrade.
	buffered : bytes
		Bytes the server sent after its handshake response.
	"""

	def __init__(self, sock: socket.socket, buffered: bytes = b"") -> None:
		self._sock = sock
		self._buffer = bytearray(buffered)
		self._fragments: bytearray | None = None
		self._fragment_text = False
		self._send_lock = threading.Lock()

	@classmethod
	def connect(cls, url: str, timeout: float = 5.0) -> WebSocket:
		"""Open ``url`` (``ws://`` or ``wss://``) and complete the upgrade handshake.

		Raises
		------
		ConnectionError
			If the server does not switch protocols or answers with a wrong accept key.
		"""
		parts = urlsplit(url)
		secure = parts.scheme == "wss"
		port = parts.port or (443 if secure else 80)
		sock = socket.create_connection((parts.hostname, port), timeout=timeout)
		if secure:
			sock = ssl.create_default_context().wrap_socket(sock, server_hostname=parts.hostname)
		key = base64.b64encode(os.urandom(16)).decode()
		target = parts.path or "/"
		if parts.query:
			target += "?" + parts.query
		sock.sendall(
			(
				f"GET {target} HTTP/1.1\r\nHost: {parts.hostname}:{port}\r\nUpgrade: websocket\r\n"
				f"Connection: Upgrade\r\nSec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n"
			).encode()
		)
		response = b""
		while b"\r\n\r\n" not in response:
			chunk = sock.recv(4096)
			if not chunk:
				sock.close()
				raise ConnectionError("websocket handshake: connection closed")
			response += chunk
			if len(response) > 65536:
				sock.close()
				raise ConnectionError("websocket handshake: header too large")
		head, rest = response.split(b"\r\n\r\n", 1)
		lines = head.decode("latin-1").split("\r\n")
		if " 101 " not in lines[0] + " ":
			sock.close()
			raise ConnectionError(f"websocket handshake refused: {lines[0]}")
		headers = {
			name.strip().lower(): value.strip() for name, _, value in (line.partition(":") for line in lines[1:])
		}
		expected = base64.b64encode(hashlib.sha1((key + _GUID).encode(), usedforsecurity=False).digest()).decode()
		if headers.get("sec-websocket-accept") != expected:
			sock.close()
			raise ConnectionError("websocket handshake: wrong accept key")
		sock.settimeout(None)
		return cls(sock, rest)

	def _parse_frame(self) -> tuple[bool, int, bytes] | None:
		"""Take one complete frame from the buffer, or None while it is still incomplete (nothing is consumed)."""
		buf = self._buffer
		if len(buf) < 2:
			return None
		b0, b1 = buf[0], buf[1]
		length, offset = b1 & 0x7F, 2
		if length == 126:
			if len(buf) < 4:
				return None
			length, offset = struct.unpack(">H", buf[2:4])[0], 4
		elif length == 127:
			if len(buf) < 10:
				return None
			length, offset = struct.unpack(">Q", buf[2:10])[0], 10
		if length > _MAX_MESSAGE:
			raise WebSocketClosedError("message too large")
		mask = None
		if b1 & 0x80:
			if len(buf) < offset + 4:
				return None
			mask, offset = bytes(buf[offset : offset + 4]), offset + 4
		if len(buf) < offset + length:
			return None
		payload = bytes(buf[offset : offset + length])
		del buf[: offset + length]
		if mask:
			payload = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
		return bool(b0 & 0x80), b0 & 0x0F, payload

	def _send_frame(self, opcode: int, payload: bytes) -> None:
		head = bytes([0x80 | opcode])
		n = len(payload)
		if n < 126:
			head += bytes([0x80 | n])
		elif n < 65536:
			head += bytes([0x80 | 126]) + struct.pack(">H", n)
		else:
			head += bytes([0x80 | 127]) + struct.pack(">Q", n)
		mask = os.urandom(4)
		masked = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
		with self._send_lock:
			self._sock.sendall(head + mask + masked)

	def send_text(self, text: str) -> None:
		"""Send one text message."""
		self._send_frame(0x1, text.encode())

	def recv(self, timeout: float | None = None) -> tuple[bool, bytes] | None:
		"""Return the next whole message as ``(is_text, payload)``, or None when ``timeout`` seconds pass first.

		The wait is bounded as a whole: pings are answered and partial frames or fragmented messages are kept in
		the buffer for the next call, so a caller can check its own stop conditions between calls without losing
		data. ``timeout=None`` waits indefinitely.

		Raises
		------
		WebSocketClosedError
			On a close frame or a closed connection.
		"""
		deadline = None if timeout is None else time.monotonic() + timeout
		while True:
			while (frame := self._parse_frame()) is not None:
				fin, opcode, payload = frame
				if opcode == 0x8:
					raise WebSocketClosedError("closed by server")
				if opcode == 0x9:
					self._send_frame(0xA, payload)
					continue
				if opcode == 0xA:
					continue
				if opcode in (0x1, 0x2):
					self._fragments, self._fragment_text = bytearray(payload), opcode == 0x1
				elif self._fragments is None:
					raise WebSocketClosedError("continuation frame without a message")
				else:
					self._fragments += payload
				if len(self._fragments) > _MAX_MESSAGE:
					raise WebSocketClosedError("message too large")
				if fin:
					message, self._fragments = bytes(self._fragments), None
					return self._fragment_text, message
			remaining = None if deadline is None else deadline - time.monotonic()
			if remaining is not None and remaining <= 0:
				return None
			pending = getattr(self._sock, "pending", None)
			if not (pending and pending()):
				ready, _, _ = select.select([self._sock], [], [], remaining)
				if not ready:
					return None
			chunk = self._sock.recv(65536)
			if not chunk:
				raise WebSocketClosedError("connection closed")
			self._buffer += chunk

	def close(self) -> None:
		"""Send a close frame (best effort) and close the socket."""
		with contextlib.suppress(OSError):
			self._send_frame(0x8, b"")
		self._sock.close()


def parse_observation(payload: bytes) -> tuple[dict[str, Any], dict[str, bytes]]:
	"""Split a runtime observation: ``[u32 header length][header JSON][JPEGs in the order of frames]``.

	Raises
	------
	ValueError
		If the message is shorter than its header says.
	"""
	if len(payload) < 4:
		raise ValueError("observation too short")
	(size,) = struct.unpack(">I", payload[:4])
	header = json.loads(payload[4 : 4 + size])
	offset = 4 + size
	frames: dict[str, bytes] = {}
	for frame in header.get("frames", []):
		end = offset + int(frame["size"])
		if end > len(payload):
			raise ValueError("observation body shorter than its frames")
		frames[frame["key"]] = payload[offset:end]
		offset = end
	return header, frames


@dataclass(frozen=True)
class Frame:
	"""One received JPEG with the local receive time (Unix seconds) and a per-source sequence number."""

	jpeg: bytes
	received_at: float
	sequence: int


class CameraRelay:
	"""Keep the newest preview frame of one Studio camera while someone is watching.

	Parameters
	----------
	connect : callable
		Opens the preview socket for this camera.
	clock : callable
		Wall clock in Unix seconds.
	idle_s : float
		Release the camera when no frame was requested for this long.
	"""

	def __init__(
		self, connect: Callable[[], MessageSocket], clock: Callable[[], float] = time.time, idle_s: float = 15.0
	) -> None:
		self._connect = connect
		self._clock = clock
		self.idle_s = idle_s
		self._frame: Frame | None = None
		self._requested_at = float("-inf")
		self._lock = threading.Lock()
		self.status = "idle"
		self.error: str | None = None
		self._stop = threading.Event()
		self._thread: threading.Thread | None = None

	def latest(self) -> Frame | None:
		"""The newest frame, or None; asking keeps the relay connected."""
		with self._lock:
			self._requested_at = self._clock()
			return self._frame

	def peek(self) -> Frame | None:
		"""The newest frame without counting as a viewer."""
		with self._lock:
			return self._frame

	def wanted(self) -> bool:
		"""Whether a viewer asked for frames within ``idle_s``."""
		return self._clock() - self._requested_at <= self.idle_s

	def receive_frame(self, jpeg: bytes) -> None:
		"""Keep ``jpeg`` as the newest frame and mark the camera live."""
		with self._lock:
			sequence = self._frame.sequence + 1 if self._frame else 1
			self._frame = Frame(jpeg, self._clock(), sequence)
		self.status, self.error = "live", None

	def run_once(self) -> None:
		"""Connect once and receive until the socket closes, an error arrives or nobody is watching."""
		self.status = "connecting"
		try:
			ws = self._connect()
		except OSError as error:
			self.status, self.error = "error", f"Studio unreachable: {error}"
			return
		try:
			# Viewer expiry is checked on every iteration, so a stream that never pauses is still released.
			while not self._stop.is_set() and self.wanted():
				message = ws.recv(0.5)
				if message is None:
					continue
				is_text, payload = message
				if is_text:
					try:
						message = json.loads(payload)
					except ValueError:
						continue
					if message.get("event") == "error":
						self.status, self.error = "error", str(message.get("message", "camera error"))
						return
					continue
				self.receive_frame(payload)
		except WebSocketClosedError:
			if self.status != "error":
				self.status = "idle"
		except OSError as error:
			self.status, self.error = "error", str(error)
		finally:
			ws.close()
		if self.status == "live":
			self.status = "idle"

	def start(self, retry_s: float = 3.0) -> None:
		"""Run in a background thread: connect while wanted, wait ``retry_s`` after an error."""
		if self._thread is not None:
			return

		def loop() -> None:
			while not self._stop.is_set():
				if self.wanted():
					self.run_once()
					if self.status == "error":
						self._stop.wait(retry_s)
				else:
					self._stop.wait(0.2)

		self._thread = threading.Thread(target=loop, name="studio-camera-relay", daemon=True)
		self._thread.start()

	def stop(self) -> None:
		"""Stop the background thread."""
		self._stop.set()


def environment_draft(environment: dict[str, Any]) -> dict[str, Any]:
	"""Studio's ``EnvironmentDraft`` for a saved environment, as Studio's own UI builds it."""
	robots = []
	for entry in environment.get("robots") or []:
		tele = entry.get("tele_operator") or {"type": "none"}
		robots.append(
			{
				"robot_id": entry["robot"]["id"],
				"tele_operator": {"type": "robot", "robot_id": tele["robot_id"]}
				if tele.get("type") == "robot"
				else {"type": "none"},
			}
		)
	return {
		"id": environment["id"],
		"name": environment["name"],
		"robots": robots,
		"cameras": [{"camera_id": camera["id"]} for camera in environment.get("cameras") or [] if camera.get("id")],
	}


def task_for_action(action: str) -> tuple[str, str]:
	"""Bowl and fixed task text for a sorting action; anything else is refused.

	Raises
	------
	ValueError
		If ``action`` is not one of :data:`ACTIONS`.
	"""
	if action not in ACTIONS:
		raise ValueError(f"not a sorting action: {action!r}")
	return DEFAULT_TASKS[ACTIONS[action]]


@dataclass
class RunTimings:
	"""Measured milliseconds of a run's phases; None until a phase finished."""

	connect_ms: float | None = None
	environment_ms: float | None = None
	model_ms: float | None = None
	first_observation_ms: float | None = None


@dataclass
class _Pending:
	request_id: str
	command: str
	sent_at: float


class PolicyRun:
	"""One runtime session that runs a model on one fixed task, then holds the arm.

	Parameters
	----------
	connect : callable
		Opens the project's runtime session socket.
	environment : dict
		``EnvironmentDraft`` to load (see :func:`environment_draft`).
	model : dict
		``model_id``, ``backend`` and ``device`` of the export to load.
	task : str or None
		Fixed task text (from :func:`task_for_action`); None when ``before_control`` chooses it.
	hz : float
		Action rate Studio takes from the model's queue.
	max_s : float
		The run sets control to None after this many seconds of model control.
	clock : callable
		Monotonic seconds.
	before_control : callable or None
		Called with the run after the model is loaded and right before control is enabled. It may set ``task``
		(for example from an inspection of a fresh session frame) and returns None to go ahead or a reason to hold
		the arm still; a hold ends the run without enabling control.
	"""

	def __init__(
		self,
		connect: Callable[[], MessageSocket],
		*,
		environment: dict[str, Any],
		model: dict[str, Any],
		task: str | None,
		hz: float = 30,
		max_s: float = 60,
		clock: Callable[[], float] = time.monotonic,
		wall_clock: Callable[[], float] = time.time,
		before_control: Callable[[PolicyRun], str | None] | None = None,
	) -> None:
		self._connect = connect
		self.environment = environment
		self.model = model
		self.task = task
		self.hz = hz
		self.max_s = max_s
		self._clock = clock
		self._wall = wall_clock
		self._before_control = before_control
		self._ws: MessageSocket | None = None
		self._stop = threading.Event()
		self._lock = threading.Lock()
		self.phase = "starting"
		self.reason: str | None = None
		self.started_at = clock()
		self.running_since: float | None = None
		self.timings = RunTimings()
		self.joints: dict[str, float] | None = None
		self.action: dict[str, float] | None = None
		self.frames: dict[str, Frame] = {}
		self.observations = 0
		self.session: dict[str, Any] | None = None
		self.statuses: dict[str, str] = {}

	# -- protocol ---------------------------------------------------------------------------------
	def _send(self, command: str, **fields: Any) -> _Pending:
		if self._ws is None:
			raise OSError("runtime session is not connected")
		request_id = uuid.uuid4().hex
		self._ws.send_text(json.dumps({"command": command, "request_id": request_id, **fields}))
		return _Pending(request_id, command, self._clock())

	def _handle(self, is_text: bool, payload: bytes) -> dict[str, Any] | None:
		"""Record one server message; return it when it is JSON."""
		if not is_text:
			header, frames = parse_observation(payload)
			now = self._wall()
			with self._lock:
				if header.get("state") is not None:
					self.joints = header["state"]
				if header.get("action") is not None:
					self.action = header["action"]
				for key, jpeg in frames.items():
					previous = self.frames.get(key)
					self.frames[key] = Frame(jpeg, now, previous.sequence + 1 if previous else 1)
				self.observations += 1
			if self.timings.first_observation_ms is None and self.running_since is not None:
				self.timings.first_observation_ms = (self._clock() - self.running_since) * 1000
			return None
		message = json.loads(payload)
		kind = message.get("type")
		if kind == "state":
			self.session = message.get("data")
		elif kind == "status":
			self.statuses[message.get("component", "?")] = message.get("state", "?")
			if message.get("state") == "failed":
				self._fail(f"{message.get('component')}: {message.get('error') or 'failed'}")
		elif kind == "error":
			self._fail(str(message.get("message", "session error")))
		return message

	def _await_ack(self, pending: _Pending, timeout_s: float = 120, cancellable: bool = True) -> dict[str, Any] | None:
		"""Wait for the ack of ``pending``; None on failure, timeout, or (when cancellable) a stop request."""
		if self._ws is None:
			raise OSError("runtime session is not connected")
		while self._clock() - pending.sent_at < timeout_s:
			if self.phase == "failed" or (cancellable and self._stop.is_set()):
				return None
			received = self._ws.recv(0.2)
			if received is None:
				continue
			message = self._handle(*received)
			if message and message.get("type") == "ack" and message.get("request_id") == pending.request_id:
				return message
		self._fail(f"{pending.command} did not finish in time")
		return None

	def wait_for_frame(self, key: str, newer_than: float, timeout_s: float) -> Frame | None:
		"""Receive until camera ``key`` has a frame received after ``newer_than`` (Unix seconds), or give up.

		Returns None on timeout, stop request or failure.
		"""
		if self._ws is None:
			return None
		deadline = self._clock() + timeout_s
		while True:
			with self._lock:
				frame = self.frames.get(key)
			if frame is not None and frame.received_at > newer_than:
				return frame
			remaining = deadline - self._clock()
			if remaining <= 0 or self._stop.is_set() or self.phase == "failed":
				return None
			received = self._ws.recv(min(0.1, remaining))
			if received is not None:
				self._handle(*received)

	def _fail(self, reason: str) -> None:
		if self.phase not in ("failed", "stopped", "held"):
			logger.warning("policy run stopping: %s", reason)
			self.phase, self.reason = "failed", reason

	def _load(self, command: str, phase: str, **fields: Any) -> bool:
		self.phase = phase
		ack = self._await_ack(self._send(command, **fields))
		if ack is None:
			return False
		if not ack.get("ok"):
			self._fail((ack.get("error") or {}).get("message", f"{command} refused"))
			return False
		return True

	# -- lifecycle --------------------------------------------------------------------------------
	def step_until_running(self) -> None:
		"""Connect, load environment and model, and start model control; stops at the first refusal."""
		t0 = self._clock()
		try:
			self._ws = self._connect()
		except OSError as error:
			self._fail(f"Studio unreachable: {error}")
			return
		self.timings.connect_ms = (self._clock() - t0) * 1000
		try:
			t = self._clock()
			if not self._load("load_environment", "loading_environment", environment=self.environment):
				self._end_before_motion()
				return
			self.timings.environment_ms = (self._clock() - t) * 1000
			t = self._clock()
			if not self._load("load_model", "loading_model", **self.model):
				self._end_before_motion()
				return
			self.timings.model_ms = (self._clock() - t) * 1000
			if self._before_control is not None:
				self.phase = "checking"
				hold = self._before_control(self)
				if self._stop.is_set() or self.phase == "failed":
					self._end_before_motion()
					return
				if hold is None and not self.task:
					hold = "no task was chosen"
				if hold is not None:
					self.phase, self.reason = "held", hold
					self._close()
					return
			if self._stop.is_set():
				self._finish("stopped before motion")
				return
			control = {
				"type": "model",
				"task": self.task,
				"hz": self.hz,
				"execution": {"mode": "sync", "request_threshold": 0.5},
				"grace_s": 3,
			}
			if not self._load("set_control", "starting_control", control=control):
				self._release()
				return
			self.phase = "running"
			self.running_since = self._clock()
		except (OSError, ValueError) as error:
			self._fail(str(error))
			self._release()

	def _end_before_motion(self) -> None:
		"""End a run whose control was never enabled: stopped on request, else keep the failure reason."""
		if self._stop.is_set() and self.phase != "failed":
			self._finish("stopped before motion")
		else:
			self._close()

	def pump(self, budget_s: float = 0.0) -> None:
		"""Receive what is waiting; stop on request, time limit or failure."""
		if self._ws is None or self.phase not in ("running", "failed"):
			return
		deadline = self._clock() + budget_s
		try:
			while self.phase == "running":
				if self._stop.is_set():
					self._finish("stopped by operator")
					return
				if self.running_since is not None and self._clock() - self.running_since >= self.max_s:
					self._finish(f"time limit of {self.max_s:g} s reached")
					return
				# recv is bounded, so pings or a half-received frame cannot delay STOP or the time limit.
				received = self._ws.recv(max(0.0, min(0.2, deadline - self._clock())))
				if received is None:
					if self._clock() >= deadline:
						return
					continue
				self._handle(*received)
		except (OSError, ValueError) as error:
			self._fail(str(error))
		if self.phase == "failed":
			self._release()

	def _finish(self, reason: str) -> None:
		self.phase, self.reason = "stopping", reason
		self._release()
		if self.phase == "stopping":
			self.phase = "stopped"

	def _release(self) -> None:
		"""Hold the arm (control None) and close the session; best effort after a failure."""
		if self._ws is None:
			return
		try:
			self._await_ack(self._send("set_control", control=None), timeout_s=5, cancellable=False)
		except (OSError, ValueError):
			logger.exception("could not release control")
		self._close()

	def _close(self) -> None:
		if self._ws is not None:
			self._ws.close()
			self._ws = None

	def request_stop(self) -> None:
		"""Ask the run to hold the arm and end at the next step."""
		self._stop.set()

	def run(self) -> None:
		"""Blocking: start, then pump until the run ends."""
		self.step_until_running()
		while self.phase == "running":
			self.pump(0.5)
		self._close()

	def snapshot(self) -> dict[str, Any]:
		"""JSON-ready summary for the dashboard."""
		with self._lock:
			frames = {key: {"sequence": f.sequence, "received_at": f.received_at} for key, f in self.frames.items()}
			joints = dict(self.joints) if self.joints else None
		running_s = None if self.running_since is None else round(self._clock() - self.running_since, 2)
		return {
			"phase": self.phase,
			"reason": self.reason,
			"task": self.task,
			"model": self.model,
			"running_s": running_s,
			"max_s": self.max_s,
			"timings_ms": {k: None if v is None else round(v, 1) for k, v in vars(self.timings).items()},
			"joints": joints,
			"frames": frames,
			"observations": self.observations,
			"statuses": dict(self.statuses),
		}


@dataclass
class StudioClient:
	"""Studio's REST API at ``base_url`` (for example ``http://127.0.0.1:7860``)."""

	base_url: str
	timeout: float = 5.0
	_ws_base: str = field(init=False)

	def __post_init__(self) -> None:
		self.base_url = self.base_url.rstrip("/")
		self._ws_base = "ws" + self.base_url[4:] if self.base_url.startswith("http") else self.base_url

	def get_json(self, path: str) -> Any:
		"""GET ``path`` and decode JSON."""
		with urllib.request.urlopen(self.base_url + path, timeout=self.timeout) as response:  # noqa: S310 - configured URL
			return json.loads(response.read())

	def ws_url(self, path: str) -> str:
		"""Websocket URL for ``path``."""
		return self._ws_base + path

	def camera_socket(self, camera: dict[str, Any]) -> WebSocket:
		"""Open Studio's preview socket for one project camera."""
		return WebSocket.connect(self.ws_url("/api/cameras/ws?camera=" + quote(json.dumps(camera))), self.timeout)

	def runtime_socket(self, project_id: str, hz: float = 10) -> WebSocket:
		"""Open a new runtime session for ``project_id``."""
		return WebSocket.connect(self.ws_url(f"/api/projects/{project_id}/runtime/ws?hz={hz:g}"), self.timeout)


class StudioHub:
	"""The dashboard's view of one Studio project: cached lists, camera relays, inspection and at most one run.

	Parameters
	----------
	client : StudioClient
		Studio API access (replaceable in tests).
	project_id : str or None
		Project to show; the first project when None.
	control_enabled : bool
		Whether :meth:`start_run` may move the arm. Set only by the operator's command line, never by a request.
	inspector : object or None
		Has ``inspect_jpeg(bytes) -> dict`` (a :class:`~defect_sorter.live_inspection.LiveInspector`).
	max_run_s, hz : float
		Time limit and action rate of each run.
	run_factory : callable
		Builds the run (``PolicyRun`` signature).
	background : bool
		Start relays and runs on threads; tests drive them directly.
	clock : callable
		Wall clock in Unix seconds.
	max_frame_age_s : float
		Oldest camera frame :meth:`inspect` accepts as evidence.
	evidence_ttl_s : float
		Oldest inspection evidence that may enable model control in ``INSPECT_AND_SORT``.
	frame_wait_s : float
		How long ``INSPECT_AND_SORT`` waits for a fresh session frame after the model is loaded.
	"""

	LIST_TTL_S = 5.0
	ACTIVE_PHASES = (
		"starting",
		"loading_environment",
		"loading_model",
		"checking",
		"starting_control",
		"running",
		"stopping",
	)

	def __init__(
		self,
		client: Any,
		project_id: str | None,
		*,
		control_enabled: bool = False,
		inspector: Any = None,
		max_run_s: float = 60,
		hz: float = 30,
		run_factory: Callable[..., Any] = PolicyRun,
		background: bool = True,
		clock: Callable[[], float] = time.time,
		max_frame_age_s: float = 1.0,
		evidence_ttl_s: float = 2.0,
		frame_wait_s: float = 3.0,
	) -> None:
		self.client = client
		self.max_frame_age_s = max_frame_age_s
		self.evidence_ttl_s = evidence_ttl_s
		self.frame_wait_s = frame_wait_s
		self._run_lock = threading.Lock()
		self._pending: threading.Event | None = None
		self.project_id = project_id
		self.control_enabled = control_enabled
		self.inspector = inspector
		self.max_run_s = max_run_s
		self.hz = hz
		self._run_factory = run_factory
		self._background = background
		self._clock = clock
		self._lock = threading.Lock()
		self._lists: dict[str, Any] = {}
		self._listed_at = float("-inf")
		self._error: str | None = None
		self.relays: dict[str, CameraRelay] = {}
		self.run: Any = None
		self.inspection: dict[str, Any] | None = None
		self.crop_jpeg: bytes | None = None

	def _refresh(self) -> None:
		now = self._clock()
		if now - self._listed_at < self.LIST_TTL_S:
			return
		self._listed_at = now
		try:
			project = None
			if self.project_id is None:
				projects = self.client.get_json("/api/projects")
				if not projects:
					raise OSError("Studio has no projects")
				project = projects[0]
				self.project_id = str(project["id"])
			elif "project" not in self._lists:
				project = self.client.get_json(f"/api/projects/{self.project_id}")
			base = f"/api/projects/{self.project_id}"
			lists = {
				"cameras": self.client.get_json(f"{base}/cameras"),
				"environments": self.client.get_json(f"{base}/environments"),
				"models": self.client.get_json(f"{base}/models"),
			}
			if project is not None:
				lists["project"] = {"id": str(project["id"]), "name": project.get("name", "")}
			else:
				lists["project"] = self._lists.get("project")
			self._lists, self._error = lists, None
		except (OSError, ValueError, KeyError, TypeError) as error:
			self._error = str(error)
			self._lists.pop("cameras", None)
			return
		for camera in self._lists["cameras"]:
			camera_id = str(camera["id"])
			if camera_id not in self.relays:
				relay = CameraRelay(lambda camera=camera: self.client.camera_socket(camera), clock=self._clock)
				self.relays[camera_id] = relay
				if self._background:
					relay.start()

	def _camera_key(self, camera_id: str, run: Any = None) -> str | None:
		session = getattr(run if run is not None else self.run, "session", None) or {}
		for camera in (session.get("environment") or {}).get("cameras", []):
			if str(camera.get("camera_id")) == camera_id:
				return camera.get("key")
		return None

	def frame(self, camera_id: str) -> Frame | None:
		"""Newest frame of a camera: from the active run's session when it holds the camera, else the relay."""
		run = self.run
		if run is not None and getattr(run, "phase", None) in ("checking", "running"):
			key = self._camera_key(camera_id)
			if key and key in run.frames:
				return run.frames[key]
		relay = self.relays.get(camera_id)
		return relay.latest() if relay else None

	def state(self) -> dict[str, Any]:
		"""JSON-ready summary of Studio, its cameras, the inspector and the current run."""
		with self._lock:
			self._refresh()
		now = self._clock()
		cameras = []
		for camera in self._lists.get("cameras") or []:
			camera_id = str(camera["id"])
			relay = self.relays.get(camera_id)
			frame = relay.peek() if relay else None
			cameras.append(
				{
					"id": camera_id,
					"name": camera.get("name", camera_id),
					"driver": camera.get("driver"),
					"status": relay.status if relay else "idle",
					"error": relay.error if relay else None,
					"age_ms": None if frame is None else round((now - frame.received_at) * 1000),
					"sequence": None if frame is None else frame.sequence,
				}
			)
		inspector = None
		if self.inspector is not None:
			inspector = {
				"model": getattr(self.inspector, "model", None),
				"device": getattr(self.inspector, "device", None),
				"threshold": getattr(self.inspector, "threshold", None),
				"band": getattr(self.inspector, "band", None),
			}
		return {
			"configured": True,
			"reachable": self._error is None and "cameras" in self._lists,
			"error": self._error,
			"project": self._lists.get("project"),
			"cameras": cameras,
			"environments": [
				{"id": str(e["id"]), "name": e.get("name", "")} for e in self._lists.get("environments") or []
			],
			"models": [
				{"id": str(m["id"]), "name": m.get("name", ""), "backends": list(m.get("available_backends") or [])}
				for m in self._lists.get("models") or []
			],
			"control_enabled": self.control_enabled,
			"max_run_s": self.max_run_s,
			"inspector": inspector,
			"inspection": self.inspection,
			"run": None if self.run is None else self.run.snapshot(),
			"timestamp": now * 1000,
		}

	def _score(self, frame: Frame, camera_id: str) -> dict[str, Any]:
		result = dict(self.inspector.inspect_jpeg(frame.jpeg))
		self.crop_jpeg = result.pop("crop_jpeg", None)
		result.update(
			camera_id=camera_id,
			frame_age_ms=round((self._clock() - frame.received_at) * 1000),
			timestamp=self._clock() * 1000,
		)
		self.inspection = result
		return result

	def inspect(self, camera_id: str) -> tuple[int, dict[str, Any]]:
		"""Score the newest frame of ``camera_id``.

		409 when there is no inspector, no frame, the camera is not live, or the frame is older than
		``max_frame_age_s``: an old or disconnected camera is never scored as current evidence.
		"""
		if self.inspector is None:
			return 409, {"error": "no inspector configured; start the dashboard with --anomaly-model or --purity"}
		run = self.run
		key = self._camera_key(camera_id) if getattr(run, "phase", None) in ("checking", "running") else None
		if key is not None:
			frame = run.frames.get(key)
		else:
			relay = self.relays.get(camera_id)
			frame = relay.latest() if relay else None
			if frame is not None and relay.status != "live":
				detail = f": {relay.error}" if relay.error else ""
				return 409, {"error": f"camera {camera_id} is not live ({relay.status}{detail})"}
		if frame is None:
			return 409, {"error": f"no frame from camera {camera_id} yet"}
		age = self._clock() - frame.received_at
		if age > self.max_frame_age_s:
			return 409, {"error": f"the newest frame from camera {camera_id} is {age:.1f} s old"}
		return 200, self._score(frame, camera_id)

	def _inspect_in_session(self, camera_id: str) -> Callable[[Any], str | None]:
		"""Hook for :class:`PolicyRun`: score a session frame newer than the loaded model, then choose the task."""

		def check(run: Any) -> str | None:
			key = self._camera_key(camera_id, run)
			if key is None:
				return f"camera {camera_id} is not part of this environment; holding still"
			frame = run.wait_for_frame(key, self._clock(), self.frame_wait_s)
			if frame is None:
				return "no fresh frame from the camera; holding still"
			result = self._score(frame, camera_id)
			age = self._clock() - frame.received_at
			if age > self.evidence_ttl_s:
				return f"inspection evidence expired ({age:.1f} s old); holding still"
			if result["label"] not in ("normal", "defective"):
				detail = result.get("reason") or f"score {result.get('score')}"
				return f"held for review: {detail}"
			_bowl, run.task = task_for_action("SORT_GREEN" if result["label"] == "normal" else "SORT_PINK")
			return None

		return check

	def _active(self) -> bool:
		return self.run is not None and getattr(self.run, "phase", "running") in self.ACTIVE_PHASES

	def start_run(self, request: dict[str, Any]) -> tuple[int, dict[str, Any]]:
		"""Start one run: a fixed sort, or ``INSPECT_AND_SORT``, which scores a fresh session frame after loading.

		The run slot is reserved before any slow work, so concurrent starts get 409, and :meth:`stop_run` cancels
		a start that is still preparing.
		"""
		if not self.control_enabled:
			return 403, {"error": "arm control is off; restart the dashboard with --studio-control to allow runs"}
		with self._run_lock:
			if self._pending is not None or self._active():
				return 409, {"error": "a run is already active"}
			cancelled = threading.Event()
			self._pending = cancelled
		try:
			return self._prepare_run(request, cancelled)
		finally:
			with self._run_lock:
				if self._pending is cancelled:
					self._pending = None

	def _prepare_run(self, request: dict[str, Any], cancelled: threading.Event) -> tuple[int, dict[str, Any]]:
		action = request.get("action")
		hook = None
		if action == "INSPECT_AND_SORT":
			if self.inspector is None:
				return 409, {"error": "no inspector configured; start the dashboard with --anomaly-model or --purity"}
			bowl, task = "pending", None
			hook = self._inspect_in_session(str(request.get("camera_id")))
		else:
			try:
				bowl, task = task_for_action(str(action))
			except ValueError as error:
				return 400, {"error": str(error)}
		try:
			environment = environment_draft(
				self.client.get_json(f"/api/projects/{self.project_id}/environments/{request['environment_id']}")
			)
		except (OSError, ValueError, KeyError) as error:
			return 502, {"error": f"could not read the environment: {error}"}
		model = {
			"model_id": str(request.get("model_id")),
			"backend": str(request.get("backend")),
			"device": str(request.get("device") or "auto"),
		}
		project_id = self.project_id
		options: dict[str, Any] = {"before_control": hook} if hook is not None else {}
		with self._run_lock:
			if cancelled.is_set():
				return 409, {"error": "stopped before the run started"}
			self.run = self._run_factory(
				lambda: self.client.runtime_socket(project_id, hz=10),
				environment=environment,
				model=model,
				task=task,
				hz=self.hz,
				max_s=self.max_run_s,
				**options,
			)
			run = self.run
		if self._background:
			threading.Thread(target=run.run, name="studio-policy-run", daemon=True).start()
		return 202, {"decision": bowl, "task": task}

	def stop_run(self) -> dict[str, Any]:
		"""Hold the arm: cancel a start that is still preparing and ask an existing run to stop; always allowed."""
		with self._run_lock:
			pending, run = self._pending, self.run
			if pending is not None:
				pending.set()
			if run is not None:
				run.request_stop()
		return {
			"stopping": pending is not None
			or (run is not None and getattr(run, "phase", "running") in self.ACTIVE_PHASES)
		}
