"""
Sprint 4 (Collaboration) verification: Public Sharing, Comments.

Creates test data and runs:
  Test 1: Anonymous access to public share link -> 200 OK.
  Test 2: Expired share link -> 403.
  Test 3: User B cannot delete User A's comment -> 403.

Run (from project root):
  python manage.py verify_sprint4

Requires: migrations applied (cabinets 0007/0008/0009, document_comments),
          organizations app, at least one DocumentType.
"""

import logging
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APIClient

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Verify Sprint 4: public cabinet share, expiry, comment owner-only delete'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Sprint 4 (Collaboration) verification'))
        self.stdout.write('=' * 60)

        api_prefix = '/api/v4'
        public_share_path = api_prefix + '/public/shares/'

        # Resolve dependencies
        User = self._get_user_model()
        Organization = self._get_organization_model()
        Document = self._get_document_model()
        DocumentType = self._get_document_type_model()
        DocumentFile = self._get_document_file_model()
        Cabinet = self._get_cabinet_model()
        CabinetShare = self._get_cabinet_share_model()
        Comment = self._get_comment_model()

        org = Organization.objects.first()
        if not org:
            self.stdout.write(self.style.ERROR('No organization. Create one first.'))
            return
        user_a = User.objects.filter(is_superuser=True).first() or User.objects.first()
        if not user_a:
            self.stdout.write(self.style.ERROR('No user. Create one first.'))
            return
        user_b = User.objects.exclude(pk=user_a.pk).first()
        if not user_b:
            self.stdout.write(self.style.WARNING('Only one user; creating second user for comment test.'))
            user_b = User.objects.create_user(
                username='verify_sprint4_b',
                email='verify_sprint4_b@test.local',
                password='testpass123',
            )

        doc_type = DocumentType.objects.first()
        if not doc_type:
            doc_type = DocumentType.objects.create(label='Verify Sprint4')
        doc = Document.objects.create(
            label='Sprint4 Verify Doc',
            document_type=doc_type,
            organization=org,
        )
        try:
            df = DocumentFile(document=doc, filename='verify_sprint4.txt')
            df.file.save('verify_sprint4.txt', ContentFile(b'content'), save=True)
        except Exception as e:
            self.stdout.write(self.style.WARNING('DocumentFile: %s' % e))
            doc.delete()
            return

        cabinet = Cabinet.objects.create(label='Sprint4 Verify Cabinet', organization=org)
        cabinet.documents.add(doc)

        # Share 1: valid (no password, no expiry)
        share_valid = CabinetShare.objects.create(
            cabinet=cabinet,
            organization=org,
            created_by=user_a,
        )
        share_uuid = str(share_valid.uuid)

        # Test 1: Anonymous access -> Success
        self.stdout.write('Test 1: Anonymous GET public share...')
        client_anon = APIClient()
        resp1 = client_anon.get(public_share_path + '%s/' % share_uuid)
        if resp1.status_code == 200:
            data = getattr(resp1, 'data', None) or resp1.json()
            label = data.get('label', '')
            docs = data.get('documents', [])
            self.stdout.write(self.style.SUCCESS('  PASS: 200, label=%s, documents=%s' % (label, len(docs))))
        else:
            self.stdout.write(self.style.ERROR('  FAIL: %s (expected 200)' % resp1.status_code))

        # Share 2: expired
        from datetime import timedelta
        share_expired = CabinetShare.objects.create(
            cabinet=cabinet,
            organization=org,
            created_by=user_a,
            expires_at=timezone.now() - timedelta(days=1),
        )
        self.stdout.write('Test 2: Expired share GET...')
        resp2 = client_anon.get(public_share_path + '%s/' % str(share_expired.uuid))
        if resp2.status_code == 403:
            data2 = getattr(resp2, 'data', None) or resp2.json()
            if data2.get('expired'):
                self.stdout.write(self.style.SUCCESS('  PASS: 403 with expired=true'))
            else:
                self.stdout.write(self.style.WARNING('  PASS: 403 but no expired flag'))
        else:
            self.stdout.write(self.style.ERROR('  FAIL: %s (expected 403)' % resp2.status_code))

        # Comment: create as User A, delete as User B -> 403
        comment = Comment.objects.create(
            document=doc,
            user=user_a,
            text='Sprint4 verify comment',
        )
        comments_path = api_prefix + '/documents/%s/comments/%s/' % (doc.pk, comment.pk)
        client_b = APIClient()
        client_b.force_authenticate(user=user_b)
        self.stdout.write('Test 3: User B deletes User A comment...')
        resp3 = client_b.delete(comments_path, HTTP_X_ORGANIZATION_ID=str(org.pk))
        if resp3.status_code == 403:
            self.stdout.write(self.style.SUCCESS('  PASS: 403 (only author can delete)'))
        else:
            self.stdout.write(self.style.ERROR('  FAIL: %s (expected 403)' % resp3.status_code))

        # Cleanup
        comment.delete()
        share_expired.delete()
        share_valid.delete()
        cabinet.delete()
        doc.delete()
        if user_b.username == 'verify_sprint4_b':
            user_b.delete()

        self.stdout.write('=' * 60)
        self.stdout.write(self.style.SUCCESS('Verification finished. Review output above.'))

    def _get_user_model(self):
        from django.contrib.auth import get_user_model
        return get_user_model()

    def _get_organization_model(self):
        from mayan.apps.organizations.models import Organization
        return Organization

    def _get_document_model(self):
        from mayan.apps.documents.models import Document
        return Document

    def _get_document_type_model(self):
        from mayan.apps.documents.models import DocumentType
        return DocumentType

    def _get_document_file_model(self):
        from mayan.apps.documents.models import DocumentFile
        return DocumentFile

    def _get_cabinet_model(self):
        from mayan.apps.cabinets.models import Cabinet
        return Cabinet

    def _get_cabinet_share_model(self):
        from mayan.apps.cabinets.models import CabinetShare
        return CabinetShare

    def _get_comment_model(self):
        from mayan.apps.document_comments.models import Comment
        return Comment
