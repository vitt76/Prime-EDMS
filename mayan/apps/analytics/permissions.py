from django.utils.translation import ugettext_lazy as _

from mayan.apps.permissions import PermissionNamespace

namespace = PermissionNamespace(label=_('Analytics'), name='analytics')

permission_analytics_view_asset_bank = namespace.add_permission(
    label=_('View Asset Bank dashboard'), name='view_asset_bank'
)
permission_analytics_view_campaign_performance = namespace.add_permission(
    label=_('View Campaign Performance dashboard'), name='view_campaign_performance'
)
permission_analytics_view_user_activity = namespace.add_permission(
    label=_('View User Activity dashboard'), name='view_user_activity'
)
permission_analytics_view_search_analytics = namespace.add_permission(
    label=_('View Search Analytics dashboard'), name='view_search_analytics'
)
permission_analytics_view_content_intelligence = namespace.add_permission(
    label=_('View Content Intelligence dashboard'), name='view_content_intelligence'
)
permission_analytics_view_distribution = namespace.add_permission(
    label=_('View Distribution Analytics dashboard'), name='view_distribution'
)


