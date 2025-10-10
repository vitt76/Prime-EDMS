with open('mayan/apps/converter_pipeline_extension/views.py', 'a') as f:
    f.write('''


class DocumentFileConvertRedirectView(ExternalObjectViewMixin, RedirectView):
    external_object_class = DocumentFile
    external_object_pk_url_kwarg = 'document_file_id'

    def get_redirect_url(self, *args, **kwargs):
        document_file = self.get_external_object()
        return f"/#/converter-pipeline/convert/{document_file.pk}/"
''')
