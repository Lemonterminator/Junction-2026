import json
import threading
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer

import pytest

from defect_sorter.dashboard import make_handler
from defect_sorter.system_metrics import SystemMetrics


@pytest.fixture
def served(tmp_path):
	frontend = tmp_path / "frontend"
	frontend.mkdir()
	(frontend / "index.html").write_text("<h1>Dashboard</h1>")
	(frontend / "app.mjs").write_text("export const test = true;")
	(frontend / "narration.wav").write_bytes(b"RIFF" + b"\0" * 32)
	(frontend / "led.woff2").write_bytes(b"wOF2font")
	secret = tmp_path / "private.txt"
	secret.write_text("private")
	(frontend / "leak.mjs").symlink_to(secret)
	telemetry = tmp_path / "telemetry.json"
	server = ThreadingHTTPServer(
		("127.0.0.1", 0),
		make_handler(frontend, SystemMetrics(tmp_path / "proc", tmp_path / "sys", host_platform="Linux"), telemetry),
	)
	thread = threading.Thread(target=server.serve_forever, daemon=True)
	thread.start()
	yield f"http://127.0.0.1:{server.server_address[1]}", telemetry
	server.shutdown()
	server.server_close()
	thread.join()


def get(url, headers=None):
	try:
		with urllib.request.urlopen(urllib.request.Request(url, headers=headers or {}), timeout=5) as response:
			return response.status, response.headers, response.read()
	except urllib.error.HTTPError as error:
		return error.code, error.headers, error.read()


def test_serves_dashboard_and_modules_but_no_traversal_or_symlinks(served):
	base, _ = served
	assert b"Dashboard" in get(base + "/")[2]
	assert "javascript" in get(base + "/app.mjs")[1]["Content-Type"]
	assert get(base + "/narration.wav")[0] == 200
	status, headers, body = get(base + "/led.woff2")
	assert status == 200
	assert headers["Content-Type"] == "font/woff2"
	assert body == b"wOF2font"
	for path in ["/../private.txt", "/%2e%2e/private.txt", "/leak.mjs", "/.env", "/tests/"]:
		assert get(base + path)[0] == 404


def test_resource_endpoint_is_cached_json_with_explicit_missing_values(served):
	base, _ = served
	status, headers, body = get(base + "/api/system")
	assert status == 200
	assert headers["Cache-Control"] == "no-store"
	sample = json.loads(body)
	assert sample["cpu_percent"] is None
	assert sample["source"] == "linux-proc-sysfs"
	assert get(base + "/api/system")[2] == body


def test_optional_telemetry_file_is_read_only_and_missing_data_is_explicit(served):
	base, telemetry = served
	assert get(base + "/api/telemetry")[0] == 204
	telemetry.write_text('{"schema_version": 1, "mode": "real"}')
	assert json.loads(get(base + "/api/telemetry")[2])["mode"] == "real"
	telemetry.write_text("partial JSON")
	assert get(base + "/api/telemetry")[0] == 503


def test_audio_supports_byte_ranges_for_browser_seek(served):
	base, _ = served
	url = base + "/narration.wav"
	assert get(url)[1]["Accept-Ranges"] == "bytes"
	status, headers, body = get(url, {"Range": "bytes=4-9"})
	assert status == 206
	assert headers["Content-Range"] == "bytes 4-9/36"
	assert headers["Content-Length"] == "6"
	assert body == b"\0" * 6
	assert get(url, {"Range": "bytes=-4"})[2] == b"\0" * 4
	for invalid in ["bytes=1000-", "bytes=12-2", "bytes=-0", "bytes=0-1,4-5"]:
		status, headers, _ = get(url, {"Range": invalid})
		assert status == 416
		assert headers["Content-Range"] == "bytes */36"


