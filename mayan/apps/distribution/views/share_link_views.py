from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView

from ..models import Publication, ShareLink


class ShareLinkCreateView(LoginRequiredMixin, TemplateView):
    template_name = 'distribution/share_link_create.html'

    def dispatch(self, request, *args, **kwargs):
        self.publication = get_object_or_404(
            Publication,
            pk=kwargs.get('publication_id'),
            owner=request.user
        )
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['publication'] = self.publication
        return context

    def post(self, request, *args, **kwargs):
        expires_at = request.POST.get('expires_at')
        max_downloads = request.POST.get('max_downloads')

        share_link = ShareLink.objects.create(
            publication=self.publication,
            expires_at=expires_at or None,
            max_downloads=max_downloads or None
        )

        messages.success(
            request,
            _('Ссылка для публикации "{title}" создана.').format(title=self.publication.title)
        )

        return redirect('{}?publication={}'.format(
            reverse('distribution:share_link_manage'),
            self.publication.pk
        ))
