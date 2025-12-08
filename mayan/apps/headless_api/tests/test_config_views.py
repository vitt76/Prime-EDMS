from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from mayan.apps.documents.models import DocumentType
from mayan.apps.metadata.models import DocumentTypeMetadataType, MetadataType


class HeadlessDocumentTypeConfigAPITests(APITestCase):
    """Tests for headless document type configuration endpoints."""

    def setUp(self):
        self.user = self._create_user()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.doc_type = DocumentType.objects.create(label='Images')

        self.required_meta = MetadataType.objects.create(
            name='author',
            label='Author',
            validation='^.{3,}$'
        )
        self.optional_meta = MetadataType.objects.create(
            name='description',
            label='Description'
        )

        DocumentTypeMetadataType.objects.create(
            document_type=self.doc_type,
            metadata_type=self.required_meta,
            required=True
        )
        DocumentTypeMetadataType.objects.create(
            document_type=self.doc_type,
            metadata_type=self.optional_meta,
            required=False
        )

    def _create_user(self):
        from django.contrib.auth import get_user_model

        User = get_user_model()
        return User.objects.create_user(
            username='config-user',
            password='ConfigPass123!'
        )

    def test_list_document_types(self):
        response = self.client.get('/api/v4/headless/config/document_types/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertGreaterEqual(len(response.data), 1)
        first = response.data[0]
        self.assertIn('id', first)
        self.assertIn('label', first)
        self.assertIn('url', first)

    def test_detail_includes_required_optional_metadata(self):
        url = f'/api/v4/headless/config/document_types/{self.doc_type.pk}/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data

        self.assertEqual(data['id'], self.doc_type.pk)
        required_names = {field['name'] for field in data['required_metadata']}
        optional_names = {field['name'] for field in data['optional_metadata']}

        self.assertIn('author', required_names)
        self.assertIn('description', optional_names)

