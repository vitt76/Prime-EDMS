import logging
import operator
import time
from datetime import timedelta
import uuid

from django.conf import settings
from django.apps import apps
from django.utils import timezone

from rest_framework.filters import BaseFilterBackend

from .classes import SearchBackend, SearchModel
from .exceptions import DynamicSearchException
from .literals import QUERY_PARAMETER_ANY_FIELD
from .utils import get_match_all_value

logger = logging.getLogger(name=__name__)


class RESTAPISearchFilter(BaseFilterBackend):
    def _should_track_search(self, search_model):
        try:
            model = search_model.model
        except Exception:
            return False

        # Track only document searches to avoid logging every list filter usage.
        return (
            model._meta.app_label == 'documents' and model._meta.model_name in ('document', 'documentsearchresult')
        )

    def _get_results_count(self, search_queryset):
        try:
            return search_queryset.count()
        except Exception:
            try:
                return len(search_queryset)
            except Exception:
                return None

    def _track_search_query(self, *, request, query_dict_cleaned, results_count, response_time_ms):
        try:
            SearchQuery = apps.get_model('analytics', 'SearchQuery')
        except Exception:
            return
        try:
            SearchSession = apps.get_model('analytics', 'SearchSession')
        except Exception:
            SearchSession = None

        query_text = query_dict_cleaned.get(QUERY_PARAMETER_ANY_FIELD) or ''
        if not query_text:
            query_text = ' '.join([str(value) for value in query_dict_cleaned.values()]).strip()

        user = request.user if getattr(request, 'user', None) and request.user.is_authenticated else None
        user_department = ''
        if user:
            user_department = getattr(user, 'department', '') or ''

        # Best-effort search session linking (for Search-to-Find metrics).
        search_session_id = None
        if user and SearchSession is not None:
            now = timezone.now()
            window_start = now - timedelta(minutes=30)
            session = (
                SearchSession.objects.filter(user=user, ended_at__isnull=True, started_at__gte=window_start)
                .order_by('-started_at')
                .first()
            )
            if not session:
                session = SearchSession.objects.create(id=uuid.uuid4(), user=user, started_at=now)
            search_session_id = session.pk

        query = SearchQuery.objects.create(
            user=user,
            query_text=(query_text or '')[:500],
            search_type=SearchQuery.SEARCH_TYPE_KEYWORD,
            results_count=results_count,
            response_time_ms=response_time_ms,
            filters_applied=query_dict_cleaned,
            user_department=user_department,
            search_session_id=search_session_id
        )

        if user and SearchSession is not None and search_session_id:
            try:
                SearchSession.objects.filter(pk=search_session_id, first_search_query__isnull=True).update(
                    first_search_query=query
                )
            except Exception:
                pass

    def get_search_model(self, queryset):
        try:
            model = queryset.model
        except AttributeError:
            return
        else:
            try:
                return SearchModel.get_for_model(instance=model)
            except KeyError:
                return

    def filter_queryset(self, request, queryset, view):
        if not getattr(view, 'search_disable_list_filtering', False):
            search_model = self.get_search_model(queryset=queryset)
            if search_model:
                query_dict = request.GET.dict().copy()
                query_dict.update(request.POST.dict())

                global_and_search = get_match_all_value(
                    value=query_dict.get('_match_all')
                )

                search_model_fields = list(
                    map(
                        operator.itemgetter(0),
                        search_model.get_fields_simple_list()
                    )
                )

                search_model_fields.append(QUERY_PARAMETER_ANY_FIELD)

                valid_search_models_query_dict_keys = set(
                    query_dict.keys()
                ).intersection(
                    set(search_model_fields)
                )

                query_dict_cleaned = {
                    key: query_dict[key] for key in valid_search_models_query_dict_keys
                }

                if query_dict_cleaned:
                    try:
                        start = time.monotonic()
                        search_queryset = SearchBackend.get_instance().search(
                            global_and_search=global_and_search,
                            search_model=search_model,
                            query=query_dict_cleaned, user=request.user
                        )
                    except DynamicSearchException as exception:
                        if settings.DEBUG or settings.TESTING:
                            raise

                        logger.error(
                            'Error performing REST API list search filtering; %s',
                            exception
                        )
                        return search_model.model._meta.default_manager.none()
                    else:
                        if self._should_track_search(search_model=search_model):
                            results_count = self._get_results_count(
                                search_queryset=search_queryset
                            )
                            response_time_ms = int((time.monotonic() - start) * 1000)

                            self._track_search_query(
                                request=request,
                                query_dict_cleaned=query_dict_cleaned,
                                results_count=results_count,
                                response_time_ms=response_time_ms
                            )
                        return queryset.filter(pk__in=search_queryset)
                else:
                    return queryset
            else:
                return queryset
        else:
            return queryset
