# Technical Context: Prime-EDMS

## Технологический стек

### Backend

#### Основной фреймворк
- **Django**: 3.2.14
- **Python**: 3.9 (базовый образ Mayan EDMS)
- **Mayan EDMS**: 4.3.1 (базовая платформа)

#### База данных и хранилище
- **PostgreSQL**: 12.10-alpine (основная БД)
- **Redis**: 6.2-alpine (кэширование, Celery results, блокировки)
- **S3 Storage**: Beget S3 (ru-1 регион) для хранения файлов
- **Локальное хранилище**: `/var/lib/mayan` для медиа-файлов

#### Очереди и задачи
- **RabbitMQ**: 3.10-management-alpine (Celery broker)
- **Celery**: 5.2.3 (асинхронная обработка задач)
- **Celery Beat**: 2.2.1 (периодические задачи)

#### Веб-серверы
- **Gunicorn**: 20.1.0 (WSGI сервер для основного приложения)
- **Daphne**: 3.0.2 (ASGI сервер для WebSocket уведомлений)

#### API и интеграции
- **Django REST Framework**: 3.13.1 (REST API)
- **drf-spectacular**: 0.27.2 (OpenAPI документация)
- **django-cors-headers**: 3.10.0 (CORS поддержка)

#### AI и обработка медиа
- **yandexgptlite**: (YandexGPT интеграция)
- **gigachat**: (GigaChat интеграция)
- **Pillow**: 9.2.0 (обработка изображений)
- **CairoSVG**: 2.5.2 (SVG рендеринг)
- **PyPDF2**: 1.28.4 (обработка PDF)
- **ffmpeg**: (обработка видео, установлен в Dockerfile)

#### Поиск и индексация
- **Whoosh**: 2.7.4 (полнотекстовый поиск)
- **Elasticsearch**: 7.17.1 (опциональный поисковый движок)
- **elasticsearch-dsl**: 7.4.0

#### Дополнительные библиотеки
- **channels**: 3.0.5 (WebSocket поддержка)
- **channels-redis**: 4.1.0 (Redis backend для channels)
- **django-redis**: 5.4.0 (Redis кэш backend)
- **django-prometheus**: 2.3.1 (метрики)
- **django-ratelimit**: 4.1.0 (ограничение запросов)
- **boto3/botocore**: (S3 интеграция)
- **django-storages**: (S3 storage backend)

### Frontend

#### DAM Frontend (Vue 3 SPA)
**Расположение:** `frontend/`

**Основной стек:**
- **Vue**: 3.x (SPA фреймворк)
- **TypeScript**: (типизация)
- **Vite**: 5.4.11 (сборщик и dev-сервер)
- **Pinia**: (state management)
- **Axios**: (HTTP клиент)

**UI библиотеки:**
- **Tailwind CSS**: (utility-first CSS фреймворк)
- **Chart.js**: 4.5.1 (графики и визуализация)

**Порт:** 5173 (development)

#### Public Frontend (Nuxt 3 SSR)
**Расположение:** `public-frontend/`

**Основной стек:**
- **Nuxt**: 3.8.0 (SSR/SSG фреймворк на базе Vue 3)
- **Vue**: 3.4.21 (базовый фреймворк)
- **TypeScript**: 5.3.3 (строгая типизация)
- **Node.js**: 18+ (требование)

**Nuxt модули:**
- **@nuxtjs/tailwindcss**: 6.10.0 (Tailwind CSS интеграция)
- **@nuxtjs/i18n**: 8.1.0 (интернационализация RU/EN)
- **@nuxt/image**: 1.3.0 (оптимизация изображений)
- **@pinia/nuxt**: 0.5.1 (Pinia state management)
- **@nuxtjs/sitemap**: 2.4.0 (генерация sitemap)
- **@nuxtjs/color-mode**: 3.4.0 (темная/светлая тема)

**UI библиотеки:**
- **Tailwind CSS**: (utility-first CSS фреймворк)
- **@headlessui/vue**: 1.7.16 (headless UI компоненты)
- **@heroicons/vue**: 2.1.1 (иконки)
- **@tailwindcss/forms**: 0.5.7 (стилизация форм)

