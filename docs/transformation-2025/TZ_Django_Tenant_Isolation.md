# ТЕХНИЧЕСКОЕ ЗАДАНИЕ
## Часть 2: Tenant-изоляция в Django (Mayan) — Shared DB + Shared Schema

**Версия:** 1.0  
**Дата:** 30 декабря 2025  
**Статус:** Ready for Development  
**Целевая аудитория:** Python/Django разработчики, Database Architect, DevOps  

---

## 1. EXECUTIVE SUMMARY

Требуется реализовать **мульти-тенантную архитектуру** в Django (Mayan EDMS) для поддержки SaaS-модели (один backend, много клиентов) и Standalone-модели (один клиент на выделенном сервере).

**Подход:** Shared Database + Shared Schema + ForeignKey изоляция на уровне `Organization` + Middleware фильтрация.

**Ключевые компоненты:**
- Новое приложение `mayan.apps.organizations` с моделями Org, Subscription, Plan
- Middleware для определения текущего тенанта по домену или токену
- TenantAwareManager для фильтрации QuerySet'ов
- Migration для привязки существующих данных к Organization

---

## 2. ЦЕЛИ И KPI

| # | Цель | Метрика | Целевое значение |
|---|------|---------|------------------|
| 1 | Мульти-тенанси | Количество одновременных тенантов | ≥ 100 на одном сервере |
| 2 | Data isolation | % запросов, защищённых от cross-tenant access | 100% (или 0 успешных хаков) |
| 3 | Performance | Время запроса с фильтрацией по Organization | ≤ 200ms (vs 150ms без фильтра) |
| 4 | Масштабируемость | Поддержка future шардирования | Готовность к migration на shared schema per tenant |
| 5 | Business logic | Enforcement квот (storage, users) | 100% блокировка при превышении |
| 6 | Operational | Время создания нового тенанта | ≤ 5 мин (с инициализацией структуры) |

---

## 3. АРХИТЕКТУРА: SHARED DB + SHARED SCHEMA

```
┌─────────────────────────────────────────────────────────┐
│                   Django Backend                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌───────────────────────────────────────────────────┐ │
│  │ Middleware (TenantResolver)                       │ │
│  │ - По домену или токену определяет Organization   │ │
│  │ - Записывает в request.organization               │ │
│  └───────────────────────────────────────────────────┘ │
│                        ↓                                 │
│  ┌───────────────────────────────────────────────────┐ │
│  │ ViewSet / View                                    │ │
│  │ - Читает request.organization                    │ │
│  │ - QuerySet автоматически фильтруется             │ │
│  └───────────────────────────────────────────────────┘ │
│                        ↓                                 │
│  ┌───────────────────────────────────────────────────┐ │
│  │ ORM Models (TenantAwareManager)                   │ │
│  │ - Document.objects.filter(organization=...)      │ │
│  │ - Все tenant-aware модели используют manager     │ │
│  └───────────────────────────────────────────────────┘ │
│                        ↓                                 │
└────────────────────────┬────────────────────────────────┘
                         │
                ┌────────▼────────┐
                │  PostgreSQL DB  │
                │ (shared schema) │
                │                 │
                │ Table: org_1_docs
                │ Table: org_2_docs
                │ (через FK на Organization)
                └─────────────────┘
```

---

## 4. ФУНКЦИОНАЛЬНЫЕ ТРЕБОВАНИЯ

### 4.1. Модели (mayan.apps.organizations)

#### 4.1.1. Модель `Organization`

**Назначение:** Представлять тенанта (компанию, аккаунт).

**Поля:**

