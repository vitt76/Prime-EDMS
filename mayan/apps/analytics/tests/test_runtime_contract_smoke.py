from unittest import mock

from django.core.management.base import CommandError
from django.test import SimpleTestCase

from mayan.apps.analytics.management.commands.runtime_contract_smoke import (
    Command,
)


class RuntimeContractSmokeCommandTest(SimpleTestCase):
    def setUp(self):
        super().setUp()
        self.command = Command()

    def test_derive_ws_base_url_uses_split_runtime_port(self):
        self.assertEqual(
            self.command._derive_ws_base_url(base_url='http://localhost:8080'),
            'ws://localhost:8001/ws'
        )
        self.assertEqual(
            self.command._derive_ws_base_url(base_url='http://localhost:8000'),
            'ws://localhost:8001/ws'
        )

    def test_derive_ws_base_url_keeps_non_split_port(self):
        self.assertEqual(
            self.command._derive_ws_base_url(base_url='https://example.com:8443'),
            'wss://example.com:8443/ws'
        )

    def test_handle_runs_http_and_websocket_checks(self):
        def fake_request(*, url, headers):
            if 'analytics/health' in url:
                return 200, '{}'
            if 'dashboard/geography' in url:
                return (200 if headers.get('X-Organization-Id') else 400), '{}'
            if 'distribution/campaigns' in url:
                return (200 if headers.get('X-Organization-Id') else 400), '{}'
            if 'distribution/share_links' in url:
                return (200 if headers.get('X-Organization-Id') else 400), '{}'
            raise AssertionError(f'Unexpected HTTP url: {url}')

        websocket_urls = []

        def fake_websocket(*, url):
            websocket_urls.append(url)
            if 'organization_id=' in url:
                return 101, 'HTTP/1.1 101 Switching Protocols'
            return 403, 'HTTP/1.1 403 Forbidden'

        with mock.patch.object(self.command, '_request', side_effect=fake_request):
            with mock.patch.object(
                self.command, '_websocket_handshake', side_effect=fake_websocket
            ):
                self.command.handle(
                    base_url='http://localhost:8080',
                    token='demo-token',
                    organization_id='org-123',
                    ws_base_url='',
                    skip_websocket=False,
                )

        self.assertEqual(len(websocket_urls), 4)
        self.assertTrue(
            all(url.startswith('ws://localhost:8001/ws/') for url in websocket_urls)
        )

    def test_handle_raises_on_failed_websocket_check(self):
        def fake_request(*, url, headers):
            if 'analytics/health' in url:
                return 200, '{}'
            if 'dashboard/geography' in url:
                return (200 if headers.get('X-Organization-Id') else 400), '{}'
            if 'distribution/campaigns' in url:
                return (200 if headers.get('X-Organization-Id') else 400), '{}'
            if 'distribution/share_links' in url:
                return (200 if headers.get('X-Organization-Id') else 400), '{}'
            raise AssertionError(f'Unexpected HTTP url: {url}')

        def fake_websocket(*, url):
            if 'notifications/' in url and 'organization_id=' in url:
                return 500, 'HTTP/1.1 500 Internal Server Error'
            if 'organization_id=' in url:
                return 101, 'HTTP/1.1 101 Switching Protocols'
            return 403, 'HTTP/1.1 403 Forbidden'

        with mock.patch.object(self.command, '_request', side_effect=fake_request):
            with mock.patch.object(
                self.command, '_websocket_handshake', side_effect=fake_websocket
            ):
                with self.assertRaises(CommandError):
                    self.command.handle(
                        base_url='http://localhost:8080',
                        token='demo-token',
                        organization_id='org-123',
                        ws_base_url='',
                        skip_websocket=False,
                    )
