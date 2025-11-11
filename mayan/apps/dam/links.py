from django.utils.translation import ugettext_lazy as _

from mayan.apps.navigation.classes import Link

from .icons import icon_dam, icon_ai_analysis_list
from .permissions import permission_ai_analysis_view


link_dam_dashboard = Link(
    icon=icon_dam,
    text=_('Dashboard'),
    view='dam:dashboard'
)

link_ai_analysis_list = Link(
    icon=icon_ai_analysis_list,
    permissions=(permission_ai_analysis_view,),
    text=_('AI Analyses'),
    view='dam:ai_analysis_list'
)

link_dam_test = Link(
    icon=icon_dam,
    text=_('DAM Test'),
    view='dam:test'
)
