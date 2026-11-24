import io
import json
import signal
import subprocess

import cv2
import numpy as np
import pytest

from defect_sorter.alignment import TableFrame
from defect_sorter.cell_link import (
	CellHub,
	CycleRun,
	TableWatcher,
	decide_bowl,
	measure_frame,
	read_scene,
	verify_drop,
)
from defect_sorter.depth_bridge import RawFrame
from defect_sorter.geometry import Intrinsics, Plane

# ------------------------------------------------------------------------------------------------ decision


def view(name, label, score):
	return {"name": name, "label": label, "score": score}


class TestDecideBowl:
	def test_every_scored_view_good_goes_to_green_with_the_worst_score(self):
		d = decide_bowl(
			[view("level", "normal", 0.1), view("roll_right", "normal", 0.3), view("bottom", "normal", 0.2)]
		)
		assert d["bowl"] == "green"
		assert d["label"] == "normal"
		assert d["score"] == pytest.approx(0.3)

	def test_one_defective_view_rejects_the_brick(self):
		d = decide_bowl(
			[view("level", "normal", 0.1), view("roll_left", "defective", 0.8), view("bottom", "uncertain", None)]
		)
		assert d["bowl"] == "pink"
		assert d["label"] == "defective"
		assert d["score"] == pytest.approx(0.8)
		assert "roll_left" in d["reason"]

	def test_a_view_inside_the_uncertain_band_waits_for_a_person(self):
		d = decide_bowl(
			[view("level", "normal", 0.1), view("roll_right", "uncertain", 0.5), view("bottom", "normal", 0.2)]
		)
		assert d["bowl"] is None
		assert d["label"] == "uncertain"
		assert "roll_right" in d["reason"]

	def test_too_few_scored_views_wait_for_a_person(self):
		d = decide_bowl([view("level", "normal", 0.1), view("bottom", "uncertain", None)], min_views=2)
		assert d["bowl"] is None
		assert d["label"] == "uncertain"
		assert "1 of 2" in d["reason"]

	def test_no_views_at_all_is_uncertain_with_no_score(self):
		d = decide_bowl([])
		assert d["bowl"] is None
		assert d["score"] is None


class TestVerifyDrop:
	def test_one_more_object_in_the_chosen_bowl_confirms_the_drop(self):
		v = verify_drop({"green": 0, "pink": 2}, {"green": 0, "pink": 3}, "pink")
		assert v["confirmed"] is True

	def test_nothing_new_in_the_bowl_is_not_confirmed(self):
		v = verify_drop({"green": 1, "pink": 0}, {"green": 1, "pink": 0}, "pink")
		assert v["confirmed"] is False
		assert "pink" in v["text"]

	def test_landing_in_the_other_bowl_is_reported(self):
		v = verify_drop({"green": 0, "pink": 0}, {"green": 1, "pink": 0}, "pink")
		assert v["confirmed"] is False
		assert "green" in v["text"]

	def test_without_a_table_reading_nothing_is_claimed(self):
		assert verify_drop(None, {"pink": 1}, "pink")["confirmed"] is None
		assert verify_drop({"pink": 0}, None, "pink")["confirmed"] is None


# ------------------------------------------------------------------------------------------------ cycle supervision


class Pipe(io.StringIO):
	"""stdin of the fake child: keeps what was written readable after close."""

	def close(self):
		self.was_closed = True


class FakeProcess:
	def __init__(self, argv):
		self.argv = argv
		self.stdin = Pipe()
		self.stdin.was_closed = False
		self.signals = []
		self.returncode = None

	def poll(self):
		return self.returncode

	def send_signal(self, sig):
		self.signals.append(sig)

	def wait(self, timeout=None):
		if self.returncode is None:
			raise subprocess.TimeoutExpired(self.argv, timeout)
		return self.returncode

	def written(self):
		return [json.loads(line) for line in self.stdin.getvalue().splitlines()]


BASE = ["python", "-m", "defect_sorter.hybrid", "--port", "/dev/ttyACM0", "--bridge", "http://h:8092", "--model", "m1"]


