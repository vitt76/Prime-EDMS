import uuid
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _


STATUS_CHOICES = (
    ('draft', _('Draft')),
    ('published', _('Published')),
)

PLAN_TYPE_CHOICES = (
    ('saas', _('SaaS')),
    ('standalone', _('Standalone')),
    ('both', _('Both')),
)


class Page(models.Model):
    slug = models.SlugField(unique=True)
    title = models.JSONField(default=dict)
    meta_title = models.JSONField(default=dict)
    meta_description = models.JSONField(default=dict)
    og_image = models.URLField(blank=True)
    canonical_url = models.URLField(blank=True)
    sections = models.JSONField(default=list)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    published_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('slug',)

    def __str__(self) -> str:
        return self.slug


class Post(models.Model):
    slug = models.SlugField(unique=True)
    title = models.JSONField(default=dict)
    excerpt = models.JSONField(default=dict)
    content = models.TextField(blank=True)
    content_html = models.TextField(blank=True)
    featured_image = models.URLField(blank=True)
    author_name = models.CharField(max_length=255, blank=True)
    author_avatar = models.URLField(blank=True)
    category = models.CharField(max_length=255, blank=True)
    tags = models.JSONField(default=list)
    reading_time_minutes = models.PositiveIntegerField(default=5)
    seo_title = models.JSONField(default=dict)
    seo_description = models.JSONField(default=dict)
    og_image = models.URLField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    published_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-published_at', '-created_at')

    def __str__(self) -> str:
        return self.slug


class Plan(models.Model):
    name = models.CharField(max_length=255)
    description = models.JSONField(default=dict)
    price_monthly = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    price_yearly = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=10, default='USD')
    billing_period = models.CharField(max_length=20, default='month')
    storage_gb = models.IntegerField(null=True, blank=True)
    max_users = models.IntegerField(null=True, blank=True)
    max_api_calls_monthly = models.IntegerField(null=True, blank=True)
    features = models.JSONField(default=list)
    recommended = models.BooleanField(default=False)
    type = models.CharField(max_length=20, choices=PLAN_TYPE_CHOICES, default='saas')
    cta_text = models.CharField(max_length=255, blank=True)
    cta_url = models.CharField(max_length=255, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ('order', 'name')

    def __str__(self) -> str:
        return self.name


class FAQ(models.Model):
    section = models.CharField(max_length=255)
    question = models.JSONField(default=dict)
    answer = models.JSONField(default=dict)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ('section', 'order')

    def __str__(self) -> str:
        return f'{self.section} #{self.order}'


class Lead(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    company = models.CharField(max_length=255, blank=True)
    message = models.TextField(blank=True)
    phone = models.CharField(max_length=64, blank=True)
    subject = models.CharField(max_length=255, blank=True)
    source = models.CharField(max_length=255, default='contact')
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self) -> str:
        return f'{self.email} ({self.source})'


class EmailVerificationToken(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    token = models.CharField(max_length=128, unique=True)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)

    @classmethod
    def create_for_user(cls, user, ttl_hours: int = 48):
        token = uuid.uuid4().hex
        return cls.objects.create(
            user=user,
            token=token,
            expires_at=timezone.now() + timedelta(hours=ttl_hours)
        )

    def is_valid(self) -> bool:
        return self.used_at is None and self.expires_at > timezone.now()
