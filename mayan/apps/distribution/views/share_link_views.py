from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView

from ..models import GeneratedRendition, Publication, ShareLink


class ShareLinkCreateView(LoginRequiredMixin, TemplateView):
    template_name = 'distribution/share_link_create.html'

    def dispatch(self, request, *args, **kwargs):
        self.rendition = get_object_or_404(
            GeneratedRendition,
            pk=kwargs.get('rendition_id'),
            publication_item__publication__owner=self.request.user
        )
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['rendition'] = self.rendition
        context['publication'] = self.rendition.publication_item.publication
        return context

    def post(self, request, *args, **kwargs):
        expires_at = request.POST.get('expires_at')
        max_downloads = request.POST.get('max_downloads')

        share_link = ShareLink.objects.create(
            rendition=self.rendition,
            expires_at=expires_at or None,
            max_downloads=max_downloads or None
        )

        messages.success(
            request,
            _('Ссылка для рендишена "{preset}" публикации "{title}" создана.').format(
                preset=self.rendition.preset.name,
                title=self.rendition.publication_item.publication.title
            )
        )

        return redirect('{}?publication={}'.format(
            reverse('distribution:share_link_manage'),
            self.rendition.publication_item.publication.pk
        ))
