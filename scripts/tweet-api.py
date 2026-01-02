#!/usr/bin/env python3
"""
Tweet API Shim Service

A lightweight HTTP server that handles X (Twitter) OAuth 1.0a signing,
bypassing N8N's credential system which has compatibility issues.

Usage:
    python3 tweet-api.py

The service listens on 127.0.0.1:5680 (localhost only).

API:
    POST / with JSON body {"text": "Your tweet"}
    Returns: X API response

Install as systemd service:
    sudo cp tweet-api.py /opt/n8n/
    sudo cp tweet-api.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable --now tweet-api
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os

# Try to import oauth library
try:
    import requests
    from requests_oauthlib import OAuth1
except ImportError:
    print("Missing dependencies. Install with:")
    print("  sudo pip3 install requests requests-oauthlib --break-system-packages")
    exit(1)

# X API Credentials - can be overridden via environment variables
API_KEY = os.environ.get("X_API_KEY", "AZTl19972fOWCXLGIr7P9nyvj")
API_SECRET = os.environ.get("X_API_SECRET", "elHIcKhX5zc9b851vKhrvTeFcDyHlh2bOJnkp3HgOwTn3iCJxD")
ACCESS_TOKEN = os.environ.get("X_ACCESS_TOKEN", "2718719726-KeW77I7drF6B25H4qqHgtWMvqDjvP9ceGXpR1Kp")
ACCESS_SECRET = os.environ.get("X_ACCESS_SECRET", "LixS9benOm0c21As2oSDGxtKu3UpgXPUBVjDVZqpNfGy1")

# Create OAuth1 session
auth = OAuth1(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET)


class TweetHandler(BaseHTTPRequestHandler):
    """HTTP request handler for tweet API."""

    def log_message(self, format, *args):
        """Log to stdout for systemd journal."""
        print(f"{self.address_string()} - {format % args}")

    def do_POST(self):
        """Handle POST request to create a tweet."""
        # Read request body
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length else b"{}"

        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            self.send_error(400, "Invalid JSON")
            return

        text = data.get("text", "")
        if not text:
            self.send_error(400, "Missing 'text' field")
            return

        # Post to X API
        try:
            response = requests.post(
                "https://api.twitter.com/2/tweets",
                auth=auth,
                json={"text": text},
                timeout=30
            )

            # Send response
            self.send_response(response.status_code)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(response.text.encode())

        except requests.RequestException as e:
            self.send_error(500, f"X API error: {str(e)}")

    def do_GET(self):
        """Health check endpoint."""
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"status": "ok", "service": "tweet-api"}')


def main():
    """Start the HTTP server."""
    host = "127.0.0.1"
    port = 5680

    server = HTTPServer((host, port), TweetHandler)
    print(f"Tweet API running on http://{host}:{port}")
    print("Press Ctrl+C to stop")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.shutdown()


if __name__ == "__main__":
    main()
