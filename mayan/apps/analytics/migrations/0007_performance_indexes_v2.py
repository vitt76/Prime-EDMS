from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('analytics', '0006_search_sessions_cdn_feature_engagement'),
    ]

    operations = [
        migrations.RunSQL(
            sql=(
                'CREATE INDEX IF NOT EXISTS idx_asset_events_user_timestamp '
                'ON analytics_asset_events(user_id, timestamp DESC);'
            ),
            reverse_sql='DROP INDEX IF EXISTS idx_asset_events_user_timestamp;'
        ),
        migrations.RunSQL(
            sql=(
                'CREATE INDEX IF NOT EXISTS idx_search_queries_user_timestamp '
                'ON analytics_search_queries(user_id, timestamp DESC);'
            ),
            reverse_sql='DROP INDEX IF EXISTS idx_search_queries_user_timestamp;'
        ),
    ]


