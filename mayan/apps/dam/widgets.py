from django import forms
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _


class DAMWidget(forms.widgets.Widget):
    """
    Lightweight widget for rendering AI/DAM analysis inside document detail views.

    The widget fetches `DocumentAIAnalysis` data and renders a compact summary.
    No AJAX is used to keep the implementation simple for now.
    """

    default_css_class = 'dam-analysis-widget'

    def __init__(self, attrs=None):
        attrs = attrs or {}
        css_class = attrs.get('class', '')
        if self.default_css_class not in css_class:
            attrs['class'] = ('{} {}'.format(css_class, self.default_css_class)).strip()
        super().__init__(attrs=attrs)

    def render(self, name, value, attrs=None, renderer=None):
        attrs = (attrs or {}).copy()
        document_id = attrs.get('data-document-id') or value
        data = self._get_analysis_data(document_id=document_id)
        html = self._render_block(data=data)
        return mark_safe(html)

    # ------------------------------------------------------------------ helpers
    def _get_analysis_data(self, document_id):
        if not document_id:
            return {'status': 'missing'}

        try:
            from mayan.apps.dam.models import DocumentAIAnalysis
        except ImportError:
            return {'status': 'missing'}

        try:
            analysis = DocumentAIAnalysis.objects.select_related('document').get(
                document_id=document_id
            )
        except DocumentAIAnalysis.DoesNotExist:
            return {'status': 'missing'}

        tags = getattr(analysis, 'get_ai_tags_list', lambda: [])()
        categories = analysis.categories or []
        completed = ''
        if getattr(analysis, 'analysis_completed', None):
            completed = analysis.analysis_completed.strftime('%d.%m.%Y %H:%M')

        return {
            'status': analysis.analysis_status or 'pending',
            'description': analysis.ai_description or '',
            'tags': tags,
            'categories': categories,
            'provider': analysis.ai_provider or _('Unknown'),
            'completed': completed
        }

    def _render_block(self, data):
        status = data.get('status', 'missing')

        if status == 'completed':
            return self._render_completed(data)
        if status == 'processing':
            return self._render_processing()
        if status == 'failed':
            return self._render_failed()
        return self._render_missing()

    def _render_completed(self, data):
        description = data.get('description')
        tags_html = ''.join(
            '<span class="badge badge-primary mr-1 mb-1">{}</span>'.format(tag)
            for tag in data.get('tags', [])
        )
        categories_html = ''.join(
            '<span class="badge badge-info mr-1 mb-1">{}</span>'.format(cat)
            for cat in data.get('categories', [])
        )
        provider = data.get('provider')
        completed = data.get('completed')

        return '''
        <div class="dam-analysis-content panel panel-default">
            <div class="panel-heading">
                <strong>{title}</strong>
            </div>
            <div class="panel-body">
                {description_block}
                {tags_block}
                {categories_block}
                <div class="text-muted small">
                    {provider_label}: {provider}{completed_block}
                </div>
            </div>
        </div>
        '''.format(
            title=_('AI analysis'),
            description_block=(
                '<p class="mb-2">{}</p>'.format(description)
                if description else
                '<p class="text-muted">{}</p>'.format(_('No description provided'))
            ),
            tags_block=(
                '<div class="mb-2"><strong>{}:</strong><div class="mt-1">{}</div></div>'.format(
                    _('Tags'), tags_html)
                if tags_html else ''
            ),
            categories_block=(
                '<div class="mb-2"><strong>{}:</strong><div class="mt-1">{}</div></div>'.format(
                    _('Categories'), categories_html)
                if categories_html else ''
            ),
            provider_label=_('Provider'),
            provider=provider,
            completed_block=' | {} {}'.format(_('Completed'), completed) if completed else ''
        )

    def _render_processing(self):
        return '''
        <div class="alert alert-info text-center dam-analysis-content">
            <i class="fas fa-spinner fa-spin fa-lg mr-2"></i>
            {message}
        </div>
        '''.format(message=_('AI analysis is still running'))

    def _render_failed(self):
        return '''
        <div class="alert alert-danger dam-analysis-content">
            <strong>{title}</strong><br/>
            {message}
        </div>
        '''.format(
            title=_('AI analysis failed'),
            message=_('Try rerunning the task or check provider logs.')
        )

    def _render_missing(self):
        return '''
        <div class="alert alert-default dam-analysis-content">
            {message}
        </div>
        '''.format(message=_('No AI analysis data for this document yet.'))