```python
class Organization(models.Model):
    """
    Тенант / Компания
    
    Используется для:
    1. Изоляции данных (все модели имеют FK на Organization)
    2. Мультитенанси (один backend обслуживает N организаций)
    3. Управления подписками (каждая Org имеет Subscription)
    """
    
    # Основные поля
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(
        max_length=255, 
        unique=True,
        help_text="Название организации (уникальное)"
    )
    slug = models.SlugField(
        unique=True,
        help_text="URL-friendly название (для API)"
    )
    description = models.TextField(blank=True)
    
    # Business информация
    email = models.EmailField(
        help_text="Email администратора организации"
    )
    phone = models.CharField(max_length=20, blank=True)
    website = models.URLField(blank=True)
    
    industry = models.CharField(
        max_length=50,
        choices=[
            ('media', 'Media & Entertainment'),
            ('marketing', 'Marketing Agency'),
            ('ecommerce', 'E-commerce'),
            ('healthcare', 'Healthcare'),
            ('legal', 'Legal'),
            ('other', 'Other')
        ],
        default='other'
    )
    
    # Статус
    is_active = models.BooleanField(
        default=True,
        help_text="Может ли эта Org использовать систему?"
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('trial', 'Trial (free)'),
            ('active', 'Active (paid)'),
            ('suspended', 'Suspended (payment issue)'),
            ('archived', 'Archived (deleted)')
        ],
        default='trial',
        db_index=True
    )
    
    # Подписка
    subscription = models.OneToOneField(
        'Subscription',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='organization'
    )
    
    # Deployment mode (SaaS vs Standalone)
    deployment_mode = models.CharField(
        max_length=20,
        choices=[
            ('saas', 'SaaS (Cloud)'),
            ('standalone', 'Standalone (On-Premises)')
        ],
        default='saas',
        editable=False,  # Set once, cannot change
        db_index=True
    )
    
    # Custom domain (для SaaS, опционально)
    custom_domain = models.CharField(
        max_length=255,
        unique=True,
        blank=True,
        null=True,
        help_text="Кастомный домен (например, dam.company.com)"
    )
    custom_domain_verified = models.BooleanField(default=False)
    
    # Квоты (переопределяют defaults из Plan)
    storage_limit_gb = models.IntegerField(
        default=100,
        null=True,
        blank=True,
        help_text="NULL = unlimited. Переопределяет Plan квоту."
    )
    max_users = models.IntegerField(
        default=5,
        help_text="Максимум активных пользователей"
    )
    max_ai_analyses_monthly = models.IntegerField(
        default=100,
        help_text="Максимум AI операций в месяц"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Для оперативных нужд
    logo = models.ImageField(
        upload_to='org-logos/',
        blank=True,
        null=True
    )
    branding_color = models.CharField(
        max_length=7,  # #RRGGBB
        default='#3B82F6'
    )
    
    class Meta:
        db_table = 'organizations_organization'
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active', 'status']),
            models.Index(fields=['custom_domain']),
            models.Index(fields=['created_at']),
        ]
        verbose_name = 'Organization'
        verbose_name_plural = 'Organizations'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"
    
    # Methods
    def get_storage_used_gb(self):
        """Получить используемое хранилище (сумма всех файлов в Org)"""
        from django.db.models import Sum
        from mayan.apps.documents.models import DocumentFile
        
        total_bytes = DocumentFile.objects.filter(
            document__organization=self
        ).aggregate(total=Sum('file_size'))['total'] or 0
        
        return round(total_bytes / (1024 ** 3), 2)
    
    def get_active_users_count(self):
        """Количество активных пользователей в Org"""
        return self.user_set.filter(is_active=True).count()
    
    def is_storage_exceeded(self):
        """Превышен ли лимит хранилища?"""
        if self.storage_limit_gb is None:
            return False
        return self.get_storage_used_gb() > self.storage_limit_gb
    
    def is_user_limit_exceeded(self):
        """Превышен ли лимит пользователей?"""
        return self.get_active_users_count() >= self.max_users
    
    def can_perform_ai_analysis(self):
        """Можно ли выполнить AI анализ в этом месяце?"""
        from django.utils import timezone
        from dateutil.relativedelta import relativedelta
        
        current_month_start = timezone.now().replace(day=1)
        
        from mayan.apps.dam.models import DocumentAIAnalysis
        analyses_this_month = DocumentAIAnalysis.objects.filter(
            document__organization=self,
            created_at__gte=current_month_start
        ).count()
        
        return analyses_this_month < self.max_ai_analyses_monthly
```

**Индексы:**
```sql
CREATE INDEX idx_org_slug ON organizations_organization(slug);
CREATE INDEX idx_org_active_status ON organizations_organization(is_active, status);
CREATE INDEX idx_org_custom_domain ON organizations_organization(custom_domain);
CREATE INDEX idx_org_created ON organizations_organization(created_at DESC);
```

---

#### 4.1.2. Модель `Subscription`

```python
class Subscription(models.Model):
    """
    Подписка на тарифный план
    
    Связывает Organization с Plan и управляет биллингом
    """
    
    id = models.UUIDField(primary_key=True, default=uuid4)
    organization = models.OneToOneField(
        Organization,
        on_delete=models.CASCADE,
        related_name='subscription_details'
    )
    
    # План
    plan = models.ForeignKey(
        'Plan',
        on_delete=models.PROTECT,
        related_name='subscriptions'
    )
    
    # Биллинг
    billing_cycle = models.CharField(
        max_length=10,
        choices=[
            ('monthly', 'Monthly'),
            ('yearly', 'Yearly')
        ],
        default='monthly'
    )
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(null=True, blank=True)
    renewal_date = models.DateField(null=True, blank=True)
    
    # Статус
    status = models.CharField(
        max_length=20,
        choices=[
            ('trial', 'Trial (free)'),
            ('active', 'Active'),
            ('paused', 'Paused'),
            ('cancelled', 'Cancelled'),
            ('expired', 'Expired')
        ],
        default='trial',
        db_index=True
    )
    
    # Payment method
    payment_method = models.CharField(
        max_length=50,
        choices=[
            ('card', 'Credit Card'),
            ('invoice', 'Invoice'),
            ('trial', 'Trial'),
            ('free', 'Free (Internal)')
        ],
        default='trial'
    )
    
    payment_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('paid', 'Paid'),
            ('failed', 'Failed')
        ],
        default='pending'
    )
    
    # Payment details
    next_billing_date = models.DateField(null=True, blank=True)
    last_payment_date = models.DateField(null=True, blank=True)
    
    # Amount
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, default='USD')
    
    # Metadata
    stripe_subscription_id = models.CharField(max_length=255, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'organizations_subscription'
        indexes = [
            models.Index(fields=['status', 'renewal_date']),
            models.Index(fields=['organization', 'status']),
        ]
    
    def __str__(self):
        return f"{self.organization.name} - {self.plan.name}"
    
    def is_active(self):
        """Активна ли подписка прямо сейчас?"""
        from django.utils import timezone
        today = timezone.now().date()
        
        if self.status not in ['active', 'trial']:
            return False
        
        if self.end_date and self.end_date < today:
            return False
        
        return True
    
    def days_until_renewal(self):
        """Дней до следующего платежа"""
        from django.utils import timezone
        if not self.renewal_date:
            return None
        return (self.renewal_date - timezone.now().date()).days
    
    def mark_as_expired(self):
        """Отметить подписку как истекшую"""
        self.status = 'expired'
        self.save()
```

