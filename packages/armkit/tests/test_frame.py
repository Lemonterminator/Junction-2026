import pytest
from armkit.calibration import TICKS_PER_DEGREE as TPD
from armkit.frame import ModelFrame, capture_frame, refine_frame
from armkit.park import current_pose
from test_park import arm


class TestFrame:
	def test_offsets_make_the_readings_match_the_reference_pose(self):
		bus, prof = arm(a_deg=10.0, b_deg=-30.0)  # stored-midpoint angles of the arm as it stands
		frame = capture_frame(bus, prof, {"a": 0.0, "b": 60.0})  # ...while the operator says it is really here
		assert frame.offsets_deg["a"] == pytest.approx(-10.0, abs=0.2)
		assert frame.offsets_deg["b"] == pytest.approx(90.0, abs=0.2)

	def test_the_pose_seen_through_a_frame_is_the_reference_pose(self):
		bus, prof = arm(a_deg=10.0, b_deg=-30.0)
		frame = capture_frame(bus, prof, {"a": 0.0, "b": 60.0})
		pose = current_pose(bus, prof, frame=frame)
		assert pose["a"] == pytest.approx(0.0, abs=0.2)
		assert pose["b"] == pytest.approx(60.0, abs=0.2)

	def test_a_frame_survives_a_file_round_trip(self, tmp_path):
		frame = ModelFrame({"a": -10.0, "b": 90.0}, reference="studio-zero")
		frame.save(tmp_path / "f.json")
		assert ModelFrame.load(tmp_path / "f.json") == frame

	def test_a_joint_that_the_reference_pose_does_not_name_is_refused(self):
		bus, prof = arm()
		with pytest.raises(ValueError, match="b"):
			capture_frame(bus, prof, {"a": 0.0})


class TestFrameIsRequiredForPlanning:
	def test_measuring_a_chain_joint_without_a_frame_is_refused_before_anything_moves(self):
		from armkit.measure import measure_all

		bus, prof = arm(a_deg=-89.0)
		before = bus.read_positions()
		report = measure_all(bus, prof, clock=bus, confirm=lambda m: True)
		assert not report.ok
		assert any("frame" in i for i in report.issues)
		assert bus.read_positions() == before

	def test_moving_without_a_frame_is_refused(self):
		from armkit.park import plan_move, run_move

		bus, prof = arm(a_deg=0.0)
		plan = plan_move(prof, current_pose(bus, prof, frame=ModelFrame.identity(prof)), {"a": -89.0})
		before = bus.read_positions()
		result = run_move(bus, prof, plan, confirm=lambda m: True, clock=bus)
		assert not result.ok
		assert "frame" in result.reason
		assert bus.read_positions() == before

	def test_moves_go_where_the_frame_says(self):
		from armkit.park import plan_move, run_move

		bus, prof = arm(a_deg=0.0)
		frame = ModelFrame.trusted({"a": 20.0, "b": 0.0}, "test")  # model angle = midpoint angle + 20
		start = current_pose(bus, prof, frame=frame)
		assert start["a"] == pytest.approx(20.0, abs=0.2)
		plan = plan_move(prof, start, {"a": -60.0}, margin_m=0.0)
		assert run_move(bus, prof, plan, confirm=lambda m: True, clock=bus, frame=frame).ok
		# model -60 is midpoint -80, i.e. encoder 2200 - 80 * TPD
		assert bus.joint("a").encoder == pytest.approx(2200 - 80 * TPD, abs=15)


