import numpy as np
import pytest

from defect_sorter.closed_loop import DEFAULT_TASKS, ArmFaultError, run_episode
from defect_sorter.inspection import ThresholdInspector
from defect_sorter.kinematics import forward
from defect_sorter.twin import (
	HOME_DEG,
	JOINT_LIMITS_DEG,
	STATE_NAMES,
	CellLayout,
	ScriptedExpert,
	TopCamera,
	TwinCell,
	solve_ik,
	tcp_pose,
)

DOWN = np.array([0.0, 0.0, -1.0])


def test_tcp_is_the_urdf_gripper_frame_offset_from_gripper_link():
	# URDF gripper_frame_joint: xyz (-0.0079, -0.000218, -0.0981) in gripper_link.
	angles = {"shoulder_lift": 20.0, "elbow_flex": -30.0}
	gripper = forward(angles)
	expected = gripper[:3, :3] @ np.array([-0.0079, -0.000218121, -0.0981274]) + gripper[:3, 3]
	position, approach = tcp_pose(angles)
	np.testing.assert_allclose(position, expected, atol=1e-9)
	np.testing.assert_allclose(approach, -gripper[:3, 2], atol=1e-9)


@pytest.mark.parametrize("target", [(0.20, 0.0, 0.02), (0.22, 0.08, 0.06), (0.16, -0.15, 0.07), (0.16, 0.15, 0.07)])
def test_ik_reaches_target_with_jaws_pointing_down(target):
	angles = solve_ik(np.array(target))
	assert angles is not None
	position, approach = tcp_pose(angles)
	np.testing.assert_allclose(position, target, atol=1e-3)
	assert np.degrees(np.arccos(np.clip(approach @ DOWN, -1, 1))) < 5.0
	for name, value in angles.items():
		lo, hi = JOINT_LIMITS_DEG[name]
		assert lo <= value <= hi


def test_ik_returns_none_out_of_reach():
	assert solve_ik(np.array([0.8, 0.0, 0.05])) is None


def test_joint_motion_is_rate_limited_and_clamped_to_limits():
	cell = TwinCell(seed=0, dt=0.1, joint_speed_deg_s=60.0)
	start = cell.state.copy()
	target = start.copy()
	target[0] = start[0] + 90.0
	cell.apply(target)
	assert cell.state[0] == pytest.approx(start[0] + 6.0)
	far = start.copy()
	far[0] = 500.0
	for _ in range(100):
		cell.apply(far)
	assert cell.state[0] == pytest.approx(JOINT_LIMITS_DEG["shoulder_pan"][1])


def _drive_to(cell: TwinCell, xyz, gripper: float, steps: int = 200) -> None:
	angles = solve_ik(np.array(xyz))
	assert angles is not None
	action = np.array([angles[n.removesuffix(".pos")] for n in STATE_NAMES[:5]] + [gripper])
	for _ in range(steps):
		cell.apply(action)


def test_grasp_carry_and_release_puts_brick_in_bowl():
	cell = TwinCell(seed=1)
	bx, by = cell.brick.xy
	_drive_to(cell, (bx, by, 0.08), 100.0)
	_drive_to(cell, (bx, by, cell.grasp_height()), 100.0)
	_drive_to(cell, (bx, by, cell.grasp_height()), 0.0, steps=30)
	assert cell.brick.held
	gx, gy = cell.layout.bowls["green"][0]
	_drive_to(cell, (bx, by, 0.10), 0.0)
	_drive_to(cell, (gx, gy, 0.10), 0.0)
	_drive_to(cell, (gx, gy, 0.10), 100.0, steps=30)
	assert not cell.brick.held
	outcome = cell.outcome()
	assert (outcome.bowl, outcome.settled) == ("green", True)


def test_closing_away_from_brick_grasps_nothing():
	cell = TwinCell(seed=2)
	bx, by = cell.brick.xy
	_drive_to(cell, (bx + 0.05, by, cell.grasp_height()), 100.0)
	_drive_to(cell, (bx + 0.05, by, cell.grasp_height()), 0.0, steps=30)
	assert not cell.brick.held
	assert cell.outcome().bowl is None


def test_driving_through_the_table_raises_arm_fault():
	cell = TwinCell(seed=3)
	bx, by = cell.brick.xy
	with pytest.raises(ArmFaultError):
		_drive_to(cell, (bx, by, -0.03), 100.0)


def test_top_camera_projects_table_points_to_known_pixels():
	camera = TopCamera(x_range=(0.0, 0.40), y_range=(-0.15, 0.15), px_per_m=1000.0)
	assert camera.shape == (300, 400)
	assert camera.to_pixel(0.0, 0.15) == (0, 0)
	assert camera.to_pixel(0.10, 0.05) == (100, 100)
	assert camera.to_pixel(0.40, -0.15) == (400, 300)


def test_defective_brick_crop_contains_dark_marker_strokes():
	normal = TwinCell(seed=4, defective=False).observe().target_crop
	defective = TwinCell(seed=4, defective=True).observe().target_crop
	assert normal is not None
	assert defective is not None
	assert normal.shape == defective.shape

	def dark(crop):
		return int((crop.max(axis=2) < 70).sum())

	assert dark(normal) == 0
	assert dark(defective) > 50


def test_observation_has_both_cameras_and_six_dof_state():
	obs = TwinCell(seed=5).observe()
	assert set(obs.images) == {"top", "wrist"}
	assert all(image.dtype == np.uint8 and image.ndim == 3 for image in obs.images.values())
	assert obs.state.shape == (6,)
	np.testing.assert_allclose(obs.state[:5], [HOME_DEG[n.removesuffix(".pos")] for n in STATE_NAMES[:5]])


def test_layout_rejects_overlapping_bowls():
	with pytest.raises(ValueError, match="overlap"):
		CellLayout(bowls={"green": ((0.2, 0.0), 0.06), "pink": ((0.2, 0.05), 0.06)})


@pytest.mark.parametrize("seed", range(4))
def test_scripted_expert_sorts_by_task_in_the_closed_loop(seed):
	cell = TwinCell(seed=seed, defective=seed % 2 == 1)
	truth = cell.ground_truth()
	inspector = ThresholdInspector(lambda crop: 0.9 if truth == "defective" else 0.1, threshold=0.5, model="truth")
	record = run_episode(cell, inspector, ScriptedExpert(cell), DEFAULT_TASKS, max_steps=900)
	assert record.status == "DONE", record.reason
	assert record.outcome_bowl == DEFAULT_TASKS[truth][0]
	assert record.mode == "twin"
