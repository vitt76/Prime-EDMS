import logging

from django.conf import settings
from django.contrib import messages
from django.template import RequestContext
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.generic.base import RedirectView

from mayan.apps.views.generics import (
    ConfirmView, FormView, SingleObjectListView
)
from mayan.apps.views.literals import LIST_MODE_CHOICE_ITEM

from .classes import SearchBackend
from .exceptions import DynamicSearchException
from .forms import SearchForm, AdvancedSearchForm
from .icons import (
    icon_result_list, icon_search, icon_search_advanced,
    icon_search_backend_reindex, icon_search_submit
)
from .links import link_search_again
from .literals import QUERY_PARAMETER_ANY_FIELD, SEARCH_MODEL_NAME_KWARG
from .permissions import permission_search_tools
from .tasks import task_reindex_backend
from .utils import get_match_all_value
from .view_mixins import SearchModelViewMixin

logger = logging.getLogger(name=__name__)


class ResultsView(SearchModelViewMixin, SingleObjectListView):
    search_disable_list_filtering = True
    view_icon = icon_result_list

    def get_extra_context(self):
        context = {
            'hide_object': True,
            'no_results_icon': icon_search_submit,
            'no_results_main_link': link_search_again.resolve(
                context=RequestContext(
                    request=self.request, dict_={
                        'search_model': self.search_model
                    }
                )
            ),
            'no_results_text': _(
                'Try again using different terms. '
            ),
            'no_results_title': _('No search results'),
            'search_model': self.search_model,
            'title': _('Search results for: %s') % self.search_model.label,
        }

        if self.search_model.list_mode == LIST_MODE_CHOICE_ITEM:
            context['list_as_items'] = True

        return context

    def get_source_queryset(self):
        query_dict = self.request.GET.dict().copy()
        query_dict.update(self.request.POST.dict())

        global_and_search = get_match_all_value(
            value=query_dict.get('_match_all')
        )

        try:
            queryset = SearchBackend.get_instance().search(
                global_and_search=global_and_search,
                search_model=self.search_model,
                query=query_dict, user=self.request.user
            )
        except DynamicSearchException as exception:
            if settings.DEBUG or settings.TESTING:
                raise

            messages.error(message=exception, request=self.request)
            return self.search_model.model._meta.default_manager.none()
        else:
            return queryset


class SearchAgainView(RedirectView):
    query_string = True

    def get_redirect_url(self, *args, **kwargs):
        query_dict = self.request.GET.dict().copy()
        query_dict.update(self.request.POST.dict())

        search_term_any_field = query_dict.get(
            QUERY_PARAMETER_ANY_FIELD, ''
        ).strip()

        if search_term_any_field:
            self.pattern_name = 'search:search'
        else:
            self.pattern_name = 'search:search_advanced'

        return super().get_redirect_url(*args, **kwargs)


class SearchBackendReindexView(ConfirmView):
    extra_context = {
        'message': _(
            'This tool is required only for some search backends. '
            'Search results will be affected while the backend is '
            'being reindexed.'
        ),
        'title': _('Reindex search backend'),
        'subtitle': _(
            'This tool erases and populates the search backend\'s '
            'internal index.'
        ),
    }
    view_icon = icon_search_backend_reindex
    view_permission = permission_search_tools

    def get_post_action_redirect(self):
        return reverse(viewname='common:tools_list')

    def view_action(self):
        task_reindex_backend.apply_async()

        messages.success(
            message=_('Search backend reindexing queued.'),
            request=self.request
        )


class SearchView(SearchModelViewMixin, FormView):
    template_name = 'appearance/generic_form.html'
    title = _('Search')
    view_icon = icon_search

    def get_extra_context(self):
        self.search_model = self.get_search_model()
        return {
            'form': self.get_form(),
            'form_action': reverse(
                viewname='search:results', kwargs={
                    SEARCH_MODEL_NAME_KWARG: self.search_model.get_full_name()
                }
            ),
            'search_model': self.search_model,
            'submit_icon': icon_search_submit,
            'submit_label': _('Search'),
            'submit_method': 'GET',
            'title': _('Search for: %s') % self.search_model.label,
        }

    def get_form(self):
        query_dict = self.request.GET.dict().copy()
        query_dict.update(self.request.POST.dict())

        search_term_any_field = query_dict.get(
            QUERY_PARAMETER_ANY_FIELD, ''
        ).strip()

        if search_term_any_field:
            return SearchForm(
                initial={
                    QUERY_PARAMETER_ANY_FIELD: search_term_any_field
                }
            )
        else:
            return SearchForm()


class AdvancedSearchView(SearchView):
    title = _('Advanced search')
    view_icon = icon_search_advanced

    def get_form(self):
        return AdvancedSearchForm(
            data=self.request.GET.dict(),
            search_model=self.get_search_model()
        )