def cycle(go=True, inspect=None, clock=None, on_end=None, bowl=None, unsure=None):
	processes = []

	def spawn(argv):
		p = FakeProcess(argv)
		processes.append(p)
		return p

	t = clock or [100.0]
	run = CycleRun(
		BASE,
		go=go,
		inspect_view=inspect or (lambda name: {"label": "normal", "score": 0.1, "reason": None}),
		spawn=spawn,
		background=False,
		clock=lambda: t[0],
		on_end=on_end,
		preset_bowl=bowl,
		unsure_bowl=unsure,
	)
	run.start()
	return run, processes[0], t


def event(kind, **fields):
	return json.dumps({"event": kind, "t": 0.0, **fields})


class TestCycleCommand:
	def test_the_dashboard_adds_the_auto_bowl_and_stdio_control_and_go_only_when_asked(self):
		_, moving, _ = cycle(go=True)
		_, planning, _ = cycle(go=False)
		assert moving.argv == [*BASE, "--bowl", "auto", "--control", "stdio", "--go"]
		assert planning.argv == [*BASE, "--bowl", "auto", "--control", "stdio"]

	@pytest.mark.parametrize("extra", [["--go"], ["--bowl", "green"], ["--control", "none"]])
	def test_a_configured_command_may_not_decide_the_bowl_or_motion_itself(self, extra):
		with pytest.raises(ValueError, match="dashboard"):
			CycleRun([*BASE, *extra], go=False, inspect_view=lambda n: {}, spawn=FakeProcess, background=False)


