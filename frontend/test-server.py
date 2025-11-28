#!/usr/bin/env python3
import http.server
import socketserver
import os

class Handler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

# Change to dist directory
os.chdir('dist')

# Start server
with socketserver.TCPServer(("", 3001), Handler) as httpd:
    print("DAM Frontend Test Server running at http://localhost:3001")
    print("Press Ctrl+C to stop")
    httpd.serve_forever()
