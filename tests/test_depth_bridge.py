import http.client
import threading
from http.server import ThreadingHTTPServer

import cv2
import numpy as np
import pytest

from defect_sorter.depth_bridge import (
	RawFrame,
	colorize_depth,
	crop,
	decode_raw,
	encode_jpeg,
	encode_raw,
	fetch_raw,
	fit_plane,
	fresh_frames,
	height_image,
	layered_height_image,
	load_plane,
	make_stream_handler,
	resolve_plane,
	save_plane,
	table_heights,
)
from defect_sorter.geometry import Intrinsics
from defect_sorter.webview import FrameBuffer


class TestColorizeDepth:
	def test_fixed_scale_near_bright_far_dark_missing_black(self):
		depth = np.array([[0.3, 1.2, 0.0, np.nan, 0.2, 2.0]], dtype=np.float32)
		img = colorize_depth(depth, near_m=0.3, far_m=1.2)
		assert img.dtype == np.uint8
		assert img.shape == (1, 6, 3)
		grey = img[0, :, 0]
		assert grey.tolist() == [255, 1, 0, 0, 255, 1]  # closer than near clips to 255, beyond far to 1
		np.testing.assert_array_equal(img[..., 0], img[..., 1])
		np.testing.assert_array_equal(img[..., 0], img[..., 2])

	def test_a_brick_on_the_table_is_brighter_by_its_height(self):
		# table at 0.90 m, brick top 5 cm closer: 0.05 m over a 0.9 m scale is 254 * 0.05 / 0.9 ≈ 14 grey levels
		depth = np.full((4, 4), 0.90, dtype=np.float32)
		depth[1:3, 1:3] = 0.85
		img = colorize_depth(depth, near_m=0.3, far_m=1.2)
		diff = int(img[1, 1, 0]) - int(img[0, 0, 0])
		assert diff == pytest.approx(254 * 0.05 / 0.9, abs=1)

	def test_scale_must_be_ordered(self):
		with pytest.raises(ValueError, match="near"):
			colorize_depth(np.zeros((1, 1)), near_m=1.0, far_m=0.5)


class TestHeightImage:
	def test_table_dark_missing_black_brick_bright(self):
		h = np.array([[0.0, -0.004, 0.02, 0.10, 0.30, np.nan]], dtype=np.float32)
		img = height_image(h, max_m=0.10)
		assert img[0, :, 0].tolist() == [1, 1, 52, 255, 255, 0]  # 2 cm of 10 cm: 1 + 254 * 0.2 = 51.8
		np.testing.assert_array_equal(img[..., 0], img[..., 2])

	def test_tilted_camera_gives_a_flat_table_and_the_brick_height(self):
		# camera looking down at a table tilted 30 degrees: absolute depth varies across the image, height must not
		intr = Intrinsics(fx=600.0, fy=600.0, ppx=320.0, ppy=240.0)
		h, w = 480, 640
		u, v = np.meshgrid(np.arange(w), np.arange(h))
		rays = np.stack([(u - intr.ppx) / intr.fx, (v - intr.ppy) / intr.fy, np.ones((h, w))], axis=-1)
		tilt = np.radians(30)
		normal = np.array([0.0, -np.sin(tilt), -np.cos(tilt)])  # towards the camera
		offset = 0.7  # camera 0.7 m from the table plane
		# a point p on the plane satisfies normal . p + offset = 0; a 2 cm brick top satisfies normal . p + offset = 0.02
		table_z = -offset / (rays @ normal)
		brick_z = -(offset - 0.02) / (rays @ normal)
		depth = table_z.copy()
		depth[200:260, 300:360] = brick_z[200:260, 300:360]
		depth[0:10, 0:10] = 0.0  # missing depth
		assert depth.max() - depth.min() > 0.1  # the table alone spans more than 10 cm of depth

		plane = fit_plane(depth.astype(np.float32), intr)
		heights = table_heights(depth.astype(np.float32), intr, plane)

		assert plane.inlier_fraction > 0.9
		assert abs(float(np.median(heights[400:470, 20:200]))) < 0.001
		assert float(np.median(heights[210:250, 310:350])) == pytest.approx(0.02, abs=0.001)
		assert np.isnan(heights[0:10, 0:10]).all()


