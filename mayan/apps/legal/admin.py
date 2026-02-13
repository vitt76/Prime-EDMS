from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from .models import UserConsentLog


@admin.register(UserConsentLog)
class UserConsentLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'consent_type', 'ip_address', 'timestamp', 'session_id')
    list_filter = ('consent_type', 'timestamp')
    search_fields = ('ip_address', 'session_id', 'user_agent')
    readonly_fields = ('ip_address', 'user_agent', 'consent_type', 'timestamp', 'session_id', 'url_referer')
    date_hierarchy = 'timestamp'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
