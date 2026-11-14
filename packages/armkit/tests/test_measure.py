from typing import ClassVar

import pytest
import test_procedure
from armkit.calibration import TICKS_PER_DEGREE as TPD
from armkit.frame import ModelFrame
from armkit.measure import measure_all
from armkit.simulation import SimJoint, SimulatedBus
from test_procedure import profile


class Logged(SimulatedBus):
	"""Records each joint's true model angle (zero at the middle of its stops) after every simulated step."""

	ZERO: ClassVar[dict[str, float]] = {"a": 2200.0, "b": 2000.0}

	def __init__(self, *a, **kw):
		super().__init__(*a, **kw)
		self.angles = []

	def sleep(self, seconds):
		super().sleep(seconds)
		self.angles.append({n: (self.joint(n).encoder - self.ZERO[n]) / TPD for n in self.joints})


def arm(a_deg=-89.0, b_deg=0.0, b_gravity=0, stored=((950, 3450), (950, 3050))):
	"""Toy arm. True stops a 1000..3400, b 1000..3000; the stored ranges are a little wider than that by default."""
	a = SimJoint(id=1, encoder=2200.0 + a_deg * TPD, stop_low=1000.0, stop_high=3400.0)
	b = SimJoint(id=2, encoder=2000.0 + b_deg * TPD, stop_low=1000.0, stop_high=3000.0, gravity=b_gravity)
	(a.limit_min, a.limit_max), (b.limit_min, b.limit_max) = stored
	bus = Logged({"a": a, "b": b})
	bus.hold()
	return bus


TOY_FRAME = ModelFrame.trusted({"a": 0.0, "b": 0.0}, "toy: stored range midpoints are model zeros by construction")


def run(bus, prof=None, **kw):
	kw.setdefault("confirm", lambda m: True)
	kw.setdefault("frame", TOY_FRAME)
	return measure_all(bus, prof or profile(test_procedure.TestCollisionAwareness.SHAPES), clock=bus, **kw)


class TestPipeline:
	def test_every_end_of_every_joint_is_measured_from_the_bottom_up(self):
		bus = arm()
		report = run(bus)
		assert report.ok, report.issues
		assert list(report.joints) == ["a", "b"]  # the base joint first
		assert report.joints["a"].lower == pytest.approx(1000, abs=8)
		assert report.joints["a"].upper == pytest.approx(3400, abs=8)
		assert report.joints["b"].lower == pytest.approx(1000, abs=8)
		assert report.joints["b"].upper == pytest.approx(3000, abs=8)

	def test_the_proposed_calibration_keeps_the_offsets_and_uses_the_measured_ranges(self):
		bus = arm()
		stored = bus.read_calibration()
		report = run(bus, end_margin_ticks=20)
		for name, (lo, hi) in {"a": (1000, 3400), "b": (1000, 3000)}.items():
			proposed = report.proposed[name]
			assert proposed.homing_offset == stored[name].homing_offset
			assert proposed.range_min == pytest.approx(lo + 20, abs=8)
			assert proposed.range_max == pytest.approx(hi - 20, abs=8)

	def test_nothing_is_stored_and_the_arm_ends_where_it_started(self):
		bus = arm()
		stored = bus.read_calibration()
		start = bus.read_positions()
		run(bus)
		assert bus.read_calibration() == stored
		for name in start:
			assert bus.read_positions()[name] == pytest.approx(start[name], abs=15)

	def test_the_true_pose_never_collides_at_any_moment(self):
		bus = arm(a_deg=0.0)  # starts where joint b's upward sweep would hit the ball: the arm has to be parked first
		prof = profile(test_procedure.TestCollisionAwareness.SHAPES)
		report = run(bus, prof)
		assert report.ok, report.issues
		assert min(prof.collision.clearance(a).distance_m for a in bus.angles) > 0.0

	def test_a_single_confirmation_covers_the_whole_run_and_no_means_nothing_moves(self):
		bus = arm()
		asked = []
		before = bus.read_positions()
		report = run(bus, confirm=lambda m: asked.append(m) or False)
		assert len(asked) == 1
		assert not report.ok
		assert bus.read_positions() == before

	def test_a_subset_of_joints_can_be_measured(self):
		report = run(arm(), joints=["b"])
		assert list(report.joints) == ["b"]

	def test_a_weight_bearing_joint_reports_ends_beyond_its_stored_range_instead_of_guessing(self):
		bus = arm(b_gravity=150, stored=((950, 3450), (1040, 2960)))
		report = run(bus)
		b = report.joints["b"]
		assert b.lower is None
		assert b.upper is None
		assert report.proposed["b"] == bus.read_calibration()["b"]  # kept as stored, not invented
		assert any("b" in n and "stored limit" in n for n in report.issues)