---

#### 4.1.3. Модель `Plan`

```python
class Plan(models.Model):
    """
    Тарифный план (система-уровне, не тенант-уровне)
    
    Определяет features и лимиты для Subscription
    """
    
    id = models.CharField(
        max_length=50,
        primary_key=True,
        help_text="Идентификатор плана (start, pro, enterprise)"
    )
    name = models.CharField(max_length=100)
    description = models.TextField()
    
    # Pricing
    price_monthly = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="NULL = custom pricing (Enterprise)"
    )
    price_yearly = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    currency = models.CharField(max_length=3, default='USD')
    
    # Limits
    storage_gb = models.IntegerField(
        null=True,
        blank=True,
        help_text="NULL = unlimited"
    )
    max_users = models.IntegerField()
    max_ai_analyses_monthly = models.IntegerField()
    
    # Features (booleans)
    has_advanced_ai = models.BooleanField(default=False)
    has_analytics = models.BooleanField(default=True)
    has_distribution = models.BooleanField(default=False)
    has_priority_support = models.BooleanField(default=False)
    has_custom_domain = models.BooleanField(default=False)
    has_api_access = models.BooleanField(default=True)
    has_webhooks = models.BooleanField(default=False)
    
    # Availability
    is_available = models.BooleanField(default=True)
    is_popular = models.BooleanField(default=False, help_text="Выделить как популярный")
    
    # Display
    display_order = models.IntegerField(default=0)
    display_name = models.CharField(
        max_length=255,
        help_text="Отображаемое название (для маркетинга)"
    )
    
    # For what deployment modes
    available_for_saas = models.BooleanField(default=True)
    available_for_standalone = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'organizations_plan'
        ordering = ['display_order']
        indexes = [
            models.Index(fields=['is_available']),
        ]
    
    def __str__(self):
        return f"{self.name} (${self.price_monthly})"
    
    def get_all_features(self):
        """Получить список всех features (для сравнительной таблицы)"""
        return [
            ('Advanced AI', self.has_advanced_ai),
            ('Analytics', self.has_analytics),
            ('Distribution', self.has_distribution),
            ('Priority Support', self.has_priority_support),
            ('Custom Domain', self.has_custom_domain),
            ('API Access', self.has_api_access),
            ('Webhooks', self.has_webhooks),
        ]
```

---

#### 4.1.4. Модель `DomainSettings` (опционально)

```python
class DomainSettings(models.Model):
    """
    Кастомные домены для SaaS клиентов (опционально)
    """
    
    id = models.UUIDField(primary_key=True, default=uuid4)
    organization = models.OneToOneField(
        Organization,
        on_delete=models.CASCADE,
        related_name='domain_settings'
    )
    
    custom_domain = models.CharField(
        max_length=255,
        unique=True,
        help_text="Например, dam.company.com"
    )
    custom_domain_verified = models.BooleanField(
        default=False,
        help_text="Проверен ли DNS?"
    )
    
    # SSL
    ssl_certificate = models.TextField(blank=True)
    ssl_key = models.TextField(blank=True)
    ssl_expiry_date = models.DateField(null=True, blank=True)
    
    # Verification token (для DNS проверки)
    verification_token = models.CharField(
        max_length=255,
        unique=True,
        default=uuid4
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'organizations_domain_settings'
    
    def __str__(self):
        return f"{self.organization.name} ({self.custom_domain})"
    
    def get_dns_verification_record(self):
        """DNS TXT record для верификации домена"""
        return {
            'name': f'_dambrand.{self.custom_domain}',
            'type': 'TXT',
            'value': f'verification={self.verification_token}'
        }
```

---

### 4.2. TenantAwareManager и Миксин

#### 4.2.1. TenantAwareManager

