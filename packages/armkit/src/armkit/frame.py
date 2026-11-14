"""The link between servo readings and the kinematic model: a measured offset per joint.

Servo readings are turned into angles relative to the middle of each joint's stored range. Whether that angle is the
model's joint angle depends on how the arm was calibrated: on a hand-calibrated arm the middle of a recorded range can
sit tens of degrees away from the model's zero. Planning against the collision model with a wrong link plans for a pose
the arm is not in, so planning code requires a :class:`ModelFrame` that was *measured*: the operator holds the arm in
a described reference pose and :func:`capture_frame` records the offsets (model angle minus stored-midpoint angle).
"""

from __future__ import annotations

import json
from collections.abc import Collection, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path

from armkit.calibration import Calibration
from armkit.profile import ArmProfile
from armkit.servo import ServoBus


@dataclass(frozen=True)
class ModelFrame:
	"""Per-joint link from stored-midpoint angles to model angles: ``model = sign * stored + offset``.

	``verified`` says the offsets were measured; ``verified_directions`` names the joints whose sign was checked with a
	second, clearly different pose (a single pose cannot tell a reversed joint from a correct one).
	"""

	offsets_deg: dict[str, float]
	reference: str = ""
	verified: bool = True
	signs: dict[str, int] = field(default_factory=dict)
	verified_directions: frozenset[str] = frozenset()
	first_pose_deg: dict[str, float] = field(default_factory=dict)
	"""Model angles of the pose the offsets were captured in."""

	@classmethod
	def identity(cls, profile: ArmProfile) -> ModelFrame:
		"""The assumption that stored midpoints are model zeros; marked unverified, so planning refuses it."""
		return cls(dict.fromkeys(profile.robot.names, 0.0), "assumed: stored range midpoints are model zeros", False)

	@classmethod
	def trusted(
		cls, offsets_deg: Mapping[str, float], reference: str, signs: Mapping[str, int] | None = None
	) -> ModelFrame:
		"""A frame whose offsets and directions are known by construction (simulations, tests)."""
		return cls(dict(offsets_deg), reference, True, dict(signs or {}), frozenset(offsets_deg))

	def sign(self, joint: str) -> int:
		return self.signs.get(joint, 1)

	def directions_known(self, joints: Collection[str]) -> bool:
		"""True when every joint in ``joints`` had its direction checked."""
		return set(joints) <= self.verified_directions

	def to_model(self, joint: str, stored_deg: float) -> float:
		return self.sign(joint) * stored_deg + self.offsets_deg.get(joint, 0.0)

	def to_stored(self, joint: str, model_deg: float) -> float:
		return (model_deg - self.offsets_deg.get(joint, 0.0)) * self.sign(joint)

	def save(self, path: Path) -> None:
		data = {
			"reference": self.reference,
			"offsets_deg": self.offsets_deg,
			"signs": self.signs,
			"verified_directions": sorted(self.verified_directions),
			"first_pose_deg": self.first_pose_deg,
		}
		path.write_text(json.dumps(data, indent=4) + "\n")

	@classmethod
	def load(cls, path: Path) -> ModelFrame:
		data = json.loads(path.read_text())
		return cls(
			{k: float(v) for k, v in data["offsets_deg"].items()},
			data.get("reference", ""),
			True,
			{k: int(v) for k, v in data.get("signs", {}).items()},
			frozenset(data.get("verified_directions", ())),
			{k: float(v) for k, v in data.get("first_pose_deg", {}).items()},
		)


def capture_frame(
	bus: ServoBus,
	profile: ArmProfile,
	reference_pose_deg: Mapping[str, float],
	*,
	reference: str = "",
	calibration: Calibration | None = None,
) -> ModelFrame:
	"""Offsets that make the arm's current readings equal ``reference_pose_deg`` (model angles of every chain joint).

	Call it while the arm really is in that pose. Nothing moves and nothing is written.
	"""
	missing = [n for n in profile.robot.names if n not in reference_pose_deg]
	if missing:
		raise ValueError(f"the reference pose does not give {', '.join(missing)}")
	calibration = calibration or bus.read_calibration()
	positions = bus.read_positions()
	offsets = {n: float(reference_pose_deg[n]) - calibration[n].to_degrees(positions[n]) for n in profile.robot.names}
	return ModelFrame(offsets, reference, first_pose_deg={n: float(reference_pose_deg[n]) for n in profile.robot.names})