class TestStoredCalibrationIsReadOnce:
	def test_each_check_uses_the_calibration_read_at_the_start_not_a_fresh_read(self):
		bus = arm()
		reads = {"n": 0}
		original = bus.read_calibration

		def read():
			reads["n"] += 1
			return original()

		bus.read_calibration = read
		report = run(bus)
		assert report.ok, report.issues
		# one read at the start and one at the end to verify nothing changed; the checks get the verified copy
		assert reads["n"] == 2

	def test_a_change_to_the_stored_calibration_during_the_run_is_reported(self):
		from armkit.calibration import Calibration, JointCalibration

		bus = arm()
		original = bus.read_calibration
		calls = {"n": 0}

		def read():
			calls["n"] += 1
			cal = original()
			if calls["n"] == 2:  # the verification read at the end finds joint a's offset changed
				a = cal["a"]
				return Calibration(
					{**dict(cal.items()), "a": JointCalibration(a.id, a.drive_mode, 55, a.range_min, a.range_max)}
				)
			return cal

		bus.read_calibration = read
		report = run(bus)
		assert not report.ok
		assert any("changed during the run" in i for i in report.issues)


class TestPreview:
	def test_a_preview_runs_the_pipeline_on_a_simulated_copy_and_never_touches_the_real_bus(self):
		from armkit.measure import preview_measure

		real = arm(a_deg=-89.0)
		before = (real.read_positions(), real.read_calibration())
		writes = []
		real.write_goals = lambda goals: writes.append(goals)
		preview = preview_measure(real, profile(test_procedure.TestCollisionAwareness.SHAPES), frame=TOY_FRAME)
		assert writes == []
		assert (real.read_positions(), real.read_calibration()) == before
		assert preview.report.ok, preview.report.issues
		assert any("searching" in line for line in preview.log)

	def test_the_preview_reports_the_closest_approach_of_the_whole_run(self):
		from armkit.measure import preview_measure

		prof = profile(test_procedure.TestCollisionAwareness.SHAPES)
		preview = preview_measure(arm(a_deg=-89.0), prof, frame=TOY_FRAME)
		assert preview.closest is not None
		assert preview.closest.distance_m > 0.0

	def test_a_preview_without_a_usable_frame_says_why_like_the_real_run(self):
		from armkit.measure import preview_measure

		preview = preview_measure(arm(), profile(test_procedure.TestCollisionAwareness.SHAPES), frame=None)
		assert not preview.report.ok
		assert any("frame" in i for i in preview.report.issues)


class TestOneEndMeasured:
	def test_a_measured_end_is_used_even_when_the_other_end_could_not_be(self):
		from armkit.calibration import JointCalibration
		from armkit.measure import JointMeasurement, propose

		stored = JointCalibration(2, 0, -1370, 839, 3191)
		proposed = propose(
			{"shoulder_lift": JointMeasurement(stored, lower=838.0, upper=None)},
			{"shoulder_lift": stored},
			margin_ticks=20,
		)
		assert proposed["shoulder_lift"] == JointCalibration(2, 0, -1370, 858, 3191)

	def test_a_joint_with_nothing_measured_keeps_its_stored_values(self):
		from armkit.calibration import JointCalibration
		from armkit.measure import propose

		stored = JointCalibration(5, 0, 923, 0, 4095)
		assert propose({}, {"wrist_roll": stored}, margin_ticks=20)["wrist_roll"] == stored


class TestNotesAndIssues:
	def test_ends_left_at_the_stored_limit_are_unmeasured_and_fail_the_run(self):
		bus = arm(b_gravity=150, stored=((950, 3450), (1040, 2960)))  # b's stops lie outside its stored range
		report = run(bus)
		assert not report.ok  # a stored limit is never accepted in place of a measurement
		assert any("b" in n and "NOT MEASURED" in n for n in report.issues)
