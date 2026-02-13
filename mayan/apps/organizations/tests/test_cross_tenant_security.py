"""
Sprint 4 Security: Cross-tenant access prevention tests.

Verifies that a user who is member of org A only cannot obtain data
belonging to org B via API (documents, share links, analytics dashboard, reports).
Middleware resolves X-Organization-Id only when user is member; otherwise
falls back to user default org. Tenant-scoped APIs filter by request.organization.
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from mayan.apps.analytics.permissions import permission_analytics_view_asset_bank
from mayan.apps.documents.models import Document, DocumentType
from mayan.apps.organizations.models import Organization, UserOrganizationRole
from mayan.apps.permissions.classes import Permission
from mayan.apps.permissions.models import Role

User = get_user_model()


class CrossTenantAPISecurityTestCase(TestCase):
    """
    User in org A only: requests with X-Organization-Id: org_B must not
    return org B data. Middleware sets request.organization to None then
    to user default (org A), so APIs return org A data only.
    """

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='sec_user',
            password='pass123',
            email='sec@example.com',
        )
        self.org_a = Organization.objects.create(
            name='Org A',
            slug='org-a',
            email='a@example.com',
            status='active',
            deployment_mode='saas',
        )
        self.org_b = Organization.objects.create(
            name='Org B',
            slug='org-b',
            email='b@example.com',
            status='active',
            deployment_mode='saas',
        )
        UserOrganizationRole.objects.create(
            user=self.user,
            organization=self.org_a,
            role=UserOrganizationRole.ROLE_OWNER,
            is_default=True,
        )
        # user is NOT in org_b
        role = Role.objects.create(label='Analytics Viewer')
        role.grant(permission=permission_analytics_view_asset_bank)
        group = Group.objects.create(name='Sec Test Group')
        role.groups.add(group)
        group.user_set.add(self.user)
        Permission.invalidate_cache()
        self.document_type = DocumentType.objects.create(label='Test')
        self.doc_a1 = Document.objects.create(
            label='Doc A1',
            document_type=self.document_type,
            organization=self.org_a,
        )
        self.doc_a2 = Document.objects.create(
            label='Doc A2',
            document_type=self.document_type,
            organization=self.org_a,
        )
        self.doc_b1 = Document.objects.create(
            label='Doc B1',
            document_type=self.document_type,
            organization=self.org_b,
        )
        self.client.force_authenticate(user=self.user)

    def test_dashboard_with_other_org_header_returns_own_org_metrics(self):
        """GET dashboard with X-Organization-Id: org_B (user not in org_B) -> metrics are org_A (default)."""
        response = self.client.get(
            '/api/v4/headless/analytics/dashboard/',
            HTTP_X_ORGANIZATION_ID=str(self.org_b.pk),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['organization'], str(self.org_a.pk))
        self.assertEqual(response.data['organization_name'], self.org_a.name)
        self.assertEqual(response.data['total_documents'], 2)

    def test_dashboard_with_own_org_header_returns_own_org_metrics(self):
        """GET dashboard with X-Organization-Id: org_A -> org A metrics."""
        response = self.client.get(
            '/api/v4/headless/analytics/dashboard/',
            HTTP_X_ORGANIZATION_ID=str(self.org_a.pk),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['organization'], str(self.org_a.pk))
        self.assertEqual(response.data['total_documents'], 2)

    def test_reports_generate_with_other_org_header_creates_task_for_default_org(self):
        """POST reports/generate/ with X-Organization-Id: org_B -> task created for org_A (default)."""
        from mayan.apps.analytics.models import AnalyticsReportTask
        response = self.client.post(
            '/api/v4/headless/analytics/reports/generate/',
            {'report_type': 'asset_usage'},
            format='json',
            HTTP_X_ORGANIZATION_ID=str(self.org_b.pk),
        )
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        task_id = response.data['task_id']
        task = AnalyticsReportTask.objects.get(pk=task_id)
        self.assertEqual(task.organization_id, self.org_a.pk)
