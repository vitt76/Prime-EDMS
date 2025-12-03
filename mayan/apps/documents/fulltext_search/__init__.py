"""
Document Full-Text Search Module.

Phase B2.2: Search Optimization.
Provides optimized full-text search for documents using PostgreSQL.

Future: This module will be extended with Smart Search capabilities:
- Semantic search using vector embeddings (pgvector, FAISS)
- Visual search using CLIP embeddings for image similarity
- AI-powered query understanding and expansion
- Multi-modal search (text + image combined)
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
