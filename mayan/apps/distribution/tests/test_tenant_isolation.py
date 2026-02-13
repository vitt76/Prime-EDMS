"""
Tests for ShareLink tenant isolation.

Verifies:
1. ShareLink.objects is filtered by current organization context.
2. API list/create with X-Organization-Id returns/creates only that org's links.
3. Public access by token works without organization (unfiltered).
"""

import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.core.files import File

from mayan.apps.documents.models import Document, DocumentFile
from mayan.apps.documents.models import DocumentType

from mayan.apps.organizations.managers import (
    clear_current_organization,
    set_current_organization,
)
from mayan.apps.organizations.models import Organization, UserOrganizationRole

from ..models import (
    Publication,
    PublicationItem,
    GeneratedRendition,
    ShareLink,
    RenditionPreset,
)

User = get_user_model()


class ShareLinkTenantIsolationTestMixin:
    """Mixin: two orgs, two users, document type, and one ShareLink per org."""

    def setUp(self):
        super().setUp()

        self.org1 = Organization.objects.create(
            name='Org Alpha',
            slug='org-alpha',
            email='alpha@example.com',
            status='active',
            deployment_mode='saas',
        )
        self.org2 = Organization.objects.create(
            name='Org Beta',
            slug='org-beta',
            email='beta@example.com',
            status='active',
            deployment_mode='saas',
        )

        self.user1 = User.objects.create_user(
            username='user_alpha',
            email='u1@alpha.example.com',
            password='testpass123',
        )
        self.user2 = User.objects.create_user(
            username='user_beta',
            email='u2@beta.example.com',
            password='testpass123',
        )

        UserOrganizationRole.objects.create(
            user=self.user1,
            organization=self.org1,
            role=UserOrganizationRole.ROLE_OWNER,
            is_default=True,
        )
        UserOrganizationRole.objects.create(
            user=self.user2,
            organization=self.org2,
            role=UserOrganizationRole.ROLE_OWNER,
            is_default=True,
        )

        self.document_type = DocumentType.objects.create(label='Test Type')

        # Doc + file for org1
        self.doc1 = Document.objects.create(
            label='Alpha Doc',
            document_type=self.document_type,
            organization=self.org1,
        )
        self._add_file_to_document(self.doc1)
        self.doc1.refresh_from_db()

        # Doc + file for org2
        self.doc2 = Document.objects.create(
            label='Beta Doc',
            document_type=self.document_type,
            organization=self.org2,
        )
        self._add_file_to_document(self.doc2)
        self.doc2.refresh_from_db()

        # Preset (global)
        self.preset = RenditionPreset.objects.create(
            name='Test Preset',
            resource_type='image',
            format='png',
        )

        # Publication + item + rendition + share link for org1
        self.pub1 = Publication.objects.create(
            owner=self.user1,
            title='Pub Alpha',
        )
        self.item1 = PublicationItem.objects.create(
            publication=self.pub1,
            document_file=self.doc1.file_latest,
        )
        self.rendition1 = GeneratedRendition.objects.create(
            publication_item=self.item1,
            preset=self.preset,
            status='completed',
        )
        self.share_link1 = ShareLink.objects_unfiltered.create(
            rendition=self.rendition1,
            organization=self.org1,
        )

        # Publication + item + rendition + share link for org2
        self.pub2 = Publication.objects.create(
            owner=self.user2,
            title='Pub Beta',
        )
        self.item2 = PublicationItem.objects.create(
            publication=self.pub2,
            document_file=self.doc2.file_latest,
        )
        self.rendition2 = GeneratedRendition.objects.create(
            publication_item=self.item2,
            preset=self.preset,
            status='completed',
        )
        self.share_link2 = ShareLink.objects_unfiltered.create(
            rendition=self.rendition2,
            organization=self.org2,
        )

    def _add_file_to_document(self, document):
        """Add a minimal file to document so file_latest exists."""
        path = os.path.join(
            settings.BASE_DIR, 'apps', 'documents', 'tests', 'contrib',
            'sample_documents', 'title_page.png'
        )
        if not os.path.exists(path):
            path = os.path.join(
                settings.BASE_DIR, 'mayan', 'apps', 'documents', 'tests',
                'contrib', 'sample_documents', 'title_page.png'
            )
        if os.path.exists(path):
            with open(path, 'rb') as f:
                doc_file = DocumentFile(
                    document=document,
                    file=File(f),
                    filename=os.path.basename(path),
                )
                doc_file.save()
        else:
            from django.core.files.base import ContentFile
            doc_file = DocumentFile(
                document=document,
                file=File(ContentFile(b'\x89PNG\r\n\x1a\n')),
                filename='minimal.png',
            )
            doc_file.save()

    def tearDown(self):
        clear_current_organization()
        super().tearDown()


