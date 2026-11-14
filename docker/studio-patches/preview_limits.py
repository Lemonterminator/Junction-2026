"""Limits for Physical AI Studio's live session preview (mounted into the Studio container as ``api.preview_limits``).

Studio pushes every camera as a JPEG on every preview tick. On a congested link (venue Wi-Fi) the websocket send
blocks, older frames queue in TCP buffers and the operator sees the arm seconds late. Capping the preview rate and
JPEG quality, and optionally leaving cameras out of the preview, keeps the stream inside the link's capacity.
Recording is unaffected: the dataset worker reads the session store at the dataset's own fps.

Environment variables (read once per session socket):

* ``STUDIO_PREVIEW_MAX_HZ``: upper bound on the preview rate the browser asks for (default 10).
* ``STUDIO_PREVIEW_JPEG_QUALITY``: preview JPEG quality, 1-100 (default 60).
* ``STUDIO_PREVIEW_SKIP``: comma-separated camera keys not sent to the preview (default none).
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

DEFAULT_MAX_HZ = 10.0
DEFAULT_JPEG_QUALITY = 60


@dataclass(frozen=True)
class PreviewLimits:
	"""Effective preview settings for one session socket.

	Attributes
	----------
	hz : float
		Preview rate in Hz.
	jpeg_quality : int
		JPEG quality of preview frames.
	skip : frozenset of str
		Camera keys left out of the preview.
	"""

	hz: float
	jpeg_quality: int
	skip: frozenset[str]


def preview_limits(requested_hz: float, env: Mapping[str, str]) -> PreviewLimits:
	"""Combine the browser's requested rate with the limits configured in ``env``.

	Parameters
	----------
	requested_hz : float
		Rate the browser asked for (Studio's UI asks for 20 Hz).
	env : Mapping[str, str]
		Environment, normally ``os.environ``.

	Returns
	-------
	PreviewLimits
		The capped rate, the JPEG quality and the skipped camera keys.

	Raises
	------
	ValueError
		If a configured value is not a positive rate or a quality in 1-100.
	"""
	max_hz = float(env.get("STUDIO_PREVIEW_MAX_HZ", DEFAULT_MAX_HZ))
	if not max_hz > 0:
		raise ValueError(f"STUDIO_PREVIEW_MAX_HZ must be positive, got {max_hz}")
	quality = int(env.get("STUDIO_PREVIEW_JPEG_QUALITY", DEFAULT_JPEG_QUALITY))
	if not 1 <= quality <= 100:
		raise ValueError(f"STUDIO_PREVIEW_JPEG_QUALITY must be in 1-100, got {quality}")
	skip = frozenset(key.strip() for key in env.get("STUDIO_PREVIEW_SKIP", "").split(",") if key.strip())
	return PreviewLimits(hz=min(requested_hz, max_hz), jpeg_quality=quality, skip=skip)
