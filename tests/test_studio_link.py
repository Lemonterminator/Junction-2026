import base64
import hashlib
import json
import socket
import struct
import threading

import pytest

from defect_sorter.studio_link import (
	CameraRelay,
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

	def poll(self, timeout):
		return bool(self.messages) or self.close_when_empty

	def recv(self):
		if not self.messages:
			raise WebSocketClosedError("end of script")
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


def test_inspect_and_sort_maps_the_measured_label_and_holds_on_uncertain():
	inspector = FakeInspector("uncertain", 0.52)
	hub, client, runs = _hub(inspector=inspector)
	client.camera_sockets.append(FakeSocket([b"\xff\xd8frame"], close_when_empty=True))
	hub.state()
	hub.frame("c1")
	hub.relays["c1"].run_once()
	request = {
		"action": "INSPECT_AND_SORT",
		"camera_id": "c1",
		"environment_id": "e1",
		"model_id": "m1",
		"backend": "openvino",
	}
	status, body = hub.start_run(request)
	assert status == 200
	assert body["decision"] == "review"
	assert runs == []
	assert inspector.seen == [b"\xff\xd8frame"]
	inspector.label, inspector.score = "defective", 0.9
	status, body = hub.start_run(request)
	assert status == 202
	assert body["inspection"]["label"] == "defective"
	assert runs[0].kwargs["task"].endswith("pink bowl.")


def test_inspect_without_a_frame_or_inspector_is_an_explicit_failure():
	hub, _, _ = _hub(inspector=None)
	hub.state()
	assert hub.inspect("c1")[0] == 409
	hub2, _, _ = _hub(inspector=FakeInspector("normal", 0.1))
	hub2.state()
	status, body = hub2.inspect("c1")
	assert status == 409
	assert "no frame" in body["error"]
