import pytest

from defect_sorter.hybrid import (
	REST,
	ROLL_LIMIT,
	SHOW_ROUTINE,
	GraspMonitor,
	GraspOutcome,
	PlaceOutcome,
	ReleaseMonitor,
	body_degrees,
	close_on_brick,
	environment_draft,
	model_control,
	normalized_state,
	offset_brick,
	place_instruction,
	port_holders,
	scripted_grasp_target,
	with_gripper,
)
from defect_sorter.joint_calibration import TICKS_PER_DEGREE

BODY = ("shoulder_pan", "shoulder_lift", "elbow_flex", "wrist_flex", "wrist_roll")


def state(grip: float, lift_mm: float) -> dict[str, float]:
	"""A joint state whose fake tool height (see ``height``) is ``lift_mm``."""
	return {
		"shoulder_pan": 0.0,
		"shoulder_lift": lift_mm,
		"elbow_flex": 0.0,
		"wrist_flex": 0.0,
		"wrist_roll": 0.0,
		"gripper": grip,
	}


def height(s: dict[str, float]) -> float:
	return s["shoulder_lift"]


def run(monitor: GraspMonitor, trace: list[tuple[float, float, float]]) -> GraspOutcome | None:
	"""Feed (t, grip, height) samples until the monitor decides; the decision or None."""
	for t, grip, h in trace:
		outcome = monitor.update(t, state(grip, h))
		if outcome is not None:
			return outcome
	return None


def ramp(t0: float, t1: float, a: float, b: float, dt: float = 0.1) -> list[tuple[float, float]]:
	n = round((t1 - t0) / dt)
	return [(t0 + k * dt, a + (b - a) * k / n) for k in range(n + 1)]


class TestGraspMonitor:
	def test_closing_on_the_brick_and_lifting_it_is_held(self):
		trace = [(t, 45.0, 0.0) for t in (0.0, 0.5, 1.0)]  # open at the hover
		trace += [(t, g, 0.0) for t, g in ramp(1.1, 2.0, 45.0, 15.0)]  # close on the brick: stops at its width
		trace += [(t, 15.0, h) for t, h in ramp(2.1, 3.5, 0.0, 40.0)]  # lift it
		assert run(GraspMonitor(height_mm=height), trace) is GraspOutcome.HELD

	def test_held_needs_the_lift_not_only_the_closed_gripper(self):
		trace = [(0.0, 45.0, 0.0)] + [(t, 15.0, 0.0) for t in (1.0, 2.0, 3.0, 4.0)]
		assert run(GraspMonitor(height_mm=height, timeout_s=10.0), trace) is None

	def test_closing_on_nothing_is_a_miss(self):
		trace = [(0.0, 45.0, 0.0)] + [(t, g, 0.0) for t, g in ramp(0.5, 1.5, 45.0, 2.0)]
		trace += [(t, 2.0, 5.0) for t in (1.6, 1.8, 2.0, 2.2, 2.4)]
		assert run(GraspMonitor(height_mm=height), trace) is GraspOutcome.MISSED

	def test_a_gripper_that_was_never_opened_decides_nothing_until_the_timeout(self):
		trace = [(t / 2, 15.0, 0.0) for t in range(10)]
		assert run(GraspMonitor(height_mm=height, timeout_s=10.0), trace) is None
		assert run(GraspMonitor(height_mm=height, timeout_s=3.0), trace) is GraspOutcome.TIMEOUT

	def test_times_out(self):
		trace = [(t, 45.0, 0.0) for t in (0.0, 5.0, 12.5)]
		assert run(GraspMonitor(height_mm=height, timeout_s=12.0), trace) is GraspOutcome.TIMEOUT


class TestUnits:
	def test_normalized_body_joints_become_degrees_around_the_range_midpoint(self):
		ranges = dict.fromkeys(BODY, (1000, 3000))  # half range 1000 ticks
		deg = body_degrees({"elbow_flex": 50.0, "wrist_roll": -100.0}, ranges)
		assert deg["elbow_flex"] == pytest.approx(500 / TICKS_PER_DEGREE)
		assert deg["wrist_roll"] == pytest.approx(-1000 / TICKS_PER_DEGREE)

	def test_studio_observation_keys_lose_their_pos_suffix(self):
		obs = {"shoulder_pan.pos": 1.0, "gripper.pos": 15.0}
		assert normalized_state(obs) == {"shoulder_pan": 1.0, "gripper": 15.0}


