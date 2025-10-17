from django.utils.translation import ugettext_lazy as _

from mayan.apps.rest_api import serializers

from ..models import AccessLog


class AccessLogSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id', 'share_link', 'event', 'ip_address', 'user_agent',
            'timestamp', 'rendition'
        )
        model = AccessLog
        read_only_fields = (
            'id', 'timestamp', 'rendition'
        )
