"""
Permissions for DAM module.
"""

from django.utils.translation import ugettext_lazy as _

from mayan.apps.permissions import PermissionNamespace

namespace = PermissionNamespace(label=_('Digital Asset Management'), name='dam')

# AI Analysis permissions
permission_ai_analysis_view = namespace.add_permission(
    label=_('View AI analysis results'), name='ai_analysis_view'
)

permission_ai_analysis_create = namespace.add_permission(
    label=_('Create AI analysis'), name='ai_analysis_create'
)

permission_ai_analysis_edit = namespace.add_permission(
    label=_('Edit AI analysis results'), name='ai_analysis_edit'
)

permission_ai_analysis_delete = namespace.add_permission(
    label=_('Delete AI analysis'), name='ai_analysis_delete'
)

# Metadata preset permissions
permission_metadata_preset_view = namespace.add_permission(
    label=_('View metadata presets'), name='metadata_preset_view'
)

permission_metadata_preset_create = namespace.add_permission(
    label=_('Create metadata presets'), name='metadata_preset_create'
)

permission_metadata_preset_edit = namespace.add_permission(
    label=_('Edit metadata presets'), name='metadata_preset_edit'
)

permission_metadata_preset_delete = namespace.add_permission(
    label=_('Delete metadata presets'), name='metadata_preset_delete'
)
