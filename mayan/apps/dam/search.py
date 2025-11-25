from django.utils.translation import ugettext_lazy as _

from mayan.apps.dynamic_search.classes import SearchModel
from mayan.apps.documents.permissions import permission_document_view


def invalidate_search_model_cache(*search_models):
    """Force SearchModel cached properties to refresh."""
    for search_model in search_models:
        if hasattr(search_model, '__dict__'):
            search_model.__dict__.pop('search_fields', None)


# Transformation functions for JSON fields
def transformation_ai_tags_to_string(value):
    """Convert AI tags JSON array to searchable string."""
    if value is None:
        return ''
    if isinstance(value, list):
        return ' '.join(str(tag) for tag in value if tag)
    return str(value) if value else ''


def transformation_categories_to_string(value):
    """Convert categories JSON array to searchable string."""
    if value is None:
        return ''
    if isinstance(value, list):
        return ' '.join(str(cat) for cat in value if cat)
    return str(value) if value else ''


def transformation_people_to_string(value):
    """Convert people JSON array to searchable string."""
    if value is None:
        return ''
    if isinstance(value, list):
        return ' '.join(str(person) for person in value if person)
    return str(value) if value else ''


def transformation_locations_to_string(value):
    """Convert locations JSON array to searchable string."""
    if value is None:
        return ''
    if isinstance(value, list):
        return ' '.join(str(loc) for loc in value if loc)
    return str(value) if value else ''


def transformation_colors_to_string(value):
    """Convert dominant colors JSON array to searchable string."""
    if value is None:
        return ''
    if isinstance(value, list):
        return ' '.join(str(color) for color in value if color)
    return str(value) if value else ''


