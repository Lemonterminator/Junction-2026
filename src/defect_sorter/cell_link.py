"""The dashboard's link to the real cell: the hybrid sort cycle, its inspection views, and the table seen in depth.

* :class:`CycleRun` runs one ``sorter-hybrid`` cycle as a child process with ``--bowl auto --control stdio``
  (:class:`~defect_sorter.hybrid.ControlChannel`). Its events become timed steps for the page. When the arm holds the
  brick still in a show view, the cycle asks for that view to be inspected (a fresh front-camera frame); after the show
  it asks for the bowl, which :func:`decide_bowl` chooses from all views, or a person chooses on the page when the
  views are not clear. STOP is a line on the child's stdin and then the end of its stdin, which the child turns into
  the Ctrl+C path (a scripted move holds the present position, a policy run sets control to None); SIGINT follows
  if the child has not ended after a grace period. Nothing is ever retried or restarted here.
* :class:`TableWatcher` reads the depth bridge's raw frames while someone looks and measures the table with the same
  functions the cycle uses (:func:`measure_frame`): bowl rims and loose bricks in the table frame, objects in each
  bowl, and an annotated picture. It only reads.
* :class:`CellHub` is what the dashboard serves: at most one cycle, the start rules (a moving cycle needs
  ``--cell-control`` on the dashboard's command line; a dry run does not), and the drop check against the table
  (:func:`verify_drop`).
"""

from __future__ import annotations

import collections
import contextlib
import json
import logging
import signal
import subprocess
import threading
import time
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import TYPE_CHECKING, Any

import numpy as np

if TYPE_CHECKING:
	from defect_sorter.alignment import TableFrame
	from defect_sorter.depth_bridge import RawFrame
	from defect_sorter.geometry import Intrinsics, Plane
	from defect_sorter.scene import SceneConfig

logger = logging.getLogger(__name__)

BOWLS = ("green", "pink")
FINAL_PHASES = ("done", "failed", "stopped", "held")
_OWN_FLAGS = ("--go", "--bowl", "--control")


# ------------------------------------------------------------------------------------------------ decisions


def decide_bowl(views: Sequence[Mapping[str, Any]], *, min_views: int = 2) -> dict[str, Any]:
	"""The bowl for a brick from the inspections of its show views.

	A defect seen in any view rejects the brick (pink): a defect is often visible from one side only. Green needs at
	least ``min_views`` scored views and every one of them clearly normal. A view scored inside the uncertain band,
	or too few scored views (the brick was not found in the frame), leaves the bowl to a person (``bowl`` None).

	Returns
	-------
	dict
		``bowl`` (green, pink or None), ``label`` (normal, defective or uncertain), ``score`` (the highest score of
		the scored views, None without any) and ``reason``.
	"""
	scored = [v for v in views if isinstance(v.get("score"), int | float)]
	score = max((float(v["score"]) for v in scored), default=None)
	defective = [v["name"] for v in scored if v.get("label") == "defective"]
	if defective:
		return {
			"bowl": "pink",
			"label": "defective",
			"score": score,
			"reason": f"defect seen in {', '.join(defective)}",
		}
	unsure = [v["name"] for v in scored if v.get("label") != "normal"]
	if unsure:
		return {
			"bowl": None,
			"label": "uncertain",
			"score": score,
			"reason": f"unsure in {', '.join(unsure)}: a person decides",
		}
	if len(scored) < min_views:
		return {
			"bowl": None,
			"label": "uncertain",
			"score": score,
			"reason": f"brick scored in {len(scored)} of {min_views} views needed: a person decides",
		}
	return {"bowl": "green", "label": "normal", "score": score, "reason": f"normal in all {len(scored)} views"}


def verify_drop(before: Mapping[str, int] | None, after: Mapping[str, int] | None, bowl: str) -> dict[str, Any]:
	"""Whether the top camera sees one more object in ``bowl`` after the drop than before the cycle.

	``confirmed`` is None when either table reading is missing: nothing is claimed without evidence. Touching bricks
	can merge into one object, so a missing confirmation is reported as such, not as a failed drop.
	"""
	if before is None or after is None:
		return {"confirmed": None, "text": "not checked: no table reading from the top camera"}
	gained = {c: after.get(c, 0) - before.get(c, 0) for c in set(before) | set(after)}
	if gained.get(bowl, 0) > 0:
		return {"confirmed": True, "text": f"the top camera sees one more object in the {bowl} bowl"}
	others = [c for c, n in gained.items() if c != bowl and n > 0]
	if others:
		return {"confirmed": False, "text": f"nothing new in the {bowl} bowl, but one more in the {others[0]} bowl"}
	return {"confirmed": False, "text": f"no new object seen in the {bowl} bowl"}


