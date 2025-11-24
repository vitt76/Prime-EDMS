from django.contrib import messages
from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.generic import DetailView, ListView, TemplateView, UpdateView

from mayan.apps.acls.models import AccessControlList
from mayan.apps.documents.models import Document
from mayan.apps.documents.permissions import permission_document_view
from mayan.apps.views.generics import (
    ConfirmView, MultipleObjectFormActionView, SimpleView,
    SingleObjectCreateView, SingleObjectDeleteView, SingleObjectEditView,
    SingleObjectListView
)
from mayan.apps.views.mixins import ViewPermissionCheckViewMixin

from .forms import DocumentAIAnalysisForm
from .icons import icon_dam, icon_ai_analysis_list
from .models import DocumentAIAnalysis
from .permissions import (
    permission_ai_analysis_delete, permission_ai_analysis_edit,
    permission_ai_analysis_view
)
from .tasks import analyze_document_with_ai


class DocumentAIAnalysisDetailView(SimpleView):
    """
    Detail view for DAM AI analysis results.
    Shows AI-generated metadata, tags, rights, etc.
    """
    template_name = 'dam/asset_detail.html'
    view_permission = permission_ai_analysis_view

    def get_object(self):
        """Get AI analysis object."""
        ai_analysis_id = self.kwargs.get('ai_analysis_id')
        
        # Get object with related document
        # view_permission is already checked by SimpleView via ViewPermissionCheckViewMixin
        ai_analysis = get_object_or_404(
            DocumentAIAnalysis.objects.select_related('document'),
            pk=ai_analysis_id
        )
        
        return ai_analysis

    def get_extra_context(self):
        """Add context data for template."""
        ai_analysis = self.get_object()

        return {
            'object': ai_analysis,
            'document': ai_analysis.document,
            'latest_file': ai_analysis.document.files.order_by('-timestamp').first(),
            'can_reanalyze': ai_analysis.analysis_status in ['completed', 'failed'],
            'can_edit': ai_analysis.analysis_status == 'completed',
            'formatted_tags': ai_analysis.get_ai_tags_list(),
            'formatted_colors': ai_analysis.get_dominant_colors_list(),
            'title': _('AI Analysis: %s') % ai_analysis.document.label,
        }


class DocumentAIAnalysisEditView(UpdateView):
    """
    Edit view for DAM AI analysis results.
    Allows manual override of AI-generated metadata.
    """
    model = DocumentAIAnalysis
    form_class = DocumentAIAnalysisForm
    template_name = 'dam/asset_edit.html'
    pk_url_kwarg = 'ai_analysis_id'

    def get_queryset(self):
        return DocumentAIAnalysis.objects.select_related('document')

    def get_success_url(self):
        return reverse(
            'dam:asset_detail',
            kwargs={'ai_analysis_id': self.object.pk}
        )

    def form_valid(self, form):
        messages.success(
            self.request,
            _('AI analysis metadata updated successfully.')
        )
        return super().form_valid(form)


class DocumentAIAnalysisReanalyzeView(ConfirmView):
    """
    Trigger re-analysis of a document with AI.
    """
    model = DocumentAIAnalysis
    object_permission = permission_ai_analysis_edit
    pk_url_kwarg = 'ai_analysis_id'

    def get_object(self):
        if not hasattr(self, '_dam_ai_analysis_object'):
            queryset = self.get_queryset()
            self._dam_ai_analysis_object = get_object_or_404(
                queryset, pk=self.kwargs.get(self.pk_url_kwarg)
            )
        return self._dam_ai_analysis_object

    def get_extra_context(self):
        return {
            'object': self.get_object(),
            'submit_label': _('Start re-analysis'),
            'title': _('Re-analyze document with AI')
        }

    def view_action(self, form=None):
        ai_analysis = self.get_object()
        ai_analysis.analysis_status = 'pending'
        ai_analysis.save()

        analyze_document_with_ai.delay(ai_analysis.document.id)

        messages.success(
            self.request,
            _('Document re-analysis scheduled. This may take several minutes.')
        )

    def get_success_url(self):
        return reverse(
            'dam:asset_detail',
            kwargs={'ai_analysis_id': self.get_object().pk}
        )


class DAMDashboardView(SimpleView):
    """
    DAM dashboard with statistics and overview.
    """
    template_name = 'dam/dashboard.html'
    view_icon = icon_dam

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get statistics
        total_analyses = DocumentAIAnalysis.objects.count()
        completed_analyses = DocumentAIAnalysis.objects.filter(analysis_status='completed').count()
        processing_analyses = DocumentAIAnalysis.objects.filter(analysis_status='processing').count()
        failed_analyses = DocumentAIAnalysis.objects.filter(analysis_status='failed').count()
        pending_analyses = DocumentAIAnalysis.objects.filter(analysis_status='pending').count()

        # Get recent analyses
        recent_analyses = DocumentAIAnalysis.objects.select_related('document').order_by('-created')[:10]

        # Get provider statistics
        provider_stats = DocumentAIAnalysis.objects.values('ai_provider').annotate(
            count=Count('ai_provider')
        ).order_by('-count')

        context.update({
            'title': _('Digital Asset Management Dashboard'),
            'total_analyses': total_analyses,
            'completed_analyses': completed_analyses,
            'processing_analyses': processing_analyses,
            'failed_analyses': failed_analyses,
            'pending_analyses': pending_analyses,
            'completion_rate': (completed_analyses / total_analyses * 100) if total_analyses > 0 else 0,
            'recent_analyses': recent_analyses,
            'provider_stats': provider_stats,
        })

        return context


class DocumentAIAnalysisListView(ViewPermissionCheckViewMixin, ListView):
    """
    List view for all AI analyses.
    """
    model = DocumentAIAnalysis
    template_name = 'dam/ai_analysis_list.html'
    context_object_name = 'object_list'
    object_permission = permission_ai_analysis_view

    def get_queryset(self):
        return DocumentAIAnalysis.objects.select_related('document').order_by('-created')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': _('AI Analysis Results'),
            'hide_object': True,
        })
        return context


class DAMTestView(SimpleView):
    """
    Test view for DAM functionality.
    """
    template_name = 'dam/test.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class DocumentDAMMetadataView(DetailView):
    """
    Show DAM metadata for a document (creates AI analysis if needed).
    """
    template_name = 'dam/asset_detail.html'

    def get_object(self):
        document_id = self.kwargs.get('document_id')
        document = get_object_or_404(Document, pk=document_id)

        # Check permissions
        AccessControlList.objects.check_access(
            obj=document,
            permissions=(permission_document_view,),
            user=self.request.user
        )

        # Get or create AI analysis
        ai_analysis, created = DocumentAIAnalysis.objects.get_or_create(
            document=document,
            defaults={'analysis_status': 'pending'}
        )

        # Trigger analysis if newly created
        if created:
            analyze_document_with_ai.delay(document.id)

        return ai_analysis

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ai_analysis = self.get_object()

        context['document'] = ai_analysis.document
        context['latest_file'] = ai_analysis.document.files.order_by('-timestamp').first()
        context['can_reanalyze'] = ai_analysis.analysis_status in ['completed', 'failed']
        context['can_edit'] = ai_analysis.analysis_status == 'completed'
        context['formatted_tags'] = ai_analysis.get_ai_tags_list()
        context['formatted_colors'] = ai_analysis.get_dominant_colors_list()

        return context