# Extend document search with AI metadata fields
def extend_document_search():
    """Add AI metadata fields to document search."""

    # Get the existing document search models
    from mayan.apps.documents.search import (
        search_model_document, search_model_document_file,
        search_model_document_file_page, search_model_document_version,
        search_model_document_version_page
    )

    # Add AI analysis fields to document search model
    # Text fields (no transformation needed)
    search_model_document.add_model_field(
        field='ai_analysis__ai_description',
        label=_('AI Description')
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
        field='ai_analysis__alt_text',
        label=_('Alt Text')
    )

    search_model_document.add_model_field(
        field='ai_analysis__language',
        label=_('AI Detected Language')
    )

    search_model_document.add_model_field(
        field='ai_analysis__ai_provider',
        label=_('AI Provider')
    )

    search_model_document.add_model_field(
        field='ai_analysis__analysis_status',
        label=_('AI Analysis Status')
    )

    # JSON fields (with transformation functions)
    search_model_document.add_model_field(
        field='ai_analysis__ai_tags',
        label=_('AI Tags'),
        transformation_function=transformation_ai_tags_to_string
    )

    search_model_document.add_model_field(
        field='ai_analysis__categories',
        label=_('AI Categories'),
        transformation_function=transformation_categories_to_string
    )

    search_model_document.add_model_field(
        field='ai_analysis__people',
        label=_('AI Detected People'),
        transformation_function=transformation_people_to_string
    )

    search_model_document.add_model_field(
        field='ai_analysis__locations',
        label=_('AI Detected Locations'),
        transformation_function=transformation_locations_to_string
    )

    search_model_document.add_model_field(
        field='ai_analysis__dominant_colors',
        label=_('Dominant Colors'),
        transformation_function=transformation_colors_to_string
    )

    # Add AI analysis fields to document file search model
    search_model_document_file.add_model_field(
        field='document__ai_analysis__ai_description',
        label=_('Document AI Description')
    )

    search_model_document_file.add_model_field(
        field='document__ai_analysis__ai_tags',
        label=_('Document AI Tags'),
        transformation_function=transformation_ai_tags_to_string
    )

    search_model_document_file.add_model_field(
        field='document__ai_analysis__categories',
        label=_('Document AI Categories'),
        transformation_function=transformation_categories_to_string
    )

    search_model_document_file.add_model_field(
        field='document__ai_analysis__language',
        label=_('Document AI Detected Language')
    )

    search_model_document_file.add_model_field(
        field='document__ai_analysis__people',
        label=_('Document AI Detected People'),
        transformation_function=transformation_people_to_string
    )

    search_model_document_file.add_model_field(
        field='document__ai_analysis__locations',
        label=_('Document AI Detected Locations'),
        transformation_function=transformation_locations_to_string
    )

    search_model_document_file.add_model_field(
        field='document__ai_analysis__ai_provider',
        label=_('Document AI Provider')
    )

    search_model_document_file.add_model_field(
        field='document__ai_analysis__analysis_status',
        label=_('Document AI Analysis Status')
    )

    # Add AI analysis fields to document file page search model
    search_model_document_file_page.add_model_field(
        field='document_file__document__ai_analysis__ai_description',
        label=_('Document AI Description')
    )

    search_model_document_file_page.add_model_field(
        field='document_file__document__ai_analysis__ai_tags',
        label=_('Document AI Tags'),
        transformation_function=transformation_ai_tags_to_string
    )

    search_model_document_file_page.add_model_field(
        field='document_file__document__ai_analysis__categories',
        label=_('Document AI Categories'),
        transformation_function=transformation_categories_to_string
    )

    search_model_document_file_page.add_model_field(
        field='document_file__document__ai_analysis__language',
        label=_('Document AI Detected Language')
    )

    search_model_document_file_page.add_model_field(
        field='document_file__document__ai_analysis__people',
        label=_('Document AI Detected People'),
        transformation_function=transformation_people_to_string
    )

    search_model_document_file_page.add_model_field(
        field='document_file__document__ai_analysis__locations',
        label=_('Document AI Detected Locations'),
        transformation_function=transformation_locations_to_string
    )

    search_model_document_file_page.add_model_field(
        field='document_file__document__ai_analysis__ai_provider',
        label=_('Document AI Provider')
    )

    search_model_document_file_page.add_model_field(
        field='document_file__document__ai_analysis__analysis_status',
        label=_('Document AI Analysis Status')
    )

    # Add AI analysis fields to document version search model
    search_model_document_version.add_model_field(
        field='document__ai_analysis__ai_description',
        label=_('Document AI Description')
    )

    search_model_document_version.add_model_field(
        field='document__ai_analysis__ai_tags',
        label=_('Document AI Tags'),
        transformation_function=transformation_ai_tags_to_string
    )

    search_model_document_version.add_model_field(
        field='document__ai_analysis__categories',
        label=_('Document AI Categories'),
        transformation_function=transformation_categories_to_string
    )

    search_model_document_version.add_model_field(
        field='document__ai_analysis__language',
        label=_('Document AI Detected Language')
    )

    search_model_document_version.add_model_field(
        field='document__ai_analysis__people',
        label=_('Document AI Detected People'),
        transformation_function=transformation_people_to_string
    )

    search_model_document_version.add_model_field(
        field='document__ai_analysis__locations',
        label=_('Document AI Detected Locations'),
        transformation_function=transformation_locations_to_string
    )

    search_model_document_version.add_model_field(
        field='document__ai_analysis__ai_provider',
        label=_('Document AI Provider')
    )

    search_model_document_version.add_model_field(
        field='document__ai_analysis__analysis_status',
        label=_('Document AI Analysis Status')
    )

    # Add AI analysis fields to document version page search model
    search_model_document_version_page.add_model_field(
        field='document_version__document__ai_analysis__ai_description',
        label=_('Document AI Description')
    )

    search_model_document_version_page.add_model_field(
        field='document_version__document__ai_analysis__ai_tags',
        label=_('Document AI Tags'),
        transformation_function=transformation_ai_tags_to_string
    )

    search_model_document_version_page.add_model_field(
        field='document_version__document__ai_analysis__categories',
        label=_('Document AI Categories'),
        transformation_function=transformation_categories_to_string
    )

    search_model_document_version_page.add_model_field(
        field='document_version__document__ai_analysis__language',
        label=_('Document AI Detected Language')
    )

    search_model_document_version_page.add_model_field(
        field='document_version__document__ai_analysis__people',
        label=_('Document AI Detected People'),
        transformation_function=transformation_people_to_string
    )

    search_model_document_version_page.add_model_field(
        field='document_version__document__ai_analysis__locations',
        label=_('Document AI Detected Locations'),
        transformation_function=transformation_locations_to_string
    )

    search_model_document_version_page.add_model_field(
        field='document_version__document__ai_analysis__ai_provider',
        label=_('Document AI Provider')
    )

    search_model_document_version_page.add_model_field(
        field='document_version__document__ai_analysis__analysis_status',
        label=_('Document AI Analysis Status')
    )

    # Invalidate cached search field lists so new fields become available
    invalidate_search_model_cache(
        search_model_document,
        search_model_document_file,
        search_model_document_file_page,
        search_model_document_version,
        search_model_document_version_page
    )
