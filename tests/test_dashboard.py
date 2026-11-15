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
