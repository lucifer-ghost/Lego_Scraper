"""
LEGO Deal Radar Server
Compatible with:
- Local development: python server.py (or python web_app.py) on http://localhost:5000
- Vercel Serverless Function deployment (handles 'handler' entrypoint)
"""

import sys
import os
import json
import urllib.parse
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
import webbrowser
import threading

# Add current directory to path
base_dir = os.path.dirname(os.path.abspath(__file__))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

from scraper import get_lego_deals, get_lego_cars

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

class handler(BaseHTTPRequestHandler):
    """
    Vercel serverless & local development HTTP handler.
    Vercel looks for a top-level 'handler' class inheriting from BaseHTTPRequestHandler.
    """

    def _set_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-Requested-With")

    def do_OPTIONS(self):
        self.send_response(200)
        self._set_cors_headers()
        self.end_headers()

    def do_GET(self):
        # Resolve path: handle Vercel proxy headers if present
        raw_uri = self.headers.get("x-forwarded-uri") or self.headers.get("x-matched-path") or self.path
        parsed = urllib.parse.urlparse(raw_uri)
        path = parsed.path

        # Also inspect self.path directly for query parameters
        parsed_self = urllib.parse.urlparse(self.path)
        query_str = parsed_self.query if parsed_self.query else parsed.query
        params = urllib.parse.parse_qs(query_str)

        # 1. API: Scan LEGO Deals
        if path == "/api/scan" or path.endswith("/api/scan"):
            min_disc = int(params.get("min_discount", ["40"])[0])
            max_disc = int(params.get("max_discount", ["50"])[0])
            platform = params.get("platform", ["both"])[0]
            pages_raw = params.get("pages", ["all"])[0]
            if str(pages_raw).lower() in ("all", "0", "auto"):
                pages = 0  # 0 indicates auto-detect complete catalog
            else:
                try:
                    pages = int(pages_raw)
                except ValueError:
                    pages = 0
            official_param = params.get("official_only", ["true"])[0].lower()
            official = official_param not in ("false", "0", "no")

            print(f"[API] Scan: min={min_disc}%, max={max_disc}%, platform={platform}, official={official}, pages={'Auto' if pages == 0 else pages}")
            sys.stdout.flush()

            deals = get_lego_deals(
                min_discount=min_disc,
                max_discount=max_disc,
                platform=platform,
                official_only=official,
                pages=pages,
                verbose=True
            )

            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self._set_cors_headers()
            self.end_headers()
            payload = json.dumps({"count": len(deals), "deals": deals})
            self.wfile.write(payload.encode("utf-8"))
            return

        # 2. API: LEGO Cars & F1 Collection
        if path == "/api/cars" or path.endswith("/api/cars"):
            platform = params.get("platform", ["both"])[0]
            category = params.get("category", ["all"])[0]
            refresh = params.get("refresh", ["false"])[0].lower() in ("true", "1")
            pages = int(params.get("pages", ["2"])[0])

            print(f"[API] Cars: platform={platform}, category={category}, refresh={refresh}")
            sys.stdout.flush()

            cars = get_lego_cars(
                platform=platform,
                category=category,
                pages=pages,
                force_refresh=refresh,
                verbose=True
            )

            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self._set_cors_headers()
            self.end_headers()
            payload = json.dumps({"count": len(cars), "cars": cars})
            self.wfile.write(payload.encode("utf-8"))
            return

        # 3. Static Files: Serve React dist bundle
        dist_dir = os.path.join(base_dir, "frontend", "dist")
        if os.path.exists(dist_dir):
            clean_path = path.lstrip("/")
            file_path = os.path.join(dist_dir, clean_path)
            if not clean_path or not os.path.exists(file_path) or os.path.isdir(file_path):
                file_path = os.path.join(dist_dir, "index.html")

            if os.path.exists(file_path):
                ext = os.path.splitext(file_path)[1].lower()
                mime_types = {
                    '.html': 'text/html; charset=utf-8',
                    '.js': 'application/javascript; charset=utf-8',
                    '.mjs': 'application/javascript; charset=utf-8',
                    '.css': 'text/css; charset=utf-8',
                    '.json': 'application/json; charset=utf-8',
                    '.svg': 'image/svg+xml',
                    '.png': 'image/png',
                    '.jpg': 'image/jpeg',
                    '.ico': 'image/x-icon',
                    '.woff': 'font/woff',
                    '.woff2': 'font/woff2',
                }
                ctype = mime_types.get(ext, 'application/octet-stream')
                self.send_response(200)
                self.send_header("Content-type", ctype)
                self._set_cors_headers()
                self.end_headers()
                with open(file_path, "rb") as f:
                    self.wfile.write(f.read())
                return

        # Fallback 404
        self.send_response(404)
        self._set_cors_headers()
        self.end_headers()
        self.wfile.write(b"Not Found")

    def log_message(self, format, *args):
        sys.stderr.write(f"[Server] {format % args}\n")

# Backwards and framework compatibility aliases
DealsHandler = handler
app = handler

def run_server(port=5000, auto_open=True):
    server_address = ('', port)
    httpd = ThreadingHTTPServer(server_address, handler)
    url = f"http://localhost:{port}"
    print(f"\n=======================================================")
    print(f"🚀 LEGO Deal Radar Dashboard running at: {url}")
    print(f"Press Ctrl+C in terminal to stop.")
    print(f"=======================================================\n")
    sys.stdout.flush()
    # Preload car catalog in background thread for instant response
    threading.Thread(target=lambda: get_lego_cars(platform='both', verbose=False), daemon=True).start()
    if auto_open:
        threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping dashboard server...")
        httpd.server_close()

if __name__ == "__main__":
    port = 5000
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        port = int(sys.argv[1])
    run_server(port=port)