**Утилиты:**
- **@vueuse/core**: 10.7.2 (Vue composition utilities)
- **axios**: 1.6.5 (HTTP клиент)
- **zod**: 3.23.8 (валидация схем)
- **markdown-it**: 14.0.0 (парсинг Markdown)
- **clsx**: 2.1.0 (условные CSS классы)

**Тестирование:**
- **Vitest**: 1.6.0 (unit тесты)
- **@vue/test-utils**: 2.4.5 (Vue компоненты тестирование)
- **Playwright**: 1.41.2 (E2E тесты)
- **MSW**: 2.0.0 (Mock Service Worker для моков API)
- **jsdom**: 23.2.0 (DOM окружение для тестов)

**Dev инструменты:**
- **Prettier**: 3.2.4 (форматирование кода)
- **ESLint**: (линтинг)
- **@types/node**: 20.11.5 (TypeScript типы для Node.js)

**Особенности:**
- **SSR**: Server-Side Rendering включен по умолчанию
- **SSG**: Static Site Generation для статических страниц
- **i18n**: Поддержка русского (по умолчанию) и английского языков
- **Dark Mode**: Поддержка темной темы с системным определением
- **Image Optimization**: Автоматическая оптимизация через IPX provider (WebP/AVIF)
- **Route Rules**: SWR кеширование для статических страниц
- **Prerendering**: Автоматический prerender для SEO-страниц

**Порт:** 3000 (development)

**Структура проекта:**
```
public-frontend/
├── assets/css/          # Глобальные стили (Tailwind)
├── components/          # Vue компоненты
│   ├── Blog/          # Компоненты блога
│   ├── Common/         # Переиспользуемые UI компоненты
│   ├── Forms/         # Формы (Contact, Login, Register)
│   ├── Sections/      # Секции страниц (Hero, Features, CTA, FAQ, Pricing)
│   └── SEO/           # SEO компоненты (PageMeta, JsonLd)
├── composables/        # Vue composables (useApi, useAuth, useForm, useSeo)
├── layouts/           # Layouts (default, auth)
├── locales/           # Переводы (ru.json, en.json)
├── middleware/        # Nuxt middleware (analytics, redirects)
├── pages/             # File-based routing
│   ├── index.vue      # Главная страница
│   ├── blog/          # Блог (index, [slug])
│   ├── pricing.vue    # Страница цен
│   ├── contact.vue    # Контакты
│   └── auth/          # Авторизация (login, register, verify-email)
├── plugins/           # Nuxt plugins (analytics, animations, crisp)
├── server/            # Server-side код
│   ├── api/           # API routes
│   └── middleware/    # Server middleware (security headers)
├── stores/            # Pinia stores (authStore, contentStore)
├── tests/             # Тесты
│   ├── e2e/          # Playwright E2E тесты
│   ├── integration/  # Интеграционные тесты
│   ├── mocks/        # MSW mock handlers
│   └── unit/         # Vitest unit тесты
└── types/             # TypeScript типы
```

**API интеграция:**
- Проксирование API запросов через Vite dev server (`/api` → `http://localhost:8080`)
- Endpoints:
  - `/api/v4/public/pages/:slug/` - Получение страниц
  - `/api/v4/public/posts/` - Список постов блога
  - `/api/v4/public/plans/` - Тарифные планы
  - `/api/v4/public/faq/` - FAQ элементы
  - `/api/v4/public/leads/` - Отправка форм обратной связи
  - `/api/v4/public/register/` - Регистрация пользователей
  - `/api/v4/public/verify-email/:token/` - Подтверждение email

**Оптимизации производительности:**
- Image optimization через Nuxt Image (WebP/AVIF форматы)
- Code splitting (vendor chunks для Vue, UI библиотек, утилит)
- Route-based caching (SWR для статических страниц)
- Prerendering для SEO-страниц (/, /pricing, /about, /blog)
- Compression для публичных ассетов
- Lazy loading компонентов и изображений

**SEO оптимизация:**
- Server-Side Rendering для лучшей индексации
- Автоматическая генерация sitemap
- JSON-LD structured data
- Meta tags через PageMeta компонент
- Оптимизированные URLs с i18n префиксами

**Доступность:**
- WCAG 2.1 Level AA compliance (в процессе)
- Keyboard navigation
- Screen reader support
- Semantic HTML

