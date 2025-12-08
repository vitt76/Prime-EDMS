from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from mayan.apps.documents.events import event_document_created
from mayan.apps.documents.models import Document, DocumentType


class HeadlessMyUploadsViewTests(APITestCase):
    """Ensure my_uploads endpoint returns only documents created by current user."""

    def setUp(self):
        User = get_user_model()
        self.user1 = User.objects.create_user(
            username='user1', password='pass123', is_staff=True, is_superuser=True
        )
        self.user2 = User.objects.create_user(
            username='user2', password='pass123', is_staff=True, is_superuser=True
        )

        self.doc_type = DocumentType.objects.create(label='Default')

        self.doc1 = Document.objects.create(
            document_type=self.doc_type,
            label='Doc 1'
        )
        self.doc2 = Document.objects.create(
            document_type=self.doc_type,
            label='Doc 2'
        )

        # Emit events to populate Action stream
        event_document_created.commit(actor=self.user1, target=self.doc1)
        event_document_created.commit(actor=self.user2, target=self.doc2)

        self.client = APIClient()
        self.url = '/api/v4/headless/documents/my_uploads/'

    def test_returns_only_user_documents(self):
        self.client.force_authenticate(user=self.user1)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [item['id'] for item in response.data['results']]
        self.assertIn(self.doc1.pk, ids)
        self.assertNotIn(self.doc2.pk, ids)