class TestCycleEvents:
	def test_phases_become_timed_steps_and_data_is_kept(self):
		run, _, t = cycle()
		run.feed(event("phase", name="measure", go=True))
		run.feed(event("bowls", bowls={"green": {"centre_mm": [7, -235, 10], "radius_mm": 90}}))
		t[0] = 102.0
		run.feed(event("brick", attempt=1, centre_mm=[81, -81, 19], yaw_deg=12.0, size_mm=[31, 26]))
		run.feed(event("phase", name="hover", attempt=1, steps=220, seconds=99.0))
		t[0] = 113.0
		run.feed(event("phase", name="grasp", attempt=1, mode="policy"))
		snap = run.snapshot()
		assert snap["phase"] == "grasp"
		assert [s["name"] for s in snap["steps"]] == ["measure", "hover", "grasp"]
		assert snap["steps"][0]["seconds"] == pytest.approx(2.0)
		assert snap["steps"][1]["seconds"] == pytest.approx(11.0), "an event field never replaces the measured time"
		assert snap["steps"][2]["seconds"] is None, "the current step is still running"
		assert snap["bowls"]["green"]["radius_mm"] == 90
		assert snap["brick"]["centre_mm"] == [81, -81, 19]
		assert snap["attempt"] == 1

	def test_log_lines_and_raw_output_are_kept_newest_last(self):
		run, _, _ = cycle()
		run.feed(event("log", text="green bowl at (7, -235) mm"))
		run.feed("Traceback (most recent call last):")
		assert [line["text"] for line in run.snapshot()["log"]][-2:] == [
			"green bowl at (7, -235) mm",
			"Traceback (most recent call last):",
		]

	def test_each_view_is_inspected_and_answered(self):
		seen = []

		def inspect(name):
			seen.append(name)
			return {"label": "normal", "score": 0.12, "reason": None, "crop_jpeg": b"\xff\xd8crop"}

		run, proc, _ = cycle(inspect=inspect)
		run.feed(event("view", id="q1", name="level", timeout_s=8))
		assert seen == ["level"]
		assert proc.written() == [{"reply": "q1"}]
		views = run.snapshot()["views"]
		assert views == [
			{
				"name": "level",
				"label": "normal",
				"score": 0.12,
				"reason": None,
				"timings_ms": None,
				"cameras": None,
				"crop": True,
			}
		]
		assert run.view_crop(0) == b"\xff\xd8crop"
		assert run.view_crop(5) is None

	def test_per_camera_scores_are_kept_with_the_view(self):
		cams = {"front": {"score": 51.2, "threshold": 43.5, "verdict": "defective", "frames": 3}}
		run, _, _ = cycle(inspect=lambda n: {"label": "defective", "score": 0.59, "reason": None, "cameras": cams})
		run.feed(event("view", id="q1", name="bottom", timeout_s=8))
		assert run.snapshot()["views"][0]["cameras"] == cams

	def test_a_failed_inspection_is_a_missing_view_and_the_show_goes_on(self):
		def inspect(name):
			raise OSError("camera gone")

		run, proc, _ = cycle(inspect=inspect)
		run.feed(event("view", id="q1", name="bottom", timeout_s=8))
		assert proc.written() == [{"reply": "q1"}]
		v = run.snapshot()["views"][0]
		assert v["label"] == "uncertain"
		assert v["score"] is None
		assert "camera gone" in v["reason"]

	def test_clean_views_decide_the_bowl_without_a_person(self):
		run, proc, _ = cycle()
		for name in ("level", "roll_right", "roll_left", "bottom"):
			run.feed(event("view", id=name, name=name, timeout_s=8))
		run.feed(event("decide", id="d1", timeout_s=120))
		assert proc.written()[-1] == {"reply": "d1", "bowl": "green", "source": "inspection"}
		snap = run.snapshot()
		assert snap["decision"]["bowl"] == "green"
		assert snap["decision"]["source"] == "inspection"
		assert snap["awaiting_review"] is False

	def test_an_unsure_brick_waits_for_the_operator_who_chooses_once(self):
		run, proc, _ = cycle(inspect=lambda n: {"label": "uncertain", "score": 0.5, "reason": None})
		run.feed(event("view", id="v", name="level", timeout_s=8))
		run.feed(event("decide", id="d1", timeout_s=120))
		assert proc.written() == [{"reply": "v"}], "no bowl is sent on an uncertain result"
		assert run.snapshot()["awaiting_review"] is True
		assert run.review("pink") == (200, {"bowl": "pink"})
		assert proc.written()[-1] == {"reply": "d1", "bowl": "pink", "source": "operator"}
		snap = run.snapshot()
		assert snap["decision"]["source"] == "operator"
		assert snap["awaiting_review"] is False
		assert run.review("green")[0] == 409, "the decision is taken once"

	def test_a_bowl_named_in_the_command_is_used_after_the_views_are_still_inspected(self):
		run, proc, _ = cycle(inspect=lambda n: {"label": "defective", "score": 0.9, "reason": None}, bowl="green")
		run.feed(event("view", id="v", name="level", timeout_s=8))
		run.feed(event("decide", id="d1", timeout_s=120))
		assert proc.written()[-1] == {"reply": "d1", "bowl": "green", "source": "command"}
		decision = run.snapshot()["decision"]
		assert decision["bowl"] == "green"
		assert decision["label"] == "defective", "the inspection result is still shown"
		assert decision["source"] == "command"

	def test_with_unsure_to_pink_an_unsure_brick_is_rejected_without_waiting(self):
		run, proc, _ = cycle(inspect=lambda n: {"label": "uncertain", "score": 0.52, "reason": None}, unsure="pink")
		run.feed(event("view", id="v", name="level", timeout_s=8))
		run.feed(event("decide", id="d1", timeout_s=120))
		assert proc.written()[-1] == {"reply": "d1", "bowl": "pink", "source": "rule"}
		snap = run.snapshot()
		assert snap["awaiting_review"] is False
		assert snap["decision"]["label"] == "uncertain"
		assert "unsure" in snap["decision"]["reason"]

	def test_a_preset_bowl_must_be_a_known_one(self):
		with pytest.raises(ValueError, match="bowl"):
			CycleRun(BASE, go=False, inspect_view=lambda n: {}, spawn=FakeProcess, background=False, preset_bowl="blue")

	def test_the_operator_can_hold_the_brick_instead(self):
		run, proc, _ = cycle(inspect=lambda n: {"label": "uncertain", "score": None, "reason": "no brick"})
		run.feed(event("decide", id="d1", timeout_s=120))
		assert run.review(None) == (200, {"bowl": None})
		assert proc.written()[-1] == {"reply": "d1", "bowl": None, "source": "operator"}

	def test_a_review_choice_must_name_a_bowl(self):
		run, _, _ = cycle(inspect=lambda n: {"label": "uncertain", "score": 0.5, "reason": None})
		run.feed(event("decide", id="d1", timeout_s=120))
		assert run.review("blue")[0] == 400

	def test_the_end_event_finishes_the_cycle_once(self):
		ended = []
		run, proc, t = cycle(on_end=ended.append)
		run.feed(event("phase", name="measure"))
		t[0] = 160.0
		run.feed(event("end", ok=True, reason=None))
		proc.returncode = 0
		run.finish(0)
		snap = run.snapshot()
		assert snap["phase"] == "done"
		assert snap["end"] == {"ok": True, "reason": None}
		assert snap["active"] is False
		assert snap["seconds"] == pytest.approx(60.0)
		assert ended == [run]

	def test_an_exit_without_a_report_is_a_failure(self):
		run, proc, _ = cycle()
		proc.returncode = 1
		run.finish(1)
		snap = run.snapshot()
		assert snap["phase"] == "failed"
		assert snap["end"]["ok"] is False
		assert "1" in snap["end"]["reason"]

	def test_a_reported_hold_for_review_and_a_stop_are_told_apart(self):
		held, _, _ = cycle()
		held.feed(event("end", ok=False, reason="held for review: no bowl was chosen"))
		held.finish(1)
		assert held.snapshot()["phase"] == "held"
		stopped, _, _ = cycle()
		stopped.stop()
		stopped.feed(event("end", ok=False, reason="stopped by the operator: the arm holds where it is"))
		stopped.finish(130)
		assert stopped.snapshot()["phase"] == "stopped"