class TestDirections:
	def _arm_with_reversed_b(self):
		bus, prof = arm(a_deg=10.0, b_deg=-30.0)
		# reference pose A: model a = 0, b = 60 (b's readings run the other way to the model)
		first = capture_frame(bus, prof, {"a": 0.0, "b": 60.0})
		# the operator moves to pose B: model a = +40 (reading +40 too), b = 60 - 45 = 15 (reading goes UP by 45)
		bus.joint("a").encoder += 40 * TPD
		bus.joint("b").encoder += 45 * TPD
		return bus, prof, first

	def test_a_second_pose_finds_a_reversed_joint_and_keeps_the_others(self):
		bus, prof, first = self._arm_with_reversed_b()
		frame = refine_frame(first, bus, prof, {"a": 40.0, "b": 15.0})
		assert frame.signs["a"] == 1
		assert frame.signs["b"] == -1
		assert current_pose(bus, prof, frame=frame)["b"] == pytest.approx(15.0, abs=0.5)
		assert frame.verified_directions == {"a", "b"}

	def test_a_joint_that_did_not_move_between_the_poses_is_left_unverified(self):
		bus, prof, first = self._arm_with_reversed_b()
		frame = refine_frame(first, bus, prof, {"a": 40.0, "b": 60.0 - 45.0}, min_change_deg=20.0)
		assert frame.verified_directions == {"a", "b"}
		bus2, prof2 = arm(a_deg=0.0, b_deg=0.0)
		first2 = capture_frame(bus2, prof2, {"a": 0.0, "b": 0.0})
		bus2.joint("a").encoder += 40 * TPD
		frame2 = refine_frame(first2, bus2, prof2, {"a": 40.0, "b": 0.0})
		assert frame2.verified_directions == {"a"}
		assert not frame2.directions_known(["a", "b"])

	def test_a_pose_held_far_from_what_was_described_is_rejected(self):
		bus, prof, first = self._arm_with_reversed_b()
		with pytest.raises(ValueError, match="a"):
			refine_frame(first, bus, prof, {"a": 120.0, "b": 15.0})  # the arm moved 40, not 120

	def test_signs_survive_a_file_round_trip(self, tmp_path):
		frame = ModelFrame(
			{"a": 1.0, "b": 2.0}, "r", signs={"a": 1, "b": -1}, verified_directions=frozenset({"a", "b"})
		)
		frame.save(tmp_path / "f.json")
		assert ModelFrame.load(tmp_path / "f.json") == frame

	def test_planning_needs_every_chain_joint_direction_verified(self):
		from armkit.measure import measure_all

		bus, prof = arm(a_deg=-89.0)
		one_pose = ModelFrame({"a": 0.0, "b": 0.0}, "one pose only")  # offsets known, directions not checked
		report = measure_all(bus, prof, clock=bus, confirm=lambda m: True, frame=one_pose)
		assert not report.ok
		assert any("direction" in i for i in report.issues)


class TestDirectionsFromHandMoves:
	def _trace(self, moves):
		"""Readings (stored-midpoint degrees) over time while an operator moves joints one at a time."""
		pose = {"a": 0.0, "b": 0.0}
		trace = [dict(pose)]
		for joint, delta in moves:
			for k in range(1, 11):
				trace.append({**pose, joint: pose[joint] + delta * k / 10})
			pose[joint] += delta
			for k in range(1, 11):  # and back again
				trace.append({**pose, joint: pose[joint] - delta * k / 10})
			pose[joint] -= delta
		return trace

	def test_each_joints_direction_is_its_first_clear_excursion(self):
		from armkit.frame import directions_from_trace

		trace = self._trace([("a", 30.0), ("b", -35.0)])  # a moved with the model, b against it
		signs = directions_from_trace(trace, ["a", "b"], threshold_deg=15.0)
		assert signs == {"a": 1, "b": -1}

	def test_small_wobbles_do_not_count(self):
		from armkit.frame import directions_from_trace

		trace = self._trace([("a", 30.0)])
		for row in trace:
			row["b"] += 3.0  # the operator's hand nudged b a little
		assert directions_from_trace(trace, ["a", "b"], threshold_deg=15.0) == {"a": 1}

	def test_the_frame_takes_the_new_directions_and_keeps_the_reference_pose_where_it_was(self):
		from armkit.frame import with_directions

		first = ModelFrame({"a": -10.0, "b": 90.0}, "ref", first_pose_deg={"a": 0.0, "b": 60.0})
		frame = with_directions(first, {"a": 1, "b": -1})
		assert frame.verified_directions == {"a", "b"}
		# the reference pose still reads as the reference: stored b there was 60 - 90 = -30
		assert frame.to_model("b", -30.0) == pytest.approx(60.0)
		assert frame.to_model("b", -20.0) == pytest.approx(50.0)  # and b now runs the other way
