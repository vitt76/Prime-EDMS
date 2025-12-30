from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone


class Command(BaseCommand):
    help = 'Initialize default CDN rates for analytics.'

    def handle(self, *args, **options):
        try:
            from mayan.apps.analytics.models import CDNRate
        except Exception as exc:
            self.stderr.write(f'Cannot import CDNRate: {exc}')
            return

        cost_per_gb_usd = float(getattr(settings, 'ANALYTICS_CDN_COST_PER_GB_USD', 0.10))
        today = timezone.now().date()

        obj, created = CDNRate.objects.get_or_create(
            region='default',
            channel='default',
            effective_from=today,
            defaults={'cost_per_gb_usd': cost_per_gb_usd}
        )
        if not created:
            obj.cost_per_gb_usd = cost_per_gb_usd
            obj.save(update_fields=('cost_per_gb_usd',))

        self.stdout.write(f'Default CDN rate ready (USD/GB={cost_per_gb_usd}).')