# ------------------------------------------------------------------------------------------------ cycle


def _spawn(argv: list[str]) -> subprocess.Popen[str]:
	# Same process group as the dashboard: a Ctrl+C in the operator's terminal also stops the cycle.
	return subprocess.Popen(  # noqa: S603 - the operator's configured command
		argv,
		stdin=subprocess.PIPE,
		stdout=subprocess.PIPE,
		stderr=subprocess.PIPE,
		text=True,
		bufsize=1,
	)


class CycleRun:
	"""One supervised ``sorter-hybrid`` cycle.

	Parameters
	----------
	command : sequence of str
		The cycle command without ``--go``, ``--bowl`` and ``--control``, which the dashboard adds.
	go : bool
		Add ``--go`` (the arm moves); otherwise the cycle measures and plans only.
	inspect_view : callable
		View name to an inspection result (``label``, ``score``, ``reason``, optional ``timings_ms`` and
		``crop_jpeg``) of a front-camera frame taken while the arm holds still. It may raise; the view then counts
		as not scored.
	spawn : callable
		argv to a process with ``stdin``, ``stdout``, ``stderr``, ``poll``, ``wait`` and ``send_signal``.
	background : bool
		Read the child's output on threads; tests call :meth:`feed` and :meth:`finish` directly.
	clock : callable
		Wall clock in Unix seconds.
	on_end : callable or None
		Called once with this run when the child has exited.
	min_views : int
		Scored views needed before :func:`decide_bowl` passes a brick without a person.
	preset_bowl : str or None
		A bowl the operator's command already named: the views are still inspected and shown, then this bowl is
		used (``source`` "command") whatever they say.
	unsure_bowl : {"pink", None}
		Where an unsure brick goes without asking (``source`` "rule"); None waits for a person. Only the reject bowl
		is allowed: an unsure brick is never passed as good.
	"""

	def __init__(
		self,
		command: Sequence[str],
		*,
		go: bool,
		inspect_view: Callable[[str], Mapping[str, Any]],
		spawn: Callable[[list[str]], Any] = _spawn,
		background: bool = True,
		clock: Callable[[], float] = time.time,
		on_end: Callable[[CycleRun], None] | None = None,
		min_views: int = 2,
		log_lines: int = 80,
		preset_bowl: str | None = None,
		unsure_bowl: str | None = None,
	) -> None:
		if preset_bowl is not None and preset_bowl not in BOWLS:
			raise ValueError(f"no such bowl: {preset_bowl!r}")
		if unsure_bowl not in (None, "pink"):
			raise ValueError(f"an unsure brick goes to pink or waits for a person, not {unsure_bowl!r}")
		self.preset_bowl = preset_bowl
		self.unsure_bowl = unsure_bowl
		own = [a for a in command if a.split("=")[0] in _OWN_FLAGS]
		if own:
			raise ValueError(f"the cycle command must not contain {', '.join(own)}: the dashboard adds those")
		self.argv = [*command, "--bowl", "auto", "--control", "stdio", *(["--go"] if go else [])]
		self.go = go
		self._inspect = inspect_view
		self._spawn = spawn
		self._background = background
		self._clock = clock
		self._on_end = on_end
		self.min_views = min_views
		self._lock = threading.Lock()
		self._write_lock = threading.Lock()
		self._proc: Any = None
		self.started_at: float | None = None
		self.ended_at: float | None = None
		self.phase = "starting"
		self.steps: list[dict[str, Any]] = []
		self.log: collections.deque[dict[str, Any]] = collections.deque(maxlen=log_lines)
		self.bowls: dict[str, Any] | None = None
		self.brick: dict[str, Any] | None = None
		self.attempt: int | None = None
		self.views: list[dict[str, Any]] = []
		self._crops: list[bytes | None] = []
		self.decision: dict[str, Any] | None = None
		self._awaiting: str | None = None
		self.end: dict[str, Any] | None = None
		self.stop_requested = False
		self.released_bowl: str | None = None
		self.verify: dict[str, Any] | None = None
		self._finished = False

	# -- process ----------------------------------------------------------------------------------
	def start(self) -> None:
		"""Start the child and, in the background, read its output until it exits.

		Raises
		------
		OSError
			When the command cannot be started; the run is then failed with that reason (nothing ran).
		"""
		self.started_at = self._clock()
		try:
			self._proc = self._spawn(self.argv)
		except OSError as error:
			with self._lock:
				self._finished = True
				self.ended_at = self._clock()
				self.phase = "failed"
				self.end = {"ok": False, "reason": f"could not start the cycle: {error}"}
			raise
		if not self._background:
			return

		def read_stdout() -> None:
			for line in self._proc.stdout:
				self.feed(line)
			self.finish(self._proc.wait())

		def read_stderr() -> None:
			for line in self._proc.stderr:
				self._log(line.rstrip())

		threading.Thread(target=read_stdout, name="cycle-stdout", daemon=True).start()
		threading.Thread(target=read_stderr, name="cycle-stderr", daemon=True).start()

	@property
	def active(self) -> bool:
		"""Whether the child may still hold the arm (it has not exited)."""
		return self._proc is not None and not self._finished

	@property
	def decided_bowl(self) -> str | None:
		"""The bowl the brick was released over, as the cycle reported it."""
		return self.released_bowl

	def _reply(self, message: dict[str, Any]) -> None:
		with self._write_lock:
			try:
				self._proc.stdin.write(json.dumps(message) + "\n")
				self._proc.stdin.flush()
			except (OSError, ValueError, AttributeError):
				logger.warning("cycle input closed; %s not delivered", message)

	def stop(self) -> dict[str, bool]:
		"""Ask the cycle to hold the arm and end: a stop line, then the end of its input; always allowed."""
		if not self.active:
			return {"stopping": False}
		self.stop_requested = True
		self._log("STOP requested from the dashboard")
		self._reply({"command": "stop"})
		with self._write_lock, contextlib.suppress(OSError):
			self._proc.stdin.close()
		if self._background:
			threading.Thread(target=self.enforce_stop, name="cycle-stop", daemon=True).start()
		return {"stopping": True}

	def enforce_stop(self, grace_s: float = 15.0) -> None:
		"""SIGINT to a child that has not exited ``grace_s`` after a stop (it takes the same Ctrl+C path).

		The grace is longer than a policy run takes to set control to None (up to 10 s): a second SIGINT during that
		would cut the release short. Through ``docker exec`` the signal reaches only the client; the end of stdin is
		what stops the cycle there.
		"""
		try:
			self._proc.wait(timeout=grace_s)
		except subprocess.TimeoutExpired:
			logger.warning("cycle still running %.1f s after STOP: sending SIGINT", grace_s)
			self._proc.send_signal(signal.SIGINT)

	# -- events -----------------------------------------------------------------------------------
	def _log(self, text: str) -> None:
		if not text:
			return
		with self._lock:
			self.log.append({"t": self._clock(), "text": text})

	def feed(self, line: str) -> None:
		"""Take one line of the child's stdout: an event, or plain output kept in the log."""
		try:
			message = json.loads(line)
		except ValueError:
			message = None
		if not isinstance(message, dict) or "event" not in message:
			self._log(line.rstrip())
			return
		kind = message["event"]
		if kind == "log":
			self._log(str(message.get("text", "")))
		elif kind == "phase":
			self._phase(message)
		elif kind == "bowls":
			self.bowls = message.get("bowls")
		elif kind == "brick":
			self.brick = {k: message.get(k) for k in ("centre_mm", "yaw_deg", "size_mm")}
			self.attempt = message.get("attempt")
		elif kind == "view":
			self._inspect_view(str(message.get("id")), str(message.get("name")))
		elif kind == "decide":
			self._decide(str(message.get("id")))
		elif kind == "end":
			self.end = {"ok": bool(message.get("ok")), "reason": message.get("reason")}

	def _phase(self, message: dict[str, Any]) -> None:
		name = str(message.get("name"))
		fields = {k: v for k, v in message.items() if k not in ("event", "t", "name")}
		with self._lock:
			self.phase = name
			self.steps.append({"name": name, "at": self._clock(), "fields": fields})
			if name in ("hover", "grasp", "missed") and "attempt" in fields:
				self.attempt = fields["attempt"]
			if name == "released":
				self.released_bowl = fields.get("bowl")

	def _inspect_view(self, qid: str, name: str) -> None:
		try:
			result = dict(self._inspect(name))
		except Exception as error:  # a failed view is a missing view, never a crash of the cycle
			logger.warning("view %s not inspected: %s", name, error)
			result = {"label": "uncertain", "score": None, "reason": f"inspection failed: {error}"}
		crop = result.get("crop_jpeg")
		record = {
			"name": name,
			"label": result.get("label", "uncertain"),
			"score": result.get("score"),
			"reason": result.get("reason"),
			"timings_ms": result.get("timings_ms"),
			"cameras": result.get("cameras"),
			"crop": crop is not None,
		}
		with self._lock:
			self.views.append(record)
			self._crops.append(crop)
		self._reply({"reply": qid})

	def _decide(self, qid: str) -> None:
		with self._lock:
			decision = decide_bowl(self.views, min_views=self.min_views) | {"source": "inspection"}
			if self.preset_bowl is not None:
				decision |= {"bowl": self.preset_bowl, "source": "command"}
			elif decision["bowl"] is None and self.unsure_bowl is not None:
				decision |= {
					"bowl": self.unsure_bowl,
					"source": "rule",
					"reason": f"{decision['reason']}; unsure goes to {self.unsure_bowl}",
				}
			self.decision = decision
			if decision["bowl"] is None:
				self._awaiting = qid
				self.phase = "review"
		if decision["bowl"] is not None:
			self._reply({"reply": qid, "bowl": decision["bowl"], "source": decision["source"]})

	def review(self, bowl: str | None) -> tuple[int, dict[str, Any]]:
		"""The operator's choice for a brick the inspection left open: green, pink, or None to keep holding it."""
		if bowl is not None and bowl not in BOWLS:
			return 400, {"error": f"choose green, pink or none, not {bowl!r}"}
		with self._lock:
			qid, self._awaiting = self._awaiting, None
			if qid is None:
				return 409, {"error": "no decision is waiting for a person"}
			self.decision = (self.decision or {}) | {"bowl": bowl, "source": "operator"}
		self._log(f"operator chose {bowl or 'to hold the brick'}")
		self._reply({"reply": qid, "bowl": bowl, "source": "operator"})
		return 200, {"bowl": bowl}

	def finish(self, returncode: int | None) -> None:
		"""The child exited: the final phase from its report, then ``on_end`` (once)."""
		with self._lock:
			if self._finished:
				return
			self._finished = True
			self._awaiting = None
			self.ended_at = self._clock()
			if self.end is None:
				self.end = {"ok": False, "reason": f"the cycle exited with code {returncode} without a report"}
			reason = str(self.end.get("reason") or "")
			if self.end["ok"]:
				self.phase = "done"
			elif reason.startswith("held for review"):
				self.phase = "held"
			elif self.stop_requested or returncode == 130:
				self.phase = "stopped"
			else:
				self.phase = "failed"
		if self._on_end is not None:
			self._on_end(self)

	def set_verify(self, result: dict[str, Any]) -> None:
		"""Keep the drop check made after the cycle."""
		self.verify = result

	# -- view -------------------------------------------------------------------------------------
	def view_crop(self, index: int) -> bytes | None:
		"""The scored crop of view ``index``, if it had one."""
		with self._lock:
			return self._crops[index] if 0 <= index < len(self._crops) else None

	def snapshot(self) -> dict[str, Any]:
		"""JSON-ready state for the page; times are seconds since the cycle started."""
		with self._lock:
			t0 = self.started_at or self._clock()
			end = self.ended_at if self.ended_at is not None else self._clock()
			steps = []
			for i, step in enumerate(self.steps):
				until = self.steps[i + 1]["at"] if i + 1 < len(self.steps) else self.ended_at
				steps.append(
					{
						**step["fields"],
						"name": step["name"],
						"at_s": round(step["at"] - t0, 2),
						"seconds": None if until is None else round(until - step["at"], 2),
					}
				)
			return {
				"id": None if self.started_at is None else round(self.started_at * 1000),
				"active": self.active,
				"go": self.go,
				"phase": self.phase,
				"seconds": round(end - t0, 2),
				"steps": steps,
				"log": [{"t_s": round(e["t"] - t0, 2), "text": e["text"]} for e in self.log],
				"bowls": self.bowls,
				"brick": self.brick,
				"attempt": self.attempt,
				"views": [dict(v) for v in self.views],
				"decision": self.decision,
				"awaiting_review": self._awaiting is not None,
				"released_bowl": self.released_bowl,
				"end": self.end,
				"stop_requested": self.stop_requested,
				"verify": self.verify,
				"preset_bowl": self.preset_bowl,
			}


