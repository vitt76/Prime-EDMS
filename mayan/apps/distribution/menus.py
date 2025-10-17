from django.utils.translation import ugettext_lazy as _

from mayan.apps.navigation.classes import Link

from .icons import icon_distribution
from .permissions import permission_publication_api_view

# Главное меню Distribution как пункт первого уровня со ссылкой
link_distribution_menu = Link(
    icon=icon_distribution,
    permissions=(permission_publication_api_view,),
    text=_('Публикации'),
    view='distribution:publication_list'
)
