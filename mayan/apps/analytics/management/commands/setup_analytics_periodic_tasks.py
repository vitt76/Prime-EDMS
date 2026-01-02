from django.core.management.base import BaseCommand
from django_celery_beat.models import IntervalSchedule, PeriodicTask


class Command(BaseCommand):
    help = 'Create/update Celery Beat periodic tasks for analytics.'

    def handle(self, *args, **options):
        hourly_6, _ = IntervalSchedule.objects.get_or_create(
            every=6, period=IntervalSchedule.HOURS
        )
        daily_24, _ = IntervalSchedule.objects.get_or_create(
            every=24, period=IntervalSchedule.HOURS
        )

        tasks = (
            {
                'name': 'analytics_cleanup_old_events',
                'task': 'mayan.apps.analytics.tasks.cleanup_old_events',
                'interval': daily_24,
                'kwargs': '{"retention_days": 90}',
                'queue': 'documents',
            },
            {
                'name': 'analytics_aggregate_daily_metrics',
                'task': 'mayan.apps.analytics.tasks.aggregate_daily_metrics',
                'interval': hourly_6,
                'queue': 'documents',
            },
            {
                'name': 'analytics_aggregate_search_daily_metrics',
                'task': 'mayan.apps.analytics.tasks.aggregate_search_daily_metrics',
                'interval': hourly_6,
                'queue': 'documents',
            },
            {
                'name': 'analytics_aggregate_user_daily_metrics',
                'task': 'mayan.apps.analytics.tasks.aggregate_user_daily_metrics',
                'interval': hourly_6,
                'queue': 'documents',
            },
            {
                'name': 'analytics_calculate_cdn_daily_costs',
                'task': 'mayan.apps.analytics.tasks.calculate_cdn_daily_costs',
                'interval': daily_24,
                'queue': 'documents',
            },
            {
                'name': 'analytics_generate_alerts',
                'task': 'mayan.apps.analytics.tasks.generate_analytics_alerts',
                'interval': daily_24,
                'queue': 'documents',
            },
            {
                'name': 'analytics_aggregate_campaign_engagement',
                'task': 'mayan.apps.analytics.tasks.aggregate_campaign_engagement_daily_metrics',
                'interval': daily_24,
                'queue': 'documents',
            },
            {
                'name': 'analytics_sync_external_metrics',
                'task': 'mayan.apps.analytics.tasks.sync_external_metrics',
                'interval': hourly_6,
                'kwargs': '{"days": 7, "limit_assets": 500}',
                'queue': 'analytics',
            },
        )

        created_or_updated = 0
        for task_def in tasks:
            name = task_def.pop('name')
            PeriodicTask.objects.update_or_create(
                name=name,
                defaults={
                    **task_def,
                    'enabled': True,
                }
            )
            created_or_updated += 1

        self.stdout.write(f'Analytics periodic tasks configured: {created_or_updated}')