```python
# mayan/apps/organizations/managers.py

from django.db import models
from django.db.models import F, Q

class TenantAwareManager(models.Manager):
    """
    Manager для моделей, которые изолированы по Organization.
    
    Использует request.organization для фильтрации QuerySet.
    """
    
    def get_queryset(self):
        """
        Переопределить базовый QuerySet для добавления фильтра по Organization.
        """
        qs = super().get_queryset()
        
        # Получить Organization из контекста (если он доступен)
        organization = self._get_current_organization()
        
        if organization:
            # Фильтр по FK на Organization
            qs = qs.filter(organization=organization)
        
        return qs
    
    def _get_current_organization(self):
        """
        Получить текущую Organization из контекста.
        
        Контекст устанавливается в Middleware (request.organization).
        Если контекст недоступен, вернуть None (это может быть админка или bat job).
        """
        from django.http import HttpRequest
        from contextvars import ContextVar
        
        # Используем ContextVar для потокобезопасности
        current_request = _request_context.get(None)
        
        if current_request and hasattr(current_request, 'organization'):
            return current_request.organization
        
        return None
    
    def for_organization(self, organization):
        """
        Явно задать Organization (для обхода фильтра).
        
        Используется для админки и batch jobs.
        """
        return self.get_queryset().filter(organization=organization)
    
    def all_organizations(self):
        """
        Получить все объекты (без фильтра по Organization).
        
        Используется только для Super Admin операций.
        Требует явного разрешения (permission_class=IsSuperAdminOnly).
        """
        return super().get_queryset()

# ContextVar для безопасного хранения request в многопоточной среде
from contextvars import ContextVar
_request_context: ContextVar = ContextVar('request', default=None)

def set_current_request(request):
    """Установить текущий request в контекст"""
    _request_context.set(request)
```

#### 4.2.2. TenantAwareMixin

```python
# mayan/apps/organizations/models.py

from django.db import models
from .managers import TenantAwareManager

class TenantAwareMixin(models.Model):
    """
    Миксин для моделей, которые должны быть изолированы по Organization.
    
    Использование:
    
        class Document(TenantAwareMixin, models.Model):
            name = models.CharField(max_length=255)
            # организация автоматически добавляется
    """
    
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='%(class)s_set',  #Document.organization_set и т.д.
        help_text="Организация, которой принадлежит этот объект"
    )
    
    objects = TenantAwareManager()
    objects_unfiltered = models.Manager()  # Для админки
    
    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=['organization']),
            models.Index(fields=['organization', '-created_at']),
        ]
    
    def get_organization(self):
        """Удобный метод для получения Organization"""
        return self.organization
```

---

### 4.3. Middleware для TenantResolver

```python
# mayan/apps/organizations/middleware.py

import logging
from django.http import HttpRequest, HttpResponse
from django.utils.deprecation import MiddlewareMixin
from django.core.exceptions import PermissionDenied
from .models import Organization
from .managers import set_current_request

logger = logging.getLogger(__name__)

class TenantResolverMiddleware(MiddlewareMixin):
    """
    Middleware для определения текущей Organization.
    
    Работает по одному из 3 способов (в порядке приоритета):
    1. По кастомному домену (если есть в DomainSettings)
    2. По поддомену (app.dam-brand.com → организация с slug='dam-brand')
    3. По токену в Authorization: Token (для API клиентов)
    
    Результат сохраняется в request.organization.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def process_request(self, request: HttpRequest) -> None:
        """Определить Organization перед обработкой запроса"""
        
        # Сохранить request в контекст (для TenantAwareManager)
        set_current_request(request)
        
        # Пути, которые не требуют Organization (публичные, админка)
        exempt_paths = [
            '/api/v4/public/',  # Публичные эндпоинты
            '/admin/',           # Django admin
            '/api/v4/auth/token/obtain/',  # Логин
            '/static/',
            '/media/',
        ]
        
        if any(request.path.startswith(path) for path in exempt_paths):
            return
        
        # Попытка 1: По кастомному домену
        organization = self._resolve_by_custom_domain(request)
        
        # Попытка 2: По поддомену
        if not organization:
            organization = self._resolve_by_subdomain(request)
        
        # Попытка 3: По токену в Authorization
        if not organization:
            organization = self._resolve_by_token(request)
        
        # Попытка 4: Standalone mode (одна Organization по умолчанию)
        if not organization:
            organization = self._resolve_standalone_mode()
        
        # Если организация не найдена, вернуть 404
        if not organization:
            raise PermissionDenied("Organization not found for this request")
        
        # Если организация неактивна, вернуть 403
        if not organization.is_active:
            raise PermissionDenied("Organization is suspended or inactive")
        
        # Сохранить в request
        request.organization = organization
    
    def _resolve_by_custom_domain(self, request: HttpRequest):
        """Метод 1: По кастомному домену (если он есть в DomainSettings)"""
        host = request.get_host().split(':')[0]  # Убрать порт
        
        from .models import DomainSettings
        try:
            domain_settings = DomainSettings.objects.get(
                custom_domain=host,
                custom_domain_verified=True
            )
            logger.info(f"Resolved organization {domain_settings.organization.slug} by custom domain {host}")
            return domain_settings.organization
        except DomainSettings.DoesNotExist:
            return None
    
    def _resolve_by_subdomain(self, request: HttpRequest):
        """Метод 2: По поддомену (app.dam-brand.com → dam-brand)"""
        host = request.get_host().split(':')[0]
        
        # Расчленить хост на части
        parts = host.split('.')
        
        # Исключить случаи вроде localhost, 127.0.0.1
        if len(parts) < 2 or not all(c.isalnum() or c == '-' for c in parts[0]):
            return None
        
        subdomain = parts[0]
        
        # Попытка найти Organization по slug = subdomain
        try:
            organization = Organization.objects.get(slug=subdomain)
            logger.info(f"Resolved organization {organization.slug} by subdomain {subdomain}")
            return organization
        except Organization.DoesNotExist:
            return None
    
    def _resolve_by_token(self, request: HttpRequest):
        """Метод 3: По токену в Authorization header"""
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if not auth_header.startswith('Token '):
            return None
        
        token = auth_header[6:]  # Убрать "Token "
        
        from rest_framework.authtoken.models import Token
        from django.contrib.auth.models import User
        
        try:
            token_obj = Token.objects.get(key=token)
            user = token_obj.user
            
            # Получить Organization из пользователя
            if hasattr(user, 'organization'):
                logger.info(f"Resolved organization {user.organization.slug} by token")
                return user.organization
        except Token.DoesNotExist:
            return None
        
        return None
    
    def _resolve_standalone_mode(self):
        """Метод 4: Standalone mode (если ENV=STANDALONE, есть одна Org по умолчанию)"""
        import os
        
        deployment_mode = os.getenv('DEPLOYMENT_MODE', 'SAAS')
        
        if deployment_mode != 'STANDALONE':
            return None
        
        # В standalone mode, существует одна Organization (по умолчанию)
        try:
            organization = Organization.objects.get(slug='default')
            logger.info("Resolved default organization (standalone mode)")
            return organization
        except Organization.DoesNotExist:
            logger.error("Standalone mode enabled but default organization not found!")
            return None
    
    def process_exception(self, request: HttpRequest, exception: Exception) -> None:
        """Логировать попытки несанкционированного доступа"""
        if isinstance(exception, PermissionDenied):
            logger.warning(f"Permission denied for {request.path} from {request.remote_addr}")
```

