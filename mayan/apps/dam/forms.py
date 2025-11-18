from django import forms
from django.utils.translation import ugettext_lazy as _

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

    def clean_categories(self):
        """Convert comma-separated string back to list."""
        data = self.cleaned_data.get('categories', '')
        if data:
            return [cat.strip() for cat in data.split(',') if cat.strip()]
        return []

    def clean_people(self):
        """Convert comma-separated string back to list."""
        data = self.cleaned_data.get('people', '')
        if data:
            return [person.strip() for person in data.split(',') if person.strip()]
        return []

    def clean_locations(self):
        """Convert comma-separated string back to list."""
        data = self.cleaned_data.get('locations', '')
        if data:
            return [loc.strip() for loc in data.split(',') if loc.strip()]
        return []
