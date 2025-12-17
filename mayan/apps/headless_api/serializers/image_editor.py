from rest_framework import serializers


class HeadlessImageEditorSessionCreateSerializer(serializers.Serializer):
    document_file_id = serializers.IntegerField(min_value=1)


class HeadlessImageEditorSessionStateSerializer(serializers.Serializer):
    state = serializers.JSONField()


class HeadlessWatermarkListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    label = serializers.CharField()


