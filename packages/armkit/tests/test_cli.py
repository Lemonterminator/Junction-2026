import io
import json

import pytest
import test_procedure
from armkit import cli
from armkit.calibration import Calibration
from test_procedure import arm, profile


def _frame_file(tmp_path):
	from armkit.frame import ModelFrame

	path = tmp_path / "frame.json"
	ModelFrame.trusted({"a": 0.0, "b": 0.0}, "toy").save(path)
	return path


def profile_with_shapes():
	return profile(test_procedure.TestCollisionAwareness.SHAPES)


@pytest.fixture
def toy(monkeypatch):
	"""The toy arm as the only profile, a simulated bus instead of a serial port, and a recorder for bus opening."""
	bus = arm()
	opened = []
	monkeypatch.setitem(cli.PROFILES, "toy", profile)

	def open_bus(port, prof, acceleration):
		opened.append(port)
		return bus

	monkeypatch.setattr(cli, "_open_bus", open_bus)
	return bus, opened


def run(monkeypatch, capsys, argv, stdin=""):
	monkeypatch.setattr("sys.stdin", io.StringIO(stdin))
	code = cli.main(argv)
	return code, capsys.readouterr().out


class TestPlan:
	def test_plan_prints_the_sweeps_and_never_opens_a_port(self, toy, monkeypatch, capsys):
		_, opened = toy
		code, out = run(monkeypatch, capsys, ["plan", "--profile", "toy"])
		assert code == 0
		assert "b: upper end" in out
		assert "a: lower end" in out
		assert opened == []

	def test_run_without_go_is_a_dry_run(self, toy, monkeypatch, capsys, tmp_path):
		_, opened = toy
		code, out = run(
			monkeypatch, capsys, ["run", "--profile", "toy", "--port", "/dev/x", "--out", str(tmp_path / "c.json")]
		)
		assert code == 0
		assert "dry run" in out
		assert opened == []
		assert not (tmp_path / "c.json").exists()

	def test_an_unknown_profile_is_an_error(self, toy, monkeypatch, capsys):
		with pytest.raises(SystemExit):
			run(monkeypatch, capsys, ["plan", "--profile", "nope"])


class TestRun:
	def test_a_confirmed_run_saves_the_backup_first_and_then_the_new_calibration(
		self, toy, monkeypatch, capsys, tmp_path
	):
		bus, _ = toy
		before = bus.read_calibration()
		out_file, backup = tmp_path / "new.json", tmp_path / "old.json"
		code, out = run(
			monkeypatch,
			capsys,
			["run", "--profile", "toy", "--port", "/dev/x", "--go", "--out", str(out_file), "--backup", str(backup)],
			stdin="YES\nYES\n",
		)
		assert code == 0, out
		assert Calibration.load(backup) == before
		assert Calibration.load(out_file) == bus.read_calibration()
		assert json.loads(out_file.read_text())["a"]["range_max"] > json.loads(out_file.read_text())["a"]["range_min"]

	def test_anything_but_yes_aborts_without_touching_the_servos(self, toy, monkeypatch, capsys, tmp_path):
		bus, _ = toy
		before = bus.read_calibration()
		code, _ = run(
			monkeypatch,
			capsys,
			[
				"run",
				"--profile",
				"toy",
				"--port",
				"/dev/x",
				"--go",
				"--out",
				str(tmp_path / "n.json"),
				"--backup",
				str(tmp_path / "o.json"),
			],
			stdin="no\n",
		)
		assert code != 0
		assert bus.read_calibration() == before
		assert not (tmp_path / "n.json").exists()


class TestRestore:
	def test_restore_writes_a_saved_calibration_with_torque_off_after_confirmation(
		self, toy, monkeypatch, capsys, tmp_path
	):
		bus, _ = toy
		saved = bus.read_calibration()
		path = tmp_path / "old.json"
		saved.save(path)
		bus.joint("a").offset = 999  # pretend a failed run left a temporary frame behind
		code, out = run(
			monkeypatch,
			capsys,
			["restore", "--profile", "toy", "--port", "/dev/x", "--go", "--from", str(path)],
			stdin="YES\n",
		)
		assert code == 0, out
		assert bus.read_calibration() == saved

	def test_restore_without_go_only_describes_what_it_would_do(self, toy, monkeypatch, capsys, tmp_path):
		bus, opened = toy
		path = tmp_path / "old.json"
		bus.read_calibration().save(path)
		code, out = run(monkeypatch, capsys, ["restore", "--profile", "toy", "--port", "/dev/x", "--from", str(path)])
		assert code == 0
		assert "dry run" in out
		assert opened == []