class TestPoses:
	def test_the_show_routine_and_rest_stay_inside_every_range_and_off_the_roll_end_stops(self):
		for hold in SHOW_ROUTINE:
			assert set(hold.pose) == set(BODY)
			assert all(-100.0 < v < 100.0 for v in hold.pose.values())
			assert abs(hold.pose["wrist_roll"]) <= ROLL_LIMIT < 100.0
			assert hold.hold_s >= 0.0
		assert set(REST) == set(BODY)
		assert all(-100.0 < v < 100.0 for v in REST.values())

	def test_the_routine_shows_both_roll_directions_and_the_bottom(self):
		rolls = [h.pose["wrist_roll"] for h in SHOW_ROUTINE]
		assert max(rolls) >= 60.0
		assert min(rolls) <= -60.0
		assert any(h.name == "bottom" for h in SHOW_ROUTINE)
		assert all(h.hold_s >= 1.0 for h in SHOW_ROUTINE if h.name != "return")


class TestStudioMessages:
	def test_environment_draft_names_robots_and_cameras_by_id(self):
		env = {
			"id": "e1",
			"name": "cell",
			"created_at": "x",
			"robots": [
				{
					"robot": {"id": "r1", "name": "Follower", "payload": {}},
					"tele_operator": {"type": "robot", "robot_id": "l1", "robot": {"id": "l1"}},
				}
			],
			"cameras": [{"id": "c1", "name": "front", "payload": {}}, {"id": "c2", "name": "wrist"}],
		}
		assert environment_draft(env) == {
			"id": "e1",
			"name": "cell",
			"robots": [{"robot_id": "r1", "tele_operator": {"type": "robot", "robot_id": "l1"}}],
			"cameras": [{"camera_id": "c1"}, {"camera_id": "c2"}],
		}

	def test_model_control_runs_the_task_at_30_hz_with_a_start_ramp(self):
		control = model_control("Pick up the brick.")
		assert control["type"] == "model"
		assert control["task"] == "Pick up the brick."
		assert control["hz"] == 30
		assert control["grace_s"] > 0
		assert control["execution"]["mode"] in ("sync", "async")


class TestGripperRamp:
	def test_the_gripper_moves_at_most_one_step_size_per_waypoint_and_ends_on_its_goal(self):
		path = [{"elbow_flex": 2000 + k} for k in range(10)]
		out = with_gripper(path, start=1000, goal=1100, max_step=30)
		grips = [wp["gripper"] for wp in out]
		assert grips[-1] == 1100
		assert all(abs(b - a) <= 30 for a, b in zip([1000, *grips], grips, strict=False))
		assert [wp["elbow_flex"] for wp in out[: len(path)]] == [wp["elbow_flex"] for wp in path]

	def test_a_short_path_is_extended_holding_its_last_pose_until_the_gripper_arrives(self):
		path = [{"elbow_flex": 2000}, {"elbow_flex": 2010}]
		out = with_gripper(path, start=1000, goal=1300, max_step=50)
		assert len(out) == 6  # 300 ticks at 50 per step
		assert all(wp["elbow_flex"] == 2010 for wp in out[2:])
		assert out[-1]["gripper"] == 1300

	def test_closing_ramps_too(self):
		out = with_gripper([{"elbow_flex": 2000}] * 4, start=1300, goal=1240, max_step=20)
		assert [wp["gripper"] for wp in out] == [1280, 1260, 1240, 1240]


class TestHoldingByCommandGap:
	def test_jaws_stopped_wider_than_commanded_and_lifted_is_held_at_any_width(self):
		monitor = GraspMonitor(height_mm=height)
		trace = [(0.0, 45.0, 45.0, 0.0), (0.5, 45.0, 45.0, 0.0)]  # (t, grip measured, grip commanded, height)
		trace += [(1.0 + 0.1 * k, 26.0, 5.0, 3.0 * k) for k in range(12)]  # held wide: 26 measured, 5 commanded
		outcome = None
		for t, grip, cmd, h in trace:
			outcome = monitor.update(t, state(grip, h), action={"gripper": cmd})
			if outcome is not None:
				break
		assert outcome is GraspOutcome.HELD

	def test_holding_now_reports_blocked_jaws_for_a_timeout_decision(self):
		monitor = GraspMonitor(height_mm=height, timeout_s=100.0)
		monitor.update(0.0, state(45.0, 0.0), action={"gripper": 45.0})
		monitor.update(1.0, state(24.0, 0.0), action={"gripper": 4.0})
		assert monitor.holding_now
		monitor.update(1.5, state(4.5, 0.0), action={"gripper": 4.0})
		assert not monitor.holding_now


