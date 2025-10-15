from django import forms
from django.template.defaultfilters import filesizeformat
from django.utils.translation import ugettext_lazy as _

from mayan.apps.views.forms import DetailForm

from ..fields import DocumentFileField
from ..models.document_file_models import DocumentFile

__all__ = (
    'DocumentFileForm', 'DocumentFilePreviewForm',
    'DocumentFilePropertiesForm'
)


class DocumentFileForm(forms.ModelForm):
    class Meta:
        fields = ('filename', 'comment',)
        model = DocumentFile


class DocumentFilePreviewForm(forms.Form):
    def __init__(self, *args, **kwargs):
        document_file = kwargs.pop('instance', None)
        transformation_instance_list = kwargs.pop(
            'transformation_instance_list', ()
        )
        super().__init__(*args, **kwargs)
        self.fields['document_file'].initial = document_file
        self.fields['document_file'].widget.attrs.update(
            {
                'transformation_instance_list': transformation_instance_list
            }
        )

    document_file = DocumentFileField()


class DocumentFilePropertiesForm(DetailForm):
    """
    Detail class form to display a document file properties
    """
    fieldsets = (
        (
            _('Original'), {
                'fields': ('filename', 'size'),
            }
        ), (
            _('Detected'), {
                'fields': ('mimetype', 'encoding', 'pages'),
            }
        ), (
            _('Storage'), {
                'fields': ('file', 'exists', 'checksum'),
            }
        ), (
            _('Other'), {
                'fields': ('timestamp', 'comment'),
            }
        ),
    )

    class Meta:
        extra_fields = [
            {
                'label': _('Date added'),
                'field': 'timestamp',
                'widget': forms.widgets.DateTimeInput
            },
            {
                'label': _('MIME type'),
                'field': 'mimetype',
            },
            {
                'label': _('Encoding'),
                'field': 'encoding',
            },
            {
                'label': _('Size'),
                'func': lambda document_file: filesizeformat(
                    document_file.size
                ) if document_file.size else '-', 'field': 'size'
            },
            {'label': _('Exists in storage'), 'field': 'exists'},
            {
                'label': _('Path in storage'),
                'field': 'file'
            },
            {'label': _('Checksum'), 'field': 'checksum'},
            {
                'label': _('Pages'),
                'func': lambda document_file: document_file.pages.count(),
                'field': 'pages'
            },
        ]
        fields = ('filename', 'comment',)
        model = DocumentFile
