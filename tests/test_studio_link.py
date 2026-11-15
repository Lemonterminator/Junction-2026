import base64
import hashlib
import json
import select
import socket
import struct
import threading
import time

import pytest

from defect_sorter.studio_link import (
	CameraRelay,
	Frame,
	PolicyRun,
	WebSocket,
	WebSocketClosedError,
	environment_draft,
	parse_observation,
	task_for_action,
)

GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"


def _server_frame(opcode: int, payload: bytes) -> bytes:
	head = bytes([0x80 | opcode])
	if len(payload) < 126:
		head += bytes([len(payload)])
	elif len(payload) < 65536:
		head += bytes([126]) + struct.pack(">H", len(payload))
	else:
		head += bytes([127]) + struct.pack(">Q", len(payload))
	return head + payload


def _read_client_frame(conn: socket.socket) -> tuple[int, bytes]:
	def exact(n):
		data = b""
		while len(data) < n:
			chunk = conn.recv(n - len(data))
			if not chunk:
				raise ConnectionError
			data += chunk
		return data

	b0, b1 = exact(2)
	length = b1 & 0x7F
	if length == 126:
		length = struct.unpack(">H", exact(2))[0]
	elif length == 127:
		length = struct.unpack(">Q", exact(8))[0]
	assert b1 & 0x80, "client frames must be masked"
	mask = exact(4)
	data = bytes(b ^ mask[i % 4] for i, b in enumerate(exact(length)))
	return b0 & 0x0F, data


@pytest.fixture
def ws_server():
	"""A loopback websocket server running a scripted conversation."""
	listener = socket.socket()
	listener.bind(("127.0.0.1", 0))
	listener.listen(1)
	received: list[tuple[int, bytes]] = []
	requests: list[str] = []

	def serve(script):
		conn, _ = listener.accept()
		request = b""
		while b"\r\n\r\n" not in request:
			request += conn.recv(4096)
		text = request.decode()
		requests.append(text)
		key = next(
			line.split(":", 1)[1].strip() for line in text.split("\r\n") if line.lower().startswith("sec-websocket-key")
		)
		accept = base64.b64encode(hashlib.sha1((key + GUID).encode(), usedforsecurity=False).digest()).decode()
		conn.sendall(
			(
				"HTTP/1.1 101 Switching Protocols\r\nUpgrade: websocket\r\nConnection: Upgrade\r\n"
				f"Sec-WebSocket-Accept: {accept}\r\n\r\n"
			).encode()
		)
		script(conn, received)
		conn.close()

	def start(script):
		thread = threading.Thread(target=serve, args=(script,), daemon=True)
		thread.start()
		return f"ws://127.0.0.1:{listener.getsockname()[1]}/api/cameras/ws?camera=%7B%7D", thread

	yield start, received, requests
	listener.close()


def test_websocket_handshake_receives_frames_answers_ping_and_masks_sends(ws_server):
	_start, received, requests = ws_server
	big = bytes(range(256)) * 300

	def script(conn, got):
		conn.sendall(_server_frame(0x9, b"hi"))
		got.append(_read_client_frame(conn))
		conn.sendall(_server_frame(0x2, b"\xff\xd8jpeg"))
		# A text message split over a continuation frame.
		conn.sendall(bytes([0x01, 3]) + b'{"a' + bytes([0x80, 4]) + b'":1}')
		conn.sendall(_server_frame(0x2, big))
		got.append(_read_client_frame(conn))
		conn.sendall(_server_frame(0x8, b""))

	url, thread = ws_server[0](script)
	ws = WebSocket.connect(url, timeout=5)
	assert ws.recv() == (False, b"\xff\xd8jpeg")
	assert ws.recv() == (True, b'{"a":1}')
	assert ws.recv() == (False, big)
	ws.send_text('{"command":"x"}')
	with pytest.raises(WebSocketClosedError):
		ws.recv()
	thread.join(5)
	assert received == [(0xA, b"hi"), (0x1, b'{"command":"x"}')]
	assert requests[0].startswith("GET /api/cameras/ws?camera=%7B%7D HTTP/1.1")


