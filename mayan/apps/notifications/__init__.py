"""Notification Center app for MAD DAM.

This app extends Mayan EDMS notifications (events.Notification) with:
- Templates (notifications.NotificationTemplate)
- User preferences (notifications.NotificationPreference)
- Audit log (notifications.NotificationLog)
"""

# Django 3.2 compatibility: ensure our AppConfig.ready() is called.
default_app_config = 'mayan.apps.notifications.apps.NotificationsApp'