class TestSubsetFlag:
	def test_only_limits_the_plan_to_the_named_joints(self, toy, monkeypatch, capsys):
		code, out = run(monkeypatch, capsys, ["plan", "--profile", "toy", "--only", "b"])
		assert code == 0
		assert "b: upper end" in out
		assert "a: lower end" not in out


class TestCheck:
	def test_check_measures_one_joint_saves_a_backup_first_and_changes_nothing(
		self, toy, monkeypatch, capsys, tmp_path
	):
		bus, _ = toy
		before = bus.read_calibration()
		backup = tmp_path / "all.json"
		code, out = run(
			monkeypatch,
			capsys,
			[
				"check",
				"--profile",
				"toy",
				"--port",
				"/dev/x",
				"--joint",
				"a",
				"--go",
				"--backup",
				str(backup),
				"--frame",
				str(_frame_file(tmp_path)),
			],
			stdin="YES\n",
		)
		assert code == 0, out
		assert "lower" in out
		assert "upper" in out
		assert "stored" in out
		assert Calibration.load(backup) == before
		assert bus.read_calibration() == before

	def test_check_without_go_opens_no_port(self, toy, monkeypatch, capsys):
		_, opened = toy
		code, out = run(monkeypatch, capsys, ["check", "--profile", "toy", "--port", "/dev/x", "--joint", "a"])
		assert code == 0
		assert "dry run" in out
		assert opened == []

	def test_an_unknown_joint_is_refused(self, toy, monkeypatch, capsys):
		with pytest.raises(SystemExit):
			run(monkeypatch, capsys, ["check", "--profile", "toy", "--port", "/dev/x", "--joint", "zz"])


class TestMove:
	def _toy_at(self, monkeypatch, a_deg):
		from test_park import arm as park_arm

		bus, _ = park_arm(a_deg=a_deg)
		monkeypatch.setitem(cli.PROFILES, "toy", profile_with_shapes)
		monkeypatch.setattr(cli, "_open_bus", lambda port, prof, acceleration: bus)
		return bus

	def test_move_without_go_prints_the_plan_and_moves_nothing(self, monkeypatch, capsys):
		bus = self._toy_at(monkeypatch, 0.0)
		before = bus.read_positions()
		code, out = run(monkeypatch, capsys, ["move", "--profile", "toy", "--port", "/dev/x", "--set", "a=-89"])
		assert code == 0, out
		assert "plan ok" in out
		assert "closest approach" in out
		assert "dry run" in out
		assert "a:" in out
		assert bus.read_positions() == before

	def test_move_with_go_asks_and_then_moves(self, monkeypatch, capsys, tmp_path):
		bus = self._toy_at(monkeypatch, 0.0)
		code, out = run(
			monkeypatch,
			capsys,
			[
				"move",
				"--profile",
				"toy",
				"--port",
				"/dev/x",
				"--set",
				"a=-89",
				"--go",
				"--frame",
				str(_frame_file(tmp_path)),
			],
			stdin="YES\n",
		)
		assert code == 0, out
		assert bus.read_positions()["a"] == pytest.approx(2200 - 89 * 11.375, abs=20)

	def test_a_collision_is_reported_and_nothing_moves(self, monkeypatch, capsys):
		bus = self._toy_at(monkeypatch, -89.0)
		before = bus.read_positions()
		code, out = run(
			monkeypatch,
			capsys,
			["move", "--profile", "toy", "--port", "/dev/x", "--set", "a=0", "b=90", "--go"],
			stdin="YES\n",
		)
		assert code != 0
		assert "not ok" in out or "REFUSED" in out
		assert bus.read_positions() == before


