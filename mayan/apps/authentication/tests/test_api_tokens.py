from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.authtoken.models import Token

from mayan.apps.rest_api.tests.base import BaseAPITestCase


class AuthenticationTokenAPIViewTestCase(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        User = get_user_model()

        self._test_user = User.objects.create_user(
            username='token-user', password='test'
        )
        self._test_user.cleartext_password = 'test'

        self._other_user = User.objects.create_user(
            username='token-user-2', password='test'
        )
        self._other_user.cleartext_password = 'test'

        self._test_superuser = User.objects.create_superuser(
            username='token-admin', password='test'
        )
        self._test_superuser.cleartext_password = 'test'

        self.client.login(
            username=self._test_user.username,
            password=self._test_user.cleartext_password
        )

    def _request_token_list(self):
        return self.get(viewname='rest_api:auth-token-list')

    def _request_token_create(self, data=None):
        return self.post(
            viewname='rest_api:auth-token-list', data=data or {}
        )

    def _request_token_detail(self, token):
        return self.get(
            viewname='rest_api:auth-token-detail', kwargs={'token_key': token.key}
        )

    def _request_token_delete(self, token):
        return self.delete(
            viewname='rest_api:auth-token-detail', kwargs={'token_key': token.key}
        )

    def test_token_list_returns_only_own_tokens(self):
        token = Token.objects.create(user=self._test_user)
        Token.objects.create(user=self._other_user)

        response = self._request_token_list()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['key'], token.key)

    def test_token_list_as_superuser_returns_all_tokens(self):
        Token.objects.all().delete()
        Token.objects.create(user=self._test_user)
        Token.objects.create(user=self._other_user)

        self.client.logout()
        self.client.login(
            username=self._test_superuser.username,
            password=self._test_superuser.cleartext_password
        )

        response = self._request_token_list()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)

    def test_token_create_rotates_existing(self):
        old_token = Token.objects.create(user=self._test_user)

        response = self._request_token_create()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        new_token_key = response.data['key']
        self.assertNotEqual(old_token.key, new_token_key)
        self.assertEqual(
            Token.objects.filter(user=self._test_user).count(), 1
        )

    def test_token_create_for_other_user_without_permission(self):
        response = self._request_token_create(
            data={'user_id': self._other_user.pk}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_token_create_for_other_user_with_superuser(self):
        self.client.logout()
        self.client.login(
            username=self._test_superuser.username,
            password=self._test_superuser.cleartext_password
        )

        response = self._request_token_create(
            data={'user_id': self._other_user.pk}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Token.objects.filter(user=self._other_user).exists()
        )

    def test_token_delete(self):
        token = Token.objects.create(user=self._test_user)

        response = self._request_token_delete(token=token)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Token.objects.filter(pk=token.pk).exists())