class TestRealTimestamps:
	def test_decides_with_jittered_sample_times(self):
		# 10 Hz with real-world jitter: no two samples exactly 0.5 s apart
		times = [0.0, 0.098, 0.203, 0.297, 0.401, 0.502, 0.598, 0.699, 0.803, 0.901, 0.997, 1.104, 1.199, 1.302]
		monitor = GraspMonitor(height_mm=height)
		outcome = None
		for k, t in enumerate(times):
			grip = 45.0 if k < 3 else 1.6  # open, then shut on nothing
			outcome = monitor.update(t, state(grip, 0.0), action={"gripper": 1.0 if k >= 3 else 45.0})
			if outcome is not None:
				break
		assert outcome is GraspOutcome.MISSED
		assert t <= 0.95  # decided about settle_s after the jaws shut, not at the timeout


class TestPortHolders:
	def test_lists_other_processes_holding_the_device_and_ignores_this_one(self, tmp_path):
		dev = tmp_path / "ttyACM0"
		dev.write_text("")
		other = tmp_path / "proc" / "4242" / "fd"
		other.mkdir(parents=True)
		(other / "7").symlink_to(dev)
		mine = tmp_path / "proc" / "1001" / "fd"
		mine.mkdir(parents=True)
		(mine / "3").symlink_to(dev)
		idle = tmp_path / "proc" / "77" / "fd"
		idle.mkdir(parents=True)
		(idle / "0").symlink_to(tmp_path / "elsewhere")
		assert port_holders(str(dev), proc=tmp_path / "proc", own_pid=1001) == [4242]


class TestGraspOffset:
	def test_moves_only_the_brick_centre_in_the_table_plane(self):
		import numpy as np

		from defect_sorter.targeting import BrickPose

		brick = BrickPose(np.array([0.104, -0.033, 0.028]), -3.0, 0.032, 0.032, 300)
		moved = offset_brick(brick, dx_mm=14.0, dy_mm=20.0)
		np.testing.assert_allclose(moved.centre_m, [0.118, -0.013, 0.028])
		assert (moved.yaw_deg, moved.length_m, moved.width_m, moved.points) == (-3.0, 0.032, 0.032, 300)


class TestReleaseMonitor:
	def test_opening_after_holding_is_released(self):
		monitor = ReleaseMonitor()
		samples = [(0.1 * k, 15.0, 5.0) for k in range(20)]  # carrying: jaws blocked at the brick
		samples += [(2.0 + 0.1 * k, 15.0 + 3.0 * k, 45.0) for k in range(10)]  # opening over the bowl
		samples += [(3.0 + 0.1 * k, 44.0, 45.0) for k in range(8)]
		outcome = None
		for t, grip, cmd in samples:
			outcome = monitor.update(t, {"gripper": grip}, {"gripper": cmd})
			if outcome is not None:
				break
		assert outcome is PlaceOutcome.RELEASED
		assert t < 3.6

	def test_still_holding_times_out(self):
		monitor = ReleaseMonitor(timeout_s=5.0)
		outcomes = [monitor.update(0.5 * k, {"gripper": 15.0}, {"gripper": 5.0}) for k in range(12)]
		assert outcomes[-1] is PlaceOutcome.TIMEOUT
		assert all(o is None for o in outcomes[:10])


class TestPlaceInstruction:
	def test_the_bowl_becomes_the_trained_instruction_text(self):
		assert place_instruction("green") == "Place the brick in the green bowl on the left."
		assert place_instruction("pink") == "Place the brick in the pink bowl on the right."
		with pytest.raises(ValueError, match="blue"):
			place_instruction("blue")


class TestReplanning:
	def test_the_next_chunk_is_requested_while_most_of_the_current_one_is_left(self):
		assert model_control("Pick up the brick.", request_threshold=0.8)["execution"]["request_threshold"] == 0.8

	def test_the_threshold_must_be_a_fraction(self):
		with pytest.raises(ValueError, match="request_threshold"):
			model_control("Pick up the brick.", request_threshold=1.5)


