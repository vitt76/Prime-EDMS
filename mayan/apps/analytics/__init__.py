"""Analytics app for MAD DAM.

Implements enterprise analytics (Level 1-4) as described in the transformation
specs. This app is designed to be incrementally rolled out starting with
Level 1 asset events and the Asset Bank dashboard.
"""

# Django 3.2 compatibility: ensure our AppConfig.ready() is called.
default_app_config = 'mayan.apps.analytics.apps.AnalyticsApp'