def test_websocket_rejects_a_server_that_does_not_upgrade():
	listener = socket.socket()
	listener.bind(("127.0.0.1", 0))
	listener.listen(1)

	def serve():
		conn, _ = listener.accept()
		conn.recv(4096)
		conn.sendall(b"HTTP/1.1 404 Not Found\r\nContent-Length: 0\r\n\r\n")
		conn.close()

	threading.Thread(target=serve, daemon=True).start()
	with pytest.raises(ConnectionError, match="404"):
		WebSocket.connect(f"ws://127.0.0.1:{listener.getsockname()[1]}/x", timeout=5)
	listener.close()


def _observation(state, frames):
	header = {
		"type": "observation",
		"timestamp": 12.5,
		"state": state,
		"action": None,
		"frames": [{"key": key, "timestamp": 12.4, "size": len(data)} for key, data in frames],
	}
	raw = json.dumps(header).encode()
	return struct.pack(">I", len(raw)) + raw + b"".join(data for _, data in frames)


def test_parse_observation_splits_header_and_concatenated_jpegs():
	header, frames = parse_observation(_observation({"shoulder_pan.pos": 3.0}, [("top", b"AAA"), ("wrist", b"BB")]))
	assert header["state"] == {"shoulder_pan.pos": 3.0}
	assert frames == {"top": b"AAA", "wrist": b"BB"}


def test_parse_observation_rejects_truncated_bodies():
	with pytest.raises(ValueError, match="shorter"):
		parse_observation(_observation(None, [("top", b"AAA")])[:-1])


class FakeSocket:
	"""Scripted websocket: ``recv`` replays messages; ``sends`` records what the client wrote."""

	def __init__(self, messages, on_send=None, close_when_empty=False):
		self.messages = list(messages)
		self.close_when_empty = close_when_empty
		self.sends: list[dict] = []
		self.closed = False
		self.on_send = on_send

	def recv(self, timeout=None):
		if not self.messages:
			if self.close_when_empty:
				raise WebSocketClosedError("end of script")
			return None
		item = self.messages.pop(0)
		return (True, json.dumps(item).encode()) if isinstance(item, dict) else (False, item)

	def send_text(self, text):
		message = json.loads(text)
		self.sends.append(message)
		if self.on_send:
			self.on_send(self, message)

	def close(self):
		self.closed = True


def test_camera_relay_keeps_the_latest_frame_and_reports_studio_errors():
	clock = [100.0]
	sockets = [
		FakeSocket([b"one", b"two"], close_when_empty=True),
		FakeSocket([{"event": "error", "message": "Camera 'top' is in use", "error_code": "device_in_use"}]),
	]
	relay = CameraRelay(lambda: sockets.pop(0), clock=lambda: clock[0])
	relay.latest()  # a viewer; the relay only reads while someone is watching
	relay.run_once()
	frame = relay.latest()
	assert frame.jpeg == b"two"
	assert frame.sequence == 2
	assert frame.received_at == 100.0
	relay.run_once()
	assert relay.status == "error"
	assert relay.error == "Camera 'top' is in use"
	assert relay.latest().jpeg == b"two", "an error keeps the last frame visible; age shows it is old"


def test_camera_relay_is_idle_until_someone_asks_for_frames():
	clock = [0.0]
	relay = CameraRelay(lambda: FakeSocket([]), clock=lambda: clock[0], idle_s=10)
	assert not relay.wanted()
	relay.latest()
	assert relay.wanted()
	clock[0] = 11
	assert not relay.wanted(), "a camera nobody watches is released"


def test_environment_draft_matches_studio_load_environment_shape():
	environment = {
		"id": "env-1",
		"name": "Sorting cell",
		"robots": [
			{"robot": {"id": "r1"}, "tele_operator": {"type": "robot", "robot_id": "leader"}},
			{"robot": {"id": "r2"}, "tele_operator": {"type": "none"}},
		],
		"cameras": [{"id": "c1"}, {"id": None}, {"id": "c2"}],
	}
	assert environment_draft(environment) == {
		"id": "env-1",
		"name": "Sorting cell",
		"robots": [
			{"robot_id": "r1", "tele_operator": {"type": "robot", "robot_id": "leader"}},
			{"robot_id": "r2", "tele_operator": {"type": "none"}},
		],
		"cameras": [{"camera_id": "c1"}, {"camera_id": "c2"}],
	}