class ShareLinkFilteredByOrganizationTest(
    ShareLinkTenantIsolationTestMixin, TestCase
):
    """ShareLink.objects.all() returns only current org's links."""

    def test_sharelink_filtered_by_organization(self):
        set_current_organization(self.org1)
        links = list(ShareLink.objects.all())
        self.assertEqual(len(links), 1)
        self.assertEqual(links[0].pk, self.share_link1.pk)
        self.assertEqual(links[0].organization_id, self.org1.pk)

        set_current_organization(self.org2)
        links = list(ShareLink.objects.all())
        self.assertEqual(len(links), 1)
        self.assertEqual(links[0].pk, self.share_link2.pk)
        self.assertEqual(links[0].organization_id, self.org2.pk)

    def test_unfiltered_sees_both(self):
        clear_current_organization()
        count = ShareLink.objects_unfiltered.count()
        self.assertGreaterEqual(count, 2)
        ids = set(
            ShareLink.objects_unfiltered.values_list('pk', flat=True)
        )
        self.assertIn(self.share_link1.pk, ids)
        self.assertIn(self.share_link2.pk, ids)


class ShareLinkAPITenantIsolationTest(
    ShareLinkTenantIsolationTestMixin, TestCase
):
    """API list with X-Organization-Id returns only that org's share links."""

    def test_api_list_respects_organization(self):
        from rest_framework.test import APIClient
        from rest_framework import status

        client = APIClient()
        client.force_authenticate(user=self.user1)

        try:
            url = reverse('distribution:sharelink-list')
        except Exception:
            url = '/api/v4/distribution/share_links/'
        response = client.get(
            url,
            HTTP_X_ORGANIZATION_ID=str(self.org1.pk),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        results = data.get('results', data) if isinstance(data, dict) else data
        if isinstance(results, list):
            ids = [r['id'] for r in results]
        else:
            ids = []
        self.assertIn(self.share_link1.id, ids)
        self.assertNotIn(self.share_link2.id, ids)

        response2 = client.get(
            url,
            HTTP_X_ORGANIZATION_ID=str(self.org2.pk),
        )
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        data2 = response2.json()
        results2 = data2.get('results', data2) if isinstance(data2, dict) else data2
        if isinstance(results2, list):
            ids2 = [r['id'] for r in results2]
        else:
            ids2 = []
        self.assertIn(self.share_link2.id, ids2)
        self.assertNotIn(self.share_link1.id, ids2)


class ShareLinkPublicAccessByTokenTest(
    ShareLinkTenantIsolationTestMixin, TestCase
):
    """Public portal access by token works without organization in URL."""

    def test_public_access_by_token_unfiltered(self):
        # Resolve by token using unfiltered manager (as portal does)
        link = ShareLink.objects_unfiltered.filter(
            token=self.share_link1.token
        ).first()
        self.assertIsNotNone(link)
        self.assertEqual(link.pk, self.share_link1.pk)

        link2 = ShareLink.objects_unfiltered.filter(
            token=self.share_link2.token
        ).first()
        self.assertIsNotNone(link2)
        self.assertEqual(link2.pk, self.share_link2.pk)

    def test_portal_view_returns_200_for_valid_token(self):
        from django.test import Client
        client = Client()
        url = reverse(
            'distribution:portal',
            kwargs={'token': self.share_link1.token},
        )
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
