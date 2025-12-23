"""
Activity feed views for Headless API.

Provides REST endpoints for personalized activity feeds that Mayan EDMS
doesn't provide through its standard API.
"""

from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from django.core.paginator import EmptyPage, Paginator
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from mayan.apps.acls.models import AccessControlList
from mayan.apps.documents.models import Document
from mayan.apps.documents.permissions import permission_document_view
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

    # Noise filters: hide internal/system maintenance events by default.
    IMPORTANT_VERB_PREFIXES = (
        'documents.',
        'document_parsing.',
        'file_metadata.',
        'ocr.',
        'authentication.',
        'user_management.',
        'document_states.',
        'tags.',
        'metadata.',
        'cabinets.',
    )

    # System/noisy events that should be hidden by default from UI activity feeds.
    # Can be enabled via query param `system=1`.
    SYSTEM_VERB_PREFIXES = (
        'file_caching.',
        'logging.',
        'locks.',
        'task_manager.',
    )

    DOCUMENT_VERB_RU = {
        'documents.document_create': _('загрузил документ'),
        'documents.document_file_created': _('добавил файл к документу'),
        'documents.document_version_created': _('создал версию документа'),
        'documents.document_file_downloaded': _('скачал файл документа'),
        'documents.document_view': _('открыл документ'),
        'documents.document_delete': _('удалил документ'),
        'documents.document_trashed': _('переместил документ в корзину'),
        'documents.document_properties_edited': _('изменил документ'),
    }

    AUTH_VERB_RU = {
        'authentication.user_logged_in': _('вошёл в систему'),
        'authentication.user_logged_out': _('вышел из системы'),
    }

    # Class-level cache for ContentType objects
    _document_ct = None
    _user_ct = None

    @classmethod
    def _get_document_content_type(cls):
        """
        Get or cache Document ContentType for performance.
        """
        if cls._document_ct is None:
            cls._document_ct = ContentType.objects.get_for_model(Document)
        return cls._document_ct

    @classmethod
    def _get_user_content_type(cls):
        """
        Get or cache User ContentType for performance.
        """
        if cls._user_ct is None:
            cls._user_ct = ContentType.objects.get_for_model(get_user_model())
        return cls._user_ct

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

            # Batch prefetch Document objects to avoid N+1 queries
            prefetched_documents = self._prefetch_documents_for_actions(page_obj.object_list)

            # Serialize results
            results = [
                self._serialize_action(action, prefetched_documents=prefetched_documents)
                for action in page_obj.object_list
            ]

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
        # Only admins can request full feed.
        if filter_type == 'all' and not (
            getattr(user, 'is_staff', False) or getattr(user, 'is_superuser', False)
        ):
            filter_type = 'my_documents'

        # Action uses generic relations for actor/target/action_object; those cannot
        # be used with select_related(). We can however select_related the
        # ContentType FKs to reduce queries.
        queryset = Action.objects.select_related(
            'actor_content_type', 'target_content_type', 'action_object_content_type'
        ).order_by('-timestamp')

        # Default behavior: hide noisy internal events unless explicitly asked.
        # Query param "important" defaults to true.
        important_only = True
        try:
            raw_important = self.request.query_params.get('important', '1')
            important_only = raw_important not in ('0', 'false', 'False', 'no', 'No')
        except Exception:
            important_only = True

        include_system = False
        try:
            raw_system = self.request.query_params.get('system', '0')
            include_system = raw_system in ('1', 'true', 'True', 'yes', 'Yes')
        except Exception:
            include_system = False

        if not include_system:
            # Hide "system" actions by default:
            # - actions without an actor
            # - actions whose actor is not a user model instance
            user_ct = self._get_user_content_type()
            system_actor_q = (
                Q(actor_content_type__isnull=True) |
                Q(actor_object_id__isnull=True) |
                ~Q(actor_content_type=user_ct)
            )
            queryset = queryset.exclude(system_actor_q)

            # Hide known noisy verb namespaces (even if a user triggered them).
            if self.SYSTEM_VERB_PREFIXES:
                system_verb_q = Q()
                for prefix in self.SYSTEM_VERB_PREFIXES:
                    system_verb_q |= Q(verb__startswith=prefix)
                queryset = queryset.exclude(system_verb_q)

        if important_only:
            prefix_q = Q()
            for prefix in self.IMPORTANT_VERB_PREFIXES:
                prefix_q |= Q(verb__startswith=prefix)
            queryset = queryset.filter(prefix_q)

        if filter_type == 'my_actions':
            # Only actions performed by the current user
            queryset = queryset.filter(actor_object_id=user.pk)

        elif filter_type == 'my_documents':
            # Actions related to documents accessible to the user
            document_ct = self._get_document_content_type()
            # ACL-filter documents for the requesting user.
            # Staff/superusers with direct permission will get full queryset.
            allowed_documents = AccessControlList.objects.restrict_queryset(
                permission=permission_document_view,
                queryset=Document.valid.all(),
                user=user
            ).values_list('pk', flat=True)

            # Document-related actions can reference the document either as target
            # (documents.document_create) or as action_object (version/file processing).
            queryset = queryset.filter(
                Q(target_content_type=document_ct, target_object_id__in=allowed_documents)
                | Q(action_object_content_type=document_ct, action_object_object_id__in=allowed_documents)
            )

        elif filter_type == 'all':
            # All actions (admin view)
            pass  # No additional filtering

        else:
            # Default to my_actions
            queryset = queryset.filter(actor_object_id=user.pk)

        # Limit to recent actions for performance
        return queryset[:500]  # Last 500 actions

    def _prefetch_documents_for_actions(self, actions):
        """
        Batch prefetch Document objects referenced in actions to avoid N+1 queries.
        
        Returns a dictionary mapping document_id -> Document instance.
        """
        document_ids = set()
        document_ct = self._get_document_content_type()

        for action in actions:
            if action.target_content_type == document_ct and action.target_object_id:
                document_ids.add(action.target_object_id)
            if action.action_object_content_type == document_ct and action.action_object_object_id:
                document_ids.add(action.action_object_object_id)

        prefetched_documents = {}
        if document_ids:
            # Use only() to minimize data transfer and prefetch related objects
            documents = Document.objects.filter(pk__in=document_ids).only(
                'id', 'label', 'uuid', 'datetime_created'
            ).prefetch_related('files', 'versions__version_pages')
            prefetched_documents = {doc.pk: doc for doc in documents}

        return prefetched_documents

    def _serialize_action(self, action, prefetched_documents=None):
        """
        Serialize an Action object to API response format.
        
        Args:
            action: Action instance to serialize
            prefetched_documents: Dictionary of prefetched Document objects (document_id -> Document)
        """
        if prefetched_documents is None:
            prefetched_documents = {}
        
        return {
            'id': action.pk,
            'timestamp': action.timestamp.isoformat(),
            'actor': self._serialize_actor(action.actor),
            'verb': self._translate_verb(action.verb),
            'verb_code': action.verb,
            'target': self._serialize_target(
                action.target, 
                action.target_content_type,
                prefetched_documents=prefetched_documents
            ),
            'description': self._build_description(action, prefetched_documents=prefetched_documents)
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

        username = getattr(actor, 'username', None)
        if not username:
            # Some actions might have non-user actors; fallback to a readable identifier.
            username = (
                getattr(actor, 'email', None) or
                getattr(actor, 'label', None) or
                getattr(actor, 'name', None) or
                'system'
            )

        if hasattr(actor, 'get_full_name'):
            full_name = actor.get_full_name() or str(actor)
        else:
            full_name = str(actor)

        return {
            'id': actor.pk,
            'username': username,
            'full_name': full_name
        }

    def _serialize_target(self, target, content_type, prefetched_documents=None):
        """
        Serialize the target of the action.
        
        Args:
            target: Target object (may be None or deleted)
            content_type: ContentType of the target
            prefetched_documents: Dictionary of prefetched Document objects
        """
        if not target and not content_type:
            return None

        # Use prefetched document if available (for Document type)
        if prefetched_documents and content_type and content_type.model == 'document':
            document = prefetched_documents.get(target.pk if target else None)
            if document:
                target = document

        # Handle deleted or missing objects
        if not target:
            return {
                'id': None,
                'type': content_type.model if content_type else 'unknown',
                'label': _('Deleted %(type)s') % {'type': content_type.model if content_type else 'object'},
                'url': None
            }

        # Build URL based on content type
        url = None
        try:
            if content_type and target:
                if content_type.model == 'document':
                    url = f'/api/v4/documents/{target.pk}/'
                elif content_type.model == 'documentfile':
                    url = f'/api/v4/document_files/{target.pk}/'
                # Add more content types as needed
        except (AttributeError, Exception):
            url = None

        # Get label with error handling
        try:
            label = str(target)
        except (AttributeError, Exception):
            label = _('Deleted %(type)s') % {'type': content_type.model if content_type else 'object'}

        return {
            'id': target.pk,
            'type': content_type.model if content_type else 'unknown',
            'label': label,
            'url': url
        }

    def _translate_verb(self, verb):
        """
        Translate action verb to user-friendly text.
        """
        if verb in self.DOCUMENT_VERB_RU:
            return self.DOCUMENT_VERB_RU[verb]
        if verb in self.AUTH_VERB_RU:
            return self.AUTH_VERB_RU[verb]
        # Fallback: keep technical verb (frontend may still show it for debugging).
        return verb

    def _build_description(self, action, prefetched_documents=None):
        """
        Build a human-readable description of the action.
        
        Args:
            action: Action instance
            prefetched_documents: Dictionary of prefetched Document objects
        """
        if prefetched_documents is None:
            prefetched_documents = {}
        
        actor_name = getattr(action.actor, 'username', _('Система')) if action.actor else _('Система')
        verb_ru = self._translate_verb(action.verb)

        # Prefer document label when the action references a document as action_object.
        doc_label = None
        try:
            if action.action_object_content_type and action.action_object_content_type.model == 'document':
                # Use prefetched document if available
                if prefetched_documents and action.action_object_object_id:
                    document = prefetched_documents.get(action.action_object_object_id)
                    if document:
                        doc_label = str(document)
                    else:
                        # Fallback to direct access if not in prefetched
                        doc_label = str(action.action_object) if action.action_object else None
                else:
                    # Fallback to direct access if prefetch not available
                    doc_label = str(action.action_object) if action.action_object else None
        except (AttributeError, Exception):
            doc_label = None

        target_label = None
        try:
            if action.target:
                # Use prefetched document if available
                if prefetched_documents and action.target_content_type and action.target_content_type.model == 'document':
                    document = prefetched_documents.get(action.target_object_id)
                    if document:
                        target_label = str(document)
                    else:
                        # Fallback to direct access if not in prefetched
                        target_label = str(action.target)
                else:
                    # Fallback to direct access if prefetch not available
                    target_label = str(action.target)
        except (AttributeError, Exception):
            target_label = None

        if doc_label:
            return _('%(actor)s %(verb)s "%(doc)s"') % {
                'actor': actor_name, 'verb': verb_ru, 'doc': doc_label
            }
        if target_label:
            return _('%(actor)s %(verb)s "%(target)s"') % {
                'actor': actor_name, 'verb': verb_ru, 'target': target_label
            }
        return _('%(actor)s %(verb)s') % {'actor': actor_name, 'verb': verb_ru}


class DashboardActivityView(APIView):
    """
    Lightweight activity feed for dashboard widget.

    Endpoint: GET /api/v4/headless/dashboard/activity/
    Returns last N events (default 20, max 50) in flattened format.
    """

    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    # Class-level cache for ContentType objects
    _document_ct = None

    @classmethod
    def _get_document_content_type(cls):
        """
        Get or cache Document ContentType for performance.
        """
        if cls._document_ct is None:
            cls._document_ct = ContentType.objects.get_for_model(Document)
        return cls._document_ct

    def _prefetch_documents_for_actions(self, actions):
        """
        Batch prefetch Document objects referenced in actions to avoid N+1 queries.
        
        Returns a dictionary mapping document_id -> Document instance.
        """
        document_ids = set()
        document_ct = self._get_document_content_type()

        for action in actions:
            if action.target_content_type == document_ct and action.target_object_id:
                document_ids.add(action.target_object_id)
            if action.action_object_content_type == document_ct and action.action_object_object_id:
                document_ids.add(action.action_object_object_id)

        prefetched_documents = {}
        if document_ids:
            # Use only() to minimize data transfer and prefetch related objects
            documents = Document.objects.filter(pk__in=document_ids).only(
                'id', 'label', 'uuid', 'datetime_created'
            ).prefetch_related('files', 'versions__version_pages')
            prefetched_documents = {doc.pk: doc for doc in documents}

        return prefetched_documents

    def get(self, request):
        try:
            limit = min(int(request.query_params.get('limit', 20)), 50)

            queryset = Action.objects.select_related(
                'actor_content_type', 'target_content_type', 'action_object_content_type'
            ).order_by('-timestamp')[:limit]

            # Convert queryset to list for prefetching
            actions_list = list(queryset)
            
            # Batch prefetch Document objects to avoid N+1 queries
            prefetched_documents = self._prefetch_documents_for_actions(actions_list)

            serializer = ActivityFeedSerializer(
                actions_list, 
                many=True,
                context={'prefetched_documents': prefetched_documents}
            )
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