def test_only_fixed_trained_tasks_reach_the_policy():
	assert task_for_action("SORT_GREEN") == ("green", "Pick up the brick and place it in the green bowl.")
	assert task_for_action("SORT_PINK") == ("pink", "Pick up the brick and place it in the pink bowl.")
	for action in ["STOP", "sort_green", "Pick up the brick and place it in the green bowl.", ""]:
		with pytest.raises(ValueError, match="not a sorting action"):
			task_for_action(action)


def _acking(sock, message):
	sock.messages.append({"type": "ack", "request_id": message["request_id"], "ok": True, "result": None})


def _run(sock, clock, **kwargs):
	defaults = {
		"environment": {"id": "e", "name": "cell", "robots": [{"robot_id": "r"}], "cameras": []},
		"model": {"model_id": "m", "backend": "openvino", "device": "NPU"},
		"task": "Pick up the brick and place it in the green bowl.",
		"hz": 30,
		"max_s": 20,
		"clock": lambda: clock[0],
	}
	defaults.update(kwargs)
	return PolicyRun(lambda: sock, **defaults)


def test_policy_run_loads_runs_the_fixed_task_and_releases_the_arm_on_stop():
	clock = [0.0]

	def on_send(sock, message):
		_acking(sock, message)
		if message["command"] == "set_control" and message["control"]:
			sock.messages.append(_observation({"gripper.pos": 40.0}, [("top", b"JPEG")]))

	sock = FakeSocket([{"type": "state", "data": {"session_id": "s"}}], on_send)
	run = _run(sock, clock)
	run.step_until_running()
	assert [m["command"] for m in sock.sends] == ["load_environment", "load_model", "set_control"]
	assert sock.sends[0]["environment"]["id"] == "e"
	assert sock.sends[1] == {
		"command": "load_model",
		"request_id": sock.sends[1]["request_id"],
		"model_id": "m",
		"backend": "openvino",
		"device": "NPU",
	}
	control = sock.sends[2]["control"]
	assert control["type"] == "model"
	assert control["task"] == "Pick up the brick and place it in the green bowl."
	assert control["hz"] == 30
	assert control["grace_s"] == 3
	assert run.phase == "running"
	run.pump()
	assert run.joints == {"gripper.pos": 40.0}
	assert run.frames["top"].jpeg == b"JPEG"
	run.request_stop()
	run.pump()
	assert sock.sends[-1]["command"] == "set_control"
	assert sock.sends[-1]["control"] is None
	assert run.phase == "stopped"
	assert sock.closed


def test_policy_run_stops_on_its_own_after_the_time_limit():
	clock = [0.0]
	sock = FakeSocket([], _acking)
	run = _run(sock, clock, max_s=5)
	run.step_until_running()
	clock[0] = 6
	run.pump()
	assert sock.sends[-1] == {"command": "set_control", "request_id": sock.sends[-1]["request_id"], "control": None}
	assert run.phase == "stopped"
	assert "time limit" in run.reason


def test_policy_run_fails_without_moving_when_a_load_is_refused():
	clock = [0.0]

	def refuse_model(sock, message):
		ok = message["command"] != "load_model"
		sock.messages.append(
			{
				"type": "ack",
				"request_id": message["request_id"],
				"ok": ok,
				"error": None if ok else {"message": "no NPU export", "error_code": "x"},
			}
		)

	sock = FakeSocket([], refuse_model)
	run = _run(sock, clock)
	run.step_until_running()
	assert [m["command"] for m in sock.sends] == ["load_environment", "load_model"]
	assert run.phase == "failed"
	assert run.reason == "no NPU export"
	assert sock.closed


def test_policy_run_stops_and_does_not_retry_when_a_device_fails():
	clock = [0.0]
	sock = FakeSocket([], _acking)
	run = _run(sock, clock)
	run.step_until_running()
	sock.messages.append(
		{"type": "status", "component": "environment/follower", "state": "failed", "error": "overload"}
	)
	run.pump()
	assert run.phase == "failed"
	assert "overload" in run.reason
	assert sock.sends[-1]["command"] == "set_control"
	assert sock.sends[-1]["control"] is None
	assert [m["command"] for m in sock.sends].count("load_environment") == 1