# ------------------------------------------------------------------------------------------------ table


_DRAW = {"green": (70, 200, 70), "pink": (190, 110, 255)}


def _scene_reading(
	color_bgr: np.ndarray,
	depth_m: np.ndarray,
	intrinsics: Intrinsics,
	plane: Plane,
	table: TableFrame | None,
	*,
	config: SceneConfig | None = None,
	exclude_xy_m: np.ndarray | None = None,
) -> tuple[dict[str, Any], Any, list[tuple[Any, str]]]:
	"""Reading, scene and (object, label) pairs for the picture; table positions only with a table frame."""
	from defect_sorter.scene import PAPER_CELL, detect_scene
	from defect_sorter.targeting import bowl_pose, brick_pose, select_brick

	scene = detect_scene(color_bgr, depth_m, intrinsics, plane=plane, config=config or PAPER_CELL)
	labels: list[tuple[Any, str]] = []
	reading: dict[str, Any] = {"bowls": [], "bricks": [], "in_bowl": None}
	if table is None:
		return reading, scene, labels
	for bowl in scene.bowls:
		pose = bowl_pose(bowl, scene, depth_m, intrinsics, table)
		if pose is not None:
			reading["bowls"].append(
				{
					"colour": pose.colour,
					"centre_mm": [round(float(v) * 1000, 1) for v in pose.centre_m],
					"radius_mm": round(pose.radius_m * 1000, 1),
				}
			)
	for obj in scene.objects:
		if obj.in_bowl is not None:
			labels.append((obj, f"in {obj.in_bowl}"))
			continue
		pose = brick_pose(obj, scene, depth_m, intrinsics, table)
		if pose is None or select_brick([pose], exclude_xy_m=exclude_xy_m)[0] is None:
			labels.append((obj, "not a brick"))
			continue
		centre = [round(float(v) * 1000, 1) for v in pose.centre_m]
		reading["bricks"].append(
			{
				"centre_mm": centre,
				"yaw_deg": round(pose.yaw_deg, 1),
				"size_mm": [round(pose.length_m * 1000, 1), round(pose.width_m * 1000, 1)],
			}
		)
		labels.append((obj, f"brick {centre[0]:.0f}, {centre[1]:.0f}"))
	colours = {b.colour for b in scene.bowls} | {b["colour"] for b in reading["bowls"]}
	reading["in_bowl"] = {c: sum(1 for o in scene.objects if o.in_bowl == c) for c in sorted(colours)}
	return reading, scene, labels