def refine_frame(
	first: ModelFrame,
	bus: ServoBus,
	profile: ArmProfile,
	second_pose_deg: Mapping[str, float],
	*,
	reference: str = "",
	min_change_deg: float = 20.0,
	calibration: Calibration | None = None,
) -> ModelFrame:
	"""Check each joint's direction with a second pose (model angles), held now, that differs clearly from the first.

	For every joint whose model angle changed by at least ``min_change_deg`` between the poses, the reading must have
	changed by about as much; its sign says whether the joint runs with or against the model, and the offset is
	re-derived so the first pose still reads as it did. A reading change far from the described one means the pose was
	not held as described (or the wrong joint was moved), and raises ``ValueError``.
	"""
	missing = [n for n in profile.robot.names if n not in second_pose_deg]
	if missing:
		raise ValueError(f"the second pose does not give {', '.join(missing)}")
	calibration = calibration or bus.read_calibration()
	positions = bus.read_positions()
	offsets, signs, verified = dict(first.offsets_deg), dict(first.signs), set(first.verified_directions)
	for joint in profile.robot.names:
		model_first = first.first_pose_deg.get(joint, 0.0)
		stored_first = first.to_stored(joint, model_first)
		d_model = float(second_pose_deg[joint]) - model_first
		d_stored = calibration[joint].to_degrees(positions[joint]) - stored_first
		if abs(d_model) < min_change_deg:
			if abs(d_stored) > max(min_change_deg, 15.0):
				raise ValueError(f"{joint} was described as unchanged but its reading moved {d_stored:+.0f} deg")
			continue
		if abs(abs(d_stored) - abs(d_model)) > max(15.0, 0.35 * abs(d_model)):
			raise ValueError(
				f"{joint}: the pose was described as {d_model:+.0f} deg from the first one but the reading moved "
				f"{d_stored:+.0f} deg; hold the pose as described"
			)
		sign = 1 if d_stored * d_model > 0 else -1
		signs[joint] = sign
		offsets[joint] = model_first - sign * stored_first
		verified.add(joint)
	return ModelFrame(
		offsets, reference or first.reference, True, signs, frozenset(verified), dict(first.first_pose_deg)
	)


def directions_from_trace(
	trace: Sequence[Mapping[str, float]], joints: Collection[str], *, threshold_deg: float = 15.0
) -> dict[str, int]:
	"""Each joint's direction from readings sampled while an operator moved it, by hand, in the model's positive sense.

	For each joint the first excursion of more than ``threshold_deg`` from where the trace started decides: with the
	reading going up the joint runs with the model (+1), going down against it (-1). Joints that never moved that far
	are left out, so small nudges while handling the arm do not count.
	"""
	if not trace:
		return {}
	start = trace[0]
	signs: dict[str, int] = {}
	for row in trace[1:]:
		for joint in joints:
			if joint in signs:
				continue
			delta = row[joint] - start[joint]
			if abs(delta) > threshold_deg:
				signs[joint] = 1 if delta > 0 else -1
	return signs


def with_directions(first: ModelFrame, signs: Mapping[str, int]) -> ModelFrame:
	"""``first`` with these joints' directions set and verified; offsets are re-derived so the pose the frame was
	captured in still reads as that pose."""
	offsets, new_signs = dict(first.offsets_deg), dict(first.signs)
	for joint, sign in signs.items():
		model_first = first.first_pose_deg.get(joint, 0.0)
		stored_first = first.to_stored(joint, model_first)
		new_signs[joint] = sign
		offsets[joint] = model_first - sign * stored_first
	return ModelFrame(
		offsets,
		first.reference,
		True,
		new_signs,
		frozenset(first.verified_directions | set(signs)),
		dict(first.first_pose_deg),
	)
