"""
Sprint 4 Load Testing: Dashboard, document list, analytics sub-endpoints.

Usage:
  locust -f tests/load/locustfile.py --host=https://your-mayan-host
  With auth (token): set env AUTH_TOKEN=your-token
  With org context: set env X_ORGANIZATION_ID=uuid-of-org (for tenant-scoped endpoints)
"""
import os
from locust import HttpUser, between, task


def _headers(user):
    """Build headers with optional auth and X-Organization-Id."""
    h = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    token = os.environ.get('AUTH_TOKEN')
    if token:
        h['Authorization'] = f'Token {token}'
    org_id = os.environ.get('X_ORGANIZATION_ID')
    if org_id:
        h['X-Organization-Id'] = org_id
    return h


class AnalyticsUser(HttpUser):
    """Simulates users hitting analytics dashboard and related endpoints."""
    wait_time = between(1, 3)

    def on_start(self):
        self._headers = _headers(self)

    @task(3)
    def dashboard_main(self):
        """GET main tenant-scoped dashboard (cached after first request)."""
        self.client.get(
            '/api/v4/headless/analytics/dashboard/',
            headers=self._headers
        )

    @task(2)
    def asset_bank_top_metrics(self):
        """GET asset bank top metrics sub-endpoint."""
        self.client.get(
            '/api/v4/headless/analytics/dashboard/assets/top-metrics/',
            headers=self._headers
        )

    @task(1)
    def document_list_optimized(self):
        """GET optimized document list (paginated)."""
        self.client.get(
            '/api/v4/documents/optimized/',
            headers=self._headers
        )


class DocumentListUser(HttpUser):
    """Simulates users browsing document list only."""
    wait_time = between(0.5, 2)

    def on_start(self):
        self._headers = _headers(self)

    @task
    def document_list(self):
        """GET standard document list (paginated)."""
        self.client.get(
            '/api/v4/documents/',
            headers=self._headers
        )


