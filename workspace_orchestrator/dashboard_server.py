from __future__ import annotations

import json
import threading
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit

from .dashboard import build_dashboard_snapshot, load_dashboard_run_detail


ASSETS_DIR = Path(__file__).resolve().parent / "dashboard_assets"


@dataclass
class DashboardServerHandle:
    server: ThreadingHTTPServer
    thread: threading.Thread
    url: str

    def close(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=5)


def _asset_response(path: Path) -> tuple[bytes, str]:
    suffix_map = {
        ".html": "text/html; charset=utf-8",
        ".css": "text/css; charset=utf-8",
        ".js": "application/javascript; charset=utf-8",
    }
    return path.read_bytes(), suffix_map.get(path.suffix, "application/octet-stream")


def _handler_factory(root: Path, run_limit: int, log_limit: int):
    class DashboardHandler(BaseHTTPRequestHandler):
        server_version = "ASMObservatory/1.0"

        def _send_bytes(self, body: bytes, content_type: str, status: int = 200) -> None:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def _send_json(self, payload: dict[str, object], status: int = 200) -> None:
            self._send_bytes(
                json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8"),
                "application/json; charset=utf-8",
                status=status,
            )

        def do_GET(self) -> None:  # noqa: N802
            parsed = urlsplit(self.path)
            if parsed.path == "/":
                body, content_type = _asset_response(ASSETS_DIR / "index.html")
                self._send_bytes(body, content_type)
                return
            if parsed.path == "/assets/app.css":
                body, content_type = _asset_response(ASSETS_DIR / "app.css")
                self._send_bytes(body, content_type)
                return
            if parsed.path == "/assets/app.js":
                body, content_type = _asset_response(ASSETS_DIR / "app.js")
                self._send_bytes(body, content_type)
                return
            if parsed.path == "/assets/app_v2.js":
                body, content_type = _asset_response(ASSETS_DIR / "app_v2.js")
                self._send_bytes(body, content_type)
                return
            if parsed.path == "/api/dashboard":
                self._send_json(build_dashboard_snapshot(root, run_limit=run_limit, log_limit=log_limit).to_dict())
                return
            if parsed.path.startswith("/api/run/"):
                run_id = unquote(parsed.path.removeprefix("/api/run/"))
                try:
                    payload = load_dashboard_run_detail(root, run_id)
                except FileNotFoundError:
                    self._send_json({"status": "error", "error": "run_not_found", "run_id": run_id}, status=404)
                    return
                self._send_json(payload)
                return
            self._send_json({"status": "error", "error": "not_found", "path": parsed.path}, status=404)

        def log_message(self, format: str, *args) -> None:  # noqa: A003
            return

    return DashboardHandler


def start_dashboard_server(
    root: Path,
    host: str = "127.0.0.1",
    port: int = 8765,
    run_limit: int = 12,
    log_limit: int = 8,
) -> DashboardServerHandle:
    handler = _handler_factory(root.resolve(), run_limit=run_limit, log_limit=log_limit)
    server = ThreadingHTTPServer((host, port), handler)
    actual_host, actual_port = server.server_address[:2]
    browser_host = "127.0.0.1" if actual_host == "0.0.0.0" else str(actual_host)
    url = f"http://{browser_host}:{actual_port}"
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return DashboardServerHandle(server=server, thread=thread, url=url)


def serve_dashboard(
    root: Path,
    host: str = "127.0.0.1",
    port: int = 8765,
    run_limit: int = 12,
    log_limit: int = 8,
) -> str:
    handler = _handler_factory(root.resolve(), run_limit=run_limit, log_limit=log_limit)
    server = ThreadingHTTPServer((host, port), handler)
    actual_host, actual_port = server.server_address[:2]
    browser_host = "127.0.0.1" if actual_host == "0.0.0.0" else str(actual_host)
    url = f"http://{browser_host}:{actual_port}"
    try:
        print(f"dashboard_url: {url}")
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return url
