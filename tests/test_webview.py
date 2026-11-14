import json
import threading
import time
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer

import pytest

from defect_sorter.webview import FrameBuffer, make_handler, page_html


@pytest.fixture
def served():
	"""Serve a FrameBuffer on an ephemeral localhost port; yields (buffer, base_url, calls)."""
	buffer = FrameBuffer()
	calls: list[str] = []
	page = page_html("Test page", {"refit": "Refit"})
	server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(buffer, page, {"refit": lambda: calls.append("refit")}))
	thread = threading.Thread(target=server.serve_forever, daemon=True)
	thread.start()
	yield buffer, f"http://127.0.0.1:{server.server_address[1]}", calls
	server.shutdown()
	server.server_close()


def get(url: str, timeout: float = 5.0):
	try:
		with urllib.request.urlopen(url, timeout=timeout) as r:
			return r.status, dict(r.headers), r.read()
	except urllib.error.HTTPError as e:
		return e.code, dict(e.headers), e.read()


class TestFrameBuffer:
	def test_ids_increase_with_each_publish(self):
		b = FrameBuffer()
		b.publish(b"a", {"n": 1})
		first = b.latest()
		b.publish(b"b", {"n": 2})
		second = b.latest()
		assert second.frame_id == first.frame_id + 1
		assert second.jpeg == b"b"
		assert second.state == {"n": 2}

	def test_wait_newer_returns_none_on_timeout(self):
		b = FrameBuffer()
		b.publish(b"a", {})
		assert b.wait_newer(b.latest().frame_id, timeout=0.05) is None

	def test_wait_newer_wakes_on_publish(self):
		b = FrameBuffer()
		b.publish(b"a", {})
		after = b.latest().frame_id
		threading.Timer(0.1, lambda: b.publish(b"b", {})).start()
		got = b.wait_newer(after, timeout=2.0)
		assert got is not None
		assert got.jpeg == b"b"


class TestHandler:
	def test_page_polls_single_frames_instead_of_a_stream(self, served):
		_, base, _ = served
		status, _, body = get(base + "/")
		assert status == 200
		html = body.decode()
		assert "/frame.jpg" in html
		assert "/stream" not in html
		assert "Refit" in html

	def test_frame_before_first_publish_is_unavailable(self, served):
		_, base, _ = served
		assert get(base + "/frame.jpg?after=0", timeout=5)[0] == 503

	def test_frame_returns_complete_latest_jpeg_with_id_and_no_cache(self, served):
		buffer, base, _ = served
		buffer.publish(b"\xff\xd8jpegdata\xff\xd9", {"k": 1})
		status, headers, body = get(base + "/frame.jpg?after=0")
		assert status == 200
		assert body == b"\xff\xd8jpegdata\xff\xd9"
		assert headers["Content-Type"] == "image/jpeg"
		assert headers["Content-Length"] == str(len(body))
		assert "no-store" in headers["Cache-Control"]
		assert int(headers["X-Frame-Id"]) == buffer.latest().frame_id

	def test_frame_waits_for_a_newer_one_instead_of_resending(self, served):
		buffer, base, _ = served
		buffer.publish(b"old", {})
		current = buffer.latest().frame_id
		threading.Timer(0.2, lambda: buffer.publish(b"new", {})).start()
		t0 = time.monotonic()
		status, _, body = get(base + f"/frame.jpg?after={current}")
		assert status == 200
		assert body == b"new"
		assert time.monotonic() - t0 >= 0.15

	def test_no_newer_frame_gives_no_content(self, served):
		buffer, base, _ = served
		buffer.publish(b"old", {})
		status, _, body = get(base + f"/frame.jpg?after={buffer.latest().frame_id}")
		assert status == 204
		assert body == b""

	def test_state_is_json(self, served):
		buffer, base, _ = served
		buffer.publish(b"x", {"camera_tilt": 3.5})
		status, _, body = get(base + "/state")
		assert status == 200
		assert json.loads(body) == {"camera_tilt": 3.5}

	def test_post_action_calls_callback(self, served):
		_, base, calls = served
		req = urllib.request.Request(base + "/refit", method="POST", data=b"")
		with urllib.request.urlopen(req, timeout=5) as r:
			assert r.status == 204
		assert calls == ["refit"]

	def test_unknown_paths_are_404(self, served):
		_, base, _ = served
		assert get(base + "/nope")[0] == 404
