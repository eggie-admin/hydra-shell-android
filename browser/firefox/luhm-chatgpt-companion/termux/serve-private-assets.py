#!/usr/bin/env python3
from __future__ import annotations

from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import argparse
import functools


class Handler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, HEAD, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.send_header("Cross-Origin-Resource-Policy", "cross-origin")
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.end_headers()


parser = argparse.ArgumentParser()
parser.add_argument("--root", required=True)
parser.add_argument("--host", default="127.0.0.1")
parser.add_argument("--port", type=int, default=8799)
args = parser.parse_args()
root = Path(args.root).expanduser().resolve()
root.mkdir(parents=True, exist_ok=True)
handler = functools.partial(Handler, directory=str(root))
server = ThreadingHTTPServer((args.host, args.port), handler)
print(f"LuHm private asset bridge serving {root} on http://{args.host}:{args.port}/", flush=True)
server.serve_forever()