class TestLayeredHeightImage:
	"""Three channels on fixed scales, as a viewer sees them: R fine height, G coarse height, B depth valid."""

	def test_each_channel_on_its_own_fixed_scale(self):
		h = np.array([[0.0, 0.016, 0.024, 0.06, 0.30, 0.50, np.nan, -0.01]], dtype=np.float32)
		img = layered_height_image(h, fine_max_m=0.04, coarse_max_m=0.30)
		assert img.dtype == np.uint8
		assert img.shape == (1, 8, 3)
		b, g, r = (img[0, :, i].tolist() for i in range(3))  # OpenCV order: B, G, R
		# fine: 255 * h / 4 cm; 1.6 cm -> 102, 2.4 cm -> 153, 6 cm and above saturate
		assert r == [0, 102, 153, 255, 255, 255, 0, 0]
		# coarse: 255 * h / 30 cm; 1.6 cm -> 13.6, 2.4 cm -> 20.4, 6 cm -> 51
		assert g == [0, 14, 20, 51, 255, 255, 0, 0]
		# valid depth is 255, missing 0: a JPEG cannot keep "missing" apart from "table" by one grey level
		assert b == [255, 255, 255, 255, 255, 255, 0, 255]

	def test_a_gripper_above_the_fine_scale_still_shows_its_height(self):
		h = np.array([[0.08, 0.12]], dtype=np.float32)
		img = layered_height_image(h, fine_max_m=0.04, coarse_max_m=0.30)
		assert img[0, :, 2].tolist() == [255, 255]
		assert img[0, 1, 1] - img[0, 0, 1] == 34  # 4 cm apart on the 30 cm scale: 255 * 0.04 / 0.30

	def test_scales_must_be_ordered_and_positive(self):
		with pytest.raises(ValueError, match="fine_max_m"):
			layered_height_image(np.zeros((1, 1)), fine_max_m=0.30, coarse_max_m=0.04)
		with pytest.raises(ValueError, match="fine_max_m"):
			layered_height_image(np.zeros((1, 1)), fine_max_m=0.0, coarse_max_m=0.30)


def test_jpeg_keeps_a_thin_detail_that_differs_between_channels():
	# a 2-pixel stripe at an odd column in R only: 4:2:0 chroma subsampling would average it with its neighbours
	img = np.zeros((64, 64, 3), np.uint8)
	img[..., 0] = 255
	img[:, 31:33, 2] = 255
	out = cv2.imdecode(np.frombuffer(encode_jpeg(img, 90), np.uint8), cv2.IMREAD_COLOR)
	assert out[8:56, 31:33, 2].min() >= 220
	assert out[8:56, 20:28, 2].max() <= 30


def _flat_depth(distance_m: float, shape: tuple[int, int] = (48, 64)) -> np.ndarray:
	return np.full(shape, distance_m, np.float32)


INTR = Intrinsics(fx=60.0, fy=60.0, ppx=32.0, ppy=24.0)


class TestPlaneLock:
	def test_without_a_saved_plane_the_fresh_fit_is_used(self):
		plane = resolve_plane(_flat_depth(0.8), INTR, saved=None)
		assert plane.offset == pytest.approx(0.8, abs=1e-3)

	def test_a_saved_plane_is_kept_when_the_camera_has_not_moved(self):
		saved = fit_plane(_flat_depth(0.8), INTR)
		assert resolve_plane(_flat_depth(0.803), INTR, saved=saved) is saved

	def test_a_moved_camera_is_refused(self):
		saved = fit_plane(_flat_depth(0.8), INTR)
		with pytest.raises(ValueError, match="moved"):
			resolve_plane(_flat_depth(0.83), INTR, saved=saved)

	def test_a_scene_without_a_clear_table_is_refused(self):
		depth = np.random.default_rng(0).uniform(0.5, 1.5, (48, 64)).astype(np.float32)
		with pytest.raises(ValueError, match="table plane"):
			resolve_plane(depth, INTR, saved=None)

	def test_save_and_load_round_trip(self, tmp_path):
		plane = fit_plane(_flat_depth(0.8), INTR)
		path = tmp_path / "plane.json"
		save_plane(path, plane)
		loaded = load_plane(path)
		np.testing.assert_allclose(loaded.normal, plane.normal)
		assert loaded.offset == pytest.approx(plane.offset)
		assert loaded.inlier_fraction == pytest.approx(plane.inlier_fraction)


class TestCrop:
	def test_crop_keeps_the_region_at_its_own_size(self):
		img = np.zeros((480, 640, 3), np.uint8)
		img[100:200, 300:400] = 200
		out = crop(img, (300, 100, 100, 100))
		assert out.shape == (100, 100, 3)
		assert int(out.mean()) == 200

	def test_a_box_outside_the_image_is_refused(self):
		with pytest.raises(ValueError, match="crop"):
			crop(np.zeros((480, 640, 3), np.uint8), (600, 0, 100, 100))


def _jpeg(value: int) -> bytes:
	ok, buf = cv2.imencode(".jpg", np.full((48, 64, 3), value, dtype=np.uint8))
	assert ok
	return buf.tobytes()