class FakeGripper:
	"""A gripper that follows its goal, except that a brick stops it at ``block_at`` ticks."""

	def __init__(self, present: int, block_at: int | None) -> None:
		self.present, self.block_at, self.goals = present, block_at, []

	def read_ticks(self) -> dict[str, int]:
		return {"gripper": self.present}

	def write_goals(self, goals: dict[str, int]) -> None:
		g = goals["gripper"]
		self.goals.append(g)
		self.present = max(g, self.block_at) if self.block_at is not None else g


class TestCloseOnBrick:
	def test_stops_closing_where_the_brick_blocks_the_jaws_and_keeps_a_small_squeeze(self):
		bus = FakeGripper(present=1450, block_at=1150)
		squeeze = close_on_brick(bus, (1000, 2000), sleep=lambda s: None)
		assert squeeze is not None
		assert 1100 <= squeeze < 1150  # a little past the brick: it is held, not crushed
		assert bus.goals[-1] == squeeze

	def test_closing_on_nothing_is_a_miss(self):
		bus = FakeGripper(present=1450, block_at=None)
		assert close_on_brick(bus, (1000, 2000), sleep=lambda s: None) is None


class TestScriptedGraspTarget:
	def test_the_measured_correction_is_added_in_millimetres(self):
		import numpy as np

		target = scripted_grasp_target(np.array([0.10, -0.05, 0.008]), (-10.0, -17.0, 5.0))
		np.testing.assert_allclose(target, [0.090, -0.067, 0.013])


class TestControlChannel:
	"""JSON lines to and from the supervising dashboard; a stop or a lost supervisor interrupts like Ctrl+C."""

	def channel(self):
		import io

		from defect_sorter.hybrid import ControlChannel

		stops: list[int] = []
		out = io.StringIO()
		ch = ControlChannel(out, io.StringIO(), on_stop=lambda: stops.append(1), clock=lambda: 12.5)
		return ch, out, stops

	@staticmethod
	def lines(out) -> list[dict]:
		import json

		return [json.loads(line) for line in out.getvalue().splitlines()]

	def test_an_event_is_one_json_line_with_its_time(self):
		ch, out, _ = self.channel()
		ch.emit("phase", name="hover", steps=40)
		assert self.lines(out) == [{"event": "phase", "t": 12.5, "name": "hover", "steps": 40}]

	def test_a_question_returns_the_reply_with_its_id(self):
		import json
		import threading

		ch, out, _ = self.channel()

		def answer():
			while not out.getvalue():
				pass
			ask = self.lines(out)[0]
			ch.handle_line(json.dumps({"reply": ask["id"], "bowl": "pink"}))

		threading.Thread(target=answer, daemon=True).start()
		reply = ch.ask("decide", timeout_s=5, poll_s=0.01)
		assert self.lines(out)[0]["event"] == "decide"
		assert reply is not None
		assert reply["bowl"] == "pink"

	def test_a_reply_to_another_question_is_ignored_and_the_question_times_out(self):
		ch, _, _ = self.channel()
		ch.handle_line('{"reply": "someone-else", "bowl": "pink"}')
		assert ch.ask("decide", timeout_s=0.05, poll_s=0.01) is None

	def test_stop_interrupts_once_and_cancels_a_pending_question(self):
		ch, _, stops = self.channel()
		ch.handle_line('{"command": "stop"}')
		ch.handle_line('{"command": "stop"}')
		ch.handle_eof()
		assert stops == [1]
		assert ch.stopped
		assert ch.ask("view", timeout_s=5, poll_s=0.01) is None

	def test_the_interrupt_is_sent_before_a_waiting_question_can_see_the_stop(self):
		import io

		from defect_sorter.hybrid import ControlChannel

		seen = []
		ch = ControlChannel(io.StringIO(), io.StringIO(), on_stop=lambda: seen.append(ch.stopped))
		ch.handle_line('{"command": "stop"}')
		assert seen == [False], "the main thread must already have the interrupt pending when its wait ends"
		assert ch.stopped

	def test_a_lost_supervisor_stops_the_cycle_but_not_after_it_ended(self):
		ch, _, stops = self.channel()
		ch.handle_eof()
		assert stops == [1]
		ch2, _, stops2 = self.channel()
		ch2.close()
		ch2.handle_eof()
		assert stops2 == []

	def test_noise_on_the_input_is_ignored(self):
		ch, _, stops = self.channel()
		for line in ["", "not json", "[1, 2]", '{"command": "dance"}']:
			ch.handle_line(line)
		assert stops == []
		assert not ch.stopped

	def test_start_makes_sigint_raise_even_when_it_was_inherited_as_ignored(self):
		import io
		import signal

		from defect_sorter.hybrid import ControlChannel

		before = signal.signal(signal.SIGINT, signal.SIG_IGN)
		try:
			ch = ControlChannel(io.StringIO(), io.StringIO())
			ch.close()  # the empty input ends at once; a finished channel does not take that as a stop
			ch.start().join(timeout=5)
			assert signal.getsignal(signal.SIGINT) is signal.default_int_handler
		finally:
			signal.signal(signal.SIGINT, before)

	def test_the_reader_thread_takes_commands_from_the_input(self):
		import io

		from defect_sorter.hybrid import ControlChannel

		stops: list[int] = []
		ch = ControlChannel(io.StringIO(), io.StringIO('{"command": "stop"}\n'), on_stop=lambda: stops.append(1))
		ch.start().join(timeout=5)
		assert stops == [1]

	@pytest.mark.parametrize(
		("reply", "bowl"),
		[
			({"bowl": "green"}, "green"),
			({"bowl": "pink"}, "pink"),
			({"bowl": "blue"}, None),
			({"bowl": None}, None),
			(None, None),
		],
	)
	def test_only_a_known_bowl_is_taken_from_a_reply(self, reply, bowl):
		from defect_sorter.hybrid import bowl_from_reply

		assert bowl_from_reply(reply) == bowl


