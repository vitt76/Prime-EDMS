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
        # Если передан rendition_id, получаем его для предвыбора
        rendition_id = kwargs.get('rendition_id')
        if rendition_id:
            self.rendition = get_object_or_404(
                GeneratedRendition,
                pk=rendition_id,
                publication_item__publication__owner=self.request.user
            )
        else:
            self.rendition = None
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Получаем все публикации пользователя
        publications = Publication.objects.filter(owner=self.request.user)

        # Получаем все рендишены из этих публикаций
        renditions = GeneratedRendition.objects.filter(
            publication_item__publication__owner=self.request.user
        ).select_related(
            'publication_item__publication',
            'preset'
        ).order_by('publication_item__publication__title', 'preset__name')

        # Определяем выбранную публикацию
        selected_publication = None
        if self.rendition:
            selected_publication = self.rendition.publication_item.publication
        else:
            # Проверяем параметр publication из query string
            publication_id = self.request.GET.get('publication')
            if publication_id:
                try:
                    selected_publication = publications.get(pk=publication_id)
                except Publication.DoesNotExist:
                    pass

        context.update({
            'publications': publications,
            'renditions': renditions,
            'selected_rendition': self.rendition,
            'selected_publication': selected_publication,
        })

        return context

    def post(self, request, *args, **kwargs):
        rendition_id = request.POST.get('rendition')
        expires_at = request.POST.get('expires_at')
        max_downloads = request.POST.get('max_downloads')

        # Получаем выбранный rendition
        rendition = get_object_or_404(
            GeneratedRendition,
            pk=rendition_id,
            publication_item__publication__owner=self.request.user
        )

        share_link = ShareLink.objects.create(
            rendition=rendition,
            expires_at=expires_at or None,
            max_downloads=max_downloads or None
        )

        messages.success(
            request,
            _('Ссылка для рендишена "{preset}" публикации "{title}" создана.').format(
                preset=rendition.preset.name,
                title=rendition.publication_item.publication.title
            )
        )

        return redirect('{}?publication={}'.format(
            reverse('distribution:share_link_manage'),
            rendition.publication_item.publication.pk
        ))
