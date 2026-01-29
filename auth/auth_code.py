# auth/auth_code.py

import http.server
import socketserver
from urllib.parse import urlparse, parse_qs
import threading
import webbrowser
import time
from fyers_apiv3 import fyersModel
import config.settings as settings

redirect_uri = "http://127.0.0.1:8080/"
response_type = "code"
state = "authorize"


class AuthHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_query = urlparse(self.path).query
        params = parse_qs(parsed_query)
        auth_code = params.get("auth_code", [None])[0]
        state_value = params.get("state", [None])[0]

        if not auth_code or state_value != state:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Error: Invalid or missing authorization parameters.")
            return

        settings.auth_code = auth_code

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"<h2>Authorization successful. You may close this tab.</h2>")

        threading.Thread(target=self.server.shutdown, daemon=True).start()

    def log_message(self, format, *args):
        pass  # Silence log output


class SilentHTTPServer(socketserver.TCPServer):
    allow_reuse_address = True

    def handle_error(self, request, client_address):
        pass  # Ignore client errors


def start_local_server():
    handler = AuthHandler
    handler.protocol_version = "HTTP/1.1"

    with SilentHTTPServer(("127.0.0.1", 8080), handler) as httpd:
        print("→ OAuth local server started (waiting for redirect)...")
        httpd.serve_forever()
        print("→ OAuth server shutdown complete.")


def generate_auth_code():
    session = fyersModel.SessionModel(
        client_id=settings.client_id,
        redirect_uri=redirect_uri,
        response_type=response_type,
        state=state,
        secret_key=settings.secret_id
    )

    login_url = session.generate_authcode()

    threading.Thread(target=start_local_server, daemon=True).start()
    print("🌐 Opening browser for Fyers login...")
    webbrowser.open(login_url)

    while settings.auth_code is None:
        time.sleep(1)

    print("✅ Authorization complete.")


def generate_access_token():
    if settings.access_token:
        print("⚠️  Access token already set. Skipping generation.")
        return

    generate_auth_code()

    session = fyersModel.SessionModel(
        client_id=settings.client_id,
        redirect_uri=redirect_uri,
        secret_key=settings.secret_id,
        grant_type="authorization_code"
    )

    session.set_token(settings.auth_code)

    try:
        response = session.generate_token()
        access_token = response["access_token"]
        settings.access_token = access_token
        print("✅ Access token generated successfully.")
    except Exception as e:
        print("❌ Failed to generate token.")
        print("→ Error:", e)
        print("→ Response:", response)


if __name__ == "__main__":
    generate_access_token()
