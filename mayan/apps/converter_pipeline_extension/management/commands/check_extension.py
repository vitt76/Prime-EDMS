from django.core.management.base import BaseCommand
from django.apps import apps


class Command(BaseCommand):
    help = 'Check if Converter Pipeline Extension is loaded'

    def handle(self, *args, **options):
        self.stdout.write('🔍 Checking Converter Pipeline Extension...')

        # Check if app is in INSTALLED_APPS
        installed_apps = [app.name for app in apps.get_app_configs()]
        if 'mayan.apps.converter_pipeline_extension' in installed_apps:
            self.stdout.write(self.style.SUCCESS('✅ Extension found in INSTALLED_APPS'))
        else:
            self.stdout.write(self.style.ERROR('❌ Extension NOT found in INSTALLED_APPS'))
            self.stdout.write('Available apps:')
            for app in sorted(installed_apps):
                self.stdout.write(f'  {app}')

        # Try to get the app config
        try:
            app_config = apps.get_app_config('converter_pipeline_extension')
            self.stdout.write(self.style.SUCCESS(f'✅ App config found: {app_config}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ App config not found: {e}'))