# -- StudioHub ----------------------------------------------------------------------------------

from defect_sorter.studio_link import StudioHub  # noqa: E402


class FakeClient:
	def __init__(self):
		self.calls = []
		self.routes = {
			"/api/projects": [{"id": "p1", "name": "Sorting"}],
			"/api/projects/p1/cameras": [{"id": "c1", "name": "Top", "driver": "usb_camera"}],
			"/api/projects/p1/environments": [{"id": "e1", "name": "Cell"}],
			"/api/projects/p1/environments/e1": {
				"id": "e1",
				"name": "Cell",
				"robots": [{"robot": {"id": "r1"}, "tele_operator": {"type": "none"}}],
				"cameras": [{"id": "c1"}],
			},
			"/api/projects/p1/models": [{"id": "m1", "name": "smolvla", "available_backends": ["openvino"]}],
		}
		self.camera_sockets = []

	def get_json(self, path):
		self.calls.append(path)
		if path not in self.routes:
			raise OSError(f"404 {path}")
		return self.routes[path]

	def camera_socket(self, camera):
		return self.camera_sockets.pop(0)

	def runtime_socket(self, project_id, hz=10):
		raise AssertionError("runs use the run factory in tests")


class FakeInspector:
	def __init__(self, label, score):
		self.label, self.score, self.seen = label, score, []

	def inspect_jpeg(self, jpeg):
		self.seen.append(jpeg)
		return {
			"label": self.label,
			"score": self.score,
			"reason": None,
			"timings_ms": {"inference": 4.0},
			"crop_jpeg": b"C",
		}


class RecordingRun:
	def __init__(self, connect, **kwargs):
		self.kwargs = kwargs
		self.stopped = False

	def run(self):
		pass

	def request_stop(self):
		self.stopped = True

	def snapshot(self):
		return {"phase": "running", "task": self.kwargs["task"]}


def _hub(control=True, inspector=None, clock=None):
	client = FakeClient()
	runs = []

	def run_factory(connect, **kwargs):
		run = RecordingRun(connect, **kwargs)
		runs.append(run)
		return run

	hub = StudioHub(
		client,
		None,
		control_enabled=control,
		inspector=inspector,
		run_factory=run_factory,
		background=False,
		clock=clock or (lambda: 1000.0),
	)
	return hub, client, runs


def test_hub_state_lists_project_cameras_environments_and_models():
	hub, client, _ = _hub(control=False)
	state = hub.state()
	assert state["reachable"]
	assert state["project"] == {"id": "p1", "name": "Sorting"}
	assert state["cameras"][0]["id"] == "c1"
	assert state["cameras"][0]["status"] == "idle"
	assert state["environments"] == [{"id": "e1", "name": "Cell"}]
	assert state["models"] == [{"id": "m1", "name": "smolvla", "backends": ["openvino"]}]
	assert state["control_enabled"] is False
	assert state["run"] is None
	hub.state()
	assert client.calls.count("/api/projects/p1/cameras") == 1, "lists are cached between polls"


def test_hub_reports_an_unreachable_studio_without_raising():
	hub, client, _ = _hub()
	client.routes.pop("/api/projects")
	state = hub.state()
	assert state["reachable"] is False
	assert "404" in state["error"]


def test_hub_frames_come_from_the_camera_relay():
	clock = [1000.0]
	hub, client, _ = _hub(clock=lambda: clock[0])
	client.camera_sockets.append(FakeSocket([b"\xff\xd8one"], close_when_empty=True))
	hub.state()
	assert hub.frame("c1") is None, "the first request only asks the relay to connect"
	hub.relays["c1"].run_once()
	assert hub.frame("c1").jpeg == b"\xff\xd8one"
	assert hub.frame("unknown") is None


def test_hub_refuses_motion_unless_control_was_enabled_at_startup():
	hub, _, runs = _hub(control=False)
	status, _body = hub.start_run(
		{"action": "SORT_GREEN", "environment_id": "e1", "model_id": "m1", "backend": "openvino"}
	)
	assert status == 403
	assert runs == []