**Добавить в `settings.py`:**
```python
MIDDLEWARE = [
    # ... другие middleware ...
    'mayan.apps.organizations.middleware.TenantResolverMiddleware',
    # ... остальное ...
]
```

---

### 4.4. Привязка существующих моделей Mayan к Organization

#### 4.4.1. Какие модели должны быть TenantAware?

**Tenant-aware модели:**
```python
# Все эти модели должны иметь FK на Organization
class Document(TenantAwareMixin, models.Model):
    pass

class Cabinet(TenantAwareMixin, models.Model):
    pass

class Tag(TenantAwareMixin, models.Model):
    pass

class DocumentFile(TenantAwareMixin, models.Model):
    pass

class DocumentVersion(TenantAwareMixin, models.Model):
    pass

# DAM-модели
class DocumentAIAnalysis(TenantAwareMixin, models.Model):
    pass

class CampaignAsset(TenantAwareMixin, models.Model):
    pass

# Analytics models
class AssetEvent(TenantAwareMixin, models.Model):
    pass
```

**Глобальные модели (НЕ TenantAware):**
```python
# Эти модели глобальные (одна на всю систему)
class Plan(models.Model):  # Глобальный список тарифов
    pass

class MetadataType(models.Model):  # Глобальная типизация метаданных
    pass

class Source(models.Model):  # Источники загрузки
    pass
```

#### 4.4.2. Migration для привязки существующих данных

```python
# mayan/apps/organizations/migrations/0002_bind_existing_data.py

from django.db import migrations
from django.utils.text import slugify
import uuid

def create_default_organization_and_bind_data(apps, schema_editor):
    """
    Создать дефолтную Organization и привязать к ней всех существующих пользователей и документы.
    
    Это one-shot миграция для перехода на мульти-тенанси.
    """
    Organization = apps.get_model('organizations', 'Organization')
    User = apps.get_model('auth', 'User')
    Document = apps.get_model('documents', 'Document')
    
    # Создать Organization по умолчанию (для Standalone mode)
    default_org, created = Organization.objects.get_or_create(
        slug='default',
        defaults={
            'name': 'Default Organization',
            'email': 'admin@dam-brand.com',
            'is_active': True,
            'status': 'active',
            'deployment_mode': 'standalone'
        }
    )
    
    print(f"Created default organization: {default_org.name}")
    
    # Привязать всех существующих пользователей к Organization
    # (добавить FK на User если его нет)
    users = User.objects.all()
    for user in users:
        # Создать запись User-Organization связи
        # Это требует отдельной работы в зависимости от модели User
        pass
    
    # Привязать всех документов к default Organization
    documents = Document.objects.all()
    updated = 0
    for doc in documents:
        doc.organization = default_org
        doc.save(update_fields=['organization'])
        updated += 1
    
    print(f"Bound {updated} documents to default organization")

def rollback(apps, schema_editor):
    """Откат миграции (удалить default Organization)"""
    Organization = apps.get_model('organizations', 'Organization')
    Organization.objects.filter(slug='default').delete()

class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0001_initial'),
        ('documents', '0001_initial'),  # Зависит от существования Document
    ]

    operations = [
        migrations.RunPython(create_default_organization_and_bind_data, rollback),
    ]
```