@pytest.fixture
def served():
	buffers = {"top": FrameBuffer(), "top_depth": FrameBuffer(), "raw": FrameBuffer()}
	server = ThreadingHTTPServer(("127.0.0.1", 0), make_stream_handler(buffers))
	server.daemon_threads = True
	thread = threading.Thread(target=server.serve_forever, daemon=True)
	thread.start()
	yield buffers, server.server_address[1]
	server.shutdown()
	server.server_close()


def _read_part_with_headers(resp) -> tuple[bytes, dict[str, str]]:
	line = resp.fp.readline()
	while line in (b"\r\n", b"\n"):
		line = resp.fp.readline()
	assert line.strip() == b"--frame"
	headers = {}
	while True:
		h = resp.fp.readline().strip()
		if not h:
			break
		k, v = h.decode().split(":", 1)
		headers[k.strip().lower()] = v.strip()
	return resp.fp.read(int(headers["content-length"])), headers


def _read_part(resp) -> bytes:
	"""Read one multipart JPEG part: boundary line, headers, body."""
	line = resp.fp.readline()
	while line in (b"\r\n", b"\n"):
		line = resp.fp.readline()
	assert line.strip() == b"--frame"
	headers = {}
	while True:
		h = resp.fp.readline().strip()
		if not h:
			break
		k, v = h.decode().split(":", 1)
		headers[k.strip().lower()] = v.strip()
	assert headers["content-type"] == "image/jpeg"
	return resp.fp.read(int(headers["content-length"]))


class TestMjpegStream:
	def test_stream_sends_each_new_frame_as_a_multipart_jpeg(self, served):
		buffers, port = served
		buffers["top_depth"].publish(_jpeg(40), {})
		conn = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
		conn.request("GET", "/top_depth.mjpg")
		resp = conn.getresponse()
		assert resp.status == 200
		assert resp.getheader("Content-Type").startswith("multipart/x-mixed-replace")
		first = cv2.imdecode(np.frombuffer(_read_part(resp), np.uint8), cv2.IMREAD_COLOR)
		assert first.shape == (48, 64, 3)
		assert abs(int(first.mean()) - 40) <= 2
		buffers["top_depth"].publish(_jpeg(200), {})
		second = cv2.imdecode(np.frombuffer(_read_part(resp), np.uint8), cv2.IMREAD_COLOR)
		assert abs(int(second.mean()) - 200) <= 2
		conn.close()

	def test_each_part_carries_its_publish_time_for_latency_checks(self, served):
		import time

		buffers, port = served
		before = time.time()
		buffers["top"].publish(_jpeg(10), {})
		conn = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
		conn.request("GET", "/top.mjpg")
		_, headers = _read_part_with_headers(conn.getresponse())
		assert before <= float(headers["x-timestamp"]) <= time.time()
		conn.close()

	def test_single_jpeg_for_a_quick_look(self, served):
		buffers, port = served
		buffers["top"].publish(_jpeg(90), {})
		conn = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
		conn.request("GET", "/top.jpg")
		resp = conn.getresponse()
		assert resp.status == 200
		assert resp.getheader("Content-Type") == "image/jpeg"
		assert cv2.imdecode(np.frombuffer(resp.read(), np.uint8), cv2.IMREAD_COLOR).shape == (48, 64, 3)

	def test_unknown_stream_is_404(self, served):
		_, port = served
		conn = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
		conn.request("GET", "/nope.mjpg")
		assert conn.getresponse().status == 404


def test_bridge_publishes_colour_and_depth_for_every_camera_frame():
	from defect_sorter.depth_bridge import run_bridge

	buffers = {"top": FrameBuffer(), "top_depth": FrameBuffer()}
	frames = iter(range(3))

	def read():
		next(frames)
		return np.full((48, 64, 3), 120, np.uint8), np.full((48, 64), 0.75, np.float32), None

	run_bridge(
		read, buffers, mode="distance", near_m=0.3, far_m=1.2, stop=lambda: buffers["top"].latest().frame_id >= 3
	)

	assert buffers["top"].latest().frame_id == 3
	assert buffers["top_depth"].latest().frame_id == 3
	depth_img = cv2.imdecode(np.frombuffer(buffers["top_depth"].latest().jpeg, np.uint8), cv2.IMREAD_COLOR)
	assert abs(int(depth_img.mean()) - 128) <= 2  # 0.75 m is the middle of 0.3-1.2 m: 1 + 254 * 0.5 = 128


def _decode(buffer: FrameBuffer) -> np.ndarray:
	return cv2.imdecode(np.frombuffer(buffer.latest().jpeg, np.uint8), cv2.IMREAD_COLOR)


