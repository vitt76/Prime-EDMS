# Re-export all serializers for easier imports
from .document_file_serializers import *  # noqa
from .document_serializers import *  # noqa
from .document_type_serializers import *  # noqa
from .document_version_serializers import *  # noqa
from .favorite_document_serializers import *  # noqa
from .recently_accessed_document_serializers import *  # noqa
from .trashed_document_serializers import *  # noqa

# Phase B1: Rich document serializers
from .document_rich_serializers import (  # noqa
    DocumentRichSerializer,
    DocumentRichListSerializer
)

# Phase B2: Optimized document serializers
from .optimized_document_serializers import (  # noqa
    OptimizedDocumentSerializer,
    OptimizedDocumentListSerializer,
    OptimizedDocumentFileSerializer,
    CachedThumbnailMixin
)