def test_hub_runs_only_fixed_tasks_and_one_run_at_a_time():
	hub, _, runs = _hub()
	hub.state()
	status, body = hub.start_run(
		{"action": "Pick up everything", "environment_id": "e1", "model_id": "m1", "backend": "openvino"}
	)
	assert status == 400
	assert "not a sorting action" in body["error"]
	assert runs == []
	request = {"action": "SORT_PINK", "environment_id": "e1", "model_id": "m1", "backend": "openvino", "device": "NPU"}
	status, _body = hub.start_run(request)
	assert status == 202
	kwargs = runs[0].kwargs
	assert kwargs["task"] == "Pick up the brick and place it in the pink bowl."
	assert kwargs["environment"]["robots"] == [{"robot_id": "r1", "tele_operator": {"type": "none"}}]
	assert kwargs["model"] == {"model_id": "m1", "backend": "openvino", "device": "NPU"}
	assert hub.start_run(request)[0] == 409
	assert hub.stop_run()["stopping"] is True
	assert runs[0].stopped


class SessionRun:
	"""The parts of a PolicyRun that the inspect-in-session hook uses."""

	def __init__(self, frame):
		self.task = None
		self.session = {"environment": {"cameras": [{"camera_id": "c1", "key": "top"}]}}
		self.frame = frame
		self.asked = []

	def wait_for_frame(self, key, newer_than, timeout_s):
		self.asked.append((key, newer_than))
		return self.frame


INSPECT_AND_SORT = {
	"action": "INSPECT_AND_SORT",
	"camera_id": "c1",
	"environment_id": "e1",
	"model_id": "m1",
	"backend": "openvino",
}


def test_inspect_and_sort_scores_a_fresh_session_frame_right_before_control():
	clock = [1000.0]
	inspector = FakeInspector("defective", 0.9)
	hub, _client, runs = _hub(inspector=inspector, clock=lambda: clock[0])
	hub.state()
	status, body = hub.start_run(INSPECT_AND_SORT)
	assert status == 202
	assert body["decision"] == "pending"
	kwargs = runs[0].kwargs
	assert kwargs["task"] is None, "no task is chosen before the part is scored"
	session = SessionRun(Frame(b"\xff\xd8fresh", 1000.0, 1))
	assert kwargs["before_control"](session) is None
	assert session.asked == [("top", 1000.0)], "only a frame newer than the end of model loading counts"
	assert session.task.endswith("pink bowl.")
	assert inspector.seen == [b"\xff\xd8fresh"]
	assert hub.inspection["label"] == "defective"


def test_inspect_and_sort_holds_still_on_uncertain_or_missing_evidence():
	clock = [1000.0]
	inspector = FakeInspector("uncertain", 0.52)
	hub, _client, runs = _hub(inspector=inspector, clock=lambda: clock[0])
	hub.state()
	hub.start_run(INSPECT_AND_SORT)
	hook = runs[0].kwargs["before_control"]
	session = SessionRun(Frame(b"\xff\xd8f", 1000.0, 1))
	assert "review" in hook(session)
	assert session.task is None
	assert "no fresh frame" in hook(SessionRun(None))


def test_evidence_that_expires_while_scoring_leaves_motion_disabled():
	clock = [1000.0]

	class SlowInspector(FakeInspector):
		def inspect_jpeg(self, jpeg):
			clock[0] += 10
			return super().inspect_jpeg(jpeg)

	hub, _client, runs = _hub(inspector=SlowInspector("normal", 0.1), clock=lambda: clock[0])
	hub.state()
	hub.start_run(INSPECT_AND_SORT)
	session = SessionRun(Frame(b"\xff\xd8f", 1000.0, 1))
	reason = runs[0].kwargs["before_control"](session)
	assert "expired" in reason
	assert session.task is None


