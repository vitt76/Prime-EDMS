import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, HttpResponse, FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views.generic import (
    CreateView, DetailView, ListView, TemplateView, UpdateView, RedirectView, DeleteView, View
)

# SPA-compatible UI views using SingleObjectDetailView like converter_pipeline_extension
from mayan.apps.views.generics import SingleObjectListView, SingleObjectDetailView

# Import models early
from mayan.apps.documents.models import Document, DocumentFile
from .models import (
    GeneratedRendition,
    Publication, PublicationItem, Recipient, RenditionPreset, ShareLink
) # Добавлены импорты моделей


class PublicationListTemplateView(TemplateView):
    """SPA-compatible view for publications list"""
    template_name = 'distribution/publication_list.html'


class PublicationCreateTemplateView(TemplateView):
    """SPA-compatible view for creating publications"""
    template_name = 'distribution/publication_create.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['document_id'] = self.kwargs.get('document_id')
        return context


class RecipientsTemplateView(TemplateView):
    """SPA-compatible view for managing recipients"""
    template_name = 'distribution/recipient_list.html'


class PresetsTemplateView(TemplateView):
    """SPA-compatible view for managing presets"""
    template_name = 'distribution/preset_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['presets'] = RenditionPreset.objects.select_related('recipient').order_by('name')
        return context


class PresetCreateTemplateView(TemplateView):
    """SPA-compatible view for creating a preset"""
    template_name = 'distribution/preset_create.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recipients'] = Recipient.objects.all().order_by('name', 'email')
        return context


class PresetEditTemplateView(TemplateView):
    """SPA-compatible view for editing a preset"""
    template_name = 'distribution/preset_edit.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        preset = get_object_or_404(RenditionPreset, pk=self.kwargs['preset_id'])
        context['preset'] = preset
        context['recipients'] = Recipient.objects.all().order_by('name', 'email')
        return context


class PresetDeleteTemplateView(TemplateView):
    """SPA-compatible view for confirming preset deletion"""
    template_name = 'distribution/preset_delete.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        preset = get_object_or_404(RenditionPreset, pk=self.kwargs['preset_id'])
        context['preset'] = preset
        return context


class PresetEditView(LoginRequiredMixin, UpdateView):
    model = RenditionPreset
    fields = ['name', 'resource_type', 'format', 'width', 'height', 'quality', 'description', 'watermark']
    template_name = 'distribution/preset_edit_form.html'

    def get_success_url(self):
        messages.success(self.request, _('Пресет обновлён.'))
        return reverse('distribution:preset_list')


class PresetDeleteView(LoginRequiredMixin, DeleteView):
    model = RenditionPreset
    template_name = 'distribution/preset_confirm_delete.html'

    def get_success_url(self):
        messages.success(self.request, _('Пресет удалён.'))
        return reverse('distribution:preset_list')

class ShareLinksTemplateView(TemplateView):
    """SPA-compatible view for managing share links"""
    template_name = 'distribution/share_link_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        publication_id = self.request.GET.get('publication')
        if publication_id:
            try:
                publication = Publication.objects.get(pk=publication_id, owner=self.request.user)
                context['current_publication'] = publication
            except Publication.DoesNotExist:
                context['current_publication'] = None
        return context


class TestView(TemplateView):
    """Test view for SPA integration"""
    template_name = 'distribution/test_template.html'


class SimpleTestView(TemplateView):
    """Simple test view that returns HTML directly"""
    template_name = None

    def get(self, request, *args, **kwargs):
        html = (
            '<!DOCTYPE html><html><head><meta charset="utf-8">'
            '<title>Distribution Test</title></head>'
            '<body style="padding:20px;font-family:Arial, sans-serif;">'
            '<h1 style="color:#5cb85c;">Distribution SPA Integration Test</h1>'
            '<p style="font-size:18px;">This page is working! Distribution module is integrated.</p>'
            '<div style="margin-top:20px;">'
            '<a href="#/documents/" style="color:#337ab7;text-decoration:none;">'
            '← Back to Documents</a></div>'
            '</body></html>'
        )
        return HttpResponse(html)

