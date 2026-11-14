"""Live alignment page for the top camera: camera tilt, marker poses, and drift from a saved reference.

Run on the workstation (stop the live demo first; only one process can open the D415)::

	uv run sorter-alignment --host <tailscale-ip> --port 8091

Shows the camera's tilt against the table (adjust the mount until it reads near 0), every known marker with its
position, yaw and tilt relative to the table, and, once a reference is saved, whether each marker moved.
Presentation only: detection is :mod:`defect_sorter.markers`, depth refinement and comparison are
:mod:`defect_sorter.alignment`.
"""

from __future__ import annotations

import argparse
import logging
import threading
import time
from http.server import ThreadingHTTPServer
from pathlib import Path

import cv2
import numpy as np

from defect_sorter.alignment import (
	compare_to_reference,
	load_reference,
	refine_with_depth,
	save_reference,
	tilt_deg,
)
from defect_sorter.geometry import CameraTilt, Intrinsics, Plane, camera_tilt, deproject, fit_table_plane
from defect_sorter.markers import detect_markers
from defect_sorter.webview import FrameBuffer, make_handler, page_html

logger = logging.getLogger(__name__)

REFIT_EVERY = 15  # frames between table-plane fits
DISPLAY_WIDTH = 960


def _fmt_tilt(t: CameraTilt) -> str:
	return (
		f"camera tilt {t.total_deg:.1f} deg (far edge: {t.far_edge}; pitch {t.pitch_deg:+.1f}, roll {t.roll_deg:+.1f})"
	)


class AlignmentView:
	"""Background loop: read the camera, fit the table, detect markers, compare with the reference."""

	def __init__(self, camera, reference_path: Path) -> None:
		self._camera = camera
		self._reference_path = reference_path
		self._reference = load_reference(reference_path) if reference_path.exists() else {}
		self._plane: Plane | None = None
		self._frames = 0
		self.refit_requested = True
		self.save_requested = False
		self.buffer = FrameBuffer()

	def step(self) -> None:
		frame = self._camera.read()
		if self.refit_requested or self._plane is None or self._frames % REFIT_EVERY == 0:
			pts = deproject(frame.depth_m[::4, ::4], _scaled(frame.intrinsics, 0.25))
			valid = pts[..., 2] > 0
			if valid.sum() > 1000:
				self._plane = fit_table_plane(pts[valid])
			self.refit_requested = False
		self._frames += 1

		detections = detect_markers(frame.color_bgr, frame.intrinsics)
		poses = {d.id: refine_with_depth(d, frame.depth_m, frame.intrinsics) for d in detections}
		if self.save_requested and poses:
			save_reference(self._reference_path, poses)
			self._reference = dict(poses)
			self.save_requested = False
			logger.info("saved reference with %d markers to %s", len(poses), self._reference_path)
		deltas = compare_to_reference(poses, self._reference) if self._reference else {}
		tilt = camera_tilt(self._plane) if self._plane is not None else None

		vis = frame.color_bgr.copy()
		for d in detections:
			delta = deltas.get(d.id)
			colour = (0, 200, 255) if delta is None else ((0, 0, 255) if delta.moved else (0, 220, 0))
			cv2.polylines(vis, [np.round(d.corners_px).astype(np.int32)], True, colour, 2)
			cv2.arrowedLine(
				vis,
				tuple(np.round(d.corners_px.mean(0)).astype(int)),
				tuple(np.round((d.corners_px[1] + d.corners_px[2]) / 2).astype(int)),
				colour,
				2,
			)
			cv2.putText(
				vis,
				f"{d.id} {d.use}",
				tuple(np.round(d.corners_px[0] + (0, -8)).astype(int)),
				cv2.FONT_HERSHEY_SIMPLEX,
				0.6,
				colour,
				2,
			)
		lines = [_fmt_tilt(tilt) if tilt else "camera tilt: no table depth yet"]
		lines.append(f"reference: {len(self._reference)} markers" if self._reference else "reference: none saved")
		for i, text in enumerate(lines):
			cv2.putText(vis, text, (12, 30 + 30 * i), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 4)
			cv2.putText(vis, text, (12, 30 + 30 * i), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
		scale = DISPLAY_WIDTH / vis.shape[1]
		ok, buf = cv2.imencode(".jpg", cv2.resize(vis, None, fx=scale, fy=scale), [cv2.IMWRITE_JPEG_QUALITY, 80])

		state = {
			"t": time.time(),
			"camera_tilt": None
			if tilt is None
			else {
				"total_deg": round(tilt.total_deg, 2),
				"pitch_deg": round(tilt.pitch_deg, 2),
				"roll_deg": round(tilt.roll_deg, 2),
				"far_edge": tilt.far_edge,
			},
			"table_distance_m": None if self._plane is None else round(self._plane.offset, 4),
			"markers": [
				{
					"id": p.id,
					"use": p.use,
					"position_mm": [round(v * 1000, 1) for v in p.position_m],
					"yaw_deg": round(p.yaw_deg, 2),
					"tilt_vs_table_deg": None
					if self._plane is None
					else round(tilt_deg(p.normal, self._plane.normal), 2),
					"source": p.source,
					"delta": None
					if p.id not in deltas
					else {
						"moved": deltas[p.id].moved,
						"shift_mm": round(deltas[p.id].shift_mm, 1),
						"yaw_deg": round(deltas[p.id].yaw_deg, 2),
					},
				}
				for p in poses.values()
			],
			"missing_from_reference": [d.id for d in deltas.values() if d.missing],
		}
		self.buffer.publish(buf.tobytes() if ok else None, state)

	def request_save(self) -> None:
		self.save_requested = True

	def request_refit(self) -> None:
		self.refit_requested = True

	def run_forever(self) -> None:
		while True:
			try:
				self.step()
			except Exception:
				logger.exception("alignment step failed")
				time.sleep(0.5)


def _scaled(intr: Intrinsics, factor: float) -> Intrinsics:
	return Intrinsics(fx=intr.fx * factor, fy=intr.fy * factor, ppx=intr.ppx * factor, ppy=intr.ppy * factor)


def main(argv: list[str] | None = None) -> None:
	"""Start the camera loop and the HTTP server."""
	parser = argparse.ArgumentParser(description="Live alignment page for the top camera")
	parser.add_argument("--host", default="127.0.0.1", help="bind address; use the Tailscale IP, never 0.0.0.0")
	parser.add_argument("--port", type=int, default=8091)
	parser.add_argument("--reference", type=Path, default=Path("data/alignment/reference.json"))
	args = parser.parse_args(argv)
	logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

	from defect_sorter.realsense import D415Camera

	view = AlignmentView(D415Camera(1280, 720, 15, depth_size=(640, 480)), args.reference)
	threading.Thread(target=view.run_forever, daemon=True).start()
	logger.info("serving on http://%s:%d/", args.host, args.port)
	page = page_html("Cell alignment (top camera)", {"reference": "Save reference", "refit": "Refit table"})
	actions = {"reference": view.request_save, "refit": view.request_refit}
	ThreadingHTTPServer((args.host, args.port), make_handler(view.buffer, page, actions)).serve_forever()


if __name__ == "__main__":
	main()
