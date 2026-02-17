"""
Tests for ShareLink model business logic: is_valid(), check_password(), and portal expired response.
"""

import os

from django.conf import settings
from django.core.files import File
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from mayan.apps.documents.models import Document, DocumentFile, DocumentType
from mayan.apps.organizations.models import Organization, UserOrganizationRole

from ..models import (
    GeneratedRendition,
    Publication,
    PublicationItem,
    RenditionPreset,
    ShareLink,
)

try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
except Exception:
    User = None


def _add_file_to_document(document):
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


class ShareLinkIsValidTestCase(TestCase):
    """ShareLink.is_valid() returns False when expired or limits reached."""

    def setUp(self):
        super().setUp()
        self.org = Organization.objects.create(
            name='Test Org',
            slug='test-org',
            email='test@example.com',
            status='active',
            deployment_mode='saas',
        )
        self.user = User.objects.create_user(
            username='shareuser',
            email='share@example.com',
            password='testpass123',
        ) if User else None
        if self.user:
            UserOrganizationRole.objects.create(
                user=self.user,
                organization=self.org,
                role=UserOrganizationRole.ROLE_OWNER,
                is_default=True,
            )
        self.document_type = DocumentType.objects.create(label='Test Type')
        self.document = Document.objects.create(
            label='Test Doc',
            document_type=self.document_type,
            organization=self.org,
        )
        _add_file_to_document(self.document)
        self.document.refresh_from_db()
        self.preset = RenditionPreset.objects.create(
            name='Test Preset',
            resource_type='image',
            format='png',
        )
        self.publication = Publication.objects.create(
            owner=self.user,
            title='Test Pub',
        )
        self.item = PublicationItem.objects.create(
            publication=self.publication,
            document_file=self.document.file_latest,
        )
        self.rendition = GeneratedRendition.objects.create(
            publication_item=self.item,
            preset=self.preset,
            status='completed',
        )

    def test_is_valid_false_when_expires_at_in_past(self):
        """When expires_at is in the past, is_valid() returns False."""
        link = ShareLink.objects_unfiltered.create(
            rendition=self.rendition,
            organization=self.org,
            expires_at=timezone.now() - timezone.timedelta(days=1),
        )
        self.assertFalse(link.is_valid())

    def test_is_valid_true_when_expires_at_in_future(self):
        """When expires_at is in the future, is_valid() returns True (other limits not set)."""
        link = ShareLink.objects_unfiltered.create(
            rendition=self.rendition,
            organization=self.org,
            expires_at=timezone.now() + timezone.timedelta(days=1),
        )
        self.assertTrue(link.is_valid())

    def test_is_valid_false_when_max_downloads_reached(self):
        """When max_downloads is set and downloads_count >= max_downloads, is_valid() returns False."""
        link = ShareLink.objects_unfiltered.create(
            rendition=self.rendition,
            organization=self.org,
            max_downloads=2,
            downloads_count=2,
        )
        self.assertFalse(link.is_valid())

    def test_is_valid_true_when_downloads_below_max(self):
        """When downloads_count < max_downloads, is_valid() returns True (for download limit)."""
        link = ShareLink.objects_unfiltered.create(
            rendition=self.rendition,
            organization=self.org,
            max_downloads=3,
            downloads_count=1,
        )
        self.assertTrue(link.is_valid())

    def test_is_valid_false_when_max_views_reached(self):
        """When max_views is set and views_count >= max_views, is_valid() returns False."""
        link = ShareLink.objects_unfiltered.create(
            rendition=self.rendition,
            organization=self.org,
            max_views=1,
            views_count=1,
        )
        self.assertFalse(link.is_valid())

    def test_is_valid_true_when_views_below_max(self):
        """When views_count < max_views, is_valid() returns True (for views limit)."""
        link = ShareLink.objects_unfiltered.create(
            rendition=self.rendition,
            organization=self.org,
            max_views=5,
            views_count=2,
        )
        self.assertTrue(link.is_valid())


