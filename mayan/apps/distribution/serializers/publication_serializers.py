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
    owner_username = serializers.SerializerMethodField()
    items_count = serializers.SerializerMethodField()
    renditions_count = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'id', 'owner', 'owner_username', 'title', 'description', 'access_policy',
            'expires_at', 'max_downloads', 'presets', 'recipient_lists',
            'downloads_count', 'items', 'items_count', 'renditions_count',
            'created', 'modified'
        )
        model = Publication
        read_only_fields = ('id', 'created', 'modified', 'downloads_count', 'owner', 'owner_username', 'items_count', 'renditions_count')

    def get_owner(self, obj):
        owner = obj.owner
        if owner:
            return owner.get_username()
        return None

    def get_owner_username(self, obj):
        owner = obj.owner
        if owner:
            return owner.get_username()
        return None

    def get_items_count(self, obj):
        return obj.items.count()

    def get_renditions_count(self, obj):
        return GeneratedRendition.objects.filter(publication_item__publication=obj).count()

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
    """Serializer for ShareLink with extended information for frontend."""
    publication_title = serializers.SerializerMethodField()
    publication_id = serializers.SerializerMethodField()
    rendition_preset_name = serializers.SerializerMethodField()
    rendition_preset_format = serializers.SerializerMethodField()
    document_file_id = serializers.SerializerMethodField()
    document_id = serializers.SerializerMethodField()
    is_valid = serializers.SerializerMethodField()
    public_url = serializers.SerializerMethodField()
    owner_username = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'id', 'rendition', 'token', 'recipient', 'expires_at',
            'max_downloads', 'downloads_count', 'created', 'last_accessed',
            'publication_title', 'publication_id', 'rendition_preset_name',
            'rendition_preset_format', 'document_file_id', 'document_id',
            'is_valid', 'public_url', 'owner_username'
        )
        model = ShareLink
        read_only_fields = ('id', 'token', 'created', 'last_accessed', 'downloads_count',
                           'publication_title', 'publication_id', 'rendition_preset_name',
                           'rendition_preset_format', 'document_file_id', 'document_id',
                           'is_valid', 'public_url', 'owner_username')

    def get_publication_title(self, obj):
        if obj.rendition and obj.rendition.publication_item:
            return obj.rendition.publication_item.publication.title
        return None

    def get_publication_id(self, obj):
        if obj.rendition and obj.rendition.publication_item:
            return obj.rendition.publication_item.publication.id
        return None

    def get_rendition_preset_name(self, obj):
        if obj.rendition and obj.rendition.preset:
            return obj.rendition.preset.name
        return None

    def get_rendition_preset_format(self, obj):
        if obj.rendition and obj.rendition.preset:
            return obj.rendition.preset.format
        return None

    def get_document_file_id(self, obj):
        if obj.rendition and obj.rendition.publication_item:
            return obj.rendition.publication_item.document_file.id
        return None

    def get_document_id(self, obj):
        if obj.rendition and obj.rendition.publication_item:
            return obj.rendition.publication_item.document_file.document_id
        return None

    def get_is_valid(self, obj):
        return obj.is_valid()

    def get_public_url(self, obj):
        """Generate public URL for the share link."""
        request = self.context.get('request')
        if request and obj.token:
            # Use direct token access at root level: /{token}/
            return request.build_absolute_uri(f'/{obj.token}/')
        return None

    def get_owner_username(self, obj):
        if obj.rendition and obj.rendition.publication_item:
            owner = obj.rendition.publication_item.publication.owner
            if owner:
                return owner.get_username()
        return None


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
