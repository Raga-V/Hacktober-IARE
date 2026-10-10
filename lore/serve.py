"""F11: local server for the web page. Serves the repo root and runs live mode on POST /api/run."""
import json
import os
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

from .common import out_dir, parse_repo, progress

_lock = threading.Lock()


class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path in ("/", ""):
            self.send_response(302)
            self.send_header("Location", "/web/")
            self.end_headers()
            return
        if not self.path.startswith(("/web/", "/out/")) or ".." in self.path:
            return self.send_error(404)  # never serve .env or source files
        super().do_GET()

    def translate_path(self, path):
        # /out/... is served from LORE_OUT, so `LORE_OUT=out-ollama python -m lore serve` shows that run.
        if path.startswith("/out/"):
            return os.path.join(os.path.abspath(os.environ.get("LORE_OUT", "out")),
                                *path.split("?")[0][len("/out/"):].split("/"))
        return super().translate_path(path)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or "{}")
        if self.path == "/api/check":
            return self._check(body)
        if self.path != "/api/run":
            return self.send_error(404)
        try:
            repo = parse_repo(body.get("repo", ""))
        except SystemExit as e:
            return self._json(400, {"error": str(e)})
        if not _lock.acquire(blocking=False):
            return self._json(409, {"error": "a run is already in progress"})
        slug = out_dir(repo).name
        progress(repo, "queued", f"starting live run on {repo}")

        def work():
            from .__main__ import pipeline
            try:
                pipeline(repo, max_comments=300, review_prs=0, eval_n=60)
            except (Exception, SystemExit):
                pass  # pipeline already wrote the error to progress.json
            finally:
                _lock.release()

        threading.Thread(target=work, daemon=True).start()
        self._json(202, {"slug": slug})

    def _check(self, body):
        from .check import check, fetch_diff
        repo = str(body.get("slug", "")).replace("__", "/")
        text = str(body.get("input", "")).strip()
        try:
            diff = text if "diff --git" in text or text.startswith("---") else fetch_diff(repo, text)
            self._json(200, check(repo, diff))
        except (Exception, SystemExit) as e:
            self._json(400, {"error": f"{type(e).__name__}: {e}"})

    def _json(self, code, data):
        raw = json.dumps(data).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)


def serve(port=8000):
    server = ThreadingHTTPServer(("127.0.0.1", port), partial(Handler, directory="."))
    print(f"Lore page: http://127.0.0.1:{port}/web/  (live mode enabled)")
    server.serve_forever()