class ShareLinkCheckPasswordTestCase(TestCase):
    """ShareLink.check_password() behavior with and without password."""

    def setUp(self):
        super().setUp()
        self.org = Organization.objects.create(
            name='Test Org',
            slug='test-org',
            email='test@example.com',
            status='active',
            deployment_mode='saas',
        )
        self.user = User.objects.create_user(
            username='shareuser',
            email='share@example.com',
            password='testpass123',
        ) if User else None
        if self.user:
            UserOrganizationRole.objects.create(
                user=self.user,
                organization=self.org,
                role=UserOrganizationRole.ROLE_OWNER,
                is_default=True,
            )
        self.document_type = DocumentType.objects.create(label='Test Type')
        self.document = Document.objects.create(
            label='Test Doc',
            document_type=self.document_type,
            organization=self.org,
        )
        _add_file_to_document(self.document)
        self.document.refresh_from_db()
        self.preset = RenditionPreset.objects.create(
            name='Test Preset',
            resource_type='image',
            format='png',
        )
        self.publication = Publication.objects.create(
            owner=self.user,
            title='Test Pub',
        )
        self.item = PublicationItem.objects.create(
            publication=self.publication,
            document_file=self.document.file_latest,
        )
        self.rendition = GeneratedRendition.objects.create(
            publication_item=self.item,
            preset=self.preset,
            status='completed',
        )

    def test_check_password_no_password_hash_returns_true(self):
        """When password_hash is empty, check_password returns True for any input (no password set)."""
        link = ShareLink.objects_unfiltered.create(
            rendition=self.rendition,
            organization=self.org,
            password_hash=None,
        )
        self.assertTrue(link.check_password(''))
        self.assertTrue(link.check_password('anything'))

    def test_check_password_correct_password_returns_true(self):
        """When password is set, check_password with correct password returns True."""
        link = ShareLink.objects_unfiltered.create(
            rendition=self.rendition,
            organization=self.org,
        )
        link.set_password('secret123')
        link.save()
        self.assertTrue(link.check_password('secret123'))

    def test_check_password_wrong_password_returns_false(self):
        """When password is set, check_password with wrong password returns False."""
        link = ShareLink.objects_unfiltered.create(
            rendition=self.rendition,
            organization=self.org,
        )
        link.set_password('secret123')
        link.save()
        self.assertFalse(link.check_password('wrong'))
        self.assertFalse(link.check_password(''))


class ShareLinkPortalExpiredTestCase(TestCase):
    """Portal view returns 410 when share link is expired."""

    def setUp(self):
        super().setUp()
        self.org = Organization.objects.create(
            name='Test Org',
            slug='test-org',
            email='test@example.com',
            status='active',
            deployment_mode='saas',
        )
        self.user = User.objects.create_user(
            username='shareuser',
            email='share@example.com',
            password='testpass123',
        ) if User else None
        if self.user:
            UserOrganizationRole.objects.create(
                user=self.user,
                organization=self.org,
                role=UserOrganizationRole.ROLE_OWNER,
                is_default=True,
            )
        self.document_type = DocumentType.objects.create(label='Test Type')
        self.document = Document.objects.create(
            label='Test Doc',
            document_type=self.document_type,
            organization=self.org,
        )
        _add_file_to_document(self.document)
        self.document.refresh_from_db()
        self.preset = RenditionPreset.objects.create(
            name='Test Preset',
            resource_type='image',
            format='png',
        )
        self.publication = Publication.objects.create(
            owner=self.user,
            title='Test Pub',
        )
        self.item = PublicationItem.objects.create(
            publication=self.publication,
            document_file=self.document.file_latest,
        )
        self.rendition = GeneratedRendition.objects.create(
            publication_item=self.item,
            preset=self.preset,
            status='completed',
        )
        self.expired_link = ShareLink.objects_unfiltered.create(
            rendition=self.rendition,
            organization=self.org,
            expires_at=timezone.now() - timezone.timedelta(days=1),
        )

    def test_portal_expired_returns_410_json(self):
        """Request to portal with expired token and Accept: application/json returns 410 and JSON."""
        from django.test import Client
        client = Client()
        url = reverse(
            'distribution:portal',
            kwargs={'token': self.expired_link.token},
        )
        response = client.get(url, HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, 410)
        self.assertEqual(response.get('Content-Type', '').split(';')[0].strip(), 'application/json')
        data = response.json()
        self.assertIn('error', data)
        self.assertIn('reason', data)

    def test_portal_expired_returns_410_html(self):
        """Request to portal with expired token (browser) returns 410 and link_expired template."""
        from django.test import Client
        client = Client()
        url = reverse(
            'distribution:portal',
            kwargs={'token': self.expired_link.token},
        )
        response = client.get(url)
        self.assertEqual(response.status_code, 410)
        self.assertContains(response, 'Ссылка', status_code=410)
