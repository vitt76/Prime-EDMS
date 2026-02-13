from rest_framework import serializers

from .models import UserConsentLog


class UserConsentLogSerializer(serializers.ModelSerializer):
    """Serializer for logging consent from public frontend. IP/User-Agent set on server."""

    consent_type = serializers.ChoiceField(
        choices=[c[0] for c in UserConsentLog.CONSENT_TYPE_CHOICES],
        required=True
    )
    session_id = serializers.CharField(required=False, allow_blank=True, default='')
    url_referer = serializers.URLField(required=False, allow_blank=True, default='')

    class Meta:
        model = UserConsentLog
        fields = ('consent_type', 'session_id', 'url_referer')
