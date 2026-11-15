"""Robot base calibration from recorded Studio episodes: tag poses on the arm next to the joint readings.

A recorded episode already pairs, at every frame, the follower's joint readings with the top camera's colour and
layered height image (``sorter-depth-bridge``). Wherever the arm holds still with its tags in view, that frame is
one :class:`~defect_sorter.joint_calibration.Observation` per tag, and
:func:`~defect_sorter.joint_calibration.solve_base` turns those into the robot base pose with Studio's joint zeros
trusted. No separate capture session and no limp arm are needed.

Each tag is placed in 3D from the recording itself: its centre pixel's ray, cut at the tag's height above the
bridge's held table plane (decoded from the height image), and its orientation from the corners (planar PnP). The
table frame comes from the anchor markers in the same frame. Small tags are detected on an upscaled copy of the
crop, because the recorded crop gives a 30 mm tag only about 25 pixels.

	uv run --extra dataset python -m defect_sorter.episode_calibration <dataset dir> --plane plane-v4.json \\
		--intrinsics 605.2 604.7 324.1 258.6 --crop 96 0 --ranges robots.json \\
		--marker 9:shoulder --marker 4:gripper --save data/calibration/robot.json

Tags small in the recording are seldom detected on the arm, so there is a second way that needs no arm tag at all:
touch points. With the gripper closed, the jaw tip is held on the centres of table markers whose positions the camera
measures; at each hold the joint readings give the tip in the base frame (Studio's zeros trusted), and a rigid fit of
those points to the markers (:func:`fit_touches`, ``--touch``) is the base pose. The fit also finds which touch was
which marker, and its residual shows how good the trusted joint zeros are.

Reading the videos needs PyAV (``av``), which Studio's backend environment has.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from itertools import permutations
from pathlib import Path

import cv2
import numpy as np

from defect_sorter.alignment import MarkerPose, TableFrame, table_frame
from defect_sorter.geometry import Intrinsics, Plane
from defect_sorter.joint_calibration import TICKS_PER_DEGREE, Observation
from defect_sorter.markers import detect_markers

logger = logging.getLogger(__name__)

BODY_JOINTS = ("shoulder_pan", "shoulder_lift", "elbow_flex", "wrist_flex", "wrist_roll")
FINE_MAX_M = 0.04
COARSE_MAX_M = 0.30


def normalized_to_degrees(value: float, range_min: float, range_max: float) -> float:
	"""A body joint in Studio's normalized unit (-100..100 over its calibrated tick range) as degrees.

	Zero is the range midpoint, as in :func:`defect_sorter.joint_calibration.ticks_to_degrees`.
	"""
	return float(value) / 100.0 * (range_max - range_min) / 2.0 / TICKS_PER_DEGREE


def state_degrees(
	state: Sequence[float], names: Sequence[str], ranges: Mapping[str, tuple[float, float]]
) -> dict[str, float]:
	"""Body joint angles (degrees) from one recorded state vector; ``names`` as in the dataset (``<joint>.pos``)."""
	out = {}
	for value, name in zip(state, names, strict=True):
		joint = name.removesuffix(".pos")
		if joint in BODY_JOINTS:
			out[joint] = normalized_to_degrees(value, *ranges[joint])
	return out


def layered_height_m(
	image_bgr: np.ndarray, *, fine_max_m: float = FINE_MAX_M, coarse_max_m: float = COARSE_MAX_M
) -> np.ndarray:
	"""Height above the table (m) from the bridge's ``layers`` image; NaN where depth was missing.

	The fine channel (R) is used below its top, the coarse one (G) above.
	"""
	img = np.asarray(image_bgr, dtype=np.float64)
	fine = img[..., 2] / 255.0 * fine_max_m
	coarse = img[..., 1] / 255.0 * coarse_max_m
	height = np.where(img[..., 2] < 250, fine, coarse)
	height[img[..., 0] < 128] = np.nan
	return height


def point_at_height(u: float, v: float, height_m: float, intrinsics: Intrinsics, plane: Plane) -> np.ndarray:
	"""Camera-space point on pixel (u, v)'s ray at ``height_m`` above ``plane``."""
	ray = np.array([(u - intrinsics.ppx) / intrinsics.fx, (v - intrinsics.ppy) / intrinsics.fy, 1.0])
	n = np.asarray(plane.normal, dtype=np.float64)
	return ray * (height_m - plane.offset) / float(n @ ray)


