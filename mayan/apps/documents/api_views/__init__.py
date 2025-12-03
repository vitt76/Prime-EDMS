# Re-export all API views for easier imports

# Phase B1: Rich document API views
from .document_rich_api_views import (  # noqa
    APIDocumentRichDetailView,
    APIDocumentRichListView
)

# Phase B1: Bulk operations API views
from .bulk_operations_api_views import (  # noqa
    BulkDocumentActionView,
    BulkTagActionView,
    BulkCabinetActionView
)

# Phase B2: Optimized document API views
from .optimized_document_api_views import (  # noqa
    OptimizedAPIDocumentListView,
    OptimizedAPIDocumentDetailView
)