class TestCycleStartFailure:
	def test_a_command_that_cannot_start_is_a_failed_cycle_with_the_reason(self):
		def spawn(argv):
			raise FileNotFoundError(2, "No such file or directory", argv[0])

		ended = []
		run = CycleRun(BASE, go=True, inspect_view=lambda n: {}, spawn=spawn, background=False, on_end=ended.append)
		with pytest.raises(FileNotFoundError, match="No such file"):
			run.start()
		snap = run.snapshot()
		assert snap["phase"] == "failed"
		assert snap["active"] is False
		assert "could not start" in snap["end"]["reason"]
		assert ended == [], "nothing ran, so there is nothing to verify"

	def test_the_hub_reports_it_and_stays_free_for_the_next_start(self):
		def spawn(argv):
			raise FileNotFoundError(2, "No such file or directory", argv[0])

		h = CellHub(
			hybrid_command=BASE,
			control_enabled=True,
			table=None,
			inspect_view=None,
			run_factory=lambda command, **kw: CycleRun(command, spawn=spawn, background=False, **kw),
			background=False,
		)
		status, body = h.start({"go": False})
		assert status == 502
		assert "could not start" in body["error"]
		assert h.state()["cycle"]["phase"] == "failed"
		assert h.start({"go": False})[0] == 502, "a failed start does not block the next one"


class TestCycleStop:
	def test_stop_is_sent_on_stdin_which_is_then_closed(self):
		run, proc, _ = cycle()
		assert run.stop() == {"stopping": True}
		assert proc.written() == [{"command": "stop"}]
		assert proc.stdin.was_closed
		assert run.snapshot()["stop_requested"] is True

	def test_a_child_that_does_not_exit_after_the_grace_gets_sigint(self):
		run, proc, _ = cycle()
		run.stop()
		run.enforce_stop(grace_s=0)
		assert proc.signals == [signal.SIGINT]

	def test_the_backup_sigint_waits_longer_than_a_policy_takes_to_release_control(self):
		import inspect

		grace = inspect.signature(CycleRun.enforce_stop).parameters["grace_s"].default
		assert grace > 10.0, "hybrid waits up to 10 s for set_control None; a second SIGINT would cut that short"

	def test_a_child_that_exited_is_left_alone(self):
		run, proc, _ = cycle()
		run.stop()
		proc.returncode = 130
		run.enforce_stop(grace_s=0)
		assert proc.signals == []

	def test_stopping_a_finished_cycle_does_nothing(self):
		run, proc, _ = cycle()
		run.feed(event("end", ok=True, reason=None))
		proc.returncode = 0
		run.finish(0)
		assert run.stop() == {"stopping": False}
		assert proc.written() == []


