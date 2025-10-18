from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers

from ..models import RenditionPreset


class RenditionPresetSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        validated_data.pop('_instance_extra_data', None)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data.pop('_instance_extra_data', None)
        return super().update(instance, validated_data)

    class Meta:
        model = RenditionPreset
        fields = (
            'description', 'format', 'height', 'id', 'name', 'quality',
            'resource_type', 'watermark', 'width'
        )
