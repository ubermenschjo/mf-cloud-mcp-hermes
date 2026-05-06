#!/usr/bin/env python3
import http.server, urllib.parse, json, threading, socket

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        code = params.get("code", [None])[0]
        state = params.get("state", [None])[0]
        err = params.get("error", [None])[0]
        err_desc = params.get("error_description", [""])[0]

        if err:
            print(f"[ERROR] {err}: {err_desc}")
            self.send_response(400)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(f"<h1>エラー</h1><p>{err}</p><p>{err_desc}</p>".encode())
        else:
            print(f"[OK] Code received: {code[:30]}...")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write("<h1>認証成功！</h1><p>このウィンドウを閉じてください。</p>".encode())

        with open("/tmp/mf_auth_result.json", "w") as f:
            json.dump({"code": code, "state": state, "error": err}, f)
        Handler.got_code.set()

    def log_message(self, *args): pass

if __name__ == "__main__":
    PORT = 8080
    Handler.got_code = threading.Event()
    server = http.server.HTTPServer(("localhost", PORT), Handler)
    print(f"Listening: http://localhost:{PORT}/callback", flush=True)
    server.handle_request()
