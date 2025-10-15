from django.utils.translation import ugettext_lazy as _

from mayan.apps.rest_api import serializers

from ..models import AccessLog


class AccessLogSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        extra_kwargs = {
            'url': {
                'lookup_url_kwarg': 'access_log_id',
                'view_name': 'rest_api:accesslog-detail'
            }
        }
        fields = (
            'id', 'share_link', 'event', 'ip_address', 'user_agent',
            'timestamp', 'url'
        )
        model = AccessLog
        read_only_fields = ('id', 'timestamp')
