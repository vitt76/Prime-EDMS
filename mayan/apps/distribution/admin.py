from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from .models import (
    AccessLog, GeneratedRendition, Publication, PublicationItem,
    Recipient, RecipientList, RenditionPreset, ShareLink
)


@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'organization', 'created')
    search_fields = ('email', 'name', 'organization')
    list_filter = ('organization', 'created')


@admin.register(RecipientList)
class RecipientListAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'created')
    search_fields = ('name', 'owner__username')
    list_filter = ('owner', 'created')
    filter_horizontal = ('recipients', 'internal_users')


@admin.register(RenditionPreset)
class RenditionPresetAdmin(admin.ModelAdmin):
    list_display = ('name', 'resource_type', 'format', 'width', 'height', 'quality')
    search_fields = ('name', 'description')
    list_filter = ('resource_type', 'format')


@admin.register(Publication)
class PublicationAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'access_policy', 'created', 'downloads_count')
    search_fields = ('title', 'description', 'owner__username')
    list_filter = ('access_policy', 'owner', 'created')
    filter_horizontal = ('presets', 'recipient_lists')


@admin.register(PublicationItem)
class PublicationItemAdmin(admin.ModelAdmin):
    list_display = ('publication', 'document_file', 'created')
    search_fields = ('publication__title', 'document_file__filename')
    list_filter = ('created',)


@admin.register(ShareLink)
class ShareLinkAdmin(admin.ModelAdmin):
    list_display = ('publication', 'token_short', 'recipient', 'downloads_count', 'created')
    search_fields = ('publication__title', 'token', 'recipient__email')
    list_filter = ('created', 'expires_at')
    readonly_fields = ('token',)

    def token_short(self, obj):
        return obj.token[:8] + '...'
    token_short.short_description = _('Token')


@admin.register(GeneratedRendition)
class GeneratedRenditionAdmin(admin.ModelAdmin):
    list_display = ('publication_item', 'preset', 'status', 'file_size', 'created')
    search_fields = ('publication_item__publication__title', 'preset__name')
    list_filter = ('status', 'created')


@admin.register(AccessLog)
class AccessLogAdmin(admin.ModelAdmin):
    list_display = ('share_link', 'event', 'ip_address', 'timestamp')
    search_fields = ('share_link__publication__title', 'ip_address')
    list_filter = ('event', 'timestamp')
    readonly_fields = ('share_link', 'event', 'ip_address', 'user_agent', 'timestamp')
