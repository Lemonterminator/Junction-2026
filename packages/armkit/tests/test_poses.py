import numpy as np
import pytest
from armkit.collision import CollisionModel, LinkShape
from armkit.model import Joint, RobotModel
from armkit.poses import find_clearance_pose, plan_sweep, plan_transition, sweep_clearance


def toy() -> CollisionModel:
	"""Planar two-joint arm, links 0.3 m. A fixed ball B at (0.3, 0.3) r 0.1 on the base; a ball F at the end of
	the forearm (0.3 m beyond joint b) r 0.05. F circles joint b at 0.3 m, so it hits B whenever joint b's position
	puts B within reach of that circle."""
	robot = RobotModel(
		joints=(
			Joint("a", (0, 0, 0), (0, 0, 0), lower_deg=-180, upper_deg=180),
			Joint("b", (0.3, 0, 0), (0, 0, 0), lower_deg=-180, upper_deg=180),
		),
		link_names=("base", "upper", "fore"),
	)
	shapes = {
		"base": LinkShape(np.array([[0.3, 0.3, 0.0]]), np.array([0.1])),
		"fore": LinkShape(np.array([[0.3, 0.0, 0.0]]), np.array([0.05])),
	}
	return CollisionModel(robot, shapes, floor_z=None)


class TestSweep:
	def test_the_clear_stretch_around_the_start_stops_where_the_forearm_meets_the_ball(self):
		# with a = 0 joint b sits at (0.3, 0): F touches B when the forearm points within ~29 degrees of +y
		check = sweep_clearance(toy(), "b", others={"a": 0.0}, start_deg=0.0, span_deg=(-180.0, 180.0), step_deg=3.0)
		assert not check.clear
		assert check.reach_deg[0] == -180.0
		assert 50.0 <= check.reach_deg[1] <= 62.0

	def test_a_sweep_that_never_touches_anything_is_clear_end_to_end(self):
		check = sweep_clearance(toy(), "b", others={"a": -89.0}, start_deg=0.0, span_deg=(-180.0, 180.0), step_deg=3.0)
		assert check.clear
		assert check.reach_deg == (-180.0, 180.0)

	def test_pose_uncertainty_in_the_other_joints_can_make_a_marginal_sweep_unsafe(self):
		# a = -35 clears B by 25 mm, but a = -15 (35 degrees of slack either way is plenty) hits it
		kw = {"others": {"a": -35.0}, "start_deg": 0.0, "span_deg": (-180.0, 180.0), "step_deg": 3.0}
		assert sweep_clearance(toy(), "b", **kw).clear
		assert not sweep_clearance(toy(), "b", **kw, uncertainty_deg=20.0).clear

	def test_uncertainty_can_be_given_per_joint(self):
		kw = {"others": {"a": -35.0}, "start_deg": 0.0, "span_deg": (-180.0, 180.0), "step_deg": 3.0}
		assert not sweep_clearance(toy(), "b", **kw, uncertainty_deg={"a": 20.0}).clear
		assert sweep_clearance(toy(), "b", **kw, uncertainty_deg={"unrelated": 20.0}).clear

	def test_a_start_that_is_already_in_contact_has_no_clear_stretch(self):
		check = sweep_clearance(toy(), "b", others={"a": 0.0}, start_deg=90.0, span_deg=(-180.0, 180.0), step_deg=3.0)
		assert not check.clear
		assert check.reach_deg == (90.0, 90.0)