class TestMeasure:
	def _toy(self, monkeypatch):
		from test_measure import arm as measure_arm

		bus = measure_arm()
		monkeypatch.setitem(cli.PROFILES, "toy", profile_with_shapes)
		monkeypatch.setattr(cli, "_open_bus", lambda port, prof, acceleration: bus)
		return bus

	def test_measure_without_go_lists_the_order_and_moves_nothing(self, monkeypatch, capsys):
		bus = self._toy(monkeypatch)
		before = bus.read_positions()
		code, out = run(monkeypatch, capsys, ["measure", "--profile", "toy", "--port", "/dev/x"])
		assert code == 0, out
		assert "a, b" in out
		assert "dry run" in out
		assert bus.read_positions() == before

	def test_measure_writes_a_proposal_and_a_backup_but_stores_nothing(self, monkeypatch, capsys, tmp_path):
		bus = self._toy(monkeypatch)
		stored = bus.read_calibration()
		out_file, backup = tmp_path / "proposed.json", tmp_path / "before.json"
		code, out = run(
			monkeypatch,
			capsys,
			[
				"measure",
				"--profile",
				"toy",
				"--port",
				"/dev/x",
				"--go",
				"--out",
				str(out_file),
				"--backup",
				str(backup),
				"--frame",
				str(_frame_file(tmp_path)),
			],
			stdin="YES\n",
		)
		assert code == 0, out
		assert Calibration.load(backup) == stored
		assert bus.read_calibration() == stored
		proposed = Calibration.load(out_file)
		assert proposed["a"].range_min == pytest.approx(1020, abs=10)
		assert "lower" in out
		assert "vs stored" in out


class TestFrameCommand:
	def _toy(self, monkeypatch, a_deg=10.0, b_deg=-30.0):
		from test_park import arm as park_arm

		bus, _ = park_arm(a_deg=a_deg, b_deg=b_deg)
		monkeypatch.setitem(cli.PROFILES, "toy", profile_with_shapes)
		monkeypatch.setitem(cli.REFERENCE_POSES, "toy-ref", ({"a": 0.0, "b": 60.0}, "a straight out, b bent up"))
		monkeypatch.setattr(cli, "_open_bus", lambda port, prof, acceleration: bus)
		return bus

	def test_without_go_it_describes_the_pose_and_reads_nothing(self, monkeypatch, capsys, tmp_path):
		self._toy(monkeypatch)
		code, out = run(monkeypatch, capsys, ["frame", "--profile", "toy", "--port", "/dev/x", "--pose", "toy-ref"])
		assert code == 0
		assert "a straight out" in out
		assert "dry run" in out

	def test_with_go_it_records_the_offsets_once_the_operator_confirms_the_pose(self, monkeypatch, capsys, tmp_path):
		from armkit.frame import ModelFrame

		self._toy(monkeypatch)
		out_file = tmp_path / "frame.json"
		code, out = run(
			monkeypatch,
			capsys,
			["frame", "--profile", "toy", "--port", "/dev/x", "--pose", "toy-ref", "--go", "--out", str(out_file)],
			stdin="YES\n",
		)
		assert code == 0, out
		frame = ModelFrame.load(out_file)
		assert frame.offsets_deg["a"] == pytest.approx(-10.0, abs=0.3)
		assert frame.offsets_deg["b"] == pytest.approx(90.0, abs=0.3)

	def test_release_lets_the_operator_pose_the_arm_by_hand_and_holds_it_afterwards(
		self, monkeypatch, capsys, tmp_path
	):
		bus = self._toy(monkeypatch)
		seen = []
		original = bus.set_torque

		def watch(enabled, joints=None):
			seen.append(enabled)
			original(enabled, joints)

		bus.set_torque = watch
		code, out = run(
			monkeypatch,
			capsys,
			[
				"frame",
				"--profile",
				"toy",
				"--port",
				"/dev/x",
				"--pose",
				"toy-ref",
				"--release",
				"--go",
				"--out",
				str(tmp_path / "f.json"),
			],
			stdin="YES\nYES\n",
		)
		assert code == 0, out
		assert seen[0] is False
		assert bus.joint("a").torque
		assert bus.joint("b").torque

	def test_no_means_nothing_is_released_or_written(self, monkeypatch, capsys, tmp_path):
		bus = self._toy(monkeypatch)
		code, _ = run(
			monkeypatch,
			capsys,
			[
				"frame",
				"--profile",
				"toy",
				"--port",
				"/dev/x",
				"--pose",
				"toy-ref",
				"--release",
				"--go",
				"--out",
				str(tmp_path / "f.json"),
			],
			stdin="no\n",
		)
		assert code != 0
		assert bus.joint("a").torque
		assert not (tmp_path / "f.json").exists()


