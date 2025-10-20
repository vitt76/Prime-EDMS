from mayan.apps.rest_api import serializers

from ..models import ShareLink


class ShareLinkMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShareLink
        fields = ('id', 'token', 'expires_at', 'downloads_count')
        read_only_fields = fields
