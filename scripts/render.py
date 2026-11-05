"""Screenshot a page of this repository with headless Chrome.

Usage: python scripts/render.py docs/sample.html docs/sample.png [WIDTHxHEIGHT]

The repository is served over HTTP on a free local port so that the page can
load ../dist/*.woff2 like a browser would.
"""

from __future__ import annotations

import functools
import shutil
import subprocess
import sys
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def render(page: str, output: Path, size: str = "1000x700") -> None:
    chrome = next((c for c in ("google-chrome", "chromium", "chromium-browser") if shutil.which(c)), None)
    if chrome is None:
        raise SystemExit("needs google-chrome or chromium on PATH")
    handler = functools.partial(SimpleHTTPRequestHandler, directory=str(ROOT))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        width, height = size.split("x")
        url = f"http://127.0.0.1:{server.server_address[1]}/{page}"
        subprocess.run(
            [chrome, "--headless=new", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
             f"--window-size={width},{height}", "--virtual-time-budget=5000",
             f"--screenshot={output.resolve()}", url],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120,
        )
    finally:
        server.shutdown()


if __name__ == "__main__":
    render(sys.argv[1], Path(sys.argv[2]), *sys.argv[3:4])
    print(sys.argv[2])
