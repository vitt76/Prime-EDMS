import base64
import json
import os
import socket
import ssl
from urllib import error, request
from urllib.parse import urlparse

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Run live HTTP and WebSocket smoke checks for tenant-scoped runtime contracts.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--base-url',
            default='http://localhost:8080',
            help='Base HTTP URL to probe from the current runtime environment.',
        )
        parser.add_argument(
            '--token',
            required=True,
            help='DRF token used for authenticated smoke requests.',
        )
        parser.add_argument(
            '--organization-id',
            required=True,
            help='Organization UUID for tenant-scoped requests.',
        )
        parser.add_argument(
            '--ws-base-url',
            default='',
            help=(
                'Optional WebSocket base URL. If omitted, derive from --base-url '
                'using the split-runtime convention (e.g. :8080 -> :8001).'
            ),
        )
        parser.add_argument(
            '--skip-websocket',
            action='store_true',
            help='Skip tenant-aware WebSocket handshake smoke checks.',
        )

    def handle(self, *args, **options):
        base_url = options['base_url'].rstrip('/')
        token = options['token']
        organization_id = options['organization_id']
        skip_websocket = bool(options['skip_websocket'])
        ws_base_url = (options.get('ws_base_url') or '').rstrip('/')
        if not skip_websocket and not ws_base_url:
            ws_base_url = self._derive_ws_base_url(base_url=base_url)

        http_checks = [
            {
                'name': 'analytics_health',
                'path': '/api/v4/analytics/health/',
                'headers': {},
                'expected': {200},
            },
            {
                'name': 'geography_ok',
                'path': '/api/v4/headless/analytics/dashboard/geography/',
                'headers': {
                    'Authorization': f'Token {token}',
                    'X-Organization-Id': organization_id,
                },
                'expected': {200},
            },
            {
                'name': 'geography_requires_org',
                'path': '/api/v4/headless/analytics/dashboard/geography/',
                'headers': {
                    'Authorization': f'Token {token}',
                },
                'expected': {400},
            },
            {
                'name': 'distribution_campaigns_ok',
                'path': '/api/v4/distribution/campaigns/',
                'headers': {
                    'Authorization': f'Token {token}',
                    'X-Organization-Id': organization_id,
                },
                'expected': {200},
            },
            {
                'name': 'distribution_campaigns_requires_org',
                'path': '/api/v4/distribution/campaigns/',
                'headers': {
                    'Authorization': f'Token {token}',
                },
                'expected': {400},
            },
            {
                'name': 'distribution_share_links_ok',
                'path': '/api/v4/distribution/share_links/',
                'headers': {
                    'Authorization': f'Token {token}',
                    'X-Organization-Id': organization_id,
                },
                'expected': {200},
            },
            {
                'name': 'distribution_share_links_requires_org',
                'path': '/api/v4/distribution/share_links/',
                'headers': {
                    'Authorization': f'Token {token}',
                },
                'expected': {400},
            },
        ]

        failures = []
        results = []

        for check in http_checks:
            status_code, body = self._request(
                url=f'{base_url}{check["path"]}',
                headers=check['headers'],
            )
            results.append(
                {
                    'name': check['name'],
                    'transport': 'http',
                    'status_code': status_code,
                    'ok': status_code in check['expected'],
                }
            )
            if status_code not in check['expected']:
                failures.append(
                    {
                        'name': check['name'],
                        'expected': sorted(check['expected']),
                        'actual': status_code,
                        'body': body,
                    }
                )

        websocket_checks = []
        if not skip_websocket:
            websocket_checks = [
                {
                    'name': 'notifications_ws_ok',
                    'url': (
                        f'{ws_base_url}/notifications/'
                        f'?token={token}&organization_id={organization_id}'
                    ),
                    'expected': {101},
                },
                {
                    'name': 'notifications_ws_requires_org',
                    'url': f'{ws_base_url}/notifications/?token={token}',
                    'expected': {403},
                },
                {
                    'name': 'analytics_ws_ok',
                    'url': (
                        f'{ws_base_url}/analytics/'
                        f'?token={token}&organization_id={organization_id}'
                    ),
                    'expected': {101},
                },
                {
                    'name': 'analytics_ws_requires_org',
                    'url': f'{ws_base_url}/analytics/?token={token}',
                    'expected': {403},
                },
            ]

        for check in websocket_checks:
            status_code, body = self._websocket_handshake(url=check['url'])
            results.append(
                {
                    'name': check['name'],
                    'transport': 'websocket',
                    'status_code': status_code,
                    'ok': status_code in check['expected'],
                }
            )
            if status_code not in check['expected']:
                failures.append(
                    {
                        'name': check['name'],
                        'expected': sorted(check['expected']),
                        'actual': status_code,
                        'body': body,
                    }
                )

        self.stdout.write(json.dumps({'results': results}, ensure_ascii=False, indent=2))

        if failures:
            raise CommandError(
                json.dumps({'failures': failures}, ensure_ascii=False, indent=2)
            )

    def _derive_ws_base_url(self, *, base_url):
        parsed = urlparse(base_url)
        scheme = 'wss' if parsed.scheme == 'https' else 'ws'
        host = parsed.hostname or 'localhost'
        port = parsed.port

        if port in (8000, 8080):
            port = 8001
        elif port is None:
            port = 443 if scheme == 'wss' else 80

        return f'{scheme}://{host}:{port}/ws'

    def _request(self, *, url, headers):
        req = request.Request(url=url, headers=headers, method='GET')
        try:
            with request.urlopen(req, timeout=15) as response:
                body = response.read().decode('utf-8', errors='ignore')
                return response.status, body
        except error.HTTPError as exc:
            body = exc.read().decode('utf-8', errors='ignore')
            return exc.code, body

    def _websocket_handshake(self, *, url):
        parsed = urlparse(url)
        host = parsed.hostname or 'localhost'
        secure = parsed.scheme == 'wss'
        default_port = 443 if secure else 80
        port = parsed.port or default_port
        path = parsed.path or '/'
        if parsed.query:
            path = f'{path}?{parsed.query}'

        key = base64.b64encode(os.urandom(16)).decode('ascii')
        request_lines = [
            f'GET {path} HTTP/1.1',
            f'Host: {host}:{port}',
            'Upgrade: websocket',
            'Connection: Upgrade',
            f'Sec-WebSocket-Key: {key}',
            'Sec-WebSocket-Version: 13',
            '\r\n',
        ]
        raw_request = '\r\n'.join(request_lines).encode('ascii')

        sock = socket.create_connection((host, port), timeout=10)
        try:
            if secure:
                context = ssl.create_default_context()
                sock = context.wrap_socket(sock, server_hostname=host)

            sock.sendall(raw_request)
            response = b''
            while b'\r\n\r\n' not in response and len(response) < 16384:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                response += chunk
        finally:
            sock.close()

        header_text = response.decode('utf-8', errors='ignore')
        status_line = header_text.splitlines()[0] if header_text else ''
        try:
            status_code = int(status_line.split()[1])
        except (IndexError, ValueError):
            status_code = 0

        return status_code, header_text