def read_scene(
	color_bgr: np.ndarray,
	depth_m: np.ndarray,
	intrinsics: Intrinsics,
	plane: Plane,
	table: TableFrame,
	*,
	config: SceneConfig | None = None,
	exclude_xy_m: np.ndarray | None = None,
) -> dict[str, Any]:
	"""Bowls, loose bricks and objects per bowl of one top-camera frame, table-frame millimetres.

	Bowl rims come from :func:`~defect_sorter.targeting.bowl_pose`, bricks from
	:func:`~defect_sorter.targeting.brick_pose` with the same size and robot-base rules the cycle uses
	(:func:`~defect_sorter.targeting.select_brick`, ``exclude_xy_m`` being the robot base).
	"""
	return _scene_reading(color_bgr, depth_m, intrinsics, plane, table, config=config, exclude_xy_m=exclude_xy_m)[0]


def _picture(
	color_bgr: np.ndarray, scene: Any, labels: list[tuple[Any, str]], markers: list[Any], note: str | None
) -> bytes:
	import cv2

	def text(
		img: np.ndarray, words: str, org: tuple[int, int], colour: tuple[int, int, int], scale: float = 0.5
	) -> None:
		# a dark outline keeps a label readable on any background, including a bowl of its own colour
		cv2.putText(img, words, org, cv2.FONT_HERSHEY_SIMPLEX, scale, (0, 0, 0), 4, cv2.LINE_AA)
		cv2.putText(img, words, org, cv2.FONT_HERSHEY_SIMPLEX, scale, colour, 1, cv2.LINE_AA)

	img = np.ascontiguousarray(color_bgr).copy()
	for bowl in scene.bowls:
		(u, v), (a, b), angle = bowl.ellipse
		colour = _DRAW.get(bowl.colour, (255, 255, 255))
		cv2.ellipse(img, ((u, v), (a, b), angle), colour, 2, cv2.LINE_AA)
		text(img, bowl.colour, (int(u) - 22, int(v) + 5), (255, 255, 255), 0.6)
	for obj, words in labels:
		x, y, w, h = obj.bbox
		colour = _DRAW.get(obj.in_bowl or "", (0, 215, 255) if words.startswith("brick") else (160, 160, 160))
		cv2.rectangle(img, (x, y), (x + w, y + h), colour, 2)
		text(img, words, (x, max(14, y - 6)), colour)
	for marker in markers:
		corners = np.asarray(marker.corners_px, dtype=np.int32).reshape(-1, 1, 2)
		cv2.polylines(img, [corners], True, (255, 200, 0), 2, cv2.LINE_AA)
		text(img, str(marker.id), tuple(int(c) for c in corners[0, 0]), (255, 200, 0), 0.45)
	if note:
		cv2.rectangle(img, (0, 0), (img.shape[1], 22), (0, 0, 0), -1)
		cv2.putText(img, note, (6, 16), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (80, 170, 255), 1, cv2.LINE_AA)
	ok, encoded = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, 80])
	return encoded.tobytes() if ok else b""