from mayan.apps.documents.permissions import permission_document_view

from .permissions import (
    permission_publication_api_create, permission_publication_api_edit,
    permission_publication_api_view, permission_recipient_manage,
    permission_rendition_preset_manage
)

logger = logging.getLogger(name=__name__)


# ===== ДОКУМЕНТЫ =====

class PublicationCreateFromDocumentView(LoginRequiredMixin, CreateView):
    """Создание публикации из одного документа"""
    model = Publication
    template_name = 'distribution/publication_create_from_document.html'
    fields = ['title', 'description']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        document = get_object_or_404(
            Document,
            pk=self.kwargs['document_id']
        )
        context['document'] = document
        context['title'] = _('Создание публикации для документа: {}').format(document)
        return context

    def form_valid(self, form):
        document = get_object_or_404(
            Document,
            pk=self.kwargs['document_id']
        )

        # Создаем публикацию
        publication = form.save(commit=False)
        publication.owner = self.request.user
        publication.save()

        # Добавляем документ в публикацию
        for document_file in document.files.all():
            publication.items.create(document_file=document_file)

        messages.success(
            self.request,
            _('Публикация "{}" создана успешно.').format(publication.title)
        )

        return HttpResponseRedirect(
            reverse('distribution:publication_detail', args=(publication.pk,))
        )


class DocumentPublicationsView(LoginRequiredMixin, ListView):
    """Просмотр всех публикаций документа"""
    model = Publication
    template_name = 'distribution/document_publications.html'
    context_object_name = 'publications'
    permission_required = permission_document_view

    def get_queryset(self):
        document = get_object_or_404(
            Document,
            pk=self.kwargs['document_id']
        )
        queryset = Publication.objects.filter(
            items__document_file__document=document
        ).distinct()
        if not self.request.user.is_staff:
            queryset = queryset.filter(owner=self.request.user)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        document = get_object_or_404(
            Document,
            pk=self.kwargs['document_id']
        )
        context['document'] = document
        context['title'] = _('Публикации документа: {}').format(document)
        return context


class PublicationCreateMultipleView(LoginRequiredMixin, TemplateView):
    """Создание публикации из нескольких выбранных документов"""
    template_name = 'distribution/publication_create_multiple.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        document_ids = self.request.GET.getlist('document_id')
        documents = Document.objects.filter(pk__in=document_ids)
        context['documents'] = documents
        context['title'] = _('Создание публикации из {} документов').format(documents.count())
        return context

    def post(self, request, *args, **kwargs):
        document_ids = request.POST.getlist('document_id')
        title = request.POST.get('title')
        description = request.POST.get('description', '')

        if not title:
            messages.error(request, _('Необходимо указать название публикации.'))
            return self.get(request, *args, **kwargs)

        # Создаем публикацию
        publication = Publication.objects.create(
            title=title,
            description=description,
            owner=request.user
        )

        # Добавляем документы в публикацию
        documents = Document.objects.filter(pk__in=document_ids)
        for document in documents:
            for document_file in document.files.all():
                publication.items.create(document_file=document_file)

        messages.success(
            request,
            _('Публикация "{}" создана успешно с {} документами.').format(
                publication.title, documents.count()
            )
        )

        return HttpResponseRedirect(
            reverse('distribution:publication_detail', args=(publication.pk,))
        )


# ===== ФАЙЛЫ ДОКУМЕНТОВ =====

