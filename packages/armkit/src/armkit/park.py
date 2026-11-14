"""Plan and run a collision-checked move of several joints to a target pose, in the frame of the stored calibration.

Joint angles are read from the calibration the servos already hold (a reading relative to the middle of each joint's
recorded range, which is where the model puts zero), so no new calibration is needed. :func:`plan_move` asks the
collision model for a path that never comes closer to a collision than the start pose or the margin allows, moving
joints one at a time when the direct path would pass too close. :func:`run_move` plays that path with the guarded path
runner (:func:`~armkit.motion.run_path`: bounded push, step back on contact) at a limited torque and puts the torque
limits back afterwards. The model only knows the arm and the floor: anything else near it (a clamp, a camera mount)
is not checked.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping

from armkit.calibration import Calibration
from armkit.frame import ModelFrame
from armkit.guard import GuardLimits
from armkit.motion import MoveLimits, MoveResult, linear_path, run_path
from armkit.poses import TransitionPlan, plan_transition
from armkit.profile import ArmProfile
from armkit.servo import Clock, RealClock, ServoBus


def current_pose(
	bus: ServoBus, profile: ArmProfile, calibration: Calibration | None = None, frame: ModelFrame | None = None
) -> dict[str, float]:
	"""Model angles (degrees) of the profile's kinematic-chain joints, from the stored calibration and the readings."""
	calibration = calibration or bus.read_calibration()
	positions = bus.read_positions()
	frame = frame or ModelFrame.identity(profile)
	return {
		n: frame.to_model(n, calibration[n].to_degrees(positions[n])) for n in profile.robot.names if n in calibration
	}


def plan_move(
	profile: ArmProfile,
	start: Mapping[str, float],
	targets: Mapping[str, float],
	*,
	step_deg: float = 0.5,
	margin_m: float = 0.005,
) -> TransitionPlan:
	"""Collision-checked path from ``start`` to ``start`` with the ``targets`` joints set (others stay)."""
	return plan_transition(profile.collision, start, {**start, **targets}, step_deg=step_deg, margin_m=margin_m)


def run_move(
	bus: ServoBus,
	profile: ArmProfile,
	plan: TransitionPlan,
	*,
	confirm: Callable[[str], bool],
	progress: Callable[[str], None] = lambda message: None,
	clock: Clock | None = None,
	move: MoveLimits | None = None,
	guard: GuardLimits | None = None,
	torque_limit_permille: int = 600,
	calibration: Calibration | None = None,
	frame: ModelFrame | None = None,
) -> MoveResult:
	"""Run a planned move. Nothing is touched unless the plan is ok, every waypoint lies inside the stored ranges and
	``confirm`` agrees; joints that move get ``torque_limit_permille`` for the move and their old limit afterwards."""
	if not plan.ok:
		return MoveResult(False, f"the plan is not ok ({plan.reason}); nothing was moved")
	if frame is None or not frame.verified:
		return MoveResult(False, "no measured model frame: the plan may not describe the real arm; nothing was moved")
	if not frame.directions_known(profile.robot.names):
		return MoveResult(False, "the model frame has not checked every joint's direction; nothing was moved")
	clock = clock or RealClock()
	move, guard = move or MoveLimits(), guard or GuardLimits()
	calibration = calibration or bus.read_calibration()
	start = bus.read_positions()
	moving = [
		j
		for j in plan.path[-1]
		if j in calibration and abs(calibration[j].to_ticks(frame.to_stored(j, plan.path[-1][j])) - start[j]) > 3
	]
	path = [{j: calibration[j].to_ticks(frame.to_stored(j, wp[j])) for j in moving} for wp in plan.path]
	for j in moving:
		lo, hi = calibration[j].range_min, calibration[j].range_max
		if any(not lo <= wp[j] <= hi for wp in path):
			return MoveResult(False, f"{j}: the move leaves the stored range {lo}..{hi}; nothing was moved")
	if not moving:
		return MoveResult(True)
	if not confirm(
		f"{', '.join(moving)} will move by themselves, slowly, at {torque_limit_permille} permille torque, "
		"along a path checked against the arm's collision model (it does not know about a clamp, camera mounts or people). "
		"Keep clear and be ready to cut power."
	):
		return MoveResult(False, "not confirmed: nothing was moved")
	old_limits = {j: bus.torque_limit(j) for j in moving}
	try:
		bus.set_torque_limit(torque_limit_permille, moving)
		first = linear_path({j: start[j] for j in moving}, path[0], step_ticks=move.step_ticks)
		progress(f"moving {', '.join(moving)}: {len(first) + len(path)} steps")
		return run_path(
			bus,
			first + path[1:],
			start={j: start[j] for j in moving},
			limits=move,
			guard=guard,
			clock=clock,
			loaded_joints=profile.robot.names,
		)
	finally:
		for j, limit in old_limits.items():
			bus.set_torque_limit(limit, [j])