def measure_frame(
	raw: RawFrame,
	*,
	anchors: tuple[int, int] = (16, 17),
	frame_file: Path | None = None,
	exclude_xy_m: np.ndarray | None = None,
	robot_base_mm: list[float] | None = None,
) -> tuple[dict[str, Any], bytes]:
	"""Measure one raw bridge frame as the cycle does, and draw what was found.

	The table frame comes from anchors ``anchors``, or from ``frame_file`` while one is hidden and the fixed markers
	show the camera has not moved (:func:`~defect_sorter.alignment.held_table_frame`). Without a table frame there
	are no table positions (``table`` None, ``reason`` says why), only the picture.

	Returns
	-------
	tuple of (dict, bytes)
		The reading (``frame_id``, ``table``, ``reason``, ``markers``, ``bowls``, ``bricks``, ``in_bowl``,
		``robot_base_mm``, ``measure_ms``) and the annotated JPEG.
	"""
	from defect_sorter.alignment import held_table_frame, load_table_frame, refine_with_depth, table_frame
	from defect_sorter.geometry import Intrinsics, deproject, fit_table_plane
	from defect_sorter.markers import detect_markers

	t0 = time.perf_counter()
	color, depth, i = raw.color_bgr, raw.depth_m, raw.intrinsics
	pts = deproject(depth[::4, ::4], Intrinsics(i.fx / 4, i.fy / 4, i.ppx / 4, i.ppy / 4))
	plane = fit_table_plane(pts[pts[..., 2] > 0])
	detections = detect_markers(color, i)
	markers = {d.id: refine_with_depth(d, depth, i) for d in detections}
	table = table_frame(plane, markers, anchors=anchors)
	if not table.basis.startswith("anchors") and frame_file is not None and frame_file.exists():
		table = held_table_frame(*load_table_frame(frame_file), markers) or table
	anchored = table.basis.startswith("anchors")
	reason = None if anchored else f"anchors {anchors[0]} and {anchors[1]} not seen (saw {sorted(markers)})"
	reading, scene, labels = _scene_reading(
		color, depth, i, plane, table if anchored else None, exclude_xy_m=exclude_xy_m
	)
	reading.update(
		frame_id=raw.frame_id,
		table=table.basis if anchored else None,
		reason=reason,
		markers=sorted(markers),
		robot_base_mm=robot_base_mm,
	)
	jpeg = _picture(color, scene, labels, detections, None if anchored else f"no table frame: {reason}")
	reading["measure_ms"] = round((time.perf_counter() - t0) * 1000, 1)
	return reading, jpeg


