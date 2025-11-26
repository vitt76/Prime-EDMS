from django import forms
from django.utils.translation import ugettext_lazy as _

from mayan.apps.documents.models import DocumentType

from .models import DocumentAIAnalysis


class DocumentAIAnalysisForm(forms.ModelForm):
    """
    Form for editing AI analysis results.
    Allows manual override of AI-generated metadata.
    """

    # Override JSONField widgets for better UX
    ai_tags = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        help_text=_('Comma-separated list of tags (e.g., "portrait, person, outdoor")'),
        label=_('AI Tags')
    )

    categories = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 2}),
        required=False,
        help_text=_('Comma-separated list of categories'),
        label=_('Categories')
    )

    people = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 2}),
        required=False,
        help_text=_('Comma-separated list of people/entities mentioned'),
        label=_('People')
    )

    locations = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 2}),
        required=False,
        help_text=_('Comma-separated list of locations'),
        label=_('Locations')
    )

    class Meta:
        model = DocumentAIAnalysis
        fields = [
            'ai_description', 'ai_tags', 'categories', 'language',
            'people', 'locations', 'copyright_notice', 'usage_rights',
            'rights_expiry', 'alt_text'
        ]
        widgets = {
            'ai_description': forms.Textarea(attrs={'rows': 4}),
            'copyright_notice': forms.Textarea(attrs={'rows': 2}),
            'usage_rights': forms.Textarea(attrs={'rows': 2}),
            'alt_text': forms.Textarea(attrs={'rows': 2}),
            'rights_expiry': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Convert JSON lists to comma-separated strings for editing
        if self.instance and self.instance.pk:
            if isinstance(self.instance.ai_tags, list):
                self.fields['ai_tags'].initial = ', '.join(self.instance.ai_tags)

            if isinstance(self.instance.categories, list):
                self.fields['categories'].initial = ', '.join(self.instance.categories)

            if isinstance(self.instance.people, list):
                self.fields['people'].initial = ', '.join(self.instance.people)

            if isinstance(self.instance.locations, list):
                self.fields['locations'].initial = ', '.join(self.instance.locations)

    def clean_ai_tags(self):
        """Convert comma-separated string back to list."""
        data = self.cleaned_data.get('ai_tags', '')
        if data:
            # Split by comma and strip whitespace
            return [tag.strip() for tag in data.split(',') if tag.strip()]
        return []


class YandexDiskSettingsForm(forms.Form):
    """Form to edit Yandex Disk integration settings."""
    client_id = forms.CharField(
        required=True,
        label=_('Client ID'),
        help_text=_('Application identifier from Yandex OAuth cabinet.')
    )
    client_secret = forms.CharField(
        required=True,
        label=_('Client secret'),
        widget=forms.PasswordInput(render_value=True),
        help_text=_('Secret issued together with Client ID.')
    )
    authorization_code = forms.CharField(
        required=False,
        label=_('Verification code'),
        help_text=_(
            'Optional. Paste the one-time code from https://oauth.yandex.ru/verification_code '
            'to exchange it for an access token automatically.'
        )
    )
    base_path = forms.CharField(
        required=True,
        label=_('Base path'),
        help_text=_('Root folder to import, e.g. disk:/ or disk:/media.')
    )
    cabinet_root_label = forms.CharField(
        required=True,
        label=_('Root cabinet label'),
        help_text=_('Top-level cabinet that will mirror Yandex Disk structure.')
    )
    document_type = forms.ModelChoiceField(
        required=False,
        queryset=DocumentType.objects.none(),
        label=_('Document type'),
        help_text=_('Document type assigned to imported files. Defaults to the first available type.')
    )
    max_file_size_mb = forms.IntegerField(
        required=True,
        min_value=1,
        label=_('Max file size (MB)'),
        help_text=_('Files larger than this limit will be skipped.')
    )
    file_limit = forms.IntegerField(
        required=False,
        min_value=0,
        label=_('Max files per import'),
        help_text=_('0 means no limit. Prevents accidental bulk imports.')
    )

    def __init__(self, *args, **kwargs):
        document_type_id = kwargs.pop('document_type_id', None)
        super().__init__(*args, **kwargs)
        self.fields['document_type'].queryset = DocumentType.objects.order_by('label')
        if document_type_id:
            try:
                self.fields['document_type'].initial = DocumentType.objects.get(pk=document_type_id)
            except DocumentType.DoesNotExist:
                pass

    def clean_document_type(self):
        document_type = self.cleaned_data.get('document_type')
        if not document_type:
            document_type = DocumentType.objects.order_by('label').first()
        if not document_type:
            raise forms.ValidationError(_('Create at least one document type before importing.'))
        return document_type

    def clean_max_file_size_mb(self):
        value = self.cleaned_data['max_file_size_mb']
        return value * 1024 * 1024

    def clean(self):
        cleaned = super().clean()
        code = cleaned.get('authorization_code')
        if code and (not cleaned.get('client_id') or not cleaned.get('client_secret')):
            raise forms.ValidationError(
                _('Provide both Client ID and Client secret to exchange the verification code.')
            )
        return cleaned