def test_inspect_rejects_frames_from_a_disconnected_or_stale_camera():
	clock = [1000.0]
	inspector = FakeInspector("normal", 0.1)
	hub, _client, _runs = _hub(inspector=inspector, clock=lambda: clock[0])
	hub.state()
	relay = hub.relays["c1"]
	relay.receive_frame(b"\xff\xd8old")
	relay.status, relay.error = "error", "camera disconnected"
	status, body = hub.inspect("c1")
	assert status == 409
	assert "not live" in body["error"]
	relay.status, relay.error = "live", None
	clock[0] += 3600
	status, body = hub.inspect("c1")
	assert status == 409
	assert "old" in body["error"]
	assert inspector.seen == [], "stale or unhealthy evidence is never scored"
	relay.receive_frame(b"\xff\xd8new")
	assert hub.inspect("c1")[0] == 200
	assert inspector.seen == [b"\xff\xd8new"]


def _blocking_environment(client):
	gate, entered = threading.Event(), threading.Event()
	read = client.get_json

	def get_json(path):
		if path.endswith("/environments/e1"):
			entered.set()
			gate.wait(5)
		return read(path)

	client.get_json = get_json
	return gate, entered


def test_concurrent_starts_reserve_one_run_slot():
	hub, client, runs = _hub()
	hub.state()
	gate, entered = _blocking_environment(client)
	request = {"action": "SORT_GREEN", "environment_id": "e1", "model_id": "m1", "backend": "openvino"}
	results = []
	first = threading.Thread(target=lambda: results.append(hub.start_run(request)))
	first.start()
	assert entered.wait(2)
	assert hub.start_run(request)[0] == 409, "the slot is reserved while the first start is still preparing"
	gate.set()
	first.join(2)
	assert results[0][0] == 202
	assert len(runs) == 1
	assert hub.stop_run()["stopping"] is True
	assert runs[0].stopped


def test_stop_during_preparation_cancels_the_pending_run():
	hub, client, runs = _hub()
	hub.state()
	gate, entered = _blocking_environment(client)
	request = {"action": "SORT_GREEN", "environment_id": "e1", "model_id": "m1", "backend": "openvino"}
	results = []
	first = threading.Thread(target=lambda: results.append(hub.start_run(request)))
	first.start()
	assert entered.wait(2)
	assert hub.stop_run()["stopping"] is True
	gate.set()
	first.join(2)
	assert results[0][0] == 409
	assert "stopped" in results[0][1]["error"]
	assert runs == []
	assert hub.start_run(request)[0] == 202, "the slot is free again after the cancelled start"


def test_inspect_without_a_frame_or_inspector_is_an_explicit_failure():
	hub, _, _ = _hub(inspector=None)
	hub.state()
	assert hub.inspect("c1")[0] == 409
	hub2, _, _ = _hub(inspector=FakeInspector("normal", 0.1))
	hub2.state()
	status, body = hub2.inspect("c1")
	assert status == 409
	assert "no frame" in body["error"]


class EndlessStream:
	"""A camera that always has the next frame ready."""

	def __init__(self, clock):
		self.clock, self.frames, self.closed = clock, 0, False

	def poll(self, timeout):
		return True

	def recv(self, timeout=None):
		self.frames += 1
		self.clock[0] += 0.1
		return False, b"\xff\xd8frame"

	def send_text(self, text):
		pass

	def close(self):
		self.closed = True


def test_relay_detaches_when_the_last_viewer_expires_even_while_frames_keep_arriving():
	clock = [0.0]
	stream = EndlessStream(clock)
	relay = CameraRelay(lambda: stream, clock=lambda: clock[0], idle_s=2)
	relay.latest()
	relay.run_once()
	assert stream.closed
	assert stream.frames <= 22, "about idle_s / 0.1 s of frames, then the camera is released"


def _socket_pair():
	client, peer = socket.socketpair()
	return WebSocket(client), peer


def test_recv_returns_at_its_deadline_while_only_pings_arrive():
	ws, peer = _socket_pair()
	peer.sendall(_server_frame(0x9, b"p"))
	started = time.monotonic()
	assert ws.recv(timeout=0.15) is None
	assert time.monotonic() - started < 1
	assert _read_client_frame(peer) == (0xA, b"p")