class TableWatcher:
	"""Measure the table from the depth bridge about once a second while someone is looking.

	Parameters
	----------
	fetch : callable
		The newest raw frame (:func:`~defect_sorter.depth_bridge.fetch_raw` bound to the bridge's address).
	measure : callable
		Raw frame to (reading, JPEG), normally :func:`measure_frame` with the cell's settings.
	clock : callable
		Wall clock in Unix seconds.
	idle_s : float
		Stop reading when nobody asked for this long.
	period_s : float
		Time between reads while watched.
	"""

	def __init__(
		self,
		fetch: Callable[[], RawFrame],
		measure: Callable[[RawFrame], tuple[dict[str, Any], bytes]],
		*,
		clock: Callable[[], float] = time.time,
		idle_s: float = 20.0,
		period_s: float = 1.0,
	) -> None:
		self._fetch = fetch
		self._measure = measure
		self._clock = clock
		self.idle_s = idle_s
		self.period_s = period_s
		self._lock = threading.Lock()
		self._requested_at = float("-inf")
		self._reading: dict[str, Any] | None = None
		self._jpeg: bytes | None = None
		self._read_at: float | None = None
		self.status = "idle"
		self.error: str | None = None
		self._stop = threading.Event()
		self._thread: threading.Thread | None = None

	def _touch(self) -> None:
		with self._lock:
			self._requested_at = self._clock()

	def wanted(self) -> bool:
		"""Whether someone asked within ``idle_s``."""
		return self._clock() - self._requested_at <= self.idle_s

	def _read(self) -> dict[str, Any]:
		reading, jpeg = self._measure(self._fetch())
		with self._lock:
			self._reading, self._jpeg, self._read_at = reading, jpeg, self._clock()
			self.status, self.error = "live", None
		return reading

	def read_once(self) -> None:
		"""Read and measure one frame; a failure keeps the last reading and reports the error."""
		try:
			self._read()
		except Exception as error:  # a bridge restart or a bad frame must not end the watcher
			with self._lock:
				self.status, self.error = "error", str(error)

	def counts_now(self) -> dict[str, int] | None:
		"""Objects per bowl in a fresh frame, or None when it cannot be read or has no table frame."""
		try:
			return self._read().get("in_bowl")
		except Exception as error:
			logger.warning("table reading failed: %s", error)
			return None

	def state(self) -> dict[str, Any]:
		"""Status, error, the newest reading and its age; asking keeps the watcher reading."""
		self._touch()
		with self._lock:
			age = None if self._read_at is None else round((self._clock() - self._read_at) * 1000)
			return {"status": self.status, "error": self.error, "reading": self._reading, "age_ms": age}

	def jpeg(self) -> bytes | None:
		"""The newest annotated picture; asking keeps the watcher reading."""
		self._touch()
		with self._lock:
			return self._jpeg

	def start(self) -> None:
		"""Read in a background thread while watched."""
		if self._thread is not None:
			return

		def loop() -> None:
			while not self._stop.is_set():
				if self.wanted():
					self.read_once()
					self._stop.wait(self.period_s)
				else:
					self._stop.wait(0.2)

		self._thread = threading.Thread(target=loop, name="table-watcher", daemon=True)
		self._thread.start()

	def stop(self) -> None:
		"""Stop the background thread."""
		self._stop.set()


