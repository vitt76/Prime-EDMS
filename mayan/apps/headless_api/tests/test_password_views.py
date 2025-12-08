from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient, APITestCase


User = get_user_model()


class HeadlessPasswordChangeAPITests(APITestCase):
    """Tests for POST /api/v4/headless/password/change/ endpoint."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='Oldpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.url = '/api/v4/headless/password/change/'

    def test_password_change_success(self):
        response = self.client.post(
            self.url,
            {
                'current_password': 'Oldpass123',
                'new_password': 'Newpass123!',
                'new_password_confirm': 'Newpass123!'
            },
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('status'), 'success')

        # Password should actually change
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('Newpass123!'))

    def test_password_change_wrong_current(self):
        response = self.client.post(
            self.url,
            {
                'current_password': 'WrongPass',
                'new_password': 'Newpass123!',
                'new_password_confirm': 'Newpass123!'
            },
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get('error_code'), 'INVALID_CURRENT_PASSWORD')

    def test_password_validation_failed(self):
        response = self.client.post(
            self.url,
            {
                'current_password': 'Oldpass123',
                'new_password': 'short',
                'new_password_confirm': 'short'
            },
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get('error_code'), 'PASSWORD_VALIDATION_FAILED')