def test_partial_frames_and_fragments_survive_a_receive_timeout():
	ws, peer = _socket_pair()
	frame = _server_frame(0x2, b"x" * 1000)
	peer.sendall(frame[:300])
	assert ws.recv(timeout=0.05) is None
	peer.sendall(frame[300:])
	assert ws.recv(timeout=1) == (False, b"x" * 1000)
	peer.sendall(bytes([0x01, 3]) + b'{"a')
	assert ws.recv(timeout=0.05) is None
	peer.sendall(bytes([0x80, 4]) + b'":1}')
	assert ws.recv(timeout=1) == (True, b'{"a":1}')


def _studio_peer(peer, noise, received, done):
	"""Ack every command; once control is set, send only pings or half of an observation."""
	observation = _server_frame(0x2, _observation({"gripper.pos": 1.0}, [("top", b"J" * 2000)]))
	half = len(observation) // 2
	noisy = False
	while not done.is_set():
		ready, _, _ = select.select([peer], [], [], 0.01)
		if ready:
			opcode, data = _read_client_frame(peer)
			if opcode == 0x8:
				return
			if opcode != 0x1:
				continue
			message = json.loads(data)
			received.append(message)
			releasing = message["command"] == "set_control" and message["control"] is None
			if releasing:
				noisy = False
				if noise == "partial":
					peer.sendall(observation[half:])
			ack = {"type": "ack", "request_id": message["request_id"], "ok": True, "result": None}
			peer.sendall(_server_frame(0x1, json.dumps(ack).encode()))
			if message["command"] == "set_control" and message["control"]:
				noisy = True
				if noise == "partial":
					peer.sendall(observation[:half])
		elif noisy and noise == "ping":
			peer.sendall(_server_frame(0x9, b"k"))


def _run_against_peer(noise, max_s):
	ws, peer = _socket_pair()
	received, done = [], threading.Event()
	threading.Thread(target=_studio_peer, args=(peer, noise, received, done), daemon=True).start()
	run = PolicyRun(
		lambda: ws,
		environment={"id": "e", "name": "cell", "robots": [], "cameras": []},
		model={"model_id": "m", "backend": "openvino", "device": "NPU"},
		task="Pick up the brick and place it in the green bowl.",
		max_s=max_s,
	)
	run.step_until_running()
	assert run.phase == "running"
	pumping = threading.Thread(target=run.pump, args=(30,), daemon=True)
	pumping.start()
	return run, received, done, pumping


def test_operator_stop_works_while_only_pings_arrive():
	run, received, done, pumping = _run_against_peer("ping", max_s=60)
	time.sleep(0.2)
	run.request_stop()
	pumping.join(2)
	done.set()
	assert not pumping.is_alive(), "STOP must not wait for the next application message"
	assert run.phase == "stopped"
	assert received[-1]["command"] == "set_control"
	assert received[-1]["control"] is None


def test_run_deadline_works_while_a_message_is_half_received():
	run, received, done, pumping = _run_against_peer("partial", max_s=0.2)
	pumping.join(3)
	done.set()
	assert not pumping.is_alive(), "the time limit must not wait for the rest of a frame"
	assert run.phase == "stopped"
	assert "time limit" in run.reason
	assert received[-1]["control"] is None
	assert run.frames["top"].jpeg == b"J" * 2000, "the half-received frame is completed, not dropped"


def test_policy_run_holds_still_when_the_pre_control_check_refuses():
	clock = [0.0]
	sock = FakeSocket([], _acking)
	run = _run(sock, clock, task=None, before_control=lambda run: "held for review: score 0.52")
	run.step_until_running()
	assert [m["command"] for m in sock.sends] == ["load_environment", "load_model"]
	assert run.phase == "held"
	assert run.reason == "held for review: score 0.52"
	assert sock.closed


def test_policy_run_uses_the_task_chosen_by_the_pre_control_check():
	clock = [0.0]
	sock = FakeSocket([], _acking)

	def choose(run):
		run.task = "Pick up the brick and place it in the pink bowl."

	run = _run(sock, clock, task=None, before_control=choose)
	run.step_until_running()
	assert sock.sends[-1]["control"]["task"] == "Pick up the brick and place it in the pink bowl."
	assert run.phase == "running"
