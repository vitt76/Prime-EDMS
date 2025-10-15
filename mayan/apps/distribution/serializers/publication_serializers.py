from django.utils.translation import ugettext_lazy as _

from mayan.apps.rest_api import serializers

from ..models import Publication, PublicationItem, ShareLink, GeneratedRendition


class PublicationItemSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        extra_kwargs = {
            'url': {
                'lookup_url_kwarg': 'publication_item_id',
                'view_name': 'rest_api:publicationitem-detail'
            }
        }
        fields = ('id', 'publication', 'document_file', 'created', 'url')
        model = PublicationItem
        read_only_fields = ('id', 'created')


class PublicationSerializer(serializers.HyperlinkedModelSerializer):
    items = PublicationItemSerializer(many=True, read_only=True)
    share_links = serializers.HyperlinkedIdentityField(
        lookup_url_kwarg='publication_id',
        view_name='rest_api:sharelink-list'
    )

    class Meta:
        extra_kwargs = {
            'url': {
                'lookup_url_kwarg': 'publication_id',
                'view_name': 'rest_api:publication-detail'
            }
        }
        fields = (
            'id', 'owner', 'title', 'description', 'access_policy',
            'expires_at', 'max_downloads', 'presets', 'recipient_lists',
            'downloads_count', 'items', 'share_links',
            'created', 'modified', 'url'
        )
        model = Publication
        read_only_fields = ('id', 'created', 'modified', 'downloads_count')


class ShareLinkSerializer(serializers.HyperlinkedModelSerializer):
    access_log_url = serializers.HyperlinkedIdentityField(
        lookup_url_kwarg='share_link_id',
        view_name='rest_api:accesslog-list'
    )

    class Meta:
        extra_kwargs = {
            'url': {
                'lookup_url_kwarg': 'share_link_id',
                'view_name': 'rest_api:sharelink-detail'
            }
        }
        fields = (
            'id', 'publication', 'token', 'recipient', 'expires_at',
            'max_downloads', 'downloads_count', 'created', 'last_accessed',
            'url', 'access_log_url'
        )
        model = ShareLink
        read_only_fields = ('id', 'token', 'created', 'last_accessed', 'downloads_count')


class GeneratedRenditionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        extra_kwargs = {
            'url': {
                'lookup_url_kwarg': 'rendition_id',
                'view_name': 'rest_api:generatedrendition-detail'
            }
        }
        fields = (
            'id', 'publication_item', 'preset', 'file_path', 'status',
            'file_size', 'checksum', 'error_message', 'created', 'modified', 'url'
        )
        model = GeneratedRendition
        read_only_fields = ('id', 'created', 'modified')
