"""Shared HTTP plumbing for the live camera pages (scene demo, alignment page).

The browser pulls one complete JPEG at a time (``GET /frame.jpg?after=<id>``) and asks for the next only after
the previous one arrived. The server answers as soon as a frame newer than ``after`` exists, or with 204 after a
short wait. Compared with a pushed MJPEG stream this cannot build a backlog on a slow link, never shows a
half-received frame, and never resends a frame that did not change. The page shows how long ago the last frame
arrived, so a stalled camera loop is visible.
"""

from __future__ import annotations

import json
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

FRAME_WAIT_S = 1.5


@dataclass(frozen=True)
class Frame:
	"""One published frame: JPEG bytes, the page state that goes with it, and when it was published."""

	frame_id: int
	jpeg: bytes | None
	state: dict
	published_at: float


class FrameBuffer:
	"""Latest frame and state, shared between the camera loop and HTTP threads."""

	def __init__(self) -> None:
		self._cond = threading.Condition()
		self._frame = Frame(frame_id=0, jpeg=None, state={}, published_at=0.0)

	def publish(self, jpeg: bytes | None, state: dict) -> None:
		"""Store a new frame (``jpeg`` may be ``None`` to update only the state) and wake waiting requests."""
		with self._cond:
			self._frame = Frame(frame_id=self._frame.frame_id + 1, jpeg=jpeg, state=state, published_at=time.time())
			self._cond.notify_all()

	def latest(self) -> Frame:
		with self._cond:
			return self._frame

	def wait_newer(self, after_id: int, timeout: float) -> Frame | None:
		"""Return the latest frame once its id is greater than ``after_id``, or ``None`` after ``timeout`` seconds."""
		with self._cond:
			if self._cond.wait_for(lambda: self._frame.frame_id > after_id, timeout=timeout):
				return self._frame
			return None


def page_html(title: str, buttons: dict[str, str]) -> bytes:
	"""Page with the live image, action buttons (``{action: label}``, posted to ``/<action>``) and the JSON state."""
	button_html = "".join(
		f"<button onclick=\"fetch('/{action}',{{method:'POST'}})\">{label}</button>"
		for action, label in buttons.items()
	)
	return f"""<!doctype html><html><head><meta charset=utf-8><title>{title}</title>
<style>body{{font-family:system-ui;background:#111;color:#eee;margin:16px}}img{{max-width:100%;border:1px solid #333;display:block}}
button{{padding:6px 12px;margin:8px 8px 8px 0}}pre{{background:#1b1b1b;padding:12px;font-size:13px;max-height:45vh;overflow:auto}}
#age{{color:#f66;min-height:1.2em}}</style></head>
<body><h3>{title}</h3><div id=age></div><img id=v alt="waiting for the first frame">{button_html}<pre id=s></pre>
<script>
const img = document.getElementById('v'), age = document.getElementById('age');
const sleep = ms => new Promise(r => setTimeout(r, ms));
let last = 0, lastT = Date.now();
async function frames() {{
  for (;;) {{
    try {{
      const r = await fetch('/frame.jpg?after=' + last, {{cache: 'no-store'}});
      if (r.status === 200) {{
        const blob = await r.blob();
        last = Number(r.headers.get('X-Frame-Id')); lastT = Date.now();
        const old = img.src; img.src = URL.createObjectURL(blob);
        if (old.startsWith('blob:')) URL.revokeObjectURL(old);
      }} else if (r.status !== 204) {{ await sleep(500); }}
    }} catch (e) {{ await sleep(1000); }}
  }}
}}
setInterval(() => {{ const s = (Date.now() - lastT) / 1000; age.textContent = s > 3 ? `no new frame for ${{s.toFixed(0)}} s` : ''; }}, 500);
setInterval(async () => {{ try {{ document.getElementById('s').textContent = JSON.stringify(await (await fetch('/state', {{cache: 'no-store'}})).json(), null, 1); }} catch (e) {{}} }}, 700);
frames();
</script></body></html>""".encode()


def make_handler(
	buffer: FrameBuffer, page: bytes, actions: dict[str, Callable[[], None]]
) -> type[BaseHTTPRequestHandler]:
	"""Handler for ``/``, ``/frame.jpg?after=<id>``, ``/state`` and ``POST /<action>``."""

	class Handler(BaseHTTPRequestHandler):
		timeout = 10  # drop clients that stop reading instead of blocking a thread forever

		def log_message(self, format: str, *args: object) -> None:
			pass

		def do_GET(self) -> None:
			url = urlparse(self.path)
			if url.path == "/":
				self._send(200, "text/html", page)
			elif url.path == "/state":
				self._send(200, "application/json", json.dumps(buffer.latest().state).encode())
			elif url.path == "/frame.jpg":
				self._frame(parse_qs(url.query))
			else:
				self._send(404, "text/plain", b"not found")

		def do_POST(self) -> None:
			action = actions.get(urlparse(self.path).path.lstrip("/"))
			if action is None:
				self._send(404, "text/plain", b"not found")
				return
			action()
			self.send_response(204)
			self.end_headers()

		def _frame(self, query: dict[str, list[str]]) -> None:
			try:
				after = int(query.get("after", ["0"])[0])
			except ValueError:
				after = 0
			frame = buffer.wait_newer(after, FRAME_WAIT_S)
			if frame is None and buffer.latest().jpeg is not None:
				self.send_response(204)
				self.end_headers()
				return
			if frame is None or frame.jpeg is None:
				self._send(503, "text/plain", b"no frame yet")
				return
			self._send(200, "image/jpeg", frame.jpeg, {"Cache-Control": "no-store", "X-Frame-Id": str(frame.frame_id)})

		def _send(self, code: int, content_type: str, body: bytes, headers: dict[str, str] | None = None) -> None:
			self.send_response(code)
			self.send_header("Content-Type", content_type)
			self.send_header("Content-Length", str(len(body)))
			for key, value in (headers or {}).items():
				self.send_header(key, value)
			self.end_headers()
			self.wfile.write(body)

	return Handler
