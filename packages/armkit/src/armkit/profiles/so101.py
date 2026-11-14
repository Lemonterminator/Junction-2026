"""SO-101 follower arm (Feetech STS3215, six servos, ids 1-6) as an :class:`~armkit.profile.ArmProfile`.

Kinematics, joint limits and collision shapes come from the SO-101 follower URDF ``so101_new_calib`` (SO-ARM100 project,
Onshape export) that Physical AI Studio's SO-101 plugin ships for its 3D view. Joint zero is the middle of each range,
as in the LeRobot "new" calibration.

* ``SPHERES`` are bounding spheres (centre x, y, z and radius, metres, link frame) fitted to the URDF's collision
  meshes, 14 per link, with the moving jaw folded into the gripper link at its closed position. They were produced with
  :func:`armkit.collision.collision_from_urdf` and baked here so no mesh files are needed at runtime. They bound the
  meshes from outside, so they over-estimate the arm; near the rest pose and over the floor they are tight.
* ``IGNORED_PAIRS`` are link pairs whose spheres overlap at the rest or the all-zero pose (parts built to sit next to
  each other); they are not checked.
* ``REST_DEG`` is the folded pose Studio's setup wizard shows for a freshly powered, uncalibrated arm
  (its ``HOME_POSITION_STATE``). The calibration procedure starts from this pose; the operator confirms the real arm is
  resting there. Wrist roll and gripper are not constrained by the fold, so their rest angles matter little.
* The wrist roll is treated as a full-turn joint (range 0..4095, no search), as LeRobot does.
"""

from __future__ import annotations

import numpy as np

from armkit.collision import CollisionModel, LinkShape
from armkit.model import Joint, RobotModel
from armkit.profile import ArmProfile, JointSetup

JOINTS: tuple[Joint, ...] = (
	Joint(
		"shoulder_pan",
		(0.0388353, -8.97657e-09, 0.0624),
		(3.14159, 4.18253e-17, -3.14159),
		lower_deg=-110.0,
		upper_deg=110.0,
	),
	Joint(
		"shoulder_lift", (-0.0303992, -0.0182778, -0.0542), (-1.5708, -1.5708, 0.0), lower_deg=-100.0, upper_deg=100.0
	),
	Joint(
		"elbow_flex",
		(-0.11257, -0.028, 1.73763e-16),
		(-3.63608e-16, 8.74301e-16, 1.5708),
		lower_deg=-96.83,
		upper_deg=96.83,
	),
	Joint(
		"wrist_flex",
		(-0.1349, 0.0052, 3.62355e-17),
		(4.02456e-15, 8.67362e-16, -1.5708),
		lower_deg=-95.0,
		upper_deg=95.0,
	),
	Joint(
		"wrist_roll", (5.55112e-17, -0.0611, 0.0181), (1.5708, 0.0486795, 3.14159), lower_deg=-157.21, upper_deg=162.79
	),
)
LINKS: tuple[str, ...] = (
	"base_link",
	"shoulder_link",
	"upper_arm_link",
	"lower_arm_link",
	"wrist_link",
	"gripper_link",
)
TOOL_XYZ = (-0.0079, -0.000218121, -0.0981274)
TOOL_RPY = (0.0, 3.14159, 0.0)
"""The tool point is ``gripper_frame_link``: between the jaw tips, z axis out of the jaws."""

GRIPPER_TRAVEL_DEG = (-10.0, 100.0)
REST_DEG = {
	"shoulder_pan": 0.0,
	"shoulder_lift": -90.0,
	"elbow_flex": 90.0,
	"wrist_flex": 60.0,
	"wrist_roll": 50.0,
	"gripper": 85.0,
}
IGNORED_PAIRS = (
	("base_link", "upper_arm_link"),
	("gripper_link", "shoulder_link"),
	("lower_arm_link", "shoulder_link"),
	("shoulder_link", "wrist_link"),
	("upper_arm_link", "wrist_link"),
)
FLOOR_Z = -0.002
"""Underside of the base plate in the base frame."""