class AddDocumentsToPublicationView(LoginRequiredMixin, TemplateView):
    """Добавление документов в существующую публикацию"""
    template_name = 'distribution/add_documents_to_publication.html'

    def dispatch(self, request, *args, **kwargs):
        self.publication = get_object_or_404(
            Publication,
            pk=kwargs['publication_id'],
            owner=request.user
        )
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Получаем документы пользователя, которые еще не в этой публикации
        from mayan.apps.documents.models import Document
        existing_document_ids = set(
            item.document_file.document_id
            for item in self.publication.items.all()
        )
        # Получаем документы пользователя (упрощенный подход)
        # Mayan ACL система сама проверит разрешения при добавлении
        available_documents = Document.objects.exclude(
            pk__in=existing_document_ids
        ).order_by('-datetime_created')[:50]  # Ограничиваем для производительности

        context.update({
            'publication': self.publication,
            'available_documents': available_documents,
            'title': _('Добавление документов в публикацию: {}').format(self.publication.title)
        })
        return context

    def post(self, request, *args, **kwargs):
        selected_document_ids = request.POST.getlist('document_ids')
        if not selected_document_ids:
            messages.warning(request, _('Не выбрано ни одного документа.'))
            return self.get(request, *args, **kwargs)

        added_count = 0
        for document_id in selected_document_ids:
            try:
                document = get_object_or_404(Document, pk=document_id)
                # Добавляем все файлы документа в публикацию
                for document_file in document.files.all():
                    if not self.publication.items.filter(document_file=document_file).exists():
                        PublicationItem.objects.create(
                            publication=self.publication,
                            document_file=document_file
                        )
                        added_count += 1
            except Exception as e:
                messages.error(request, _('Ошибка при добавлении документа {}: {}').format(document_id, str(e)))

        if added_count > 0:
            messages.success(request, _('Добавлено {} файлов в публикацию.').format(added_count))
            # Запускаем генерацию rendition'ов для новых элементов
            from .tasks import generate_rendition_task
            for item in self.publication.items.filter(document_file__document__pk__in=selected_document_ids):
                for preset in self.publication.presets.all():
                    generate_rendition_task.delay(
                        GeneratedRendition.objects.get_or_create(
                            publication_item=item,
                            preset=preset,
                            defaults={'status': 'pending'}
                        )[0].id
                    )

        return redirect('distribution:publication_detail', pk=self.publication.pk)


class AddToPublicationView(LoginRequiredMixin, TemplateView):
    """Добавление файла в существующую публикацию"""
    template_name = 'distribution/add_to_publication.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        document_file = get_object_or_404(
            DocumentFile,
            pk=self.kwargs['document_file_id']
        )
        publications = Publication.objects.filter(
            owner=self.request.user
        ).order_by('-created')
        context['document_file'] = document_file
        context['publications'] = publications
        context['title'] = _('Добавление файла в публикацию')
        return context

    def post(self, request, *args, **kwargs):
        document_file = get_object_or_404(
            DocumentFile,
            pk=self.kwargs['document_file_id']
        )
        publication_id = request.POST.get('publication_id')

        if not publication_id:
            messages.error(request, _('Необходимо выбрать публикацию.'))
            return self.get(request, *args, **kwargs)

        try:
            publication = Publication.objects.get(
                pk=publication_id,
                owner=request.user
            )
        except Publication.DoesNotExist:
            messages.error(request, _('Публикация не найдена.'))
            return self.get(request, *args, **kwargs)

        # Проверяем, не добавлен ли уже этот файл
        if publication.items.filter(document_file=document_file).exists():
            messages.warning(
                request,
                _('Файл уже добавлен в эту публикацию.')
            )
        else:
            publication.items.create(document_file=document_file)
            messages.success(
                request,
                _('Файл добавлен в публикацию "{}".').format(publication.title)
            )

        return HttpResponseRedirect(
            reverse('documents:document_file_list', args=(document_file.document.pk,))
        )


