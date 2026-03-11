"""
Tests for ShareLink tenant isolation.

Verifies:
1. ShareLink.objects is filtered by current organization context.
2. API list/create with X-Organization-Id returns/creates only that org's links.
3. Public access by token works without organization (unfiltered).
"""

import os

from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from django.core.files import File

from mayan.apps.documents.models import Document, DocumentFile
from mayan.apps.documents.models import DocumentType
from mayan.apps.organizations.managers import (
    clear_current_organization,
    set_current_organization,
)
from mayan.apps.organizations.tests.mixins import SaaSTenantTestHarnessMixin

from ..models import (
    CampaignPublication,
    DistributionCampaign,
    Publication,
    PublicationItem,
    GeneratedRendition,
    Recipient,
    ShareLink,
    RenditionPreset,
)
from ..permissions import permission_publication_api_view


class ShareLinkTenantIsolationTestMixin(SaaSTenantTestHarnessMixin):
    """Mixin: two orgs, two users, document type, and one ShareLink per org."""

    def setUp(self):
        super().setUp()
        self.org1 = self.create_organization(
            name='Org Alpha',
            slug='org-alpha',
            email='alpha@example.com',
        )
        self.org2 = self.create_organization(
            name='Org Beta',
            slug='org-beta',
            email='beta@example.com',
        )

        self.user1 = self.create_user_in_organization(
            username='user_alpha',
            organization=self.org1,
            is_default=True,
        )
        self.user2 = self.create_user_in_organization(
            username='user_beta',
            organization=self.org2,
            is_default=True,
        )
        self.grant_permissions(
            user=self.user1,
            permissions=(permission_publication_api_view,),
            label='Distribution API View Alpha'
        )
        self.alpha_role = self.grant_permissions(
            user=self.user1,
            permissions=(permission_publication_api_view,),
            label='Distribution API ACL Alpha'
        )
        self.grant_permissions(
            user=self.user2,
            permissions=(permission_publication_api_view,),
            label='Distribution API View Beta'
        )
        self.beta_role = self.grant_permissions(
            user=self.user2,
            permissions=(permission_publication_api_view,),
            label='Distribution API ACL Beta'
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

        self.recipient, _ = Recipient.objects.get_or_create(
            email='distribution-tenant@test.com',
            defaults={'name': 'Distribution Tenant Recipient'}
        )

        # Preset (global)
        self.preset = RenditionPreset.objects.create(
            name='Test Preset',
            resource_type='image',
            format='png',
            recipient=self.recipient,
        )

        # Publication + item + rendition + share link for org1
        self.pub1 = Publication.objects.create(
            owner=self.user1,
            title='Pub Alpha',
            organization=self.org1,
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
        self.grant_access(
            obj=self.share_link1,
            permission=permission_publication_api_view,
            role=self.alpha_role
        )

        # Publication + item + rendition + share link for org2
        self.pub2 = Publication.objects.create(
            owner=self.user2,
            title='Pub Beta',
            organization=self.org2,
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
        self.grant_access(
            obj=self.share_link2,
            permission=permission_publication_api_view,
            role=self.beta_role
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
        from rest_framework import status

        try:
            url = reverse('distribution:sharelink-list')
        except Exception:
            url = '/api/v4/distribution/share_links/'

        response = self.api_client_for(self.user1).get(
            url,
            **self.organization_headers(self.org1)
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

        response2 = self.api_client_for(self.user2).get(
            url,
            **self.organization_headers(self.org2)
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


class DistributionCampaignAPITenantIsolationTest(
    ShareLinkTenantIsolationTestMixin, TestCase
):
    """Campaign API list should stay within the selected organization."""

    def setUp(self):
        super().setUp()

        self.add_user_to_organization(
            user=self.user1,
            organization=self.org2,
            is_default=False,
        )

        self.campaign1 = DistributionCampaign.objects.create(
            owner=self.user1,
            organization=self.org1,
            title='Campaign Alpha',
            metadata={'organization_id': str(self.org1.pk)},
        )
        self.grant_access(
            obj=self.campaign1,
            permission=permission_publication_api_view,
            role=self.alpha_role
        )
        CampaignPublication.objects.create(
            campaign=self.campaign1,
            publication=self.pub1,
        )

        self.campaign2 = DistributionCampaign.objects.create(
            owner=self.user1,
            organization=self.org2,
            title='Campaign Beta',
            metadata={'organization_id': str(self.org2.pk)},
        )
        self.grant_access(
            obj=self.campaign2,
            permission=permission_publication_api_view,
            role=self.alpha_role
        )
        CampaignPublication.objects.create(
            campaign=self.campaign2,
            publication=self.pub2,
        )

    def test_campaign_api_list_respects_organization(self):
        from rest_framework import status

        client = self.api_client_for(self.user1)
        url = '/api/v4/distribution/campaigns/'

        response_org1 = client.get(
            url,
            **self.organization_headers(self.org1)
        )
        self.assertEqual(response_org1.status_code, status.HTTP_200_OK)
        ids_org1 = [item['id'] for item in response_org1.json().get('results', [])]
        self.assertIn(self.campaign1.id, ids_org1)
        self.assertNotIn(self.campaign2.id, ids_org1)

        response_org2 = client.get(
            url,
            **self.organization_headers(self.org2)
        )
        self.assertEqual(response_org2.status_code, status.HTTP_200_OK)
        ids_org2 = [item['id'] for item in response_org2.json().get('results', [])]
        self.assertIn(self.campaign2.id, ids_org2)
        self.assertNotIn(self.campaign1.id, ids_org2)
