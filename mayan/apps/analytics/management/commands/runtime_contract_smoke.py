import json
from urllib import error, request

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Run live HTTP smoke checks for tenant-scoped runtime contracts.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--base-url',
            default='http://localhost:8000',
            help='Base URL to probe from inside the runtime container.',
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

    def handle(self, *args, **options):
        base_url = options['base_url'].rstrip('/')
        token = options['token']
        organization_id = options['organization_id']

        checks = [
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
                'name': 'distribution_share_links_ok',
                'path': '/api/v4/distribution/share_links/',
                'headers': {
                    'Authorization': f'Token {token}',
                    'X-Organization-Id': organization_id,
                },
                'expected': {200},
            },
        ]

        failures = []
        results = []

        for check in checks:
            status_code, body = self._request(
                url=f'{base_url}{check["path"]}',
                headers=check['headers'],
            )
            results.append(
                {
                    'name': check['name'],
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

    def _request(self, *, url, headers):
        req = request.Request(url=url, headers=headers, method='GET')
        try:
            with request.urlopen(req, timeout=15) as response:
                body = response.read().decode('utf-8', errors='ignore')
                return response.status, body
        except error.HTTPError as exc:
            body = exc.read().decode('utf-8', errors='ignore')
            return exc.code, body
