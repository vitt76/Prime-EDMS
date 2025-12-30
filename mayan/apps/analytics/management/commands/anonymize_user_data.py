from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Anonymize/delete analytics personal data for a user (Right to be Forgotten).'

    def add_arguments(self, parser):
        parser.add_argument('--user-id', type=int, required=False)
        parser.add_argument('--username', type=str, required=False)

    def handle(self, *args, **options):
        user_id = options.get('user_id')
        username = (options.get('username') or '').strip()

        if not user_id and not username:
            self.stderr.write('Provide --user-id or --username')
            return

        User = get_user_model()
        if user_id:
            user = User.objects.filter(pk=user_id).first()
        else:
            user = User.objects.filter(username=username).first()

        if not user:
            self.stderr.write('User not found')
            return

        from mayan.apps.analytics.models import FeatureUsage, SearchQuery, SearchSession, UserSession

        deleted = {}
        deleted['feature_usage'], _ = FeatureUsage.objects.filter(user=user).delete()
        deleted['search_queries'], _ = SearchQuery.objects.filter(user=user).delete()
        deleted['search_sessions'], _ = SearchSession.objects.filter(user=user).delete()
        deleted['user_sessions'], _ = UserSession.objects.filter(user=user).delete()

        self.stdout.write(f'Analytics personal data removed: {deleted}')


