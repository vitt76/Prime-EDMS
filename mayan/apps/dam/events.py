# -*- coding: utf-8 -*-
"""
DAM event types for notifications and audit.

Sprint 3 Phase 3: Event type for "AI Analysis Completed" so that
subscribers receive notifications (including WebSocket) when analysis finishes.
"""

from django.utils.translation import ugettext_lazy as _

from mayan.apps.events.classes import EventTypeNamespace

namespace = EventTypeNamespace(label=_('Digital Asset Management'), name='dam')

# AI analysis completed: target=Document. Notifications are created for
# users subscribed to this event (globally or for the document).
# get_organization_id_for_notification resolves org from action.target (Document).
event_dam_ai_analysis_completed = namespace.add_event_type(
    label=_('AI analysis completed'),
    name='ai_analysis_completed'
)