---

### 4.5. API-контракты для управления Org

#### 4.5.1. Endpoint: `POST /api/v4/organizations/` (Создание новой Org)

**Требуется:** SuperAdmin только

**Request:**
```json
{
  "name": "Ромашка ООО",
  "slug": "romashka",
  "email": "admin@romashka.ru",
  "phone": "+7 (999) 123-45-67",
  "industry": "marketing",
  "deployment_mode": "saas",
  "subscription": {
    "plan_id": "plan-start"
  }
}
```

**Response 201 Created:**
```json
{
  "id": "org-uuid-1",
  "name": "Ромашка ООО",
  "slug": "romashka",
  "email": "admin@romashka.ru",
  "status": "trial",
  "is_active": true,
  "storage_limit_gb": 50,
  "max_users": 3,
  "subscription": {
    "plan": "plan-start",
    "status": "trial"
  },
  "created_at": "2025-12-30T16:00:00Z"
}
```

---

#### 4.5.2. Endpoint: `PATCH /api/v4/organizations/{id}/` (Обновление Org)

**Требуется:** SuperAdmin или Owner

**Request:**
```json
{
  "status": "active",
  "subscription": {
    "plan_id": "plan-pro"
  }
}
```

---

#### 4.5.3. Endpoint: `POST /api/v4/organizations/{id}/suspend/` (Блокировка)

**Требуется:** SuperAdmin

**Действие:** Установить status='suspended', заблокировать доступ для всех пользователей Org

**Response 200:**
```json
{
  "success": true,
  "message": "Organization suspended",
  "organization_id": "org-uuid-1"
}
```

---

## 5. НЕФУНКЦИОНАЛЬНЫЕ ТРЕБОВАНИЯ

### 5.1. Performance

| Требование | Значение | Инструмент |
|-----------|----------|-----------|
| **Время запроса с FK-фильтром** | ≤ 200ms | Django Debug Toolbar, New Relic |
| **QuerySet с select_related()** | ≤ 150ms | Django ORM profiling |
| **N+1 queries problem** | 0 (на критичных endpoints) | Debug Toolbar, assertNumQueries() |
| **DB connections pool** | Min 10, Max 50 | psycopg2 pool config |
| **Cache hit rate (Redis)** | ≥ 80% | Redis monitoring |

**Оптимизации:**
- `select_related()` для FK на Organization
- `prefetch_related()` для обратных связей
- Кеширование часто читаемых данных (Plans, User counts)

---

### 5.2. Security

