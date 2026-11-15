"""Hybrid sort cycle: scripted hover, learned grasp, scripted show to the front camera, scripted place.

The grasp is the one step a script does badly (the last centimetre, a brick that is a little off its measured pose),
so a policy trained on grasp-from-hover clips does it; every other step is a checked scripted move
(:mod:`defect_sorter.motion`), which gives the inspection camera the same views every time.

One cycle (``sorter-hybrid``):

1. measure the brick and the bowls with the top camera (the arm at rest, out of the way);
2. scripted, checked hover above the brick, jaws open and turned across it;
3. the policy grasps: the follower's port goes to Studio, which runs the model in a runtime session until
   :class:`GraspMonitor` sees the brick held and lifted, a miss, or a timeout; the session then holds the arm and ends;
4. on a miss: rise, back to rest, measure again and retry (at most ``--attempts``);
5. scripted show: the holds of :data:`SHOW_ROUTINE` in front of the front camera (poses from the operators' holds in
   inspect-v1), keeping the gripper closed on the brick;
6. scripted place over the chosen bowl, open, back to rest.

Joint values here are Studio's normalized units (body joints -100..100 over the calibrated range, gripper 0..100)
unless a name says degrees; :func:`body_degrees` converts to the degree convention of :mod:`defect_sorter.motion`.
Nothing moves without ``--go``.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import sys
import time
import urllib.request
import uuid
from collections import deque
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any, Protocol

from defect_sorter.joint_calibration import TICKS_PER_DEGREE

if TYPE_CHECKING:
	import numpy as np

	from defect_sorter.targeting import BrickPose

logger = logging.getLogger(__name__)

BODY_JOINTS: tuple[str, ...] = ("shoulder_pan", "shoulder_lift", "elbow_flex", "wrist_flex", "wrist_roll")
ROLL_LIMIT = 85.0
"""Largest wrist roll the show uses; the follower's roll range ends at +-100 (about +-84 degrees)."""

GRASP_TASK = "Pick up the brick."
HOVER_GRIPPER_OPEN = 45.0
"""Gripper opening at the hover, inside the 28..56 the operators opened to before a grasp."""
RELEASE_GRIPPER_OPEN = 60.0


@dataclass(frozen=True)
class ShowHold:
	"""One pose of the show routine and how long to hold it still (seconds)."""

	name: str
	pose: dict[str, float]
	hold_s: float


_LEVEL = {"shoulder_pan": 42.0, "shoulder_lift": -19.0, "elbow_flex": 59.0, "wrist_flex": 0.0, "wrist_roll": 0.0}
SHOW_ROUTINE: tuple[ShowHold, ...] = (
	ShowHold("level", _LEVEL, 1.5),
	ShowHold("roll_right", _LEVEL | {"wrist_roll": ROLL_LIMIT}, 1.0),
	ShowHold("roll_left", _LEVEL | {"wrist_roll": -ROLL_LIMIT}, 1.0),
	ShowHold(
		"bottom",
		{"shoulder_pan": 41.0, "shoulder_lift": 37.0, "elbow_flex": 55.0, "wrist_flex": -95.0, "wrist_roll": 0.0},
		1.0,
	),
	ShowHold("return", _LEVEL, 0.0),
)
"""Median poses of the operators' still holds in inspect-v1 (level, roll each way, bottom up), roll kept off the
end stops."""

REST: dict[str, float] = {
	"shoulder_pan": -8.0,
	"shoulder_lift": -95.0,
	"elbow_flex": 95.0,
	"wrist_flex": -7.0,
	"wrist_roll": 0.0,
}
"""Folded rest (median start pose of the recordings), a little inside the lift and elbow range ends."""


def body_degrees(normalized: Mapping[str, float], ranges: Mapping[str, tuple[int, int]]) -> dict[str, float]:
	"""Body joints in Studio's normalized unit as degrees with zero at the range midpoint (motion's convention)."""
	return {
		j: float(v) / 100.0 * (ranges[j][1] - ranges[j][0]) / 2.0 / TICKS_PER_DEGREE
		for j, v in normalized.items()
		if j in BODY_JOINTS
	}


def normalized_state(observation_state: Mapping[str, float]) -> dict[str, float]:
	"""Studio's observation state (``<joint>.pos`` keys) as plain joint names."""
	return {k.removesuffix(".pos"): float(v) for k, v in observation_state.items()}


