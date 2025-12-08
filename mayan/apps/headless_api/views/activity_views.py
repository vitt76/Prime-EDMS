"""
Activity feed views for Headless API.

Provides REST endpoints for personalized activity feeds that Mayan EDMS
doesn't provide through its standard API.
"""

from django.contrib.contenttypes.models import ContentType
from django.core.paginator import EmptyPage, Paginator
from django.utils.translation import ugettext_lazy as _
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from mayan.apps.documents.models import Document
from mayan.apps.events.models import Action
from mayan.apps.headless_api.serializers import ActivityFeedSerializer

import logging

logger = logging.getLogger(__name__)


class HeadlessActivityFeedView(APIView):
    """
    REST API endpoint for personalized activity feeds.

    Mayan EDMS provides system-wide event logs but doesn't expose
    user-specific activity feeds needed for dashboard functionality.

    Endpoint: GET /api/v4/headless/activity/feed/

    Query Parameters:
    - filter: 'my_actions' | 'my_documents' | 'all' (default: 'my_actions')
    - page: int (default: 1)
    - page_size: int (default: 20, max: 100)

    Response Schema:
    {
        "count": int,
        "page": int,
        "page_size": int,
        "results": [
            {
                "id": int,
                "timestamp": "ISO8601",
                "actor": {
                    "id": int,
                    "username": string,
                    "full_name": string
                },
                "verb": string,
                "verb_code": string,
                "target": {
                    "id": int,
                    "type": string,
                    "label": string,
                    "url": string | null
                },
                "description": string
            }
        ]
    }
    """
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    # Translation mappings for activity verbs
    VERB_TRANSLATIONS = {
        'document_created': _('created document'),
        'document_edited': _('edited document'),
        'document_deleted': _('deleted document'),
        'document_downloaded': _('downloaded document'),
        'document_viewed': _('viewed document'),
        'file_uploaded': _('uploaded file'),
        'tag_attached': _('attached tag'),
        'tag_removed': _('removed tag'),
        'metadata_edited': _('edited metadata'),
        'cabinet_document_added': _('added to collection'),
        'cabinet_document_removed': _('removed from collection'),
        'workflow_transition': _('changed status'),
        'user_logged_in': _('logged in'),
        'user_logged_out': _('logged out'),
    }

    def get(self, request):
        """
        Handle GET requests for activity feed.
        """
        try:
            user = request.user

            # Parse query parameters
            filter_type = request.query_params.get('filter', 'my_actions')
            page = int(request.query_params.get('page', 1))
            page_size = min(int(request.query_params.get('page_size', 20)), 100)

            # Get filtered actions
            actions = self._get_filtered_actions(user, filter_type)

            # Paginate results
            paginator = Paginator(actions, page_size)
            try:
                page_obj = paginator.page(page)
            except EmptyPage:
                page_obj = paginator.page(paginator.num_pages or 1)

            # Serialize results
            results = [self._serialize_action(action) for action in page_obj.object_list]

            response_data = {
                'count': paginator.count,
                'page': page,
                'page_size': page_size,
                'total_pages': paginator.num_pages,
                'results': results
            }

            return Response(response_data)

        except Exception as e:
            logger.error(f"Error getting activity feed for user {request.user.username}: {str(e)}")
            return Response(
                {
                    'error': _('Error retrieving activity feed'),
                    'error_code': 'INTERNAL_ERROR'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _get_filtered_actions(self, user, filter_type):
        """
        Get actions filtered by type.
        """
        queryset = Action.objects.select_related(
            'actor', 'target_content_type', 'target'
        ).order_by('-timestamp')

        if filter_type == 'my_actions':
            # Only actions performed by the current user
            queryset = queryset.filter(actor_object_id=user.pk)

        elif filter_type == 'my_documents':
            # Actions related to documents accessible to the user
            # This is a simplified version - in production, ACL checks would be needed
            document_ct = ContentType.objects.get_for_model(Document)
            queryset = queryset.filter(target_content_type=document_ct)

        elif filter_type == 'all':
            # All actions (admin view)
            pass  # No additional filtering

        else:
            # Default to my_actions
            queryset = queryset.filter(actor_object_id=user.pk)

        # Limit to recent actions for performance
        return queryset[:500]  # Last 500 actions

    def _serialize_action(self, action):
        """
        Serialize an Action object to API response format.
        """
        return {
            'id': action.pk,
            'timestamp': action.timestamp.isoformat(),
            'actor': self._serialize_actor(action.actor),
            'verb': self._translate_verb(action.verb),
            'verb_code': action.verb,
            'target': self._serialize_target(action.target, action.target_content_type),
            'description': self._build_description(action)
        }

    def _serialize_actor(self, actor):
        """
        Serialize the actor (user) of the action.
        """
        if not actor:
            return {
                'id': None,
                'username': 'system',
                'full_name': _('System')
            }

        return {
            'id': actor.pk,
            'username': getattr(actor, 'username', 'unknown'),
            'full_name': getattr(actor, 'get_full_name', lambda: _('Unknown User'))()
        }

    def _serialize_target(self, target, content_type):
        """
        Serialize the target of the action.
        """
        if not target:
            return None

        # Build URL based on content type
        url = None
        if content_type and target:
            if content_type.model == 'document':
                url = f'/api/v4/documents/{target.pk}/'
            elif content_type.model == 'documentfile':
                url = f'/api/v4/document_files/{target.pk}/'
            # Add more content types as needed

        return {
            'id': target.pk,
            'type': content_type.model if content_type else 'unknown',
            'label': str(target),
            'url': url
        }

    def _translate_verb(self, verb):
        """
        Translate action verb to user-friendly text.
        """
        return self.VERB_TRANSLATIONS.get(verb, verb)

    def _build_description(self, action):
        """
        Build a human-readable description of the action.
        """
        actor_name = getattr(action.actor, 'username', _('System')) if action.actor else _('System')
        verb = self._translate_verb(action.verb)
        target_label = str(action.target) if action.target else _('unknown object')

        return _(f"User {actor_name} {verb} '{target_label}'")


class DashboardActivityView(APIView):
    """
    Lightweight activity feed for dashboard widget.

    Endpoint: GET /api/v4/headless/dashboard/activity/
    Returns last N events (default 20, max 50) in flattened format.
    """

    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            limit = min(int(request.query_params.get('limit', 20)), 50)

            queryset = Action.objects.select_related(
                'actor_content_type', 'target_content_type', 'action_object_content_type'
            ).order_by('-timestamp')[:limit]

            serializer = ActivityFeedSerializer(queryset, many=True)
            return Response(serializer.data)

        except Exception as exc:
            logger.error(
                'Error retrieving dashboard activity feed for %s: %s',
                request.user.username,
                exc
            )
            return Response(
                {
                    'error': _('Error retrieving activity feed'),
                    'error_code': 'INTERNAL_ERROR'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