SPHERES: dict[str, tuple[tuple[float, float, float, float], ...]] = {
	"base_link": (
		(-0.0240, 0.0196, 0.0504, 0.0275),
		(0.0569, -0.0274, 0.0078, 0.0290),
		(0.0401, -0.0000, 0.0604, 0.0230),
		(0.0250, 0.0416, 0.0082, 0.0305),
		(-0.0128, -0.0339, 0.0093, 0.0305),
		(-0.0247, -0.0191, 0.0662, 0.0265),
		(0.0173, 0.0013, 0.0267, 0.0315),
		(0.0225, -0.0421, 0.0095, 0.0305),
		(0.0087, 0.0187, 0.0534, 0.0275),
		(-0.0125, 0.0335, 0.0093, 0.0305),
		(0.0520, 0.0186, 0.0217, 0.0305),
		(0.0055, -0.0160, 0.0587, 0.0235),
		(-0.0208, -0.0164, 0.0349, 0.0265),
		(0.0405, -0.0050, 0.0285, 0.0230),
	),
	"shoulder_link": (
		(-0.0434, 0.0187, -0.0155, 0.0230),
		(0.0051, 0.0003, 0.0430, 0.0150),
		(-0.0304, -0.0177, -0.0530, 0.0155),
		(-0.0441, -0.0165, 0.0331, 0.0230),
		(0.0020, -0.0001, -0.0058, 0.0240),
		(-0.0435, -0.0185, -0.0236, 0.0255),
		(-0.0189, 0.0235, -0.0308, 0.0170),
		(-0.0441, 0.0164, 0.0331, 0.0265),
		(-0.0282, 0.0167, -0.0510, 0.0185),
		(-0.0221, -0.0178, -0.0106, 0.0265),
		(-0.0092, -0.0010, 0.0413, 0.0200),
		(-0.0206, -0.0172, -0.0264, 0.0215),
		(-0.0414, 0.0185, -0.0398, 0.0220),
		(-0.0182, 0.0188, -0.0194, 0.0230),
	),
	"upper_arm_link": (
		(-0.1246, 0.0030, 0.0011, 0.0205),
		(0.0022, 0.0003, 0.0433, 0.0165),
		(-0.0631, -0.0028, -0.0099, 0.0190),
		(-0.0630, -0.0028, 0.0464, 0.0190),
		(0.0048, 0.0003, -0.0086, 0.0145),
		(-0.1081, -0.0239, 0.0351, 0.0220),
		(-0.1159, 0.0067, 0.0366, 0.0270),
		(-0.1016, 0.0038, 0.0028, 0.0220),
		(-0.0212, -0.0011, 0.0511, 0.0195),
		(-0.0784, 0.0001, 0.0184, 0.0265),
		(-0.1126, -0.0268, 0.0006, 0.0165),
		(-0.0067, 0.0004, -0.0026, 0.0225),
		(-0.0497, -0.0000, 0.0182, 0.0175),
		(-0.1182, -0.0166, 0.0352, 0.0200),
	),
	"lower_arm_link": (
		(-0.1307, 0.0023, 0.0351, 0.0195),
		(0.0021, -0.0003, -0.0062, 0.0160),
		(-0.0610, -0.0101, 0.0182, 0.0200),
		(-0.0109, 0.0002, 0.0469, 0.0255),
		(-0.1044, 0.0153, 0.0005, 0.0240),
		(-0.0353, -0.0000, -0.0060, 0.0190),
		(-0.1070, 0.0058, 0.0437, 0.0275),
		(-0.1193, -0.0098, -0.0022, 0.0220),
		(-0.1337, 0.0060, 0.0003, 0.0165),
		(-0.0354, -0.0000, 0.0424, 0.0190),
		(-0.0997, -0.0069, 0.0010, 0.0235),
		(-0.0610, 0.0101, 0.0182, 0.0200),
		(-0.1219, 0.0140, 0.0354, 0.0210),
		(-0.1081, -0.0064, 0.0431, 0.0250),
	),
	"wrist_link": (
		(-0.0166, -0.0468, 0.0147, 0.0210),
		(-0.0002, 0.0055, -0.0053, 0.0140),
		(0.0101, -0.0174, 0.0490, 0.0165),
		(0.0112, -0.0589, 0.0497, 0.0200),
		(0.0077, -0.0451, -0.0010, 0.0210),
		(0.0032, -0.0604, 0.0200, 0.0235),
		(-0.0130, -0.0244, 0.0504, 0.0220),
		(-0.0015, -0.0248, 0.0118, 0.0200),
		(-0.0109, -0.0587, 0.0508, 0.0200),
		(-0.0005, 0.0016, 0.0412, 0.0165),
		(-0.0001, -0.0062, -0.0030, 0.0145),
		(-0.0092, -0.0455, -0.0008, 0.0215),
		(0.0060, -0.0210, 0.0336, 0.0240),
		(-0.0109, -0.0604, 0.0287, 0.0215),
	),
	"gripper_link": (
		(-0.0291, -0.0153, -0.0069, 0.0230),
		(0.0127, -0.0001, -0.0972, 0.0195),
		(0.0225, 0.0160, -0.0408, 0.0160),
		(-0.0189, -0.0002, -0.0670, 0.0190),
		(0.0170, -0.0187, -0.0170, 0.0210),
		(0.0192, -0.0000, -0.0620, 0.0185),
		(-0.0178, 0.0157, -0.0108, 0.0240),
		(-0.0086, -0.0165, -0.0341, 0.0220),
		(-0.0112, -0.0003, -0.0981, 0.0165),
		(-0.0032, -0.0049, -0.0061, 0.0215),
		(0.0223, -0.0159, -0.0396, 0.0165),
		(-0.0292, -0.0002, -0.0450, 0.0235),
		(-0.0111, 0.0164, -0.0336, 0.0190),
		(0.0197, 0.0195, -0.0201, 0.0195),
	),
}