# ------------------------------------------------------------------------------------------------ hub


class FakeTable:
	def __init__(self, counts):
		self.counts = counts

	def state(self):
		return {"status": "live", "reading": {"in_bowl": self.counts[0]}}

	def jpeg(self):
		return b"\xff\xd8table"

	def counts_now(self):
		return self.counts.pop(0) if len(self.counts) > 1 else self.counts[0]


class FakeRun:
	def __init__(self, command, **kwargs):
		self.command, self.kwargs = command, kwargs
		self.stopped = False
		self.active = True
		self.verified = None

	def start(self):
		pass

	def stop(self):
		self.stopped = True
		return {"stopping": True}

	def snapshot(self):
		return {"active": self.active, "phase": "measure"}

	def review(self, bowl):
		return 200, {"bowl": bowl}

	def set_verify(self, result):
		self.verified = result


def hub(command=BASE, control=True, busy=False, table=None):
	runs = []

	def factory(command, **kwargs):
		r = FakeRun(command, **kwargs)
		runs.append(r)
		return r

	h = CellHub(
		hybrid_command=command,
		control_enabled=control,
		table=table,
		inspect_view=lambda name: {"label": "normal", "score": 0.1},
		run_factory=factory,
		busy=lambda: busy,
		background=False,
	)
	return h, runs


class TestCellHub:
	def test_without_a_hybrid_command_no_cycle_can_start(self):
		h, runs = hub(command=None)
		assert h.start({"go": False})[0] == 409
		assert runs == []
		assert h.state()["configured"] is False

	def test_a_moving_cycle_needs_control_from_the_command_line_but_a_plan_does_not(self):
		h, runs = hub(control=False)
		status, body = h.start({"go": True})
		assert status == 403
		assert "--cell-control" in body["error"]
		assert h.start({"go": False})[0] == 202
		assert runs[0].kwargs["go"] is False

	def test_a_named_bowl_is_passed_to_the_cycle_and_anything_else_is_refused(self):
		h, runs = hub()
		assert h.start({"go": True, "bowl": "pink"})[0] == 202
		assert runs[0].kwargs["preset_bowl"] == "pink"
		runs[0].active = False
		assert h.start({"go": True, "bowl": "blue"})[0] == 400
		assert h.start({"go": True})[0] == 202
		assert runs[1].kwargs["preset_bowl"] is None

	def test_only_a_real_true_starts_motion(self):
		h, runs = hub()
		h.start({"go": "yes"})
		assert runs[0].kwargs["go"] is False

	def test_one_cycle_at_a_time_and_none_while_a_studio_run_is_active(self):
		h, runs = hub()
		assert h.start({"go": True})[0] == 202
		assert h.start({"go": True})[0] == 409
		runs[0].active = False
		assert h.start({"go": True})[0] == 202
		busy, _ = hub(busy=True)
		assert busy.start({"go": False})[0] == 409

	def test_stop_reaches_the_active_cycle_and_is_harmless_without_one(self):
		h, runs = hub()
		assert h.stop() == {"stopping": False}
		h.start({"go": True})
		assert h.stop() == {"stopping": True}
		assert runs[0].stopped

	def test_review_without_a_cycle_is_refused(self):
		h, _ = hub()
		assert h.review({"bowl": "pink"})[0] == 409
		h.start({"go": True})
		assert h.review({"bowl": "pink"}) == (200, {"bowl": "pink"})

	def test_a_finished_drop_is_verified_against_the_table_before_and_after(self):
		table = FakeTable([{"green": 0, "pink": 0}, {"green": 0, "pink": 1}])
		h, runs = hub(table=table)
		h.start({"go": True})
		run = runs[0]
		run.decided_bowl = "pink"
		run.kwargs["on_end"](run)
		assert run.verified["confirmed"] is True

	def test_state_says_what_the_operator_may_do(self):
		h, _ = hub(control=False)
		s = h.state()
		assert s["configured"] is True
		assert s["control_enabled"] is False
		assert s["cycle"] is None
		assert s["table"] is None
		assert s["inspector"]["model"]
		assert s["unsure_bowl"] is None

	def test_the_unsure_rule_and_the_inspector_reach_the_cycle_and_the_page(self):
		runs = []
		info = {
			"model": "inspect-v3 PatchCore",
			"device": "NPU",
			"thresholds": {"normal_below": 0.45, "defective_above": 0.55},
		}
		h = CellHub(
			hybrid_command=BASE,
			control_enabled=True,
			table=None,
			inspect_view=lambda name: {},
			inspector_info=info,
			unsure_bowl="pink",
			run_factory=lambda command, **kw: runs.append(kw) or FakeRun(command, **kw),
			background=False,
		)
		h.start({"go": True})
		assert runs[0]["unsure_bowl"] == "pink"
		assert h.state()["inspector"] == info
		assert h.state()["unsure_bowl"] == "pink"
		with pytest.raises(ValueError, match="unsure"):
			CellHub(hybrid_command=BASE, control_enabled=True, table=None, inspect_view=None, unsure_bowl="green")


