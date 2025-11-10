"""
Permissions for DAM module.
"""

from django.utils.translation import ugettext_lazy as _

# AI Analysis permissions
permission_ai_analysis_view = {
    'namespace': 'dam',
    'name': 'ai_analysis_view',
    'label': _('View AI analysis results'),
}

permission_ai_analysis_create = {
    'namespace': 'dam',
    'name': 'ai_analysis_create',
    'label': _('Create AI analysis'),
}

permission_ai_analysis_edit = {
    'namespace': 'dam',
    'name': 'ai_analysis_edit',
    'label': _('Edit AI analysis results'),
}

permission_ai_analysis_delete = {
    'namespace': 'dam',
    'name': 'ai_analysis_delete',
    'label': _('Delete AI analysis'),
}

# Metadata preset permissions
permission_metadata_preset_view = {
    'namespace': 'dam',
    'name': 'metadata_preset_view',
    'label': _('View metadata presets'),
}

permission_metadata_preset_create = {
    'namespace': 'dam',
    'name': 'metadata_preset_create',
    'label': _('Create metadata presets'),
}

permission_metadata_preset_edit = {
    'namespace': 'dam',
    'name': 'metadata_preset_edit',
    'label': _('Edit metadata presets'),
}

permission_metadata_preset_delete = {
    'namespace': 'dam',
    'name': 'metadata_preset_delete',
    'label': _('Delete metadata presets'),
}

# All permissions
permissions = [
    permission_ai_analysis_view,
    permission_ai_analysis_create,
    permission_ai_analysis_edit,
    permission_ai_analysis_delete,
    permission_metadata_preset_view,
    permission_metadata_preset_create,
    permission_metadata_preset_edit,
    permission_metadata_preset_delete,
]
