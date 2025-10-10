from django.utils.translation import gettext_lazy as _

from mayan.apps.documents.permissions import permission_document_file_view
from mayan.apps.navigation.classes import Link


link_document_file_convert = Link(
    args=('resolved_object.pk',),
    icon='fas fa-exchange-alt',
    permissions=(permission_document_file_view,),
    text=_('Сконвертировать'),
    view='converter_pipeline_extension:document_file_convert_redirect'
)