def with_gripper(path_ticks: list[dict[str, int]], *, start: int, goal: int, max_step: int) -> list[dict[str, int]]:
	"""``path_ticks`` with a gripper goal that moves from ``start`` to ``goal`` by at most ``max_step`` per waypoint.

	The gripper cannot jump to a far goal within one control step; a jump trips the tracking stop. When the gripper
	needs more waypoints than the path has, the path is extended holding its last pose until the gripper arrives.
	"""
	n = max(1, -(-abs(goal - start) // max_step))
	out = [dict(wp) for wp in path_ticks]
	while len(out) < n:
		out.append(dict(out[-1]))
	for k, wp in enumerate(out):
		wp["gripper"] = round(start + (goal - start) * min(k + 1, n) / n)
	return out


class PolicyMonitor(Protocol):
	"""What the policy runner needs: a time limit and a per-sample decision."""

	timeout_s: float

	def update(
		self, t_s: float, state: Mapping[str, float], action: Mapping[str, float] | None = None
	) -> Enum | None: ...


class GraspOutcome(Enum):
	HELD = "held"
	MISSED = "missed"
	TIMEOUT = "timeout"
	ERROR = "error"


@dataclass
class GraspMonitor:
	"""Decides, from the joint stream while the policy runs, whether the grasp worked.

	The jaws grip something when they stop wider than they are commanded (``block_margin`` or more, and not nearly
	shut): the brick blocks them, at whatever width its orientation gives. Without the commanded value, a
	brick-width reading (``held_band``) stands in for it.

	``HELD``: after the gripper was open, the jaws have gripped for ``settle_s`` and the tool rose ``lift_mm`` since
	they closed. ``MISSED``: after being open the jaws stayed nearly shut (``missed_below``, nothing between them)
	for ``settle_s``. ``TIMEOUT``: neither within ``timeout_s``; :attr:`holding_now` then tells whether the jaws
	still grip something, so a caller never opens them away from a bowl by mistake.

	Parameters
	----------
	height_mm : callable
		Tool height (mm, any fixed zero) from a joint state in Studio's normalized units.
	"""

	height_mm: Callable[[Mapping[str, float]], float]
	timeout_s: float = 12.0
	held_band: tuple[float, float] = (9.0, 21.0)
	block_margin: float = 5.0
	open_above: float = 26.0
	missed_below: float = 7.0
	settle_s: float = 0.5
	lift_mm: float = 25.0
	holding_now: bool = False
	_t0: float | None = None
	_opened: bool = False
	_close_height: float | None = None
	_recent: deque[tuple[float, float, bool]] = field(default_factory=deque)

	def update(
		self, t_s: float, state: Mapping[str, float], action: Mapping[str, float] | None = None
	) -> GraspOutcome | None:
		"""Add one sample (seconds, measured joints, commanded joints if known); the outcome once decided."""
		if self._t0 is None:
			self._t0 = t_s
		grip = float(state["gripper"])
		h = self.height_mm(state)
		if action is not None and "gripper" in action:
			gripping = grip >= self.missed_below and grip - float(action["gripper"]) >= self.block_margin
		else:
			gripping = self.held_band[0] <= grip <= self.held_band[1]
		if grip > self.open_above and not gripping:
			self._opened = True
		if not gripping:
			self._close_height = None
		elif self._opened and self._close_height is None:
			self._close_height = h
		self.holding_now = gripping
		self._recent.append((t_s, grip, gripping))
		# keep the newest sample at or before the window start, so real (jittered) sample times span settle_s
		while len(self._recent) > 1 and self._recent[1][0] <= t_s - self.settle_s:
			self._recent.popleft()
		if self._opened and t_s - self._recent[0][0] >= self.settle_s - 1e-9:
			if all(g < self.missed_below for _, g, _ in self._recent):
				return GraspOutcome.MISSED
			if (
				all(held for _, _, held in self._recent)
				and self._close_height is not None
				and h - self._close_height >= self.lift_mm
			):
				return GraspOutcome.HELD
		if t_s - self._t0 > self.timeout_s:
			return GraspOutcome.TIMEOUT
		return None


def offset_brick(brick: BrickPose, *, dx_mm: float, dy_mm: float) -> BrickPose:
	"""``brick`` with its centre moved by (``dx_mm``, ``dy_mm``) in the table plane; everything else unchanged.

	Compensates a measured, repeatable offset between where the hover-then-policy grasp closes and the brick.
	"""
	import dataclasses

	import numpy as np

	return dataclasses.replace(brick, centre_m=brick.centre_m + np.array([dx_mm, dy_mm, 0.0]) / 1000.0)


GRASP_CORRECTION_MM: tuple[float, float, float] = (-10.0, -17.0, 5.0)
"""Median offset (table frame) from the planned grasp point to where operators closed the jaws in
grasp-from-standoff-v2 (28 clean episodes, spread about 16 mm): the calibration's systematic error at the grasp."""


def scripted_grasp_target(grasp_m: np.ndarray, correction_mm: tuple[float, float, float]) -> np.ndarray:
	"""The planned grasp point (table frame, metres) moved by ``correction_mm``."""
	import numpy as np

	return np.asarray(grasp_m, dtype=np.float64) + np.asarray(correction_mm, dtype=np.float64) / 1000.0


def close_on_brick(
	bus: Any,
	gripper_range: tuple[int, int],
	*,
	step_frac: float = 0.01,
	block_frac: float = 0.05,
	squeeze_frac: float = 0.04,
	floor_frac: float = 0.02,
	sleep: Callable[[float], None] = time.sleep,
) -> int | None:
	"""Close the gripper step by step until something stops the jaws; the holding goal (a small squeeze), or ``None``.

	The jaws are stopped when the present position stays ``block_frac`` of the range above the goal. ``None`` means the
	gripper closed to ``floor_frac`` without meeting anything: a miss.
	"""
	lo, hi = gripper_range
	span = hi - lo
	step = max(2, round(step_frac * span))
	floor = lo + round(floor_frac * span)
	goal = bus.read_ticks()["gripper"]
	while goal - step > floor:
		goal -= step
		bus.write_goals({"gripper": goal})
		sleep(0.04)
		present = bus.read_ticks()["gripper"]
		if present - goal > block_frac * span:
			squeeze = present - round(squeeze_frac * span)
			bus.write_goals({"gripper": squeeze})
			return squeeze
	return None


def port_holders(device: str, *, proc: Path = Path("/proc"), own_pid: int | None = None) -> list[int]:
	"""Processes (other than ``own_pid``) with ``device`` open, from ``/proc/<pid>/fd`` links (Linux)."""
	import os

	own = os.getpid() if own_pid is None else own_pid
	target = os.path.realpath(device)
	pids = []
	for fd_dir in proc.glob("[0-9]*/fd"):
		pid = int(fd_dir.parent.name)
		if pid == own:
			continue
		try:
			if any(os.path.realpath(fd) == target for fd in fd_dir.iterdir()):
				pids.append(pid)
		except OSError:  # the process ended or is not ours to read
			continue
	return sorted(pids)


def wait_for_port(device: str, timeout_s: float = 10.0) -> bool:
	"""Wait until no other process holds ``device``; ``False`` when one still does after ``timeout_s``."""
	end = time.monotonic() + timeout_s
	while port_holders(device):
		if time.monotonic() > end:
			return False
		time.sleep(0.2)
	return True


class PlaceOutcome(Enum):
	RELEASED = "released"
	TIMEOUT = "timeout"


PLACE_TEXTS = {
	"green": "Place the brick in the green bowl on the left.",
	"pink": "Place the brick in the pink bowl on the right.",
}
"""The place instructions exactly as the place policy was trained on them (place-v1-balanced: colour and side, as seen
from the top camera, so the two differ by more than one word); the inspection result picks one."""


def place_instruction(bowl: str) -> str:
	"""The place policy's instruction for ``bowl`` (green or pink)."""
	if bowl not in PLACE_TEXTS:
		raise ValueError(f"no place instruction for a {bowl!r} bowl")
	return PLACE_TEXTS[bowl]


@dataclass
class ReleaseMonitor:
	"""Decides, while the place policy runs, when it has let go of the brick.

	``RELEASED``: the jaws have been open (at least ``open_above``) and no longer blocked by the brick (within
	``block_margin`` of the command) for ``settle_s``. ``TIMEOUT``: not within ``timeout_s``; the caller then keeps the
	brick in the jaws and stops.
	"""

	timeout_s: float = 15.0
	open_above: float = 28.0
	block_margin: float = 5.0
	settle_s: float = 0.5
	_t0: float | None = None
	_open_since: float | None = None

	def update(
		self, t_s: float, state: Mapping[str, float], action: Mapping[str, float] | None = None
	) -> PlaceOutcome | None:
		"""Add one sample (seconds, measured joints, commanded joints if known); the outcome once decided."""
		if self._t0 is None:
			self._t0 = t_s
		grip = float(state["gripper"])
		blocked = action is not None and "gripper" in action and grip - float(action["gripper"]) >= self.block_margin
		if grip >= self.open_above and not blocked:
			if self._open_since is None:
				self._open_since = t_s
			if t_s - self._open_since >= self.settle_s - 1e-9:
				return PlaceOutcome.RELEASED
		else:
			self._open_since = None
		if t_s - self._t0 > self.timeout_s:
			return PlaceOutcome.TIMEOUT
		return None


def environment_draft(environment: Mapping[str, Any]) -> dict[str, Any]:
	"""A saved Studio environment (as ``GET .../environments/{id}`` returns it) as a runtime-session load draft."""
	return {
		"id": environment["id"],
		"name": environment["name"],
		"robots": [
			{
				"robot_id": r["robot"]["id"],
				"tele_operator": {k: v for k, v in r["tele_operator"].items() if k != "robot"},
			}
			for r in environment["robots"]
		],
		"cameras": [{"camera_id": c["id"]} for c in environment.get("cameras", [])],
	}


def model_control(
	task: str, *, hz: float = 30, grace_s: float = 2.0, mode: str = "sync", request_threshold: float = 0.8
) -> dict[str, Any]:
	"""Runtime-session control that drives the follower with the loaded model.

	A new chunk is requested once ``request_threshold`` of the current one is left: 0.8 re-plans after a fifth of a
	chunk (about 0.7 s for ACT's 100 steps at 30 Hz) instead of Studio's default of half, so the policy sees its own
	progress more often during the final approach.
	"""
	if not 0.0 <= request_threshold <= 1.0:
		raise ValueError(f"request_threshold must be in [0, 1], got {request_threshold}")
	return {
		"type": "model",
		"task": task,
		"hz": hz,
		"execution": {"mode": mode, "request_threshold": request_threshold},
		"grace_s": grace_s,
	}


@dataclass(frozen=True)
class StudioTarget:
	"""Where the policy runs: Studio's address and the project, environment and model to load."""

	base_url: str
	project_id: str
	environment_id: str
	model_id: str
	backend: str = "openvino"
	device: str = "CPU"


async def _run_policy(
	target: StudioTarget,
	task: str,
	monitor: PolicyMonitor,
	log: Callable[[str], None],
	trace_path: Path | None = None,
) -> Enum:
	import struct

	import websockets

	base = target.base_url.rstrip("/")
	if not base.startswith(("http://", "https://")):
		raise ValueError(f"Studio address must be http(s): {base}")
	url = f"{base}/api/projects/{target.project_id}/environments/{target.environment_id}"
	env = json.loads(urllib.request.urlopen(url).read())  # noqa: S310 - scheme checked above
	ws_url = "ws" + base.removeprefix("http") + f"/api/projects/{target.project_id}/runtime/ws?hz=20"
	acks: dict[str, asyncio.Future[dict[str, Any]]] = {}
	outcome: asyncio.Future[Enum] = asyncio.get_running_loop().create_future()
	running = False

	def decide(result: Enum, why: str) -> None:
		if not outcome.done():
			log(f"grasp: {result.value} ({why})")
			outcome.set_result(result)

	trace = None if trace_path is None else trace_path.open("w")
	async with websockets.connect(ws_url, max_size=None) as ws:

		async def reader() -> None:
			async for msg in ws:
				if isinstance(msg, bytes):
					n = struct.unpack(">I", msg[:4])[0]
					head = json.loads(msg[4 : 4 + n])
					if running and head.get("state"):
						state = normalized_state(head["state"])
						action = normalized_state(head["action"]) if head.get("action") else None
						now = time.monotonic()
						result = monitor.update(now, state, action)
						if trace is not None:
							trace.write(json.dumps({"t": now, "state": state, "action": action}) + "\n")
						if result is not None:
							decide(result, "monitor")
					continue
				m = json.loads(msg)
				if m.get("type") == "ack":
					fut = acks.pop(m.get("request_id"), None)
					if fut is not None and not fut.done():
						fut.set_result(m)
				elif m.get("type") == "error":
					decide(GraspOutcome.ERROR, f"session error {json.dumps(m)[:300]}")
				elif m.get("type") == "status" and m.get("state") == "failed":
					decide(GraspOutcome.ERROR, f"{m.get('component')} failed: {m.get('error')}")

		async def send(command: dict[str, Any], timeout_s: float = 120.0) -> None:
			rid = str(uuid.uuid4())
			fut: asyncio.Future[dict[str, Any]] = asyncio.get_running_loop().create_future()
			acks[rid] = fut
			await ws.send(json.dumps(command | {"request_id": rid}))
			ack = await asyncio.wait_for(fut, timeout_s)
			if not ack["ok"]:
				raise RuntimeError(f"{command['command']} refused: {json.dumps(ack.get('error'))[:300]}")

		read_task = asyncio.create_task(reader())
		try:
			await send(
				{"command": "load_environment", "environment": environment_draft(env), "unload_incompatible": False}
			)
			await send(
				{
					"command": "load_model",
					"model_id": target.model_id,
					"backend": target.backend,
					"device": target.device,
				},
				timeout_s=300.0,
			)
			running = True
			await send({"command": "set_control", "control": model_control(task)})
			log("policy running")
			return await asyncio.wait_for(asyncio.shield(outcome), monitor.timeout_s + 10.0)
		except Exception as exc:  # anything unexpected: hold the arm and report, never retry automatically
			log(f"grasp step failed: {type(exc).__name__}: {exc}")
			return GraspOutcome.ERROR
		finally:
			running = False
			try:
				await send({"command": "set_control", "control": None}, timeout_s=10.0)
				log("policy stopped: follower holding")
			except Exception as exc:
				log(f"could not stop the policy cleanly: {type(exc).__name__}: {exc}")
			read_task.cancel()
			if trace is not None:
				trace.close()


def run_policy(
	target: StudioTarget,
	task: str,
	monitor: PolicyMonitor,
	log: Callable[[str], None],
	trace_path: Path | None = None,
) -> Enum:
	"""Run a policy in a Studio runtime session until ``monitor`` decides; the session then holds the arm and ends.

	With ``trace_path`` every observed joint state and command is written there as JSON lines.
	"""
	return asyncio.run(_run_policy(target, task, monitor, log, trace_path))


def main(argv: list[str] | None = None) -> None:
	"""``sorter-hybrid``: one sort cycle; plans and measures only, unless ``--go``."""
	import numpy as np

	from defect_sorter.joint_calibration import angles_from_ticks
	from defect_sorter.kinematics import tool_pose
	from defect_sorter.motion import (
		MotionLimits,
		_heights,
		_measure_bowls,
		_measure_brick,
		execute,
		gripper_ticks,
		plan_bowl_drop,
		plan_brick_hover,
		plan_joint_move,
		plan_lift,
		plan_move,
		to_ticks,
	)
	from defect_sorter.robot_pose import load_calibration, model_from_readings
	from defect_sorter.so101_reader import SO101Driver, SO101Reader

	parser = argparse.ArgumentParser(description="Hybrid sort cycle: scripted hover, policy grasp, scripted show/place")
	parser.add_argument("--port", required=True, help="follower serial port (/dev/serial/by-id/...)")
	parser.add_argument("--bridge", required=True, metavar="URL", help="running sorter-depth-bridge, http://host:port")
	parser.add_argument("--calibration", type=Path, default=Path("data/calibration/robot.json"))
	parser.add_argument("--frame-file", type=Path, default=Path("data/depth/table-frame.json"))
	parser.add_argument("--studio", default="http://localhost:7860")
	parser.add_argument("--project", default="4288b76c-bcbe-4717-9f3c-e0a58bba7c9c")
	parser.add_argument("--environment", default="82b8829f-799a-4457-bba0-4d64a3ff302d")
	parser.add_argument("--model", required=True, help="Studio model id of the grasp policy")
	parser.add_argument("--device", default="CPU", help="OpenVINO device for the policy")
	parser.add_argument("--bowl", choices=("green", "pink"), required=True, help="where the brick goes")
	parser.add_argument("--attempts", type=int, default=3)
	parser.add_argument("--speed", type=float, default=15.0, help="scripted moves, deg/s")
	parser.add_argument(
		"--reach", type=float, default=420.0, help="reach limit from the base, mm (the bowls need 420, the hard cap)"
	)
	parser.add_argument("--grasp-timeout", type=float, default=12.0, help="seconds the policy gets per attempt")
	parser.add_argument("--no-show", action="store_true", help="skip the show to the front camera")
	parser.add_argument(
		"--grasp",
		choices=("policy", "script"),
		default="policy",
		help="grasp by the learned policy (Studio) or by a scripted descent and close from the hover",
	)
	parser.add_argument(
		"--grasp-correction",
		type=float,
		nargs=3,
		default=GRASP_CORRECTION_MM,
		metavar=("DX", "DY", "DZ"),
		help="scripted grasp: offset added to the planned grasp point, table mm (measured from the recordings)",
	)
	parser.add_argument(
		"--stop-after-grasp",
		action="store_true",
		help="after the grasp and lift, stop holding the brick (an inspection step takes over)",
	)
	parser.add_argument(
		"--place",
		choices=("script", "policy"),
		default="script",
		help="place by a scripted bowl drop, or by the language-conditioned place policy (--place-model)",
	)
	parser.add_argument("--place-model", help="Studio model id of the place policy (SmolVLA, place-v1)")
	parser.add_argument("--place-device", default="GPU", help="OpenVINO device for the place policy")
	parser.add_argument("--place-timeout", type=float, default=15.0, help="seconds the place policy gets")
	parser.add_argument(
		"--from-held", action="store_true", help="the brick is already in the jaws: skip the grasp, lift and place it"
	)
	parser.add_argument(
		"--grasp-offset",
		type=float,
		nargs=2,
		default=(0.0, 0.0),
		metavar=("DX", "DY"),
		help="move the hover target by this much (table mm) to cancel a measured, repeatable grasp offset",
	)
	parser.add_argument(
		"--trace-dir", type=Path, default=Path("data/logs/hybrid"), help="joint traces of each policy run (JSON lines)"
	)
	parser.add_argument("--go", action="store_true", help="run the cycle (the arm moves)")
	args = parser.parse_args(argv)
	if args.place == "policy" and not args.place_model:
		parser.error("--place policy needs --place-model")
	logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

	def say(msg: str) -> None:
		sys.stdout.write(f"{time.strftime('%H:%M:%S')} {msg}\n")
		sys.stdout.flush()

	cal = load_calibration(args.calibration)
	limits = MotionLimits(max_speed_deg_s=args.speed, max_reach_m=args.reach / 1000)
	dt = 0.05
	track = round(limits.max_tracking_error_deg * TICKS_PER_DEGREE)
	target = StudioTarget(args.studio, args.project, args.environment, args.model, device=args.device)

	def run_path(arm: SO101Driver, path: list[dict[str, float]], ranges: dict, gripper: int | None) -> None:
		ticks = [to_ticks(wp, ranges) for wp in path]
		if gripper is not None:
			present = arm.read_ticks()["gripper"]
			step = max(1, round(limits.max_speed_deg_s * TICKS_PER_DEGREE * dt))
			ticks = with_gripper(ticks, start=present, goal=gripper, max_step=step)
		result = execute(arm, ticks, dt_s=dt, max_tracking_error_ticks=track)
		if not result.ok:
			sys.exit(f"STOPPED: {result.reason}")

	def plan_lifts(start: dict[str, float], ranges: dict, min_height_m: float = 0.11) -> list[list[dict[str, float]]]:
		"""Lift paths until the tool is at ``min_height_m`` (at most four); empty if already there.

		Each lift tries 5 cm keeping within 2 cm of the spot, then 5 cm within 4 cm, then 3 cm within 2 cm: near a
		joint's range end (the wrist after a grasp at the edge of the reach) the smaller or looser lift still passes.
		"""
		paths, here = [], {j: start[j] for j in BODY_JOINTS}
		for _ in range(4):
			h = _heights(here, cal)[1]
			if h >= min_height_m:
				break
			for rise, drift in ((0.05, 0.02), (0.05, 0.04), (0.03, 0.02)):
				lift = plan_lift(
					here,
					calibration=cal,
					limits=limits,
					ranges=ranges,
					rise_m=min(rise, min_height_m - h + 0.005),
					max_drift_m=drift,
					dt_s=dt,
				)
				if lift.ok:
					break
			if not lift.ok:
				break
			paths.append(lift.path)
			here = lift.path[-1]
		return paths

	def plan_drop(start: dict[str, float], ranges: dict) -> tuple[list[list[dict[str, float]]], str]:
		"""Paths to the drop point over the chosen bowl: directly, or via the level carry pose; (paths, reason)."""
		bowl = bowls[args.bowl]
		direct, point, why = plan_bowl_drop(start, bowl, calibration=cal, limits=limits, ranges=ranges, dt_s=dt)
		if point is not None:
			return [direct.path], ""
		level = body_degrees(_LEVEL, ranges)
		carry = plan_joint_move(start, level, calibration=cal, limits=limits, ranges=ranges, dt_s=dt)
		if not carry.ok:
			return [], f"{why}; via the carry pose: {carry.reason}"
		after = dict(start) | carry.path[-1]
		drop, point, why2 = plan_bowl_drop(after, bowl, calibration=cal, limits=limits, ranges=ranges, dt_s=dt)
		if point is None:
			return [], f"{why}; from the carry pose: {why2}"
		return [carry.path, drop.path], ""

	def body_now(arm: SO101Reader, ranges: dict) -> dict[str, float]:
		return angles_from_ticks(arm.read_ticks(), ranges)

	def rise_and_rest(arm: SO101Driver, ranges: dict, gripper: int | None) -> None:
		start = body_now(arm, ranges)
		tool, h, _ = _heights({j: start[j] for j in BODY_JOINTS}, cal)
		up = plan_move(
			start,
			np.array([tool[0], tool[1], max(h + 0.06, 0.10)]),
			roll_deg=start["wrist_roll"],
			calibration=cal,
			limits=limits,
			ranges=ranges,
			dt_s=dt,
			approach_table=cal.base_rotation @ tool_pose(model_from_readings(start, cal))[:3, 2],
		)
		if up.ok:
			run_path(arm, up.path, ranges, gripper)
		else:
			lift = plan_lift(start, calibration=cal, limits=limits, ranges=ranges, dt_s=dt)
			if lift.ok:
				say(f"no straight rise ({up.reason}); lifting in place first")
				run_path(arm, lift.path, ranges, gripper)
			else:
				say(f"no straight rise or lift ({lift.reason}); going to rest directly")
		rest = plan_joint_move(
			body_now(arm, ranges), body_degrees(REST, ranges), calibration=cal, limits=limits, ranges=ranges
		)
		if not rest.ok:
			sys.exit(f"refused: cannot return to rest: {rest.reason}")
		run_path(arm, rest.path, ranges, gripper)

	bowls = _measure_bowls((16, 17), args.bridge, frame_file=args.frame_file)
	if args.bowl not in bowls:
		sys.exit(f"refused: the {args.bowl} bowl is not seen")
	say(
		f"{args.bowl} bowl at ({bowls[args.bowl].centre_m[0] * 1000:.0f}, {bowls[args.bowl].centre_m[1] * 1000:.0f}) mm"
	)

	held = False
	if args.from_held:
		# the brick is already in the jaws (a stopped earlier cycle): keep squeezing it and go on with the place
		with SO101Reader(args.port) as arm:
			ranges = arm.ranges()
			present = arm.read_ticks()["gripper"]
			here = body_now(arm, ranges)
		if not args.go:
			lifts = plan_lifts(here, ranges)
			after = lifts[-1][-1] if lifts else {j: here[j] for j in BODY_JOINTS}
			say(f"dry run: {len(lifts)} lift(s), tool then at {_heights(after, cal)[1] * 1000:.0f} mm")
			paths, why = plan_drop(dict(here) | after, ranges)
			steps = " + ".join(str(len(p)) for p in paths)
			say(f"dry run: bowl drop {'ok, ' + steps + ' steps' if paths else 'REFUSED: ' + why}")
			return
		lo, hi = ranges["gripper"]
		squeeze = present - min(round(0.04 * (hi - lo)), round(0.7 * track))
		held = True
	for attempt in range(1, 0 if args.from_held else args.attempts + 1):
		brick = _measure_brick(
			(16, 17), None, args.bridge, exclude_xy_m=cal.base_position_m[:2], frame_file=args.frame_file
		)
		say(
			f"attempt {attempt}: brick at ({brick.centre_m[0] * 1000:.0f}, {brick.centre_m[1] * 1000:.0f}) mm, yaw "
			f"{brick.yaw_deg:+.0f}; hover target moved by ({args.grasp_offset[0]:+.0f}, {args.grasp_offset[1]:+.0f}) mm"
		)
		brick = offset_brick(brick, dx_mm=args.grasp_offset[0], dy_mm=args.grasp_offset[1])
		with (SO101Driver if args.go else SO101Reader)(args.port) as arm:
			ranges = arm.ranges()
			plan, choice, why = plan_brick_hover(
				body_now(arm, ranges), brick, calibration=cal, limits=limits, ranges=ranges, dt_s=dt
			)
			if choice is None:
				sys.exit(f"refused: hover: {why}")
			say(
				f"hover plan ok: {len(plan.path)} steps, approach {choice.tilt_deg:.0f} deg, roll {choice.roll.roll_deg:+.0f}"
			)
			if not args.go:
				if args.grasp == "script":
					target_m = scripted_grasp_target(choice.grasp_m, tuple(args.grasp_correction))
					dry_limits = MotionLimits(
						max_speed_deg_s=min(args.speed, 10.0), max_reach_m=args.reach / 1000, min_tool_height_m=0.004
					)
					after_hover = body_now(arm, ranges) | plan.path[-1]
					down = plan_move(
						after_hover,
						target_m,
						roll_deg=choice.roll.roll_deg,
						calibration=cal,
						limits=dry_limits,
						ranges=ranges,
						dt_s=dt,
						approach_table=choice.approach,
					)
					say(
						f"scripted descent to ({target_m[0] * 1000:.0f}, {target_m[1] * 1000:.0f}, {target_m[2] * 1000:.0f}) mm: "
						+ (f"ok, {len(down.path)} steps" if down.ok else f"REFUSED: {down.reason}")
					)
				say("dry run: nothing moved (add --go)")
				return
			run_path(arm, plan.path, ranges, gripper_ticks(HOVER_GRIPPER_OPEN, ranges["gripper"]))
			if args.grasp == "script":
				target_m = scripted_grasp_target(choice.grasp_m, tuple(args.grasp_correction))
				# the descent may bring the tool point (between the jaw tips) down to the brick's mid-height
				grasp_limits = MotionLimits(
					max_speed_deg_s=min(args.speed, 10.0), max_reach_m=args.reach / 1000, min_tool_height_m=0.004
				)
				down = plan_move(
					body_now(arm, ranges),
					target_m,
					roll_deg=choice.roll.roll_deg,
					calibration=cal,
					limits=grasp_limits,
					ranges=ranges,
					dt_s=dt,
					approach_table=choice.approach,
				)
				if not down.ok:
					say(f"attempt {attempt}: no checked descent ({down.reason}); back to rest")
					rise_and_rest(arm, ranges, None)
					continue
				open_ticks = gripper_ticks(HOVER_GRIPPER_OPEN, ranges["gripper"])
				ticks = [to_ticks(wp, ranges) | {"gripper": open_ticks} for wp in down.path]
				result = execute(arm, ticks, dt_s=dt, max_tracking_error_ticks=track)
				if not result.ok:
					sys.exit(f"STOPPED during the descent: {result.reason}")
				held_goal = close_on_brick(arm, ranges["gripper"])
				if held_goal is None:
					say(f"attempt {attempt}: missed (the jaws closed on nothing); back to rest to look again")
					rise_and_rest(arm, ranges, None)
					continue
				say(f"attempt {attempt}: scripted grasp holds the brick")
				squeeze = held_goal
				held = True
				break
		# the port is free: Studio drives the follower with the grasp policy

		def height_mm(state: Mapping[str, float], ranges: dict = ranges) -> float:
			deg = body_degrees(state, ranges)
			return float(cal.to_table(tool_pose(model_from_readings(deg, cal))[:3, 3])[2] * 1000)

		monitor = GraspMonitor(height_mm=height_mm, timeout_s=args.grasp_timeout)
		trace = args.trace_dir / f"grasp-{time.strftime('%Y%m%d-%H%M%S')}-attempt{attempt}.jsonl"
		args.trace_dir.mkdir(parents=True, exist_ok=True)
		outcome = run_policy(target, GRASP_TASK, monitor, say, trace)
		say(f"grasp trace: {trace}")
		if outcome is GraspOutcome.TIMEOUT and monitor.holding_now:
			# blocked jaws without the lift are not proof of a hold (they can press on the brick or the table)
			sys.exit("STOPPED: timeout with the jaws blocked but no lift; the arm holds where it is. Check it first.")
		if outcome is GraspOutcome.ERROR:
			sys.exit("STOPPED: the grasp step failed; the arm holds where it is. Check it before anything else.")
		if not wait_for_port(args.port):
			sys.exit("STOPPED: Studio still holds the follower's port after the policy; the arm holds where it is.")
		with SO101Driver(args.port) as arm:
			present = arm.read_ticks()["gripper"]
			lo, hi = ranges["gripper"]
			squeeze = present - min(round(0.04 * (hi - lo)), round(0.7 * track))
			if outcome is GraspOutcome.HELD:
				held = True
				break
			say(f"attempt {attempt}: {outcome.value}; back to rest to look again (the gripper is not opened)")
			rise_and_rest(arm, ranges, None)
	if not held:
		sys.exit(f"gave up after {args.attempts} attempts; the arm is at rest")

	with SO101Driver(args.port) as arm:
		lifts = plan_lifts(body_now(arm, ranges), ranges)
		for path in lifts:
			run_path(arm, path, ranges, squeeze)
		say(f"lifted the brick to {_heights(body_now(arm, ranges), cal)[1] * 1000:.0f} mm ({len(lifts)} lift(s))")
		if args.stop_after_grasp:
			say("holding the brick: stopped after the grasp")
			return
		if not args.no_show:
			for hold in SHOW_ROUTINE:
				move = plan_joint_move(
					body_now(arm, ranges),
					body_degrees(hold.pose, ranges),
					calibration=cal,
					limits=limits,
					ranges=ranges,
				)
				if not move.ok:
					sys.exit(f"refused: show pose {hold.name}: {move.reason}; the arm holds the brick where it is")
				run_path(arm, move.path, ranges, squeeze)
				say(f"show: {hold.name}")
				time.sleep(hold.hold_s)
		if args.place == "policy" and args.no_show:
			# the place episodes start level in front of the front camera, where the show ends
			start_pose = plan_joint_move(
				body_now(arm, ranges), body_degrees(_LEVEL, ranges), calibration=cal, limits=limits, ranges=ranges
			)
			if not start_pose.ok:
				sys.exit(f"refused: place start pose: {start_pose.reason}; the arm holds the brick where it is")
			run_path(arm, start_pose.path, ranges, squeeze)
	if args.place == "policy":
		instruction = place_instruction(args.bowl)
		say(f"place policy: {instruction!r}")
		place_target = StudioTarget(
			args.studio, args.project, args.environment, args.place_model, device=args.place_device
		)
		trace = args.trace_dir / f"place-{time.strftime('%Y%m%d-%H%M%S')}.jsonl"
		args.trace_dir.mkdir(parents=True, exist_ok=True)
		placed = run_policy(place_target, instruction, ReleaseMonitor(timeout_s=args.place_timeout), say, trace)
		say(f"place trace: {trace}")
		if not wait_for_port(args.port):
			sys.exit(
				"STOPPED: Studio still holds the follower's port after the place policy; the arm holds where it is."
			)
		if placed is not PlaceOutcome.RELEASED:
			sys.exit(
				f"STOPPED: place policy {placed.value}; the arm holds where it is (gripper not opened by the script)"
			)
		with SO101Driver(args.port) as arm:
			say(f"released by the place policy ({args.bowl} bowl requested)")
			rise_and_rest(arm, ranges, None)
			say("cycle done: the arm is at rest")
		return
	with SO101Driver(args.port) as arm:
		paths, why = plan_drop(body_now(arm, ranges), ranges)
		if not paths:
			sys.exit(f"refused: place: {why}; the arm holds the brick where it is")
		for path in paths:
			run_path(arm, path, ranges, squeeze)
		here = to_ticks(body_now(arm, ranges), ranges)
		run_ticks = with_gripper(
			[here],
			start=arm.read_ticks()["gripper"],
			goal=gripper_ticks(RELEASE_GRIPPER_OPEN, ranges["gripper"]),
			max_step=max(1, round(limits.max_speed_deg_s * TICKS_PER_DEGREE * dt)),
		)
		result = execute(arm, run_ticks, dt_s=dt, max_tracking_error_ticks=track)
		if not result.ok:
			sys.exit(f"STOPPED while releasing: {result.reason}")
		time.sleep(0.5)
		say(f"released over the {args.bowl} bowl")
		rest = plan_joint_move(
			body_now(arm, ranges), body_degrees(REST, ranges), calibration=cal, limits=limits, ranges=ranges
		)
		if rest.ok:
			run_path(arm, rest.path, ranges, None)
			say("cycle done: the arm is at rest")
		else:
			say(f"cycle done; not returning to rest: {rest.reason}")


if __name__ == "__main__":
	main()