| Требование | Описание |
|-----------|---------|
| **Data isolation** | Никакой пользователь не может получить документ из чужой Organization, даже прямым ID |
| **Permission checks** | Все ViewSet'ы должны проверять `request.organization` перед доступом |
| **SQL Injection** | 0 уязвимостей (Django ORM защищает) |
| **CSRF Protection** | Все POST/PATCH/DELETE требуют CSRF token |
| **Rate limiting** | По Organization (API rate limits в зависимости от План |
| **Audit logging** | Все критичные операции логируются (создание Org, смена статуса, смена плана) |

---

### 5.3. Scalability

| Аспект | Решение |
|--------|---------|
| **Партиционирование таблиц** | Готово к партиционированию по `organization_id` (future) |
| **Шардирование** | Архитектура готова к миграции на шардированную БД |
| **Репликация БД** | Master-Slave для read scaling |
| **Кеширование** | Redis для часто читаемых данных |

---

## 6. ТРЕБОВАНИЯ К ТЕСТИРОВАНИЮ

### 6.1. Unit-тесты

```python
# tests/unit/test_organizations.py

from django.test import TestCase
from mayan.apps.organizations.models import Organization, Plan, Subscription

class OrganizationTestCase(TestCase):
    """Тесты для модели Organization"""
    
    def setUp(self):
        self.plan_start = Plan.objects.create(
            id='plan-start',
            name='Start',
            price_monthly=29,
            max_users=3,
            storage_gb=50
        )
    
    def test_create_organization(self):
        org = Organization.objects.create(
            name='Test Org',
            slug='test-org',
            email='test@test.com'
        )
        self.assertEqual(org.status, 'trial')
        self.assertTrue(org.is_active)
    
    def test_organization_slug_unique(self):
        """Slug должен быть уникальным"""
        Organization.objects.create(
            name='Org 1',
            slug='org-1',
            email='org1@test.com'
        )
        
        with self.assertRaises(Exception):  # IntegrityError
            Organization.objects.create(
                name='Org 2',
                slug='org-1',  # Дубль
                email='org2@test.com'
            )
    
    def test_storage_limit_exceeded(self):
        """Проверка превышения лимита хранилища"""
        org = Organization.objects.create(
            name='Test Org',
            slug='test-org',
            email='test@test.com',
            storage_limit_gb=1
        )
        
        # Здесь создать документ с 1.5 GB размером и проверить
        # self.assertTrue(org.is_storage_exceeded())
    
    def test_user_limit_exceeded(self):
        """Проверка превышения лимита пользователей"""
        org = Organization.objects.create(
            name='Test Org',
            slug='test-org',
            email='test@test.com',
            max_users=2
        )
        
        # Создать 3 пользователей и проверить
        # self.assertTrue(org.is_user_limit_exceeded())
```

---

### 6.2. Integration-тесты

```python
# tests/integration/test_tenant_isolation.py

from django.test import TestCase, RequestFactory
from mayan.apps.organizations.models import Organization
from mayan.apps.organizations.middleware import TenantResolverMiddleware
from mayan.apps.documents.models import Document

class TenantIsolationTestCase(TestCase):
    """Тесты для изоляции данных между тенантами"""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = TenantResolverMiddleware(lambda r: None)
        
        # Создать 2 организации
        self.org1 = Organization.objects.create(
            name='Org 1',
            slug='org-1',
            email='org1@test.com'
        )
        self.org2 = Organization.objects.create(
            name='Org 2',
            slug='org-2',
            email='org2@test.com'
        )
        
        # Создать документы в каждой org
        self.doc1 = Document.objects.create(
            organization=self.org1,
            title='Doc in Org 1'
        )
        self.doc2 = Document.objects.create(
            organization=self.org2,
            title='Doc in Org 2'
        )
    
    def test_tenant_resolver_by_subdomain(self):
        """Тест резолвинга Org по поддомену"""
        request = self.factory.get('/', HTTP_HOST='org-1.dam-brand.com')
        self.middleware.process_request(request)
        
        self.assertEqual(request.organization, self.org1)
    
    def test_document_isolation(self):
        """Тест, что документы одной Org не видны другой"""
        # Установить контекст для org1
        request = self.factory.get('/', HTTP_HOST='org-1.dam-brand.com')
        request.organization = self.org1
        
        # Получить документы (с фильтром по organization)
        docs = Document.objects.filter(organization=self.org1)
        
        self.assertEqual(docs.count(), 1)
        self.assertIn(self.doc1, docs)
        self.assertNotIn(self.doc2, docs)
    
    def test_cross_tenant_access_prevention(self):
        """Тест, что пользователь не может прямо обращаться к документу чужой Org по ID"""
        # Даже если юзер знает ID документа из org2, он не может его получить
        request = self.factory.get('/', HTTP_HOST='org-1.dam-brand.com')
        request.organization = self.org1
        
        try:
            doc = Document.objects.get(id=self.doc2.id)
            # Если TenantAwareManager работает правильно, это вызовет DoesNotExist
            self.fail("Cross-tenant access not prevented!")
        except Document.DoesNotExist:
            pass  # Ожидаемое поведение
```

---

### 6.3. Permission-тесты

```python
# tests/unit/test_org_permissions.py

from django.test import TestCase
from django.contrib.auth.models import User
from mayan.apps.organizations.models import Organization

class OrganizationPermissionTestCase(TestCase):
    """Тесты для проверки прав доступа"""
    
    def setUp(self):
        self.org1 = Organization.objects.create(
            name='Org 1',
            slug='org-1',
            email='org1@test.com'
        )
        self.org2 = Organization.objects.create(
            name='Org 2',
            slug='org-2',
            email='org2@test.com'
        )
    
    def test_superadmin_can_view_all_organizations(self):
        """SuperAdmin может видеть все организации"""
        # Использовать objects_unfiltered или .all_organizations()
        all_orgs = Organization.objects_unfiltered.all()
        self.assertEqual(all_orgs.count(), 2)
    
    def test_regular_user_can_only_view_own_organization(self):
        """Обычный пользователь видит только свою Organization"""
        # При запросе с request.organization = org1
        # Document.objects.all() вернёт только документы org1
        pass
```

---

## 7. МИГРАЦИИ И ROLLBACK

### 7.1. Migration strategy

**Фаза 1: Добавить Organization FK ко всем tenant-aware моделям**
```python
# migration_0001_initial_organization.py
# - Добавить field: organization = ForeignKey(Organization)
# - nullable=True (для совместимости)
```

**Фаза 2: Заполнить существующие данные**
```python
# migration_0002_populate_organization.py
# - Создать default Organization
# - Привязать все существующие объекты к default Org
```

**Фаза 3: Сделать поле обязательным**
```python
# migration_0003_make_organization_required.py
# - Изменить null=False на FK
```

### 7.2. Rollback plan

Если нужно откатиться:
```bash
python manage.py migrate organizations 0001
# Это откатит все миграции до начального состояния
```

---

## 8. ТРЕБОВАНИЯ К РАЗВЕРТЫВАНИЮ

### 8.1. ENV переменные

```bash
# .env
DEPLOYMENT_MODE=SAAS              # или STANDALONE
MAYAN_DATABASE_URL=postgresql://...
MAYAN_ORGANIZATIONS_AUTO_CREATE=true  # Автосоздание при регистрации
```

### 8.2. Инициализация при первом запуске (Standalone mode)

```python
# mayan/apps/organizations/apps.py

from django.apps import AppConfig

class OrganizationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mayan.apps.organizations'
    
    def ready(self):
        """Запускается при старте Django"""
        import os
        from django.core.management import call_command
        
        if os.getenv('DEPLOYMENT_MODE') == 'STANDALONE':
            # Создать default Organization если её нет
            from .models import Organization
            Organization.objects.get_or_create(
                slug='default',
                defaults={
                    'name': 'Default Organization',
                    'email': 'admin@dam-brand.com',
                    'is_active': True,
                    'status': 'active'
                }
            )
```

---

## 9. АРХИТЕКТУРНЫЕ РЕШЕНИЯ (СОГЛАСОВАТЬ)

### 9.1. Критические решения

| Решение | Вариант A | Вариант B | Выбрано |
|---------|-----------|----------|---------|
| **Хранение Organization ID** | FK + Filter | Шардирование на уровне схемы | FK (Shared Schema) |
| **Отдельная БД на Organization** | Отдельная PostgreSQL DB | Одна DB, один schema | Одна DB |
| **Глобальные таблицы** | Таблица в отдельной schema | Таблица в основной schema | Основной schema |
| **User-Organization связь** | OneToOne | ManyToMany (team members) | ManyToMany (нужна модель UserOrganizationRole) |

### 9.2. Риски

| # | Риск | Вероятность | Вплив | Mitigation |
|---|------|-------------|------|-----------|
| 1 | Ошибка в Middleware → Data Leak | Low | Critical | Unit-тесты, security audit |
| 2 | Performance degradation с FK-фильтром | Medium | High | Индексы, кеширование |
| 3 | Сложность миграции данных | Medium | Medium | Staging окружение, dry-run миграция |
| 4 | User vs Organization иерархия неоптимальна | Medium | Medium | Создать промежуточную модель Role |

---

## 10. ТРЕБОВАНИЯ К CODE REVIEW

**Перед мёржем ветки `feature/multi-tenancy` проверить:**

- [ ] Все tenant-aware модели используют TenantAwareManager
- [ ] Нет raw SQL queries (только ORM)
- [ ] Middleware добавлен в settings.MIDDLEWARE
- [ ] Миграции проверены (python manage.py makemigrations --dry-run)
- [ ] Tests покрывают >80% кода
- [ ] Нет хардкодированных Organization ID
- [ ] DEPLOYMENT_MODE работает в обоих режимах (SAAS и STANDALONE)
- [ ] Документация обновлена

---

## 11. TIMELINE И DELIVERABLES

### Sprint 1: Инфраструктура (Неделя 1-2)

**Deliverables:**
- [ ] Models: Organization, Subscription, Plan, DomainSettings
- [ ] TenantAwareManager и TenantAwareMixin
- [ ] TenantResolverMiddleware
- [ ] Unit-тесты для моделей

**Code commits:**
```
feat: Add Organization model for multi-tenancy
feat: Implement TenantAwareManager and Mixin
feat: Add TenantResolverMiddleware
test: Add organization and tenant isolation tests
```

### Sprint 2: Миграция существующих данных (Неделя 3)

**Deliverables:**
- [ ] Миграции для добавления FK на tenant-aware модели
- [ ] Migration для привязки существующих данных
- [ ] Integration-тесты для миграции

**Code commits:**
```
migrations: Add organization_id to Document, Cabinet, etc
migrations: Populate existing data with default Organization
test: Add migration integration tests
```

### Sprint 3: API и Admin (Неделя 4-5)

**Deliverables:**
- [ ] ViewSet'ы для управления Organizations
- [ ] Django Admin панель для SuperAdmin
- [ ] Permissions для Super Admin vs Org Admin
- [ ] E2E тесты

**Code commits:**
```
api: Add OrganizationViewSet for admin API
admin: Register Organization in django admin
perms: Add organization-level permissions
test: Add E2E tests for multi-tenant scenarios
```

### Sprint 4: Polish и Deploy (Неделя 6)

**Deliverables:**
- [ ] Performance оптимизация (индексы, кеширование)
- [ ] Security audit
- [ ] Documentation
- [ ] Production deployment

---

## 12. ОТВЕТСТВЕННОСТЬ И КОНТАКТЫ

| Роль | ФИО | Ответственность |
|------|-----|-----------------|
| **Backend Lead** | — | Архитектура, code review |
| **Backend Dev** | — | Реализация models, middleware |
| **Database Architect** | — | Schema design, индексы, миграции |
| **DevOps** | — | Развертывание, monitoring |
| **QA** | — | Тестирование, security audit |

---

**Документ согласован:** ___________  
**Дата:** 30 декабря 2025  
**Версия:** 1.0  
**Статус:** Ready for Development