def so101_robot() -> RobotModel:
	"""Kinematic model of the five body joints with the tool point between the jaws."""
	return RobotModel(JOINTS, LINKS, TOOL_XYZ, TOOL_RPY)


def so101_profile() -> ArmProfile:
	"""Profile of the SO-101 follower: calibrate the gripper first, then wrist, elbow, shoulder lift, pan; roll last."""
	robot = so101_robot()
	shapes = {
		link: LinkShape(np.array([s[:3] for s in spheres]), np.array([s[3] for s in spheres]))
		for link, spheres in SPHERES.items()
	}
	collision = CollisionModel(
		robot, shapes, ignore=IGNORED_PAIRS, floor_z=FLOOR_Z, floor_exempt=("base_link", "shoulder_link")
	)
	vertical = ("shoulder_lift", "elbow_flex", "wrist_flex")
	joints = (
		JointSetup("gripper", 6, rest_deg=REST_DEG["gripper"], travel_deg=GRIPPER_TRAVEL_DEG, park_joints=vertical),
		JointSetup("wrist_flex", 4, rest_deg=REST_DEG["wrist_flex"], park_joints=vertical),
		JointSetup("elbow_flex", 3, rest_deg=REST_DEG["elbow_flex"], park_joints=vertical),
		JointSetup("shoulder_lift", 2, rest_deg=REST_DEG["shoulder_lift"], park_joints=vertical),
		JointSetup("shoulder_pan", 1, rest_deg=REST_DEG["shoulder_pan"], park_joints=vertical),
		JointSetup("wrist_roll", 5, kind="full_turn", rest_deg=REST_DEG["wrist_roll"]),
	)
	return ArmProfile("so101-follower", robot, collision, joints)