class TestClearancePose:
	def test_picks_the_nearest_grid_pose_whose_full_sweep_is_clear(self):
		pose = find_clearance_pose(
			toy(), "b", current={"a": 0.0, "b": 0.0}, span_deg=(-180.0, 180.0), grid_points=5, step_deg=3.0
		)
		assert pose is not None
		# the grid is -178, -89, 0, 89, 178: a = 0 and +89 collide, -89 does not and is nearer than +178
		assert pose.angles_deg == {"a": pytest.approx(-89.0)}
		model = toy()
		assert all(model.is_clear({**pose.angles_deg, "b": b}) for b in np.arange(-180, 181, 3.0))

	def test_a_pose_that_is_already_clear_is_kept_exactly_rather_than_snapped_to_the_grid(self):
		pose = find_clearance_pose(toy(), "b", current={"a": -100.0, "b": 0.0}, span_deg=(-180.0, 180.0), step_deg=3.0)
		assert pose.angles_deg == {"a": -100.0}

	def test_a_preferred_pose_is_used_when_it_is_safe(self):
		pose = find_clearance_pose(
			toy(), "b", current={"a": 0.0, "b": 0.0}, span_deg=(-180.0, 180.0), preferred=[{"a": 162.0}], step_deg=3.0
		)
		assert pose.angles_deg == {"a": 162.0}

	def test_joints_outside_the_vary_list_stay_where_they_are(self):
		model = toy()
		assert (
			find_clearance_pose(
				model, "b", current={"a": 0.0, "b": 0.0}, span_deg=(-180.0, 180.0), vary=(), step_deg=3.0
			)
			is None
		)
		held = find_clearance_pose(
			model, "b", current={"a": -89.0, "b": 0.0}, span_deg=(-180.0, 180.0), vary=(), step_deg=3.0
		)
		assert held.angles_deg == {"a": -89.0}

	def test_no_pose_means_none(self):
		# the ball is so large that no position of joint a leaves the circle clear
		robot = toy().robot
		fat = CollisionModel(
			robot,
			{
				"base": LinkShape(np.array([[0.3, 0.0, 0.0]]), np.array([0.8])),
				"fore": LinkShape(np.array([[0.3, 0, 0]]), np.array([0.05])),
			},
			floor_z=None,
		)
		assert (
			find_clearance_pose(fat, "b", current={"a": 0.0, "b": 0.0}, span_deg=(-180.0, 180.0), step_deg=6.0) is None
		)


class TestTransition:
	def test_moving_one_joint_at_a_time_in_a_working_order_when_the_direct_path_is_too_close(self):
		model = toy()
		start, goal = {"a": 0.0, "b": 0.0}, {"a": 90.0, "b": 90.0}
		plan = plan_transition(model, start, goal, step_deg=3.0, margin_m=0.015)
		assert plan.ok
		assert plan.order == ("a", "b")
		assert plan.path[-1] == goal
		assert all(model.is_clear(wp, margin=0.0139) for wp in plan.path)
		steps = [max(abs(b[j] - a[j]) for j in b) for a, b in zip([start, *plan.path], plan.path, strict=False)]
		assert max(steps) <= 3.0 + 1e-9

	def test_the_direct_path_is_used_when_it_is_clear(self):
		plan = plan_transition(toy(), {"a": 0.0, "b": 0.0}, {"a": 90.0, "b": 90.0}, step_deg=3.0, margin_m=0.0)
		assert plan.ok
		assert plan.order == ()

	def test_a_goal_inside_a_collision_is_refused(self):
		plan = plan_transition(toy(), {"a": 0.0, "b": 0.0}, {"a": 0.0, "b": 90.0}, step_deg=3.0, margin_m=0.0)
		assert not plan.ok
		assert "goal" in plan.reason

	def test_no_collision_free_order_is_reported(self):
		# joint b has to pass the forearm-on-ball zone around b = 90 to get from -150 to 150, and a is unchanged
		plan = plan_transition(toy(), {"a": 0.0, "b": -150.0}, {"a": 0.0, "b": 150.0}, step_deg=3.0, margin_m=0.0)
		assert not plan.ok
		assert "no collision-free route" in plan.reason


class RuleCollision:
	"""Stand-in collision model with an explicit rule on (a, b): the base needs a > 20 while b < -10 and a < -20 while
	b > 10; between -10 and 10 anything goes. No single value of a is clear over a whole -180..180 sweep of b."""

	robot = toy().robot

	def __init__(self, blocked_beyond: float | None = None):
		self.blocked_beyond = blocked_beyond

	def is_clear(self, angles, margin=0.0):
		a, b = angles["a"], angles["b"]
		if self.blocked_beyond is not None and b > self.blocked_beyond:
			return False
		return (b >= -10 or a > 20) and (b <= 10 or a < -20)


