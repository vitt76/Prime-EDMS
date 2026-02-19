from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers

from ..models import RenditionPreset


class RenditionPresetSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        validated_data.pop('_instance_extra_data', None)
        request = self.context.get('request')
        if request and getattr(request, 'organization', None):
            validated_data.setdefault('organization', request.organization)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data.pop('_instance_extra_data', None)
        return super().update(instance, validated_data)

    class Meta:
        model = RenditionPreset
        fields = (
            'adjust_brightness', 'adjust_color', 'adjust_contrast',
            'adjust_sharpness', 'crop', 'description', 'dpi_x', 'dpi_y',
            'filters', 'format', 'height', 'id', 'name', 'organization',
            'quality', 'recipient', 'resource_type', 'watermark', 'width'
        )
