from django.utils.translation import ugettext_lazy as _

from mayan.apps.dynamic_search.classes import SearchModel
from mayan.apps.documents.permissions import permission_document_view

# Extend document search with AI metadata fields
def extend_document_search():
    """Add AI metadata fields to document search."""

    # Get the existing document search model
    from mayan.apps.documents.search import search_model_document
    from mayan.apps.documents.models import Document

    # Add AI analysis fields via related model
    search_model_document.add_model_field(
        field='ai_analysis__ai_description',
        label=_('AI Description')
    )

    search_model_document.add_model_field(
        field='ai_analysis__ai_tags',
        label=_('AI Tags')
    )

    search_model_document.add_model_field(
        field='ai_analysis__categories',
        label=_('AI Categories')
    )

    search_model_document.add_model_field(
        field='ai_analysis__language',
        label=_('AI Detected Language')
    )

    search_model_document.add_model_field(
        field='ai_analysis__people',
        label=_('AI Detected People')
    )

    search_model_document.add_model_field(
        field='ai_analysis__locations',
        label=_('AI Detected Locations')
    )

    search_model_document.add_model_field(
        field='ai_analysis__copyright_notice',
        label=_('Copyright Notice')
    )

    search_model_document.add_model_field(
        field='ai_analysis__usage_rights',
        label=_('Usage Rights')
    )

    search_model_document.add_model_field(
        field='ai_analysis__ai_provider',
        label=_('AI Provider')
    )

    search_model_document.add_model_field(
        field='ai_analysis__analysis_status',
        label=_('AI Analysis Status')
    )

    # Add facets for common search filters
    search_model_document.add_model_field(
        field='ai_analysis__categories__icontains',
        label=_('Category (contains)')
    )

    search_model_document.add_model_field(
        field='ai_analysis__language',
        label=_('Language')
    )

    search_model_document.add_model_field(
        field='ai_analysis__ai_provider',
        label=_('AI Provider')
    )

    search_model_document.add_model_field(
        field='ai_analysis__analysis_status',
        label=_('Analysis Status')
    )