class TestSweepStages:
	def test_one_stage_when_a_single_parking_pose_covers_the_whole_sweep(self):
		stages = plan_sweep(toy(), "b", current={"a": 0.0, "b": 0.0}, toward_deg=180.0, step_deg=3.0)
		assert len(stages) == 1
		assert stages[0].span_deg == (0.0, 180.0)
		model = toy()
		assert all(model.is_clear({**stages[0].pose.angles_deg, "b": b}) for b in np.arange(0.0, 181.0, 3.0))

	def test_a_sweep_no_single_pose_can_cover_is_split_where_the_poses_change(self):
		stages = plan_sweep(
			RuleCollision(), "b", current={"a": 0.0, "b": -180.0}, toward_deg=180.0, step_deg=3.0, resolution_deg=2.0
		)
		assert len(stages) == 2
		first, second = stages
		assert first.span_deg[0] == -180.0
		assert second.span_deg[1] == 180.0
		assert first.span_deg[1] == second.span_deg[0]  # the second stage starts where the first ended
		assert -10.0 <= first.span_deg[1] <= 10.0  # the change happens in the free zone
		assert first.pose.angles_deg["a"] > 20
		assert second.pose.angles_deg["a"] < -20

	def test_sweeping_downwards_works_the_same_way(self):
		stages = plan_sweep(
			RuleCollision(), "b", current={"a": 0.0, "b": 180.0}, toward_deg=-180.0, step_deg=3.0, resolution_deg=2.0
		)
		assert [round(s.span_deg[0]) > round(s.span_deg[1]) for s in stages] == [True, True]
		assert stages[0].pose.angles_deg["a"] < -20
		assert stages[1].pose.angles_deg["a"] > 20

	def test_a_region_nothing_can_clear_means_no_plan(self):
		assert (
			plan_sweep(
				RuleCollision(blocked_beyond=60.0), "b", current={"a": 0.0, "b": 0.0}, toward_deg=180.0, step_deg=3.0
			)
			is None
		)

	def test_too_many_stages_means_no_plan(self):
		assert (
			plan_sweep(
				RuleCollision(),
				"b",
				current={"a": 0.0, "b": -180.0},
				toward_deg=180.0,
				step_deg=3.0,
				resolution_deg=2.0,
				max_stages=1,
			)
			is None
		)


class LimitedRule:
	"""Stand-in with joint a limited to +-30 degrees and a rule that only a <= -28 is clear."""

	robot = RobotModel(
		joints=(
			Joint("a", (0, 0, 0), (0, 0, 0), lower_deg=-30, upper_deg=30),
			Joint("b", (0.3, 0, 0), (0, 0, 0), lower_deg=-90, upper_deg=90),
		),
		link_names=("base", "upper", "fore"),
	)

	def __init__(self, limit: float):
		self.limit = limit

	def is_clear(self, angles, margin=0.0):
		return angles["a"] <= self.limit


class TestJointLimits:
	def test_the_parking_grid_reaches_almost_to_the_limits(self):
		pose = find_clearance_pose(
			LimitedRule(-28.0), "b", current={"a": 0.0, "b": 0.0}, span_deg=(-10.0, 10.0), grid_points=3
		)
		assert pose.angles_deg == {"a": pytest.approx(-28.0)}

	def test_an_uncertain_joint_cannot_be_imagined_beyond_its_limit(self):
		# a is parked at its +30 limit; +-20 degrees of doubt would reach 50, which the joint cannot do
		kw = {
			"others": {"a": 30.0},
			"start_deg": 0.0,
			"span_deg": (-10.0, 10.0),
			"step_deg": 5.0,
			"uncertainty_deg": 20.0,
		}
		assert sweep_clearance(LimitedRule(30.0), "b", **kw).clear
		assert not sweep_clearance(LimitedRule(29.0), "b", **kw).clear
