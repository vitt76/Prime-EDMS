"""
Document Search Module.

Phase B2.2: Search Optimization.
Provides optimized full-text search for documents using PostgreSQL.
"""

from .fulltext_search import (
    DocumentFullTextSearch,
    document_fulltext_search,
    autocomplete_documents
)

__all__ = [
    'DocumentFullTextSearch',
    'document_fulltext_search',
    'autocomplete_documents'
]

