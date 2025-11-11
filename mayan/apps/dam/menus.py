from django.utils.translation import ugettext_lazy as _

from mayan.apps.navigation.classes import Menu

from .icons import icon_dam

__all__ = ('menu_dam',)

menu_dam = Menu(
    icon=icon_dam, label=_('Digital Asset Management'),
    name='dam'
)