def _centre_px(corners: np.ndarray) -> tuple[float, float]:
	"""Image of the square's centre: where its diagonals cross (exact under perspective)."""
	p0, p1, p2, p3 = (np.asarray(c, dtype=np.float64) for c in corners)
	d1, d2 = p2 - p0, p3 - p1
	t = np.linalg.solve(np.stack([d1, -d2], axis=1), p1 - p0)[0]
	x, y = p0 + t * d1
	return float(x), float(y)


def tag_poses(
	color_crop: np.ndarray,
	depth_crop: np.ndarray,
	*,
	intrinsics: Intrinsics,
	crop_xy: tuple[int, int],
	plane: Plane,
	anchors: tuple[int, int] = (16, 17),
	upscale: int = 2,
) -> tuple[TableFrame | None, dict[int, tuple[np.ndarray, np.ndarray]]]:
	"""Table frame and every tag's (rotation, position) in it, from one recorded frame.

	Parameters
	----------
	color_crop, depth_crop : numpy.ndarray
		The recorded colour and layered height images (the bridge's crop of the full camera frame).
	intrinsics : Intrinsics
		Of the full, uncropped colour frame.
	crop_xy : tuple of int
		Top-left corner of the crop in the full frame.
	plane : Plane
		The table plane the bridge held while recording.
	anchors : tuple of int
		Table anchor markers.
	upscale : int
		Detection runs on the crop enlarged this many times.

	Returns
	-------
	tuple
		``(None, {})`` when either anchor is missing.
	"""
	x0, y0 = crop_xy
	big = cv2.resize(color_crop, None, fx=upscale, fy=upscale, interpolation=cv2.INTER_CUBIC)
	big_intr = Intrinsics(
		fx=intrinsics.fx * upscale,
		fy=intrinsics.fy * upscale,
		ppx=(intrinsics.ppx - x0) * upscale,
		ppy=(intrinsics.ppy - y0) * upscale,
	)
	heights = layered_height_m(depth_crop)
	placed: dict[int, tuple[np.ndarray, np.ndarray]] = {}
	for det in detect_markers(big, big_intr):
		corners = det.corners_px / upscale
		mask = np.zeros(heights.shape, np.uint8)
		cv2.fillConvexPoly(mask, np.rint(corners).astype(np.int32), 1)
		inside = heights[(mask > 0) & np.isfinite(heights)]
		if inside.size == 0:
			continue
		u, v = _centre_px(corners)
		position = point_at_height(u + x0, v + y0, float(np.median(inside)), intrinsics, plane)
		placed[det.id] = (det.rotation, position)
	if not all(a in placed for a in anchors):
		return None, {}
	stub = {
		a: MarkerPose(a, "anchor", 0.0, placed[a][1], np.asarray(plane.normal), 0.0, "height image") for a in anchors
	}
	frame = table_frame(plane, stub, anchors=anchors)
	return frame, {mid: (frame.axes @ r, frame.point(p)) for mid, (r, p) in placed.items()}


