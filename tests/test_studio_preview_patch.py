"""Tests for the Studio live-preview limits patch in ``docker/studio-patches``.

The patch runs inside the Studio container, so it is loaded here by path rather than imported from our package.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import pytest

PATCH_DIR = Path(__file__).resolve().parents[1] / "docker" / "studio-patches"


def _load(name: str) -> ModuleType:
	spec = importlib.util.spec_from_file_location(name, PATCH_DIR / f"{name}.py")
	assert spec is not None
	assert spec.loader is not None
	module = importlib.util.module_from_spec(spec)
	sys.modules[name] = module  # dataclasses look the module up while the class is created
	spec.loader.exec_module(module)
	return module


limits = _load("preview_limits")


def test_defaults_cap_rate_and_quality() -> None:
	got = limits.preview_limits(20.0, {})
	assert got.hz == 10.0
	assert got.jpeg_quality == 60
	assert got.skip == frozenset()


def test_requested_rate_below_cap_is_kept() -> None:
	assert limits.preview_limits(5.0, {}).hz == 5.0


def test_environment_overrides() -> None:
	env = {
		"STUDIO_PREVIEW_MAX_HZ": "15",
		"STUDIO_PREVIEW_JPEG_QUALITY": "70",
		"STUDIO_PREVIEW_SKIP": " top_depth , wrist ,",
	}
	got = limits.preview_limits(20.0, env)
	assert got.hz == 15.0
	assert got.jpeg_quality == 70
	assert got.skip == frozenset({"top_depth", "wrist"})


@pytest.mark.parametrize(
	("env", "message"),
	[
		({"STUDIO_PREVIEW_MAX_HZ": "0"}, "STUDIO_PREVIEW_MAX_HZ"),
		({"STUDIO_PREVIEW_MAX_HZ": "fast"}, "could not convert"),
		({"STUDIO_PREVIEW_JPEG_QUALITY": "0"}, "STUDIO_PREVIEW_JPEG_QUALITY"),
		({"STUDIO_PREVIEW_JPEG_QUALITY": "101"}, "STUDIO_PREVIEW_JPEG_QUALITY"),
	],
)
def test_invalid_values_are_rejected(env: dict[str, str], message: str) -> None:
	with pytest.raises(ValueError, match=message):
		limits.preview_limits(20.0, env)


def test_runtime_ws_patch_uses_the_limits() -> None:
	"""The patched upstream file must route the sampler through ``preview_limits``."""
	source = (PATCH_DIR / "runtime_ws.py").read_text(encoding="utf-8")
	assert "from api.preview_limits import preview_limits" in source
	assert "quality=limits.jpeg_quality" in source
	assert "limits.skip" in source
	assert "Rate(limits.hz" in source
