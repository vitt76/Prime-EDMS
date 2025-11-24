from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

from mayan.apps.rest_api import generics

from .serializers import TokenCreateSerializer, TokenSerializer


class APITokenMixin:
    """
    Общая логика фильтрации токенов по правам пользователя.
    """

    def get_queryset(self):
        queryset = Token.objects.all()

        if self.request.user.is_superuser:
            return queryset

        return queryset.filter(user=self.request.user)

    def _get_target_user(self, serializer: TokenCreateSerializer):
        if serializer.validated_data.get('user_id'):
            target_user = serializer.validated_data['user_id']
        else:
            target_user = self.request.user

        if (
            target_user != self.request.user
            and not self.request.user.is_superuser
        ):
            raise PermissionDenied(
                'Недостаточно прав для управления токенами других пользователей.'
            )

        return target_user


class APITokenListView(APITokenMixin, generics.ListCreateAPIView):
    """
    get: вернуть список токенов текущего пользователя (для суперпользователя — всех).
    post: создать токен (при повторном вызове для того же пользователя выполняется ротация ключа).
    """

    serializer_class = TokenSerializer

    def create(self, request, *args, **kwargs):
        input_serializer = TokenCreateSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        user = self._get_target_user(serializer=input_serializer)

        # Делает ротацию ключа.
        Token.objects.filter(user=user).delete()
        token = Token.objects.create(user=user)

        output_serializer = self.get_serializer(instance=token)
        headers = self.get_success_headers(output_serializer.data)

        return Response(
            data=output_serializer.data, status=status.HTTP_201_CREATED,
            headers=headers
        )


class APITokenDetailView(APITokenMixin, generics.RetrieveDestroyAPIView):
    """
    get: вернуть информацию о токене.
    delete: отозвать токен.
    """

    lookup_field = 'key'
    lookup_url_kwarg = 'token_key'
    serializer_class = TokenSerializer