def still_moments(
	timestamps_s: np.ndarray, body_deg: np.ndarray, *, still_deg_s: float = 3.0, hold_s: float = 0.5
) -> list[int]:
	"""One frame index from the middle of every interval where all body joints stay slower than ``still_deg_s``."""
	t = np.asarray(timestamps_s, dtype=np.float64)
	q = np.asarray(body_deg, dtype=np.float64)
	if len(t) < 3:
		return []
	speed = np.max(np.abs(np.gradient(q, t, axis=0)), axis=1)
	still = speed < still_deg_s
	out, start = [], None
	for i, s in enumerate([*still, False]):
		if s and start is None:
			start = i
		elif not s and start is not None:
			if t[i - 1] - t[start] >= hold_s:
				out.append((start + i - 1) // 2)
			start = None
	return out


def episode_observations(
	frames: Sequence[tuple[np.ndarray, np.ndarray, dict[str, float]]],
	markers: Mapping[int, str],
	**pose_kwargs: object,
) -> list[Observation]:
	"""Observations from (colour crop, depth crop, joint degrees) at still moments, one per tag in view."""
	out = []
	for color, depth, angles in frames:
		frame, tags = tag_poses(color, depth, **pose_kwargs)
		if frame is None:
			continue
		for mid, link in markers.items():
			if mid in tags:
				r, p = tags[mid]
				out.append(Observation(angles_deg=dict(angles), marker_rotation=r, marker_position_m=p, link=link))
	return out


def rigid_fit(src: np.ndarray, dst: np.ndarray) -> tuple[np.ndarray, np.ndarray, float]:
	"""Rotation and translation with ``dst ≈ R @ src + t`` (least squares, Kabsch), and the RMS residual in metres."""
	a, b = np.asarray(src, dtype=np.float64), np.asarray(dst, dtype=np.float64)
	ca, cb = a.mean(axis=0), b.mean(axis=0)
	u, _, vt = np.linalg.svd((a - ca).T @ (b - cb))
	d = np.sign(np.linalg.det(vt.T @ u.T))
	r = vt.T @ np.diag([1.0, 1.0, d]) @ u.T
	t = cb - r @ ca
	rms = float(np.sqrt(np.mean(np.sum((a @ r.T + t - b) ** 2, axis=1))))
	return r, t, rms


MAX_BASE_TILT_DEG = 20.0
"""The robot base stands on the table: a pairing of touches with markers that needs it tilted more is wrong.

All touches lie in the table plane, so a near-symmetric marker layout also fits with the base turned upside down;
this keeps that mirror solution out.
"""


def _upright(rotation: np.ndarray, max_tilt_deg: float = MAX_BASE_TILT_DEG) -> bool:
	return float(rotation[2, 2]) >= np.cos(np.radians(max_tilt_deg))


@dataclass(frozen=True)
class TouchFit:
	"""Base pose from touch points, which marker each touch was, and the per-touch and RMS residuals (mm)."""

	base_rotation: np.ndarray
	base_position_m: np.ndarray
	assignment: list[int]
	residuals_mm: list[float]
	rms_mm: float


def fit_touches(touches_base: Sequence[np.ndarray], markers_table: Mapping[int, np.ndarray]) -> TouchFit:
	"""Fit the base pose to jaw-tip touches on table markers; every upright pairing of touches to markers is tried.

	Raises
	------
	ValueError
		With fewer than 3 touches, or more touches than markers.
	"""
	n = len(touches_base)
	if n < 3:
		raise ValueError(f"need at least 3 touches on different markers, got {n}")
	if n > len(markers_table):
		raise ValueError(f"{n} touches but only {len(markers_table)} markers to match them to")
	src = np.asarray(touches_base, dtype=np.float64)
	best = None
	for ids in permutations(markers_table, n):
		dst = np.array([markers_table[i] for i in ids])
		r, t, rms = rigid_fit(src, dst)
		if _upright(r) and (best is None or rms < best[3]):
			best = (r, t, list(ids), rms, dst)
	if best is None:
		raise ValueError("no pairing of touches with markers keeps the robot base upright")
	r, t, ids, rms, dst = best
	residuals = np.linalg.norm(src @ r.T + t - dst, axis=1) * 1000.0
	return TouchFit(r, t, ids, [float(x) for x in residuals], rms * 1000.0)


@dataclass(frozen=True)
class TouchZeroFit:
	"""Level base pose and joint zero corrections fitted to touches, with fitted and leave-one-out errors (mm).

	``offsets_deg`` are added to the readings (as in :class:`~defect_sorter.robot_pose.RobotCalibration`).
	``leave_one_out_mm`` is each touch's error when the fit did not see it: the honest prediction error.
	"""

	base_rotation: np.ndarray
	base_position_m: np.ndarray
	offsets_deg: dict[str, float]
	assignment: list[int]
	residuals_mm: list[float]
	rms_mm: float
	leave_one_out_mm: list[float]


ZERO_JOINTS = ("shoulder_lift", "elbow_flex", "wrist_flex")


def _group_touches(tips: np.ndarray, radius_m: float) -> list[list[int]]:
	groups: list[list[int]] = []
	for i, tip in enumerate(tips):
		for g in groups:
			if np.linalg.norm(tips[g].mean(axis=0) - tip) < radius_m:
				g.append(i)
				break
		else:
			groups.append([i])
	return groups


def fit_touches_with_zeros(
	touch_angles: Sequence[Mapping[str, float]],
	markers_table: Mapping[int, np.ndarray],
	*,
	joints: tuple[str, ...] = ZERO_JOINTS,
	group_radius_m: float = 0.05,
	max_zero_error_deg: float = 20.0,
) -> TouchZeroFit:
	"""Fit a level base (position, heading) and the zero errors of ``joints`` to jaw-tip touches on table markers.

	Touches whose tips (with the readings as they are) lie within ``group_radius_m`` of each other are taken as the
	same marker, and every pairing of those groups with the markers is tried by a rigid fit; the best pairing is
	then refined with the joint zeros free within ``max_zero_error_deg`` (a manual calibration is off by a few
	degrees, not tens), from several starting guesses. Touch one marker in different arm postures, or the zeros of
	the lift, elbow and wrist cannot be told apart.

	Raises
	------
	ValueError
		With fewer than 3 touches, fewer equations than unknowns, or more touched spots than markers.
	"""
	from scipy.optimize import least_squares
	from scipy.spatial.transform import Rotation

	from defect_sorter.kinematics import tool_pose

	n = len(touch_angles)
	unknowns = 4 + len(joints)
	if n < 3 or 3 * n < unknowns:
		raise ValueError(f"need at least 3 touches and {unknowns} equations, got {n} touches")
	tips = np.array([tool_pose(a)[:3, 3] for a in touch_angles])
	groups = _group_touches(tips, group_radius_m)
	if len(groups) > len(markers_table):
		raise ValueError(f"touches on {len(groups)} spots but only {len(markers_table)} markers")
	if len(groups) < 3:
		raise ValueError(f"touches on only {len(groups)} spots; need 3 different markers")
	centres = np.array([tips[g].mean(axis=0) for g in groups])
	best = None
	for ids in permutations(markers_table, len(groups)):
		r, t, rms = rigid_fit(centres, np.array([markers_table[i] for i in ids]))
		if _upright(r) and (best is None or rms < best[0]):
			best = (rms, r, t, ids)
	if best is None:
		raise ValueError("no pairing of touches with markers keeps the robot base upright")
	_, r0, t0, ids = best
	assignment = [0] * n
	for g, marker in zip(groups, ids, strict=True):
		for i in g:
			assignment[i] = marker
	targets = np.array([markers_table[m] for m in assignment], dtype=np.float64)
	yaw0 = float(np.degrees(np.arctan2(r0[1, 0], r0[0, 0])))

	def tip_table(x: np.ndarray, angles: Mapping[str, float]) -> np.ndarray:
		off = dict(zip(joints, x[4:], strict=True))
		r = Rotation.from_euler("z", x[3], degrees=True).as_matrix()
		return r @ tool_pose({k: v + off.get(k, 0.0) for k, v in angles.items()})[:3, 3] + x[:3]

	k = len(joints)
	lower = np.concatenate([[-np.inf] * 4, [-max_zero_error_deg] * k])
	upper = np.concatenate([[np.inf] * 4, [max_zero_error_deg] * k])

	def solve(rows: list[int], starts: list[np.ndarray]) -> np.ndarray:
		def res(x: np.ndarray) -> np.ndarray:
			return np.concatenate([(tip_table(x, touch_angles[i]) - targets[i]) * 1000.0 for i in rows])

		fits = [least_squares(res, np.clip(x0, lower + 1e-9, upper - 1e-9), bounds=(lower, upper)) for x0 in starts]
		return min(fits, key=lambda f: f.cost).x

	base0 = np.concatenate([t0, [yaw0]])
	guesses = [np.zeros(k)] + [np.full(k, s) * np.eye(k)[j] for j in range(k) for s in (-8.0, 8.0)]
	x = solve(list(range(n)), [np.concatenate([base0, g]) for g in guesses])
	errors = [float(np.linalg.norm(tip_table(x, touch_angles[i]) - targets[i]) * 1000.0) for i in range(n)]
	loo = []
	for i in range(n):
		rest = [j for j in range(n) if j != i]
		if len({assignment[j] for j in rest}) < 3 or 3 * len(rest) < unknowns:
			loo.append(float("nan"))
			continue
		xi = solve(rest, [x])
		loo.append(float(np.linalg.norm(tip_table(xi, touch_angles[i]) - targets[i]) * 1000.0))
	return TouchZeroFit(
		base_rotation=Rotation.from_euler("z", x[3], degrees=True).as_matrix(),
		base_position_m=np.asarray(x[:3], dtype=np.float64),
		offsets_deg={j: float(v) for j, v in zip(joints, x[4:], strict=True)},
		assignment=assignment,
		residuals_mm=errors,
		rms_mm=float(np.sqrt(np.mean(np.square(errors)))),
		leave_one_out_mm=loo,
	)


def video_file(root: Path, episodes: Mapping[str, Sequence], key: str, k: int) -> tuple[Path, float]:
	"""The video file holding episode row ``k`` of camera ``key``, and the time in it where that episode starts."""
	prefix = f"videos/observation.images.{key}/"
	chunk, file = int(episodes[prefix + "chunk_index"][k]), int(episodes[prefix + "file_index"][k])
	path = root / "videos" / f"observation.images.{key}" / f"chunk-{chunk:03d}" / f"file-{file:03d}.mp4"
	return path, float(episodes[prefix + "from_timestamp"][k])


def _read_dataset(root: Path, color_key: str, depth_key: str, ranges: Mapping[str, tuple[float, float]]):
	"""(colour, depth, joint degrees) at the inner still moments of every episode (needs ``av`` and ``pyarrow``).

	Studio splits a dataset over several parquet and video files; each episode's row in ``meta/episodes`` names the
	video file and the time its frames start at.
	"""
	import av
	import pyarrow.parquet as pq

	info = json.loads((root / "meta" / "info.json").read_text())
	names = info["features"]["observation.state"]["names"]
	body = [i for i, n in enumerate(names) if n.removesuffix(".pos") in BODY_JOINTS]
	cols: dict[str, list] = {"observation.state": [], "timestamp": [], "episode_index": []}
	for path in sorted((root / "data").glob("*/*.parquet")):
		table = pq.read_table(path, columns=list(cols)).to_pydict()
		for k in cols:
			cols[k] += table[k]
	episodes: dict[str, list] = {}
	for path in sorted((root / "meta" / "episodes").glob("*/*.parquet")):
		for k, v in pq.read_table(path).to_pydict().items():
			episodes.setdefault(k, []).extend(v)
	state = np.asarray(cols["observation.state"], dtype=np.float64)
	stamp = np.asarray(cols["timestamp"], dtype=np.float64)
	ep_of = np.asarray(cols["episode_index"])

	wanted: dict[tuple[Path, Path], list[tuple[float, float, dict[str, float]]]] = {}
	for k, e in enumerate(episodes["episode_index"]):
		rows = np.flatnonzero(ep_of == e)
		rows = rows[np.argsort(stamp[rows])]
		deg = np.array(
			[[normalized_to_degrees(state[r, i], *ranges[names[i].removesuffix(".pos")]) for i in body] for r in rows]
		)
		(color_path, color_t0) = video_file(root, episodes, color_key, k)
		(depth_path, depth_t0) = video_file(root, episodes, depth_key, k)
		# an episode starts and ends at rest; those holds are neither tag views over the table nor touches
		for idx in still_moments(stamp[rows], deg)[1:-1]:
			r = rows[idx]
			wanted.setdefault((color_path, depth_path), []).append(
				(color_t0 + stamp[r], depth_t0 + stamp[r], state_degrees(state[r], names, ranges))
			)

	def frames_at(path: Path, times: list[float]) -> list[np.ndarray]:
		out = []
		with av.open(str(path)) as c:
			s = c.streams.video[0]
			for t in times:
				c.seek(int(max(t - 1.0, 0.0) / s.time_base), stream=s)
				for f in c.decode(s):
					if f.time is not None and f.time >= t - 1e-3:
						out.append(f.to_ndarray(format="bgr24"))
						break
		return out

	result = []
	for (color_path, depth_path), items in wanted.items():
		colors = frames_at(color_path, [w[0] for w in items])
		depths = frames_at(depth_path, [w[1] for w in items])
		result += [(c, d, w[2]) for c, d, w in zip(colors, depths, items, strict=True)]
	return result


def touch_holds(
	holds: Sequence[Mapping[str, float]], *, max_height_m: float = 0.06, merge_m: float = 0.02
) -> list[dict[str, float]]:
	"""Joint readings of the touches among successive still holds: tip low (base frame), repeats of one touch dropped.

	The tip is computed with the readings as they are; ``max_height_m`` leaves out holds in the air and
	``merge_m`` keeps one hold per touch when the operator pauses twice on the same spot.
	"""
	from defect_sorter.kinematics import tool_pose

	out: list[dict[str, float]] = []
	last = None
	for angles in holds:
		tip = tool_pose(angles)[:3, 3]
		if abs(tip[2]) > max_height_m:
			continue
		if last is not None and np.linalg.norm(tip - last) < merge_m:
			continue
		out.append(dict(angles))
		last = tip
	return out


def _touch(args: argparse.Namespace, frames, pose_kwargs: dict, out) -> None:
	from defect_sorter.robot_pose import RobotCalibration, save_calibration

	seen: dict[int, list[np.ndarray]] = {m: [] for m in args.targets}
	for color, depth, _ in frames:
		frame, tags = tag_poses(color, depth, **pose_kwargs)
		for m in args.targets:
			if frame is not None and m in tags:
				seen[m].append(tags[m][1])
	markers = {m: np.median(v, axis=0) for m, v in seen.items() if v}
	for marker_id, x, y, z in args.target_at or []:
		markers[int(marker_id)] = np.array([x, y, z]) / 1000.0
	for m in sorted(markers):
		source = f"{len(seen.get(m, []))} frames" if seen.get(m) else "given"
		out.write(f"marker {m}: at {np.round(markers[m] * 1000).tolist()} mm ({source})\n")
	touches = touch_holds([a for _, _, a in frames], max_height_m=args.touch_height)
	out.write(f"still moments: {len(frames)}; touches on the table: {len(touches)}\n")
	fit = fit_touches_with_zeros(touches, markers, joints=() if args.trust_zeros else ZERO_JOINTS)
	for m, res, loo in zip(fit.assignment, fit.residuals_mm, fit.leave_one_out_mm, strict=True):
		out.write(f"  touch -> marker {m}: fitted {res:.1f} mm, unseen {loo:.1f} mm\n")
	r, pos = fit.base_rotation, fit.base_position_m * 1000
	zeros = ", ".join(f"{j} {v:+.1f}" for j, v in fit.offsets_deg.items()) or "Studio's, trusted"
	out.write(
		f"fit RMS {fit.rms_mm:.1f} mm, leave-one-out mean {np.nanmean(fit.leave_one_out_mm):.1f} mm; "
		f"joint zeros: {zeros} deg\n"
		f"robot base in table frame: x {pos[0]:.0f} mm, y {pos[1]:.0f} mm, z {pos[2]:.0f} mm, "
		f"yaw {np.degrees(np.arctan2(r[1, 0], r[0, 0])):.1f} deg\n"
	)
	if args.save:
		save_calibration(args.save, RobotCalibration(fit.offsets_deg, fit.base_rotation, fit.base_position_m))
		out.write(f"saved {args.save}\n")


def main(argv: list[str] | None = None) -> None:
	"""Base pose of the follower from a recorded dataset (Studio's joint zeros trusted); measure only."""
	from defect_sorter.calibration_capture import parse_marker_spec
	from defect_sorter.depth_bridge import load_plane
	from defect_sorter.joint_calibration import solve_base
	from defect_sorter.robot_pose import RobotCalibration, save_calibration

	parser = argparse.ArgumentParser(description=main.__doc__)
	parser.add_argument("dataset", type=Path, help="LeRobot v3 dataset folder as Studio stores it")
	parser.add_argument("--plane", type=Path, required=True, help="the bridge's plane file used while recording")
	parser.add_argument("--intrinsics", type=float, nargs=4, required=True, metavar=("FX", "FY", "PPX", "PPY"))
	parser.add_argument("--crop", type=int, nargs=2, default=[96, 0], metavar=("X", "Y"), help="bridge crop origin")
	parser.add_argument("--ranges", type=Path, required=True, help="Studio robot JSON (list or one robot)")
	parser.add_argument("--robot", default="Follower", help="robot name in --ranges")
	parser.add_argument("--marker", type=parse_marker_spec, action="append", metavar="ID:LINK", help="tags on the arm")
	parser.add_argument("--touch", action="store_true", help="fit jaw-tip touches on table markers instead of arm tags")
	parser.add_argument(
		"--targets", type=int, nargs="+", default=[16, 17, 18, 7, 10, 11], help="markers touched (--touch)"
	)
	parser.add_argument(
		"--touch-height", type=float, default=0.06, help="holds with the tip within this of the base height (m)"
	)
	parser.add_argument(
		"--target-at",
		type=float,
		nargs=4,
		action="append",
		metavar=("ID", "X", "Y", "Z"),
		help="a touched marker's table position in mm, when the arm hid it in the recording (repeatable)",
	)
	parser.add_argument("--trust-zeros", action="store_true", help="--touch: keep Studio's joint zeros, fit the base")
	parser.add_argument("--color", default="top_rgb_v2")
	parser.add_argument("--depth", default="top_depth_v2")
	parser.add_argument("--save", type=Path, help="write the base pose as a robot calibration (JSON)")
	args = parser.parse_args(argv)
	logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

	robots = json.loads(args.ranges.read_text())
	robot = next(r for r in (robots if isinstance(robots, list) else [robots]) if r["name"] == args.robot)
	ranges = {k: (v["range_min"], v["range_max"]) for k, v in robot["payload"]["calibration"].items()}
	frames = _read_dataset(args.dataset, args.color, args.depth, ranges)
	pose_kwargs = {
		"intrinsics": Intrinsics(*args.intrinsics),
		"crop_xy": tuple(args.crop),
		"plane": load_plane(args.plane),
	}
	out = sys.stdout
	if args.touch:
		_touch(args, frames, pose_kwargs, out)
		return
	if not args.marker:
		parser.error("give --marker ID:LINK for the arm tags, or --touch")
	markers = dict(args.marker)
	obs = episode_observations([(c, d, a) for c, d, a in frames], markers, **pose_kwargs)
	counts = {link: sum(o.link == link for o in obs) for link in markers.values()}
	out.write(f"still moments: {len(frames)}; tag observations: {counts}\n")
	fit = solve_base(obs)
	r, pos = fit.base_rotation, fit.base_position_m * 1000
	out.write(f"fit: RMS {fit.rms_position_mm:.1f} mm, {fit.rms_rotation_deg:.1f} deg; by link {fit.rms_by_link_mm}\n")
	out.write(
		f"robot base in table frame: x {pos[0]:.0f} mm, y {pos[1]:.0f} mm, z {pos[2]:.0f} mm, "
		f"yaw {np.degrees(np.arctan2(r[1, 0], r[0, 0])):.1f} deg, "
		f"tilt {np.degrees(np.arccos(np.clip(r[2, 2], -1.0, 1.0))):.1f} deg\n"
	)
	if args.save:
		save_calibration(args.save, RobotCalibration({}, fit.base_rotation, fit.base_position_m))
		out.write(f"saved {args.save}\n")


if __name__ == "__main__":
	main()
