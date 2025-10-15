from django.utils.translation import ugettext_lazy as _

from mayan.apps.rest_api import serializers

from ..models import RenditionPreset


class RenditionPresetSerializer(serializers.HyperlinkedModelSerializer):
    publications_url = serializers.HyperlinkedIdentityField(
        lookup_url_kwarg='preset_id',
        view_name='rest_api:renditionpreset-list'
    )

    class Meta:
        extra_kwargs = {
            'url': {
                'lookup_url_kwarg': 'preset_id',
                'view_name': 'rest_api:renditionpreset-detail'
            }
        }
        fields = (
            'id', 'resource_type', 'format', 'width', 'height', 'quality',
            'watermark', 'name', 'description', 'created', 'modified',
            'url', 'publications_url'
        )
        model = RenditionPreset
        read_only_fields = ('id', 'created', 'modified')
