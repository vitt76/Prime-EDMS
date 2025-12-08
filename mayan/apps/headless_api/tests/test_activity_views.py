from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from mayan.apps.documents.models import DocumentType, Document
from mayan.apps.events.models import Action


class HeadlessActivityFeedAPITests(APITestCase):
    """Tests for GET /api/v4/headless/activity/feed/ endpoint."""

    def setUp(self):
        from django.contrib.auth import get_user_model

        User = get_user_model()
        self.user = User.objects.create_user(
            username='activity-user',
            password='ActivityPass123!'
        )
        self.other_user = User.objects.create_user(
            username='other-user',
            password='OtherPass123!'
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.doc_type = DocumentType.objects.create(label='Reports')
        self.document = Document.objects.create(
            document_type=self.doc_type,
            label='Quarterly Report',
            description='Q1'
        )

        # Create actions for both users
        Action.objects.create(
            actor=self.user,
            verb='document_created',
            target=self.document,
            timestamp=timezone.now()
        )
        Action.objects.create(
            actor=self.other_user,
            verb='document_created',
            target=self.document,
            timestamp=timezone.now()
        )

    def test_filter_my_actions(self):
        response = self.client.get('/api/v4/headless/activity/feed/?filter=my_actions')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['page'], 1)
        actor_ids = {item['actor']['id'] for item in response.data['results']}
        self.assertEqual(actor_ids, {self.user.pk})

    def test_filter_all(self):
        response = self.client.get('/api/v4/headless/activity/feed/?filter=all&page_size=10')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data['count'], 2)

