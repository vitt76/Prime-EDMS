"""
Headless API: Saved Searches CRUD and run (Phase 5.3 Sprint 1 Backend).

GET/POST .../saved-searches/
GET/PATCH/DELETE .../saved-searches/<id>/
GET .../saved-searches/<id>/run/ — returns document list with saved query and filters applied.
"""

import logging

from django.http import QueryDict
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from mayan.apps.documents.serializers.optimized_document_serializers import (
    OptimizedDocumentListSerializer,
)
from mayan.apps.documents.api_views.optimized_document_api_views import (
    OptimizedAPIDocumentListView,
)

logger = logging.getLogger(__name__)


def _get_saved_search_queryset(request):
    """Return SavedSearch queryset scoped to current user and organization."""
    from mayan.apps.saved_searches.models import SavedSearch
    organization = getattr(request, 'organization', None)
    if not organization:
        return SavedSearch.objects.none()
    return SavedSearch.objects.filter(user=request.user, organization=organization)


def _build_query_params_from_saved_search(saved_search):
    """Build a QueryDict from saved_search.query and saved_search.filters for optimized list."""
    q = QueryDict(mutable=True)
    if saved_search.query:
        q['q'] = saved_search.query
    for key, value in (saved_search.filters or {}).items():
        if isinstance(value, list):
            for v in value:
                q.appendlist(key, str(v))
        else:
            q[key] = str(value) if value is not None else ''
    return q


class SavedSearchListCreateView(APIView):
    """GET list and POST create for saved searches. Tenant-scoped."""

    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        organization = getattr(request, 'organization', None)
        if not organization:
            return Response(
                {'detail': 'Organization context required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        from mayan.apps.headless_api.serializers.saved_searches import SavedSearchSerializer
        qs = _get_saved_search_queryset(request)
        serializer = SavedSearchSerializer(qs, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request):
        organization = getattr(request, 'organization', None)
        if not organization:
            return Response(
                {'detail': 'Organization context required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        from mayan.apps.headless_api.serializers.saved_searches import SavedSearchSerializer
        serializer = SavedSearchSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user, organization=organization)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class SavedSearchDetailView(APIView):
    """GET, PATCH, DELETE a single saved search. Tenant-scoped."""

    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def _get_object(self, request, pk):
        from mayan.apps.saved_searches.models import SavedSearch
        qs = _get_saved_search_queryset(request)
        return qs.filter(pk=pk).first()

    def get(self, request, pk):
        obj = self._get_object(request, pk)
        if not obj:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        from mayan.apps.headless_api.serializers.saved_searches import SavedSearchSerializer
        serializer = SavedSearchSerializer(obj, context={'request': request})
        return Response(serializer.data)

    def patch(self, request, pk):
        obj = self._get_object(request, pk)
        if not obj:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        from mayan.apps.headless_api.serializers.saved_searches import SavedSearchSerializer
        serializer = SavedSearchSerializer(obj, data=request.data, partial=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        obj = self._get_object(request, pk)
        if not obj:
            return Response(status=status.HTTP_404_NOT_FOUND)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SavedSearchRunView(APIView):
    """
    GET .../saved-searches/<id>/run/

    Returns document list (same format as optimized list) with saved query and filters applied.
    """

    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        from mayan.apps.saved_searches.models import SavedSearch
        organization = getattr(request, 'organization', None)
        if not organization:
            return Response(
                {'detail': 'Organization context required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        saved = _get_saved_search_queryset(request).filter(pk=pk).first()
        if not saved:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Build a request-like object so OptimizedAPIDocumentListView.get_queryset uses saved params
        class RequestAdapter:
            pass
        req = RequestAdapter()
        req.user = request.user
        req.query_params = _build_query_params_from_saved_search(saved)

        view = OptimizedAPIDocumentListView()
        view.request = req
        view.kwargs = {}
        view.format_kwarg = None
        try:
            queryset = view.get_queryset()
        except Exception as e:
            logger.exception('SavedSearch run get_queryset failed: %s', e)
            return Response(
                {'detail': 'Failed to run search.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        page_size = min(int(request.query_params.get('page_size', 50) or 50), 100)
        page_size = max(1, page_size)
        documents = list(queryset[:page_size])
        serializer = OptimizedDocumentListSerializer(
            documents,
            many=True,
            context={'request': request},
        )
        return Response({
            'results': serializer.data,
            'count': len(serializer.data),
        })
