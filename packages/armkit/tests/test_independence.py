"""The library stays usable outside the project it was written in."""

import re
import tomllib
from pathlib import Path

PACKAGE = Path(__file__).resolve().parents[1]
FILES = [
	*PACKAGE.joinpath("src").rglob("*.py"),
	*PACKAGE.joinpath("tests").glob("*.py"),
	PACKAGE / "README.md",
	PACKAGE / "pyproject.toml",
]
PROJECT_WORDS = re.compile(r"defect[_ -]?sorter|junction|hackathon|\bintel\b|\bchallenge\b|\bsorter\b", re.IGNORECASE)


def test_no_file_names_the_project_it_was_written_for():
	own = Path(__file__).resolve()
	offenders = [
		f"{f.relative_to(PACKAGE)}: {m.group(0)}"
		for f in FILES
		if f != own
		for m in PROJECT_WORDS.finditer(f.read_text())
	]
	assert offenders == []


def test_it_depends_on_numpy_and_scipy_only_and_the_servo_sdk_is_an_extra():
	meta = tomllib.loads((PACKAGE / "pyproject.toml").read_text())["project"]
	assert sorted(re.split(r"[<>=!~ ]", d)[0] for d in meta["dependencies"]) == ["numpy", "scipy"]
	assert list(meta["optional-dependencies"]) == ["feetech"]


def test_the_servo_sdk_is_imported_in_exactly_one_module():
	importers = [
		f.name
		for f in PACKAGE.joinpath("src").rglob("*.py")
		if re.search(r"^\s*import scservo_sdk", f.read_text(), re.MULTILINE)
	]
	assert importers == ["feetech.py"]
