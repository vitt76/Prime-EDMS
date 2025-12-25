from django.contrib import admin

from .models import NotificationLog, NotificationPreference, NotificationTemplate


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = ('event_type', 'default_priority', 'is_active', 'updated_at')
    list_filter = ('is_active', 'default_priority')
    search_fields = ('event_type', 'title_template', 'message_template')


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'notifications_enabled', 'email_notifications_enabled', 'push_notifications_enabled')
    list_filter = ('notifications_enabled', 'email_notifications_enabled', 'push_notifications_enabled')
    search_fields = ('user__username', 'user__email')


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ('notification', 'action', 'timestamp')
    list_filter = ('action',)
    readonly_fields = ('timestamp', 'uuid')