class GenerateFileRenditionsView(LoginRequiredMixin, TemplateView):
    """Генерация rendition'ов для файла"""
    template_name = 'distribution/generate_file_renditions.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        document_file = get_object_or_404(
            DocumentFile,
            pk=self.kwargs['document_file_id']
        )
        presets = RenditionPreset.objects.all().order_by('name')
        publications = Publication.objects.filter(
            items__document_file=document_file
        ).distinct()
        context['document_file'] = document_file
        context['presets'] = presets
        context['publications'] = publications
        context['title'] = _('Генерация версий файла')
        return context

    def post(self, request, *args, **kwargs):
        document_file = get_object_or_404(
            DocumentFile,
            pk=self.kwargs['document_file_id']
        )
        preset_ids = request.POST.getlist('preset_ids')

        if not preset_ids:
            messages.error(request, _('Необходимо выбрать хотя бы один пресет.'))
            return self.get(request, *args, **kwargs)

        presets = RenditionPreset.objects.filter(pk__in=preset_ids)

        publication_items = list(PublicationItem.objects.filter(
            document_file=document_file
        ).select_related('publication'))

        if not publication_items:
            messages.warning(
                request,
                _('Файл не входит ни в одну публикацию, генерация невозможна.')
            )
            return HttpResponseRedirect(
                reverse('documents:document_file_list', args=(document_file.document.pk,))
            )

        started = 0

        for preset in presets:
            for publication_item in publication_items:
                rendition = preset.generate_rendition(publication_item)
                if rendition.status in ['pending', 'processing']:
                    started += 1

        if started:
            messages.success(
                request,
                _('Запущена генерация {count} рендишенов. Обновите статус позднее.').format(count=started)
            )
        else:
            messages.info(
                request,
                _('Для выбранных пресетов уже существуют готовые версии.')
            )

        return HttpResponseRedirect(
            reverse('documents:document_file_list', args=(document_file.document.pk,))
        )


# ===== УПРАВЛЕНИЕ ПУБЛИКАЦИЯМИ =====

class PublicationDetailView(LoginRequiredMixin, DetailView):
    """Детальный просмотр публикации"""
    model = Publication
    template_name = 'distribution/publication_detail.html'
    context_object_name = 'publication'

    def get_queryset(self):
        queryset = Publication.objects.all()
        if not self.request.user.is_staff:
            queryset = queryset.filter(owner=self.request.user)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        publication = self.object
        items_queryset = publication.items.select_related(
            'document_file', 'document_file__document'
        )
        context['items'] = items_queryset
        first_item = items_queryset.first()
        if first_item:
            context['first_document_file_id'] = first_item.document_file_id
        else:
            context['first_document_file_id'] = None
        context['title'] = _('Публикация: {}').format(publication.title)
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        rendition_id = request.POST.get('delete_rendition_id')

        if rendition_id:
            try:
                rendition = GeneratedRendition.objects.get(
                    pk=rendition_id,
                    publication_item__publication=self.object
                )
                rendition.delete()
                messages.success(
                    request,
                    _('Версия файла удалена.')
                )
            except GeneratedRendition.DoesNotExist:
                messages.error(
                    request,
                    _('Не удалось найти выбранную версию файла.')
                )

        return HttpResponseRedirect(
            reverse('distribution:publication_detail', args=(self.object.pk,))
        )


# ===== УПРАВЛЕНИЕ ПОЛУЧАТЕЛЯМИ =====

class RecipientManagementView(LoginRequiredMixin, ListView):
    """Управление получателями"""
    model = Recipient
    template_name = 'distribution/recipient_management.html'
    context_object_name = 'recipients'

    def get_queryset(self):
        return Recipient.objects.all().order_by('name')


# ===== УПРАВЛЕНИЕ ПРЕСЕТАМИ =====

class PresetManagementView(LoginRequiredMixin, ListView):
    """Управление пресетами rendition'ов"""
    model = RenditionPreset
    template_name = 'distribution/preset_management.html'
    context_object_name = 'presets'

    def get_queryset(self):
        return RenditionPreset.objects.all().order_by('name')


# ===== УПРАВЛЕНИЕ ССЫЛКАМИ =====

