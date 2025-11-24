from django.contrib.auth import get_user_model

from rest_framework import serializers
from rest_framework.authtoken.models import Token


class TokenSerializer(serializers.ModelSerializer):
    """
    Сериализатор для REST-управления DRF токенами.
    Возвращает ключ, владельца и дату создания. Поле `user_id`
    используется только для чтения, чтобы не раскрывать структуру
    модели Token наружу.
    """

    user_id = serializers.IntegerField(source='user.pk', read_only=True)

    class Meta:
        model = Token
        fields = ('key', 'user_id', 'created')
        read_only_fields = fields


class TokenCreateSerializer(serializers.Serializer):
    """
    Используется только для валидации входных данных при создании/ротации.
    Если `user_id` не передан, токен создаётся для текущего пользователя.
    """

    user_id = serializers.IntegerField(required=False)

    def validate_user_id(self, value):
        User = get_user_model()
        try:
            return User.objects.get(pk=value)
        except User.DoesNotExist:
            raise serializers.ValidationError('User does not exist.')