def test_bridge_holds_the_table_plane_from_the_first_frame():
	# the second frame shows the whole scene 1 cm closer; a refit would call that the table again (fine height 0)
	from defect_sorter.depth_bridge import run_bridge

	buffers = {"top": FrameBuffer(), "top_depth": FrameBuffer()}
	depths = iter([_flat_depth(0.80), _flat_depth(0.79), _flat_depth(0.79)])

	def read():
		return np.zeros((48, 64, 3), np.uint8), next(depths), INTR

	run_bridge(read, buffers, mode="layers", stop=lambda: buffers["top"].latest().frame_id >= 3)

	r = _decode(buffers["top_depth"])[..., 2]
	assert abs(int(np.median(r)) - 64) <= 3  # 1 cm on the 4 cm fine scale: 255 * 0.25


def test_bridge_crops_colour_and_depth_to_the_same_box():
	from defect_sorter.depth_bridge import run_bridge

	buffers = {"top": FrameBuffer(), "top_depth": FrameBuffer()}

	def read():
		return np.zeros((48, 64, 3), np.uint8), _flat_depth(0.8), INTR

	run_bridge(
		read, buffers, mode="layers", crop_box=(8, 4, 40, 32), stop=lambda: buffers["top"].latest().frame_id >= 1
	)

	assert _decode(buffers["top"]).shape == (32, 40, 3)
	assert _decode(buffers["top_depth"]).shape == (32, 40, 3)


def _raw_frame(frame_id: int = 7) -> RawFrame:
	rng = np.random.default_rng(1)
	depth = np.full((48, 64), 0.8125, np.float32)
	depth[10:20, 10:30] = 0.79
	depth[0, :5] = 0.0
	depth[1, :5] = np.nan
	return RawFrame(rng.integers(0, 256, (48, 64, 3), dtype=np.uint8), depth, INTR, frame_id)


class TestRawFrame:
	def test_round_trip_keeps_colour_intrinsics_and_millimetre_depth(self):
		sent = _raw_frame()

		got = decode_raw(encode_raw(sent))

		np.testing.assert_array_equal(got.color_bgr, sent.color_bgr)
		assert got.intrinsics == INTR
		assert got.frame_id == 7
		assert got.depth_m.dtype == np.float32
		valid = np.isfinite(sent.depth_m) & (sent.depth_m > 0)
		np.testing.assert_allclose(got.depth_m[valid], sent.depth_m[valid], atol=0.0005)

	def test_missing_depth_stays_missing(self):
		got = decode_raw(encode_raw(_raw_frame()))
		assert (got.depth_m[0, :5] == 0).all()
		assert (got.depth_m[1, :5] == 0).all()

	def test_served_uncropped_next_to_the_streams(self, served):
		buffers, port = served
		conn = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
		conn.request("GET", "/raw.npz")
		assert conn.getresponse().status == 503  # nothing published yet
		conn.close()
		buffers["raw"].publish(None, {"frame": _raw_frame(3)})

		got = fetch_raw(f"http://127.0.0.1:{port}", timeout_s=5)

		assert got.frame_id == 3
		assert got.color_bgr.shape == (48, 64, 3)

	def test_only_plain_http_bridge_urls(self):
		with pytest.raises(ValueError, match="http://host:port"):
			fetch_raw("file:///etc/passwd")

	def test_an_empty_bridge_is_an_error_not_a_frame(self, served):
		_, port = served
		with pytest.raises(ConnectionError, match="503"):
			fetch_raw(f"http://127.0.0.1:{port}")

	def test_bridge_publishes_the_full_frame_even_when_streams_are_cropped(self):
		from defect_sorter.depth_bridge import run_bridge

		buffers = {"top": FrameBuffer(), "top_depth": FrameBuffer(), "raw": FrameBuffer()}

		def read():
			return np.zeros((48, 64, 3), np.uint8), _flat_depth(0.8), INTR

		run_bridge(
			read, buffers, mode="layers", crop_box=(8, 4, 40, 32), stop=lambda: buffers["top"].latest().frame_id >= 2
		)

		raw = buffers["raw"].latest().state["frame"]
		assert raw.color_bgr.shape == (48, 64, 3)
		assert raw.depth_m.shape == (48, 64)
		assert raw.intrinsics == INTR
		assert raw.frame_id == 2


class TestFreshFrames:
	def test_each_camera_frame_is_used_once(self):
		ids = iter([1, 1, 2, 2, 2, 3, 4])

		got = list(fresh_frames(lambda: _raw_frame(next(ids)), 3, timeout_s=1.0, poll_s=0.0))

		assert [f.frame_id for f in got] == [1, 2, 3]

	def test_a_stalled_bridge_times_out(self):
		with pytest.raises(TimeoutError, match="no new frame"):
			list(fresh_frames(lambda: _raw_frame(5), 2, timeout_s=0.05, poll_s=0.01))
