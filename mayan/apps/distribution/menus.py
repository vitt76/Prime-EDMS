from django.utils.translation import ugettext_lazy as _

from mayan.apps.navigation.classes import Menu

from .icons import icon_distribution

# Главное меню Distribution
menu_distribution = Menu(
    icon=icon_distribution,
    name='distribution',
    label=_('DAM Публикации')
)

# Временно пустое меню из-за проблем с namespace
# menu_distribution.bind_links(
#     links=(
#         # Ссылки временно отключены
#     )
# )
