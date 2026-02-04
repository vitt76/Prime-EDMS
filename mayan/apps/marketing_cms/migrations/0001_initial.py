from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(unique=True)),
                ('title', models.JSONField(default=dict)),
                ('meta_title', models.JSONField(default=dict)),
                ('meta_description', models.JSONField(default=dict)),
                ('og_image', models.URLField(blank=True)),
                ('canonical_url', models.URLField(blank=True)),
                ('sections', models.JSONField(default=list)),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('published', 'Published')], default='draft', max_length=20)),
                ('published_at', models.DateTimeField(blank=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={'ordering': ('slug',)},
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(unique=True)),
                ('title', models.JSONField(default=dict)),
                ('excerpt', models.JSONField(default=dict)),
                ('content', models.TextField(blank=True)),
                ('content_html', models.TextField(blank=True)),
                ('featured_image', models.URLField(blank=True)),
                ('author_name', models.CharField(blank=True, max_length=255)),
                ('author_avatar', models.URLField(blank=True)),
                ('category', models.CharField(blank=True, max_length=255)),
                ('tags', models.JSONField(default=list)),
                ('reading_time_minutes', models.PositiveIntegerField(default=5)),
                ('seo_title', models.JSONField(default=dict)),
                ('seo_description', models.JSONField(default=dict)),
                ('og_image', models.URLField(blank=True)),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('published', 'Published')], default='draft', max_length=20)),
                ('published_at', models.DateTimeField(blank=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={'ordering': ('-published_at', '-created_at')},
        ),
        migrations.CreateModel(
            name='Plan',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.JSONField(default=dict)),
                ('price_monthly', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('price_yearly', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('currency', models.CharField(default='USD', max_length=10)),
                ('billing_period', models.CharField(default='month', max_length=20)),
                ('storage_gb', models.IntegerField(blank=True, null=True)),
                ('max_users', models.IntegerField(blank=True, null=True)),
                ('max_api_calls_monthly', models.IntegerField(blank=True, null=True)),
                ('features', models.JSONField(default=list)),
                ('recommended', models.BooleanField(default=False)),
                ('type', models.CharField(choices=[('saas', 'SaaS'), ('standalone', 'Standalone'), ('both', 'Both')], default='saas', max_length=20)),
                ('cta_text', models.CharField(blank=True, max_length=255)),
                ('cta_url', models.CharField(blank=True, max_length=255)),
                ('order', models.PositiveIntegerField(default=0)),
            ],
            options={'ordering': ('order', 'name')},
        ),
        migrations.CreateModel(
            name='FAQ',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('section', models.CharField(max_length=255)),
                ('question', models.JSONField(default=dict)),
                ('answer', models.JSONField(default=dict)),
                ('order', models.PositiveIntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={'ordering': ('section', 'order')},
        ),
        migrations.CreateModel(
            name='Lead',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254)),
                ('company', models.CharField(blank=True, max_length=255)),
                ('message', models.TextField(blank=True)),
                ('phone', models.CharField(blank=True, max_length=64)),
                ('subject', models.CharField(blank=True, max_length=255)),
                ('source', models.CharField(default='contact', max_length=255)),
                ('metadata', models.JSONField(default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={'ordering': ('-created_at',)},
        ),
        migrations.CreateModel(
            name='EmailVerificationToken',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.CharField(max_length=128, unique=True)),
                ('expires_at', models.DateTimeField()),
                ('used_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ('-created_at',)},
        ),
    ]