class TestSecondPose:
	def test_refine_reads_the_second_pose_and_saves_the_directions(self, monkeypatch, capsys, tmp_path):
		from armkit.calibration import TICKS_PER_DEGREE
		from armkit.frame import ModelFrame, capture_frame
		from test_park import arm as park_arm

		bus, _ = park_arm(a_deg=10.0, b_deg=-30.0)
		monkeypatch.setitem(cli.PROFILES, "toy", profile_with_shapes)
		monkeypatch.setitem(cli.REFERENCE_POSES, "toy-second", ({"a": 40.0, "b": 15.0}, "a turned, b bent"))
		monkeypatch.setattr(cli, "_open_bus", lambda port, prof, acceleration: bus)
		first = tmp_path / "frame.json"
		capture_frame(bus, profile_with_shapes(), {"a": 0.0, "b": 60.0}, reference="toy-ref").save(first)
		bus.joint("a").encoder += 40 * TICKS_PER_DEGREE
		bus.joint("b").encoder += 45 * TICKS_PER_DEGREE  # b runs against the model
		code, out = run(
			monkeypatch,
			capsys,
			[
				"frame",
				"--profile",
				"toy",
				"--port",
				"/dev/x",
				"--pose",
				"toy-second",
				"--refine",
				str(first),
				"--go",
				"--out",
				str(first),
			],
			stdin="YES\n",
		)
		assert code == 0, out
		frame = ModelFrame.load(first)
		assert frame.signs == {"a": 1, "b": -1}
		assert frame.verified_directions == {"a", "b"}
		assert "reversed" in out

	def test_the_table_clearance_option_reaches_the_planner(self, monkeypatch, capsys, tmp_path):
		from test_park import arm as park_arm

		bus, _ = park_arm(a_deg=0.0)
		monkeypatch.setitem(cli.PROFILES, "toy", profile_with_shapes)
		monkeypatch.setattr(cli, "_open_bus", lambda port, prof, acceleration: bus)
		seen = {}
		original = cli.plan_move

		def spy(profile, *a, **kw):
			seen["floor"] = profile.collision.floor_z
			return original(profile, *a, **kw)

		monkeypatch.setattr(cli, "plan_move", spy)
		run(
			monkeypatch,
			capsys,
			["move", "--profile", "toy", "--port", "/dev/x", "--set", "a=-89", "--table-clearance", "0.08"],
		)
		assert seen["floor"] is None  # the toy has no floor: nothing to raise