def test_an_event_to_a_supervisor_that_went_away_does_not_raise():
	import io

	from defect_sorter.hybrid import ControlChannel

	out = io.StringIO()
	out.close()
	ControlChannel(out, io.StringIO(), on_stop=lambda: None).emit("log", text="still holding")


class TestCommandLine:
	def test_auto_bowl_needs_a_supervisor_and_the_show(self):
		from defect_sorter.hybrid import main

		base = ["--port", "/dev/null", "--bridge", "http://h:1", "--model", "m"]
		with pytest.raises(SystemExit):
			main([*base, "--bowl", "auto"])
		with pytest.raises(SystemExit):
			main([*base, "--bowl", "auto", "--control", "stdio", "--no-show"])


def test_squeeze_goal_clamps_offset_to_tracking_cap():
	from defect_sorter.hybrid import _squeeze_goal

	# 4% of 2000 is 80, 0.7 * 100 is 70 -> capped at 70 below present
	assert _squeeze_goal(1500, {"gripper": (1000, 3000)}, track=100) == 1430
	# 4% of 1000 is 40, 0.7 * 100 is 70 -> uses 40 below present
	assert _squeeze_goal(1500, {"gripper": (1000, 2000)}, track=100) == 1460


def test_plan_scripted_descent_caps_speed_and_height(monkeypatch):
	import numpy as np

	from defect_sorter import motion
	from defect_sorter.hybrid import _plan_scripted_descent

	seen: dict[str, object] = {}

	def fake_plan_move(start, target_m, *, roll_deg, calibration, limits, ranges, dt_s, approach_table):
		from types import SimpleNamespace

		seen["target_m"] = target_m
		seen["limits"] = limits
		seen["roll_deg"] = roll_deg
		seen["dt_s"] = dt_s
		return SimpleNamespace(ok=True, path=[dict(start)], reason="")

	monkeypatch.setattr(motion, "plan_move", fake_plan_move)

	class FakeRoll:
		roll_deg = 12.5

	class FakeChoice:
		grasp_m = np.array([0.2, 0.0, 0.02])
		approach = np.array([0.0, 0.0, -1.0])
		roll = FakeRoll()

	res = _plan_scripted_descent(
		{"shoulder_pan": 0.0},
		FakeChoice(),
		correction_mm=(5.0, -2.0, 1.0),
		speed=25.0,
		reach_mm=380.0,
		calibration=object(),
		ranges={},
		dt=0.05,
	)
	assert res.ok
	assert seen["roll_deg"] == 12.5
	assert seen["dt_s"] == 0.05
	assert seen["limits"].max_speed_deg_s == 10.0
	assert seen["limits"].min_tool_height_m == 0.004
	assert np.allclose(seen["target_m"], np.array([0.205, -0.002, 0.021]))