# ------------------------------------------------------------------------------------------------ hub


class CellHub:
	"""The dashboard's view of the cell: the table, and at most one hybrid cycle.

	Parameters
	----------
	hybrid_command : sequence of str or None
		The cycle command (see :class:`CycleRun`); None when the dashboard was started without one.
	control_enabled : bool
		Whether a cycle may move the arm (``--go``). Set only by the operator's command line, never by a request.
	table : TableWatcher or None
		The depth bridge reader.
	inspect_view : callable or None
		Inspection of one show view (see :class:`CycleRun`); without it every brick waits for a person.
	run_factory : callable
		Builds the run (``CycleRun`` signature).
	busy : callable
		True while something else drives the arm (a Studio run from the dashboard).
	keepalive : callable or None
		Called on every state request while a cycle runs (keeps the inspection camera connected).
	background : bool
		Verify the drop on a thread after a short wait; tests verify at once.
	verify_delay_s : float
		Wait after the cycle before reading the table again (the brick settles, the arm leaves the view).
	inspector_info : dict or None
		``model``, ``device`` and ``thresholds`` (the page's scale) of the view inspector, shown on the page.
	unsure_bowl : {"pink", None}
		See :class:`CycleRun`.
	"""

	def __init__(
		self,
		*,
		hybrid_command: Sequence[str] | None,
		control_enabled: bool,
		table: TableWatcher | None,
		inspect_view: Callable[[str], Mapping[str, Any]] | None,
		run_factory: Callable[..., Any] = CycleRun,
		busy: Callable[[], bool] = lambda: False,
		keepalive: Callable[[], None] | None = None,
		background: bool = True,
		verify_delay_s: float = 1.5,
		inspector_info: Mapping[str, Any] | None = None,
		unsure_bowl: str | None = None,
	) -> None:
		if unsure_bowl not in (None, "pink"):
			raise ValueError(f"an unsure brick goes to pink or waits for a person, not {unsure_bowl!r}")
		self.unsure_bowl = unsure_bowl
		self.inspector_info = dict(inspector_info or {"model": "view inspector", "device": None, "thresholds": None})
		self.hybrid_command = list(hybrid_command) if hybrid_command else None
		self.control_enabled = control_enabled
		self.table = table
		self.inspect_view = inspect_view
		self._factory = run_factory
		self._busy = busy
		self._keepalive = keepalive
		self._background = background
		self.verify_delay_s = verify_delay_s
		self._lock = threading.Lock()
		self.run: Any = None

	def active(self) -> bool:
		"""Whether a cycle may still hold the arm."""
		return self.run is not None and bool(self.run.active)

	def state(self) -> dict[str, Any]:
		"""JSON-ready summary for the page."""
		if self._keepalive is not None and self.active():
			self._keepalive()
		return {
			"configured": self.hybrid_command is not None,
			"control_enabled": self.control_enabled,
			"inspector": self.inspector_info if self.inspect_view is not None else None,
			"unsure_bowl": self.unsure_bowl,
			"table": None if self.table is None else self.table.state(),
			"cycle": None if self.run is None else self.run.snapshot(),
		}

	def _inspect(self, name: str) -> Mapping[str, Any]:
		if self.inspect_view is None:
			return {"label": "uncertain", "score": None, "reason": "no inspector configured"}
		return self.inspect_view(name)

	def start(self, request: Mapping[str, Any]) -> tuple[int, dict[str, Any]]:
		"""Start one cycle; ``{"go": true}`` moves the arm and needs control, anything else is a dry run.

		``bowl`` (green or pink) names the bowl up front; without it the inspection, or a person, chooses.
		"""
		if self.hybrid_command is None:
			return 409, {"error": "no hybrid cycle configured; start the dashboard with --hybrid-command"}
		go = request.get("go") is True
		bowl = request.get("bowl")
		if bowl is not None and bowl not in BOWLS:
			return 400, {"error": f"no such bowl: {bowl!r}"}
		if go and not self.control_enabled:
			return 403, {"error": "arm control is off; restart the dashboard with --cell-control to run the cycle"}
		with self._lock:
			if self.active():
				return 409, {"error": "a cycle is already running"}
			if self._busy():
				return 409, {"error": "a Studio run is active; stop it first"}
			before = None if self.table is None else self.table.counts_now()
			try:
				run = self._factory(
					self.hybrid_command,
					go=go,
					inspect_view=self._inspect,
					on_end=lambda r: self._ended(r, before),
					preset_bowl=bowl,
					unsure_bowl=self.unsure_bowl,
				)
			except ValueError as error:
				return 409, {"error": str(error)}
			self.run = run
			try:
				run.start()
			except OSError as error:
				logger.error("hybrid cycle did not start: %s", error)
				return 502, {"error": f"could not start the cycle: {error}"}
		return 202, {"go": go, "bowl": bowl}

	def _ended(self, run: Any, before: dict[str, int] | None) -> None:
		bowl = getattr(run, "decided_bowl", None)
		if self.table is None or bowl is None:
			return

		def check() -> None:
			if self._background:
				time.sleep(self.verify_delay_s)
			run.set_verify(verify_drop(before, self.table.counts_now(), bowl))

		if self._background:
			threading.Thread(target=check, name="cycle-verify", daemon=True).start()
		else:
			check()

	def stop(self) -> dict[str, bool]:
		"""Stop the running cycle, if any; always allowed."""
		run = self.run
		if run is None or not run.active:
			return {"stopping": False}
		return run.stop()

	def review(self, body: Mapping[str, Any]) -> tuple[int, dict[str, Any]]:
		"""Pass the operator's bowl choice to a cycle waiting for one."""
		if self.run is None:
			return 409, {"error": "no cycle is running"}
		bowl = body.get("bowl")
		return self.run.review(None if bowl in (None, "hold", "none") else str(bowl))

	def table_jpeg(self) -> bytes | None:
		"""The newest annotated top-camera picture."""
		return None if self.table is None else self.table.jpeg()

	def view_crop(self, index: int) -> bytes | None:
		"""The scored crop of one view of the current cycle."""
		return None if self.run is None or not hasattr(self.run, "view_crop") else self.run.view_crop(index)