# ------------------------------------------------------------------------------------------------ table from depth

TOP_INTR = Intrinsics(fx=600.0, fy=600.0, ppx=320.0, ppy=240.0)
TOP_H = 0.60
R_TOP = np.array([[1.0, 0.0, 0.0], [0.0, -1.0, 0.0], [0.0, 0.0, -1.0]])  # columns: camera x, y, z in table coords
TOP_FRAME = TableFrame(origin=-R_TOP.T @ np.array([0.0, 0.0, TOP_H]), axes=R_TOP, basis="anchors 16->17")
TOP_PLANE = Plane(normal=R_TOP.T @ np.array([0.0, 0.0, 1.0]), offset=TOP_H, inlier_fraction=1.0)
GREEN_C, PINK_C, BOWL_R, RIM_H = np.array([-0.09, 0.05]), np.array([0.11, 0.05]), 0.075, 0.015
BRICK_XY, BRICK_H = np.array([0.02, -0.13]), 0.019


def render_cell(brick_in_pink: bool) -> tuple[np.ndarray, np.ndarray]:
	"""Straight-down view: green and pink plates (rim 15 mm), a 32 x 16 mm brick on the table, optionally one in pink."""
	h, w = 480, 640
	v, u = np.mgrid[0:h, 0:w]

	def at(z):
		"""Table x, y where each pixel's ray meets the horizontal plane at height ``z`` (pinhole, straight down)."""
		return (u - TOP_INTR.ppx) * (TOP_H - z) / TOP_INTR.fx, -(v - TOP_INTR.ppy) * (TOP_H - z) / TOP_INTR.fy

	height = np.zeros((h, w))
	color = np.full((h, w, 3), 205, np.uint8)
	for centre, bgr in ((GREEN_C, (120, 150, 0)), (PINK_C, (180, 100, 240))):
		floor, rim = (np.hypot(x - centre[0], y - centre[1]) for x, y in (at(0.003), at(RIM_H)))
		height = np.where(floor < BOWL_R - 0.008, 0.003, height)
		height = np.where((rim >= BOWL_R - 0.008) & (rim < BOWL_R), RIM_H, height)
		color[floor < BOWL_R] = bgr
	x, y = at(BRICK_H)
	brick = (abs(x - BRICK_XY[0]) < 0.016) & (abs(y - BRICK_XY[1]) < 0.008)  # top face; walls are edge-on
	height = np.where(brick, BRICK_H, height)
	color[brick] = (200, 80, 30)
	if brick_in_pink:
		x, y = at(0.03)
		height = np.where((abs(x - PINK_C[0]) < 0.016) & (abs(y - PINK_C[1]) < 0.016), 0.03, height)
	return color, (TOP_H - height).astype(np.float32)