**Переменные окружения:**
- `NUXT_PUBLIC_API_URL` - URL Django backend (по умолчанию: http://localhost:8080)
- `NUXT_PUBLIC_APP_URL` - URL основного DAM приложения (по умолчанию: http://localhost:5173)
- `NUXT_PUBLIC_SITE_URL` - URL публичного сайта (по умолчанию: http://localhost:3000)
- `NUXT_PUBLIC_ENVIRONMENT` - Окружение (development/production)
- `NUXT_PUBLIC_GA_ID` - Google Analytics ID (опционально)

### Инфраструктура

#### Контейнеризация
- **Docker**: (контейнеризация приложения)
- **Docker Compose**: (оркестрация сервисов)

#### Мониторинг и логирование
- **Sentry SDK**: 1.5.8 (отслеживание ошибок)
- **python-json-logger**: (структурированное логирование)

## Структура зависимостей

### requirements/base.txt
Содержит базовые зависимости Django и Mayan EDMS:
- Django 3.2.14
- Celery 5.2.3
- Pillow, CairoSVG, PyPDF2
- Django REST Framework
- И другие базовые библиотеки

### requirements/common.txt
Содержит только Django 3.2.14 (базовая зависимость)

### requirements.txt
Объединяет common.txt и base.txt

### Дополнительные зависимости в Dockerfile
- channels, channels-redis, daphne (WebSocket)
- django-redis, django-prometheus, django-ratelimit
- boto3, botocore, django-storages (S3)
- gigachat, yandexgptlite (AI провайдеры)
- drf-spectacular (API документация)

## Настройка окружения

### Переменные окружения (app.env)
- **База данных**: PostgreSQL настройки через `MAYAN_DATABASES`
- **Redis**: Настройки кэша, Celery results, блокировок
- **RabbitMQ**: Celery broker URL
- **S3 Storage**: Beget S3 credentials (hardcoded в docker-compose.yml)
- **AI провайдеры**: GigaChat и YandexGPT credentials через переменные окружения
- **Storage quota**: 500GB лимит через `MADDAM_STORAGE_TOTAL_BYTES`

### Docker Compose конфигурация

#### Сервисы:
1. **postgresql**: PostgreSQL 12.10-alpine
2. **redis**: Redis 6.2-alpine с паролем
3. **rabbitmq**: RabbitMQ 3.10-management-alpine
4. **app**: Основное приложение на Gunicorn (порт 8080)
5. **app_websocket**: WebSocket сервер на Daphne (порт 8001)

#### Volumes:
- `postgres_data`: Данные PostgreSQL
- `rabbitmq_data`: Данные RabbitMQ
- `redis_data`: Данные Redis
- `mayan_data`: Медиа-файлы приложения
- `mayan_renditions`: Сгенерированные превью

## Развертывание

### Поддерживаемые платформы
- **Windows + WSL2**: Ubuntu 22.04 в WSL2
- **Ubuntu нативно**: Ubuntu 20.04+ с systemd

### Скрипты установки
- `setup-wsl.sh`: Автоматическая установка для WSL2
- `ubuntu-setup.sh`: Установка для Ubuntu
- `start-mayan.sh`: Запуск в Linux/WSL2
- `start-mayan.ps1`: Запуск в Windows PowerShell

### Docker образы
- **Базовый образ**: `mayanedms/mayanedms:s4.3`
- **Кастомный Dockerfile**: `Dockerfile.app` с дополнительными зависимостями

## Ограничения и требования

### Версии Python
- Требуется Python 3.9 (совместимость с Mayan EDMS 4.3)

### Версии Django
- Django 3.2.14 (LTS версия, совместимая с Mayan EDMS)

### Системные зависимости
- FFmpeg для обработки видео
- Build tools для компиляции Python пакетов
- Python3-dev для разработки расширений

## Интеграции

### Внешние сервисы
- **Яндекс.Диск**: Импорт файлов через API
- **Beget S3**: Облачное хранилище файлов
- **YandexGPT**: AI анализ через Yandex API
- **GigaChat**: AI анализ через GigaChat API

### Внутренние модули
- **DAM app**: Расширение для управления цифровыми активами
- **Analytics app**: Аналитика использования активов
- **Headless API**: REST API для фронтенда
- **Image Editor**: Редактор изображений
- **Distribution**: Распределение контента
- **Organizations app**: Multi-tenancy изоляция (базовая инфраструктура реализована, модели в разработке)

## Multi-tenancy Architecture

### Подход: Shared Database + Shared Schema

**Архитектура:** Одна PostgreSQL база данных, одна схема, изоляция через ForeignKey на Organization.

**Компоненты:**

#### Organizations Module (mayan.apps.organizations)
**Статус:** Базовая инфраструктура реализована, модели и middleware в разработке  
**Коммит:** `7f41e418fe`

**Реализовано:**
- ✅ Базовый модуль создан (`mayan.apps.organizations`)
- ✅ Настройки: `ORGANIZATIONS_INSTALLATION_URL`, `ORGANIZATIONS_URL_BASE_PATH`
- ✅ Патчи для HttpRequest (поддержка organization URLs)
- ✅ Тесты для settings и requests
- ✅ Интеграция в apps.py с патчингом при старте

**В разработке:**

**Модели:**
- **Organization**: Тенант/компания (UUID primary key)
  - Поля: name, slug, email, industry, status, deployment_mode
  - Квоты: storage_limit_gb, max_users, max_ai_analyses_monthly
  - Кастомные домены для SaaS клиентов
- **Subscription**: Подписка на тарифный план
  - Связь с Plan
  - Биллинг: billing_cycle, amount, currency, payment_status
  - Статусы: trial, active, paused, cancelled, expired
- **Plan**: Тарифные планы (система-уровне)
  - Pricing: price_monthly, price_yearly
  - Лимиты: storage_gb, max_users, max_ai_analyses_monthly
  - Features: has_advanced_ai, has_analytics, has_distribution, etc.
- **DomainSettings**: Кастомные домены для SaaS (опционально)

**Middleware:**
- **TenantResolverMiddleware**: Определение Organization по:
  1. Кастомному домену (dam.company.com)
  2. Поддомену (app.dam-brand.com → slug='dam-brand')
  3. Токену в Authorization header
  4. Standalone mode (default Organization)

**Managers:**
- **TenantAwareManager**: Автоматическая фильтрация QuerySet по Organization
- Использует ContextVar для потокобезопасности
- Методы: `for_organization()`, `all_organizations()`

**Миксин:**
- **TenantAwareMixin**: Добавляет FK на Organization и TenantAwareManager
- Индексы на organization_id для производительности

**Режимы развертывания:**
- **SaaS** (`DEPLOYMENT_MODE=SAAS`): Множественные организации
- **Standalone** (`DEPLOYMENT_MODE=STANDALONE`): Одна организация по умолчанию

**Переменные окружения:**
- `DEPLOYMENT_MODE`: SAAS или STANDALONE
- `MAYAN_ORGANIZATIONS_AUTO_CREATE`: Автосоздание при регистрации

**Миграции:**
- Фаза 1: Добавить FK на Organization (nullable=True)
- Фаза 2: Привязать существующие данные к default Organization
- Фаза 3: Сделать FK обязательным (null=False)

**Tenant-aware модели (требуют FK на Organization):**
- Document, DocumentFile, DocumentVersion
- Cabinet, Tag
- DocumentAIAnalysis (DAM)
- AssetEvent, CampaignAsset (Analytics)
- Publication, ShareLink (Distribution)

**Глобальные модели (НЕ tenant-aware):**
- Plan (тарифные планы)
- MetadataType (типизация метаданных)
- Source (источники загрузки)

**Производительность:**
- Индексы на organization_id для всех tenant-aware моделей
- Composite индексы: (organization_id, created_at)
- select_related('organization') для оптимизации запросов
- Целевое время запроса: ≤200ms (vs 150ms без фильтра)

**Безопасность:**
- 100% защита от cross-tenant access
- Middleware проверяет is_active перед доступом
- Audit logging всех операций с Organization
- Rate limiting по Organization (в зависимости от Plan)

**Масштабируемость:**
- Поддержка ≥100 тенантов на одном сервере
- Готовность к шардированию (future)
- Database connection pooling (min 10, max 50)
- Redis кеширование для часто читаемых данных (Plans, User counts)