class FakeHub:
	def __init__(self):
		self.started = []
		self.stops = 0

	def state(self):
		return {"configured": True, "reachable": True, "cameras": [{"id": "c1"}]}

	def frame(self, camera_id):
		from defect_sorter.studio_link import Frame

		return Frame(b"\xff\xd8jpeg", 0.0, 7) if camera_id == "c1" else None

	def inspect(self, camera_id):
		return 200, {"label": "normal", "camera_id": camera_id}

	def start_run(self, request):
		self.started.append(request)
		return 202, {"decision": "green"}

	def stop_run(self):
		self.stops += 1
		return {"stopping": True}

	crop_jpeg = b"\xff\xd8crop"


@pytest.fixture
def studio_served(tmp_path):
	frontend = tmp_path / "frontend"
	frontend.mkdir()
	(frontend / "index.html").write_text("<h1>Dashboard</h1>")
	hub = FakeHub()
	server = ThreadingHTTPServer(
		("127.0.0.1", 0),
		make_handler(frontend, SystemMetrics(tmp_path / "proc", tmp_path / "sys", host_platform="Linux"), None, hub),
	)
	thread = threading.Thread(target=server.serve_forever, daemon=True)
	thread.start()
	yield f"http://127.0.0.1:{server.server_address[1]}", hub
	server.shutdown()
	server.server_close()
	thread.join()


def post(url, body, headers=None):
	data = json.dumps(body).encode()
	request = urllib.request.Request(url, data=data, method="POST", headers=headers or {})
	try:
		with urllib.request.urlopen(request, timeout=5) as response:
			return response.status, json.loads(response.read() or b"null")
	except urllib.error.HTTPError as error:
		return error.code, json.loads(error.read() or b"null")


CONTROL = {"Content-Type": "application/json", "X-Armigo-Request": "1"}


def test_studio_routes_are_204_when_studio_is_not_configured(served):
	base, _ = served
	assert get(base + "/api/studio/state")[0] == 204
	assert get(base + "/api/studio/frame/c1.jpg")[0] == 404
	assert post(base + "/api/studio/run", {"action": "SORT_GREEN"}, CONTROL)[0] == 404


def test_studio_state_and_frames_are_served_same_origin(studio_served):
	base, _ = studio_served
	status, _, body = get(base + "/api/studio/state")
	assert status == 200
	assert json.loads(body)["cameras"] == [{"id": "c1"}]
	status, headers, body = get(base + "/api/studio/frame/c1.jpg")
	assert status == 200
	assert headers["Content-Type"] == "image/jpeg"
	assert body == b"\xff\xd8jpeg"
	assert headers["X-Frame-Sequence"] == "7"
	assert get(base + "/api/studio/frame/missing.jpg")[0] == 204
	assert get(base + "/api/studio/inspection/crop.jpg")[2] == b"\xff\xd8crop"


def test_studio_commands_need_the_json_request_header_and_a_same_origin(studio_served):
	base, hub = studio_served
	# A cross-site form post can send neither the custom header nor a JSON content type.
	assert post(base + "/api/studio/run", {"action": "SORT_GREEN"}, {"Content-Type": "text/plain"})[0] == 403
	assert (
		post(base + "/api/studio/run", {"action": "SORT_GREEN"}, {**CONTROL, "Origin": "http://evil.example"})[0] == 403
	)
	assert hub.started == []
	assert post(base + "/api/studio/run", {"action": "SORT_GREEN"}, CONTROL) == (202, {"decision": "green"})
	assert hub.started == [{"action": "SORT_GREEN"}]
	assert post(base + "/api/studio/inspect", {"camera_id": "c1"}, CONTROL) == (
		200,
		{"label": "normal", "camera_id": "c1"},
	)
	assert post(base + "/api/studio/stop", {}, CONTROL) == (200, {"stopping": True})
	assert hub.stops == 1


def test_studio_commands_reject_bodies_that_are_not_json_objects(studio_served):
	base, hub = studio_served
	request = urllib.request.Request(base + "/api/studio/run", data=b"[1", method="POST", headers=CONTROL)
	with pytest.raises(urllib.error.HTTPError) as error:
		urllib.request.urlopen(request, timeout=5)
	assert error.value.code == 400
	assert hub.started == []
