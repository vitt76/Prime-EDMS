from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from rest_framework import status
from rest_framework.test import APIClient


User = get_user_model()


@override_settings(FRONTEND_URL='http://localhost:5173')
class PublicAuthAndAnalyticsAPITestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.client = APIClient()

    def test_public_login_returns_token_and_redirect_url(self):
        user = User.objects.create_user(
            username='demo@example.com',
            email='demo@example.com',
            password='Password123!',
            is_active=True,
        )

        response = self.client.post(
            '/api/v4/public/auth/login/',
            {
                'email': user.email,
                'password': 'Password123!',
                'remember': True,
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertIn('token', response.data)
        self.assertEqual(response.data['redirect_url'], 'http://localhost:5173')
        self.assertEqual(response.data['user']['email'], user.email)

    def test_public_login_rejects_inactive_user(self):
        User.objects.create_user(
            username='inactive@example.com',
            email='inactive@example.com',
            password='Password123!',
            is_active=False,
        )

        response = self.client.post(
            '/api/v4/public/auth/login/',
            {
                'email': 'inactive@example.com',
                'password': 'Password123!',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, response.data)
        self.assertEqual(response.data['error'], 'account_inactive')

    def test_public_analytics_event_accepts_payload(self):
        response = self.client.post(
            '/api/v4/public/analytics/events/',
            {
                'event': 'page_view',
                'category': 'engagement',
                'label': 'landing',
                'url': 'http://localhost:3000/',
                'referrer': '',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED, response.data)
        self.assertEqual(response.data['status'], 'accepted')