class TestReadScene:
	def test_bowls_the_loose_brick_and_what_lies_in_each_bowl(self):
		color, depth = render_cell(brick_in_pink=True)
		reading = read_scene(color, depth, TOP_INTR, TOP_PLANE, TOP_FRAME)
		bowls = {b["colour"]: b for b in reading["bowls"]}
		assert set(bowls) == {"green", "pink"}
		np.testing.assert_allclose(bowls["green"]["centre_mm"][:2], GREEN_C * 1000, atol=4)
		np.testing.assert_allclose(bowls["pink"]["centre_mm"][:2], PINK_C * 1000, atol=4)
		assert bowls["pink"]["radius_mm"] == pytest.approx((BOWL_R - 0.004) * 1000, abs=5)
		assert len(reading["bricks"]) == 1
		brick = reading["bricks"][0]
		np.testing.assert_allclose(brick["centre_mm"][:2], BRICK_XY * 1000, atol=3)
		assert brick["centre_mm"][2] == pytest.approx(BRICK_H * 1000, abs=2)
		assert brick["size_mm"][0] == pytest.approx(32, abs=3)
		assert brick["size_mm"][1] == pytest.approx(16, abs=3)
		assert reading["in_bowl"] == {"green": 0, "pink": 1}

	def test_the_robot_base_area_is_not_a_brick(self):
		color, depth = render_cell(brick_in_pink=False)
		reading = read_scene(color, depth, TOP_INTR, TOP_PLANE, TOP_FRAME, exclude_xy_m=BRICK_XY + 0.05)
		assert reading["bricks"] == []


class TestMeasureFrame:
	def test_without_the_anchor_markers_there_are_no_table_positions_but_still_a_picture(self):
		color, depth = render_cell(brick_in_pink=False)
		reading, jpeg = measure_frame(RawFrame(color, depth, TOP_INTR, 7), anchors=(16, 17))
		assert reading["frame_id"] == 7
		assert reading["table"] is None
		assert "16" in reading["reason"]
		assert reading["bowls"] == []
		assert reading["bricks"] == []
		image = cv2.imdecode(np.frombuffer(jpeg, np.uint8), cv2.IMREAD_COLOR)
		assert image.shape == (480, 640, 3)


class TestTableWatcher:
	def test_reads_while_watched_and_reports_a_failed_read(self):
		frames = [RawFrame(np.zeros((4, 4, 3), np.uint8), np.zeros((4, 4), np.float32), TOP_INTR, 1)]

		def fetch():
			if not frames:
				raise ConnectionError("bridge answered 503")
			return frames.pop()

		clock = [50.0]
		watcher = TableWatcher(
			fetch, lambda raw: ({"frame_id": raw.frame_id, "in_bowl": {"pink": 0}}, b"J"), clock=lambda: clock[0]
		)
		assert watcher.state()["status"] == "idle"
		assert watcher.wanted()
		watcher.read_once()
		state = watcher.state()
		assert state["status"] == "live"
		assert state["reading"]["frame_id"] == 1
		assert watcher.jpeg() == b"J"
		watcher.read_once()
		state = watcher.state()
		assert state["status"] == "error"
		assert "503" in state["error"]
		assert state["reading"]["frame_id"] == 1, "the last good reading stays, marked by its age"
		clock[0] += 60
		assert not watcher.wanted()

	def test_counts_now_reads_a_fresh_frame(self):
		frame = RawFrame(np.zeros((4, 4, 3), np.uint8), np.zeros((4, 4), np.float32), TOP_INTR, 3)
		watcher = TableWatcher(lambda: frame, lambda raw: ({"in_bowl": {"pink": 2}}, b"J"))
		assert watcher.counts_now() == {"pink": 2}
		broken = TableWatcher(lambda: (_ for _ in ()).throw(OSError("down")), lambda raw: ({}, b""))
		assert broken.counts_now() is None


# ------------------------------------------------------------------------------------------------ real child process

