from django.utils.translation import ugettext_lazy as _

from mayan.apps.rest_api import serializers

from ..models import Publication, PublicationItem, ShareLink, GeneratedRendition


class PublicationItemSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'publication', 'document_file', 'created')
        model = PublicationItem
        read_only_fields = ('id', 'created')


class PublicationSerializer(serializers.ModelSerializer):
    items = PublicationItemSerializer(many=True, read_only=True)
    owner = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'id', 'owner', 'title', 'description', 'access_policy',
            'expires_at', 'max_downloads', 'presets', 'recipient_lists',
            'downloads_count', 'items',
            'created', 'modified'
        )
        model = Publication
        read_only_fields = ('id', 'created', 'modified', 'downloads_count', 'owner')

    def get_owner(self, obj):
        owner = obj.owner
        if owner:
            return owner.get_username()
        return None

    def _strip_internal_fields(self, validated_data):
        validated_data.pop('_instance_extra_data', None)
        return validated_data

    def create(self, validated_data):
        validated_data = self._strip_internal_fields(validated_data)

        request = self.context.get('request')
        if request and request.user and request.user.is_authenticated:
            validated_data['owner'] = request.user

        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data = self._strip_internal_fields(validated_data)
        validated_data.pop('owner', None)

        return super().update(instance, validated_data)


class ShareLinkSerializer(serializers.ModelSerializer):

    class Meta:
        fields = (
            'id', 'publication', 'token', 'recipient', 'expires_at',
            'max_downloads', 'downloads_count', 'created', 'last_accessed'
        )
        model = ShareLink
        read_only_fields = ('id', 'token', 'created', 'last_accessed', 'downloads_count')


class GeneratedRenditionSerializer(serializers.ModelSerializer):
    file_name = serializers.SerializerMethodField()
    download_url = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'id', 'publication_item', 'preset', 'status',
            'file_name', 'download_url', 'file_size', 'checksum',
            'error_message', 'created', 'modified'
        )
        model = GeneratedRendition
        read_only_fields = ('id', 'created', 'modified')

    def get_file_name(self, obj):
        if obj.file:
            return obj.file.name.rsplit('/', 1)[-1]
        return None

    def get_download_url(self, obj):
        request = self.context.get('request')
        if obj.file:
            try:
                url = obj.get_download_url()
                if url and request is not None:
                    return request.build_absolute_uri(url)
                return url
            except Exception:
                return None
        return None