class ShareLinkManagementView(LoginRequiredMixin, ListView):
    """Управление ссылками для скачивания"""
    model = ShareLink
    template_name = 'distribution/share_link_management.html'
    context_object_name = 'share_links'

    def get_queryset(self):
        queryset = ShareLink.objects.filter(
            rendition__publication_item__publication__owner=self.request.user
        ).select_related(
            'rendition__preset',
            'rendition__publication_item__publication'
        ).order_by('-created')

        publication_id = self.request.GET.get('publication')
        if publication_id:
            queryset = queryset.filter(rendition__publication_item__publication__pk=publication_id)
        return queryset

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

        context.update({
            'publications': publications,
            'renditions': renditions,
        })

        publication_id = self.request.GET.get('publication')
        if publication_id:
            try:
                publication = Publication.objects.get(pk=publication_id, owner=self.request.user)
                context['current_publication'] = publication
            except Publication.DoesNotExist:
                context['current_publication'] = None
        return context


# ===== ПОЛНОЦЕННЫЕ UI VIEWS =====

class PublicationEditView(LoginRequiredMixin, UpdateView):
    """Редактирование публикации"""
    model = Publication
    template_name = 'distribution/publication_edit.html'
    fields = ['title', 'description']
    context_object_name = 'publication'

    def get_queryset(self):
        queryset = Publication.objects.all()
        if not self.request.user.is_staff:
            queryset = queryset.filter(owner=self.request.user)
        return queryset

    def get_success_url(self):
        return reverse('distribution:publication_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('Редактирование публикации: {}').format(self.object.title)
        return context


class PublicationCreateView(LoginRequiredMixin, CreateView):
    """Создание новой публикации"""
    model = Publication
    template_name = 'distribution/publication_create.html'
    fields = ['title', 'description']
    success_url = reverse_lazy('distribution:publication_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class RecipientsListView(LoginRequiredMixin, ListView):
    """Список получателей"""
    model = Recipient
    template_name = 'distribution/recipient_list.html'
    context_object_name = 'recipients'

    def get_queryset(self):
        return Recipient.objects.all().order_by('name')


class PresetsListView(LoginRequiredMixin, ListView):
    """Список пресетов"""
    model = RenditionPreset
    template_name = 'distribution/preset_list.html'
    context_object_name = 'presets'

    def get_queryset(self):
        return RenditionPreset.objects.all().order_by('name')


class ShareLinksListView(LoginRequiredMixin, ListView):
    """Список ссылок для скачивания"""
    model = ShareLink
    template_name = 'distribution/share_link_list.html'
    context_object_name = 'share_links'

    def get_queryset(self):
        return ShareLink.objects.filter(
            publication__owner=self.request.user
        ).order_by('-created')


class PublicationDeleteView(LoginRequiredMixin, TemplateView):
    """Подтверждение и удаление публикации"""
    template_name = 'distribution/publication_confirm_delete.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        publication = get_object_or_404(
            Publication,
            pk=self.kwargs['pk'],
            owner=self.request.user
        )
        context['publication'] = publication
        context['title'] = _('Удаление публикации')
        return context

    def post(self, request, *args, **kwargs):
        publication = get_object_or_404(
            Publication,
            pk=self.kwargs['pk'],
            owner=self.request.user
        )

        publication_title = publication.title
        publication.delete()

        messages.success(
            request,
            _('Публикация "{title}" удалена.').format(title=publication_title)
        )

        return HttpResponseRedirect(reverse('distribution:publication_list'))


class RenditionDownloadView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        rendition = get_object_or_404(GeneratedRendition, pk=kwargs['rendition_id'])

        publication = rendition.publication_item.publication
        if not request.user.is_staff and publication.owner != request.user:
            raise Http404

        if not rendition.file:
            raise Http404

        # Попытка отдать файл напрямую
        try:
            filename = rendition.file.name.rsplit('/', 1)[-1]
            return FileResponse(
                rendition.file.open(mode='rb'),
                as_attachment=True,
                filename=filename
            )
        except FileNotFoundError:
            raise Http404
        except Exception:
            # Fallback на storage url (например, когда используется внешнее хранилище)
            try:
                redirect_url = rendition.get_download_url()
                if redirect_url:
                    return redirect(redirect_url)
            except Exception:
                pass
            raise Http404