CHILD = """
import sys
from defect_sorter.hybrid import ControlChannel

ch = ControlChannel(sys.stdout, sys.stdin)
ch.start()
try:
	ch.emit("phase", name="show")
	ch.ask("view", timeout_s=10, name="level")
	ch.ask("view", timeout_s=10, name="bottom")
	ch.emit("phase", name="decide")
	reply = ch.ask("decide", timeout_s=30)
	if reply is None or reply.get("bowl") is None:
		ch.close()
		ch.emit("end", ok=False, reason="held for review: no bowl was chosen")
		sys.exit(1)
	ch.emit("phase", name="released", bowl=reply["bowl"])
	ch.close()
	ch.emit("end", ok=True, reason=None)
except KeyboardInterrupt:
	ch.close()
	ch.emit("end", ok=False, reason="stopped by the operator: the arm holds where it is")
	sys.exit(130)
"""


def child_cycle(tmp_path, inspect):
	import sys
	import threading

	script = tmp_path / "fake_hybrid.py"
	script.write_text(CHILD)
	ended = threading.Event()
	run = CycleRun([sys.executable, str(script)], go=False, inspect_view=inspect, on_end=lambda r: ended.set())
	run.start()
	return run, ended


def wait_for(predicate, timeout_s=10.0):
	import time

	end = time.monotonic() + timeout_s
	while time.monotonic() < end:
		if predicate():
			return True
		time.sleep(0.02)
	return False


def test_a_real_child_runs_the_whole_protocol_to_the_bowl(tmp_path):
	run, ended = child_cycle(tmp_path, lambda name: {"label": "normal", "score": 0.1, "reason": None})
	assert ended.wait(15)
	snap = run.snapshot()
	assert snap["phase"] == "done"
	assert snap["released_bowl"] == "green"
	assert [v["name"] for v in snap["views"]] == ["level", "bottom"]
	assert snap["decision"]["source"] == "inspection"


def test_stop_reaches_a_real_child_waiting_for_a_decision_as_sigint(tmp_path):
	run, ended = child_cycle(tmp_path, lambda name: {"label": "uncertain", "score": 0.5, "reason": None})
	assert wait_for(lambda: run.snapshot()["awaiting_review"])
	assert run.stop() == {"stopping": True}
	assert ended.wait(15)
	snap = run.snapshot()
	assert snap["phase"] == "stopped"
	assert snap["end"]["reason"].startswith("stopped by the operator")
	assert run.stop() == {"stopping": False}


def test_an_operator_choice_reaches_a_real_child(tmp_path):
	run, ended = child_cycle(tmp_path, lambda name: {"label": "uncertain", "score": None, "reason": "no brick"})
	assert wait_for(lambda: run.snapshot()["awaiting_review"])
	assert run.review("pink")[0] == 200
	assert ended.wait(15)
	assert run.snapshot()["released_bowl"] == "pink"


def test_stop_still_works_when_the_dashboard_was_started_with_sigint_ignored(tmp_path):
	"""``nohup cmd &`` from a script starts the dashboard, and so every child, with SIGINT ignored."""
	import sys
	import threading

	script = tmp_path / "fake_hybrid.py"
	script.write_text(CHILD)
	ended = threading.Event()

	def spawn_ignoring_sigint(argv):
		return subprocess.Popen(  # noqa: S603 - this test's own interpreter and script
			argv,
			stdin=subprocess.PIPE,
			stdout=subprocess.PIPE,
			stderr=subprocess.PIPE,
			text=True,
			bufsize=1,
			preexec_fn=lambda: signal.signal(signal.SIGINT, signal.SIG_IGN),
		)

	run = CycleRun(
		[sys.executable, str(script)],
		go=False,
		inspect_view=lambda name: {"label": "uncertain", "score": 0.5, "reason": None},
		spawn=spawn_ignoring_sigint,
		on_end=lambda r: ended.set(),
	)
	run.start()
	assert wait_for(lambda: run.snapshot()["awaiting_review"])
	run.stop()
	assert ended.wait(15)
	assert run.snapshot()["phase"] == "stopped", run.snapshot()["end"]
