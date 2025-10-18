from django.utils.translation import ugettext_lazy as _

from mayan.apps.navigation.classes import Menu

from .icons import icon_distribution
from .permissions import permission_publication_api_view

menu_distribution = Menu(
    icon=icon_distribution,
    label=_('Публикации'),
    name='distribution'
)
