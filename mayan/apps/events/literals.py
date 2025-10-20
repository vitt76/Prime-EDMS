from django.utils.translation import ugettext_lazy as _

DEFAULT_EVENT_LIST_EXPORT_FILENAME = 'events_list.csv'

EVENT_MANAGER_ORDER_AFTER = 1
EVENT_MANAGER_ORDER_BEFORE = 2

EVENT_TYPE_NAMESPACE_NAME = 'events'
EVENT_EVENTS_CLEARED_NAME = 'event_cleared'
EVENT_EVENTS_EXPORTED_NAME = 'event_exported'

TEXT_UNKNOWN_EVENT_ID = _('Unknown or obsolete event type: %s')
