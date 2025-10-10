from django.conf import settings
print([app for app in settings.INSTALLED_APPS if "converter" in app.lower()])
