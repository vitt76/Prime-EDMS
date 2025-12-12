"""Headless API views for Favorites."""

import logging
from typing import Dict

from rest_framework import status
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination

from mayan.apps.acls.models import AccessControlList
from mayan.apps.documents.models import Document, FavoriteDocument
from mayan.apps.documents.permissions import permission_document_view
from mayan.apps.headless_api.serializers import FavoriteDocumentEntrySerializer

logger = logging.getLogger(__name__)


class HeadlessFavoritesPagination(PageNumberPagination):
    """Simple pagination for favorites list."""

    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class HeadlessFavoriteListView(APIView):
    """
    Return list of favorited documents with thumbnail/preview URLs.

    Response (paginated):
    {
        "count": 2,
        "next": null,
        "previous": null,
        "results": [
            {
                "document": {
                    "id": 1,
                    "label": "...",
                    "thumbnail_url": "http://localhost:8080/api/v4/documents/1/versions/latest/pages/1/image/?width=150&height=150",
                    "preview_url": "http://localhost:8080/api/v4/documents/1/versions/latest/pages/1/image/?width=800",
                    ...
                },
                "datetime_added": "2025-12-08T10:00:00Z"
            }
        ]
    }
    """

    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # Base favorites for user (ordered)
            favorites_qs = FavoriteDocument.objects.filter(
                user=request.user
            ).select_related('document', 'document__document_type').order_by('-datetime_added')

            favorite_doc_ids = list(favorites_qs.values_list('document_id', flat=True))

            # Apply ACLs to documents
            documents_qs = Document.valid.filter(pk__in=favorite_doc_ids)
            documents_qs = AccessControlList.objects.restrict_queryset(
                permission=permission_document_view,
                queryset=documents_qs,
                user=request.user
            ).select_related('document_type').prefetch_related('tags')

            # Map id -> document for serializer usage
            document_map: Dict[int, Document] = {doc.pk: doc for doc in documents_qs}

            # Filter favorites by permitted documents
            filtered_favorites_qs = favorites_qs.filter(
                document_id__in=document_map.keys()
            )

            paginator = HeadlessFavoritesPagination()
            page = paginator.paginate_queryset(filtered_favorites_qs, request, view=self)

            serializer = FavoriteDocumentEntrySerializer(
                page,
                many=True,
                context={'request': request, 'document_map': document_map}
            )

            # #region agent log
            try:
                import json as _json, time as _time
                with open(r"c:\DAM\Prime-EDMS\.cursor\debug.log", "a", encoding="utf-8") as _f:
                    _f.write(_json.dumps({
                        "id": "log_headless_fav_get_ok",
                        "timestamp": _time.time() * 1000,
                        "sessionId": "debug-session",
                        "runId": "post-fix",
                        "hypothesisId": "H-fav",
                        "location": "headless_api/views/favorites.py:get",
                        "message": "Favorites fetched",
                        "data": {
                            "favorite_doc_ids": favorite_doc_ids,
                            "allowed_count": len(document_map),
                            "page_count": len(page) if page else 0
                        }
                    }) + "\n")
            except Exception:
                pass
            # #endregion agent log

            # #region agent log http
            try:
                import json as _json, time as _time, urllib.request as _r
                _r.urlopen(
                    _r.Request(
                        "http://host.docker.internal:7242/ingest/e2a91df7-36f3-4ec3-8d36-7745f17b1cac",
                        data=_json.dumps({
                            "id": "log_headless_fav_get_ok_http",
                            "timestamp": _time.time() * 1000,
                            "sessionId": "debug-session",
                            "runId": "post-fix",
                            "hypothesisId": "H-fav",
                            "location": "headless_api/views/favorites.py:get",
                            "message": "Favorites fetched",
                            "data": {
                                "favorite_doc_ids": favorite_doc_ids,
                                "allowed_count": len(document_map),
                                "page_count": len(page) if page else 0
                            }
                        }).encode("utf-8"),
                        headers={"Content-Type": "application/json"},
                        method="POST"
                    ),
                    timeout=2
                )
            except Exception:
                pass
            # #endregion agent log http

            return paginator.get_paginated_response(serializer.data)
        except Exception as exc:
            logger.exception('Headless favorites list failed: %s', exc)
            # #region agent log
            try:
                import json as _json, time as _time
                with open(r"c:\DAM\Prime-EDMS\.cursor\debug.log", "a", encoding="utf-8") as _f:
                    _f.write(_json.dumps({
                        "id": "log_headless_fav_get_err",
                        "timestamp": _time.time() * 1000,
                        "sessionId": "debug-session",
                        "runId": "post-fix",
                        "hypothesisId": "H-fav",
                        "location": "headless_api/views/favorites.py:get",
                        "message": "Favorites get failed",
                        "data": {"error": str(exc)}
                    }) + "\n")
            except Exception:
                pass
            # #endregion agent log
            # #region agent log http
            try:
                import json as _json, time as _time, urllib.request as _r
                _r.urlopen(
                    _r.Request(
                        "http://host.docker.internal:7242/ingest/e2a91df7-36f3-4ec3-8d36-7745f17b1cac",
                        data=_json.dumps({
                            "id": "log_headless_fav_get_err_http",
                            "timestamp": _time.time() * 1000,
                            "sessionId": "debug-session",
                            "runId": "post-fix",
                            "hypothesisId": "H-fav",
                            "location": "headless_api/views/favorites.py:get",
                            "message": "Favorites get failed",
                            "data": {"error": str(exc)}
                        }).encode("utf-8"),
                        headers={"Content-Type": "application/json"},
                        method="POST"
                    ),
                    timeout=2
                )
            except Exception:
                pass
            # #endregion agent log http
            return Response(
                {'error': 'favorites_failed', 'detail': str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class HeadlessFavoriteToggleView(APIView):
    """
    Toggle favorite status for a document.

    POST /api/v4/headless/favorites/<document_id>/
    Response: {"favorited": true|false}
    """

    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, document_id):
        try:
            document = Document.valid.get(pk=document_id)
        except Document.DoesNotExist:
            return Response(
                {'error': 'Document not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Skip ACL for superusers
        if not request.user.is_superuser:
            try:
                AccessControlList.objects.check_access(
                    permission=permission_document_view,
                    user=request.user,
                    obj=document
                )
            except Exception as exc:
                logger.warning(
                    'Favorites toggle denied for user %s on document %s: %s',
                    request.user.username,
                    document_id,
                    exc
                )
                return Response(
                    {'error': 'access_denied', 'detail': str(exc)},
                    status=status.HTTP_403_FORBIDDEN
                )

        try:
            favorite, created = FavoriteDocument.objects.get_or_create(
                user=request.user,
                document=document
            )
        except Exception as exc:
            return Response(
                {'error': 'favorite_failed', 'detail': str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        if created:
            # #region agent log
            try:
                import json as _json, time as _time
                with open(r"c:\DAM\Prime-EDMS\.cursor\debug.log", "a", encoding="utf-8") as _f:
                    _f.write(_json.dumps({
                        "id": "log_headless_fav_toggle",
                        "timestamp": _time.time() * 1000,
                        "sessionId": "debug-session",
                        "runId": "post-fix",
                        "hypothesisId": "H-fav",
                        "location": "headless_api/views/favorites.py:post",
                        "message": "Favorited",
                        "data": {"document_id": document_id, "favorited": True}
                    }) + "\n")
            except Exception:
                pass
            # #endregion agent log
            # #region agent log http
            try:
                import json as _json, time as _time, urllib.request as _r
                _r.urlopen(
                    _r.Request(
                        "http://host.docker.internal:7242/ingest/e2a91df7-36f3-4ec3-8d36-7745f17b1cac",
                        data=_json.dumps({
                            "id": "log_headless_fav_toggle_http",
                            "timestamp": _time.time() * 1000,
                            "sessionId": "debug-session",
                            "runId": "post-fix",
                            "hypothesisId": "H-fav",
                            "location": "headless_api/views/favorites.py:post",
                            "message": "Favorited",
                            "data": {"document_id": document_id, "favorited": True}
                        }).encode("utf-8"),
                        headers={"Content-Type": "application/json"},
                        method="POST"
                    ),
                    timeout=2
                )
            except Exception:
                pass
            # #endregion agent log http
            return Response({'favorited': True}, status=status.HTTP_200_OK)

        favorite.delete()
        # #region agent log
        try:
            import json as _json, time as _time
            with open(r"c:\DAM\Prime-EDMS\.cursor\debug.log", "a", encoding="utf-8") as _f:
                _f.write(_json.dumps({
                    "id": "log_headless_fav_toggle",
                    "timestamp": _time.time() * 1000,
                    "sessionId": "debug-session",
                    "runId": "post-fix",
                    "hypothesisId": "H-fav",
                    "location": "headless_api/views/favorites.py:post",
                    "message": "Unfavorited",
                    "data": {"document_id": document_id, "favorited": False}
                }) + "\n")
        except Exception:
            pass
        # #endregion agent log
        # #region agent log http
        try:
            import json as _json, time as _time, urllib.request as _r
            _r.urlopen(
                _r.Request(
                    "http://host.docker.internal:7242/ingest/e2a91df7-36f3-4ec3-8d36-7745f17b1cac",
                    data=_json.dumps({
                        "id": "log_headless_fav_toggle_http",
                        "timestamp": _time.time() * 1000,
                        "sessionId": "debug-session",
                        "runId": "post-fix",
                        "hypothesisId": "H-fav",
                        "location": "headless_api/views/favorites.py:post",
                        "message": "Unfavorited",
                        "data": {"document_id": document_id, "favorited": False}
                    }).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="POST"
                ),
                timeout=2
            )
        except Exception:
            pass
        # #endregion agent log http
        return Response({'favorited': False}, status=status.HTTP_200_OK)