class TestDirectionsCommand:
	def test_hand_moves_during_the_session_set_each_joints_direction(self, monkeypatch, capsys, tmp_path):
		import time

		from armkit.calibration import TICKS_PER_DEGREE
		from armkit.frame import ModelFrame, capture_frame
		from test_park import arm as park_arm

		bus, _ = park_arm(a_deg=0.0, b_deg=0.0)
		monkeypatch.setitem(cli.PROFILES, "toy", profile_with_shapes)
		monkeypatch.setitem(cli.DIRECTION_HINTS, "toy", {"a": "turn a up", "b": "turn b up"})
		monkeypatch.setattr(cli, "_open_bus", lambda port, prof, acceleration: bus)
		first = tmp_path / "frame.json"
		capture_frame(bus, profile_with_shapes(), {"a": 0.0, "b": 0.0}, reference="toy-ref").save(first)
		asked = []

		def ask(message):
			asked.append(message)
			if len(asked) == 2:  # the operator moves a with the model, then b against it, while the sampler runs
				for joint, sign in (("a", 1), ("b", -1)):
					for _ in range(10):
						bus.joint(joint).encoder += sign * 4 * TICKS_PER_DEGREE
						time.sleep(0.03)
			return True

		monkeypatch.setattr(cli, "_ask", ask)
		code = cli.main(
			[
				"frame",
				"--profile",
				"toy",
				"--port",
				"/dev/x",
				"--directions",
				"--refine",
				str(first),
				"--go",
				"--out",
				str(first),
			]
		)
		out = capsys.readouterr().out
		assert code == 0, out
		frame = ModelFrame.load(first)
		assert frame.signs == {"a": 1, "b": -1}
		assert frame.verified_directions == {"a", "b"}
		assert bus.joint("a").torque
		assert bus.joint("b").torque
		assert "turn a up" in asked[1]

	def test_a_joint_that_was_not_moved_is_reported_and_nothing_is_saved_for_it(self, monkeypatch, capsys, tmp_path):
		from armkit.frame import ModelFrame, capture_frame
		from test_park import arm as park_arm

		bus, _ = park_arm()
		monkeypatch.setitem(cli.PROFILES, "toy", profile_with_shapes)
		monkeypatch.setitem(cli.DIRECTION_HINTS, "toy", {"a": "turn a up", "b": "turn b up"})
		monkeypatch.setattr(cli, "_open_bus", lambda port, prof, acceleration: bus)
		monkeypatch.setattr(cli, "_ask", lambda message: True)
		first = tmp_path / "frame.json"
		capture_frame(bus, profile_with_shapes(), {"a": 0.0, "b": 0.0}, reference="toy-ref").save(first)
		code = cli.main(
			[
				"frame",
				"--profile",
				"toy",
				"--port",
				"/dev/x",
				"--directions",
				"--refine",
				str(first),
				"--go",
				"--out",
				str(first),
			]
		)
		out = capsys.readouterr().out
		assert code != 0
		assert "not moved" in out
		assert ModelFrame.load(first).verified_directions == frozenset()


class TestMeasurePreview:
	def test_preview_prints_the_simulated_run_and_moves_nothing(self, monkeypatch, capsys, tmp_path):
		from test_measure import arm as measure_arm

		bus = measure_arm()
		monkeypatch.setitem(cli.PROFILES, "toy", profile_with_shapes)
		monkeypatch.setattr(cli, "_open_bus", lambda port, prof, acceleration: bus)
		before = bus.read_positions()
		code, out = run(
			monkeypatch,
			capsys,
			["measure", "--profile", "toy", "--port", "/dev/x", "--preview", "--frame", str(_frame_file(tmp_path))],
		)
		assert code == 0, out
		assert "preview" in out
		assert "closest approach" in out
		assert "searching" in out
		assert bus.read_positions() == before


class TestTableAreaOption:
	def test_corners_are_parsed_in_metres(self):
		assert cli._parse_area("-1,-1; 0.25,-1; 0.25,1; -1,1") == [(-1.0, -1.0), (0.25, -1.0), (0.25, 1.0), (-1.0, 1.0)]

	def test_fewer_than_three_corners_are_refused(self):
		with pytest.raises(ValueError, match="three"):
			cli._parse_area("0,0; 1,0")


class TestCheckNotes:
	def test_a_note_is_printed_and_does_not_fail_the_check(self, monkeypatch, capsys, tmp_path):
		from armkit.calibration import JointCalibration
		from armkit.check import RangeCheck

		bus = arm()
		monkeypatch.setitem(cli.PROFILES, "toy", profile)
		monkeypatch.setattr(cli, "_open_bus", lambda port, prof, acceleration: bus)
		found = RangeCheck(
			True,
			JointCalibration(1, 0, 0, 800, 3300),
			900.0,
			None,
			100.0,
			None,
			(),
			notes=("a: upper end beyond the stored limit",),
		)
		monkeypatch.setattr(cli, "check_range", lambda *a, **kw: found)
		code, out = run(
			monkeypatch,
			capsys,
			[
				"check",
				"--profile",
				"toy",
				"--port",
				"/dev/x",
				"--joint",
				"a",
				"--go",
				"--backup",
				str(tmp_path / "b.json"),
			],
		)
		assert code == 0
		assert "NOTE: a: upper end beyond the stored limit" in out
