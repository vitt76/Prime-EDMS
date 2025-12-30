# ТЕХНИЧЕСКОЕ ЗАДАНИЕ
## Часть 1: Публичный фронтенд на Nuxt 3 (Headless CMS)

**Версия:** 1.0  
**Дата:** 30 декабря 2025  
**Статус:** Ready for Development  
**Целевая аудитория:** Frontend-разработчики, DevOps, маркетологи  

---

## 1. EXECUTIVE SUMMARY

Требуется разработать SEO-оптимизированный публичный сайт `dam-brand.com` на **Nuxt 3 (SSR)**, работающий как headless-frontend для Django-модуля `mayan.apps.marketing_cms`. 

**Ключевые метрики:**
- Lighthouse Score: ≥ 95 (SEO, Performance)
- Core Web Vitals: LCP ≤ 2.5s, FID ≤ 100ms, CLS ≤ 0.1
- TTM (Time-to-Market): 6 недель
- SEO Ranking: ТОП-10 по 5+ основным запросам в течение 3 месяцев

---

## 2. ЦЕЛИ И KPI

| # | Цель | Метрика | Целевое значение |
|---|------|---------|------------------|
| 1 | SEO-доминирование | Lighthouse SEO Score | ≥ 95 |
| 2 | High Performance | Core Web Vitals (все зелёные) | LCP ≤ 2.5s, CLS ≤ 0.1 |
| 3 | Лидогенерация | Conversion Rate регистрация | ≥ 3% (от посетителей) |
| 4 | Маркетинговая гибкость | Время добавления новости | ≤ 15 мин (без кода) |
| 5 | Мобильная доступность | Mobile Friendly Score | 100% |
| 6 | Масштабируемость | Поддержка N новостей | N > 1000 статей без деградации |

---

## 3. ФУНКЦИОНАЛЬНЫЕ ТРЕБОВАНИЯ

### 3.1. Архитектура и технологический стек

```
┌─────────────────────────────────────────────────────┐
│ Nginx / Cloudflare (Reverse Proxy, CDN)             │
└──────────────────┬──────────────────────────────────┘
                   │
        ┌──────────┴────────────┐
        ▼                       ▼
   [Nuxt 3 SSR]          [Static Cache]
   Port 3000              (S3 + CDN)
   (Node.js)              (Images, Fonts)
        │
        └──────────────────┬──────────────────┐
                           ▼                  ▼
                    [Django API]        [Image CDN]
                    api.dam-brand.com   cdn.dam-brand.com
```

#### 3.1.1. Требуемые зависимости

| Пакет | Версия | Назначение | Обоснование |
|-------|--------|-----------|------------|
| **nuxt** | 3.8+ | Meta-фреймворк Vue | SSR/SSG, SEO-ready |
| **vue** | 3.4+ | Реактивность | Совместимость с Vue 3 SPA |
| **typescript** | 5.3+ | Типизация | Уже используется в проекте |
| **tailwindcss** | 3.4+ | Стили | Переиспользует текущий конфиг |
| **@tailwindcss/forms** | 0.5+ | Form styling | Улучшенные формы |
| **@nuxtjs/tailwindcss** | 6.10+ | Интеграция Nuxt+Tailwind | Автоконфигурация |
| **pinia** | 2.1+ | State Management | Кеширование данных |
| **axios** или **$fetch** | latest | HTTP-клиент | API-запросы |
| **vueuse/core** | 10.7+ | Composition API hooks | Утилиты |
| **@nuxtjs/i18n** | 8.1+ | Многоязычность | RU/EN локали |
| **@nuxtjs/sitemap** | 2.4+ | Sitemap generation | SEO |
| **@vueuse/head** | 2.0+ | Meta-управление | альтернатива useHead |
| **zod** или **valibot** | latest | Валидация форм | Type-safe validation |
| **clsx** или **classnames** | latest | Утилита для класс | Условные классы |
| **nuxt-image** | 1.3+ | Image optimization | WebP, AVIF, lazy-loading |
| **@nuxtjs/color-mode** | 3.4+ | Dark Mode (опционально) | theme switching |

#### 3.1.2. Файловая структура проекта

```
public-frontend/
├── app.vue                      # Root component
├── nuxt.config.ts              # Nuxt конфигурация
├── tailwind.config.ts           # Tailwind конфиг (переиспользуется)
├── tsconfig.json                # TypeScript конфиг
├── package.json
├── .env.example
│
├── pages/                        # SSR/SSG страницы (автоматические роуты)
│   ├── index.vue                # / (Главная)
│   ├── pricing.vue              # /pricing
│   ├── about.vue                # /about
│   ├── contact.vue              # /contact
│   ├── terms.vue                # /terms
│   ├── privacy.vue              # /privacy
│   ├── blog/
│   │   ├── index.vue            # /blog (список новостей)
│   │   └── [slug].vue           # /blog/:slug (деталь новости, SSR)
│   ├── auth/
│   │   ├── login.vue            # /auth/login
│   │   ├── register.vue         # /auth/register
│   │   └── verify-email/
│   │       └── [token].vue      # /auth/verify-email/:token
│   └── [...error].vue           # Custom 404 handler
│
├── components/                  # Vue компоненты
│   ├── Navigation.vue           # Navbar
│   ├── Footer.vue               # Footer
│   ├── SEO/
│   │   ├── PageMeta.vue        # Meta tags manager
│   │   └── JsonLd.vue          # Structured data
│   ├── Forms/
│   │   ├── RegisterForm.vue
│   │   ├── LoginForm.vue
│   │   ├── ContactForm.vue
│   │   └── FormInput.vue
│   ├── Sections/
│   │   ├── HeroSection.vue
│   │   ├── FeaturesSection.vue
│   │   ├── PricingSection.vue
│   │   ├── CTASection.vue
│   │   └── FAQSection.vue
│   ├── Blog/
│   │   ├── PostCard.vue
│   │   ├── PostList.vue
│   │   └── PostDetail.vue
│   ├── Common/
│   │   ├── Button.vue           # Shared UI
│   │   ├── Card.vue
│   │   ├── Badge.vue
│   │   ├── Pagination.vue
│   │   └── Alert.vue
│   └── Layouts/
│       ├── default.vue          # Default layout
│       └── blank.vue            # For auth pages
│
├── composables/                 # Composition API hooks
│   ├── useApi.ts                # API wrapper
│   ├── useAuth.ts               # Auth logic
│   ├── useForm.ts               # Form validation (Zod)
│   ├── useSeo.ts                # SEO meta management
│   ├── useI18n.ts               # i18n helpers
│   └── usePagination.ts         # Pagination logic
│
├── stores/                      # Pinia stores
│   ├── authStore.ts             # User auth state
│   ├── contentStore.ts          # Cached content (pages, posts)
│   ├── uiStore.ts               # UI state (theme, lang)
│   └── analyticsStore.ts        # Event tracking
│
├── services/                    # Business logic (не в composables)
│   ├── apiService.ts            # API client
│   ├── authService.ts           # Auth flows (register, verify)
│   ├── contentService.ts        # Content CRUD
│   └── analyticsService.ts      # Event tracking
│
├── utils/                       # Утилиты
│   ├── validators.ts            # Zod schemas
│   ├── helpers.ts               # Общие функции
│   ├── constants.ts             # Константы (URLs, defaults)
│   └── slugify.ts               # URL slug generation
│
├── types/                       # TypeScript интерфейсы
│   ├── api.ts                   # API response types
│   ├── content.ts               # Page, Post, Plan types
│   ├── auth.ts                  # User, Auth types
│   └── index.ts                 # Re-exports
│
├── assets/                      # Статические файлы (обработаны Vite)
│   ├── images/
│   │   ├── logo.svg
│   │   ├── hero-bg.jpg
│   │   └── og-*.jpg
│   ├── fonts/
│   │   └── (если свои шрифты)
│   └── styles/
│       └── (глобальные стили, если нужны вне Tailwind)
│
├── public/                      # Статические файлы (не обрабатываются)
│   ├── robots.txt
│   ├── sitemap.xml              # Или генерируется @nuxtjs/sitemap
│   ├── favicon.ico
│   └── (other static files)
│
├── middleware/                  # Nuxt middleware
│   ├── auth.ts                  # Проверка auth для защищённых страниц
│   ├── analytics.ts             # Отправка событий
│   └── redirects.ts             # Редиректы (старые URL)
│
├── layouts/                     # Layout компоненты
│   ├── default.vue              # Default layout (header + footer)
│   └── auth.vue                 # Auth layout (no header/footer)
│
├── server/                      # Server-side code (API routes, middleware, plugins)
│   ├── api/                     # Server API routes (опционально)
│   │   └── _revalidate.ts       # Webhook для ISR invalidation
│   ├── middleware/              # Nuxt server middleware
│   │   └── security-headers.ts  # CSP, HSTS headers
│   └── plugins/                 # Server plugins
│       └── seo.ts               # Sitemap generation
│
├── plugins/                     # Client plugins
│   ├── vueuse.ts                # VueUse integration
│   ├── error-handler.ts         # Global error handling
│   └── analytics.ts             # Event tracking initialization
│
├── app.config.ts                # App-level config (colors, etc)
├── .nuxtignore                  # Files to ignore in build
├── .eslintrc.json               # ESLint config
├── .prettierrc.json             # Prettier config
└── README.md
```

### 3.2. Маршруты и страницы (Детально)

#### 3.2.1. Маршрут: `/` (Главная / Hero)

**URL:** `https://dam-brand.com/`  
**Режим рендеринга:** SSR (динамический, кешируется на 1 час)  
**Meta-теги (OpenGraph, JSON-LD):**

```html
<title>DAM-система для управления медиафайлами | dam-brand</title>
<meta name="description" content="Облачное хранилище и распределение контента с AI-поиском и аналитикой для маркетинга и креативных команд">
<meta name="keywords" content="DAM, медиафайлы, управление контентом, облако">

<!-- OpenGraph (для соцсетей) -->
<meta property="og:title" content="DAM-система для управления медиафайлами | dam-brand">
<meta property="og:description" content="Облачное хранилище и распределение контента с AI-поиском...">
<meta property="og:image" content="https://cdn.dam-brand.com/og-home-ru.jpg">
<meta property="og:type" content="website">
<meta property="og:url" content="https://dam-brand.com/">

<!-- Twitter Card -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="DAM-система для управления медиафайлами | dam-brand">
<meta name="twitter:description" content="Облачное хранилище и распределение контента с AI-поиском...">
<meta name="twitter:image" content="https://cdn.dam-brand.com/og-home-ru.jpg">

<!-- Structured Data (JSON-LD) -->
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "dam-brand",
  "description": "Облачная DAM-система для управления медиафайлами",
  "url": "https://dam-brand.com",
  "logo": "https://cdn.dam-brand.com/logo.svg",
  "applicationCategory": "BusinessApplication",
  "offers": {
    "@type": "AggregateOffer",
    "priceCurrency": "USD",
    "lowPrice": "29",
    "highPrice": "custom",
    "offerCount": "3"
  },
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "4.8",
    "ratingCount": "250"
  }
}
</script>
```

**Компоненты страницы (Sections):**

1. **Navigation** (фиксированная сверху)
   - Логотип (ссылка на `/`)
   - Меню: Pricing | Blog | About | Contact | Docs
   - Auth buttons: Login | Sign Up
   - Язык: RU | EN (переключатель)

2. **Hero Section**
   - Заголовок h1: "Управляйте контентом быстрее, чем когда-либо"
   - Подзаголовок: "Облачное хранилище + AI-поиск + Аналитика для вашей команды"
   - CTA кнопка primary: "Начать бесплатно" → `/auth/register`
   - Секундарная кнопка: "Демо видео" → YouTube embed / Modal
   - Фоновое изображение (оптимизированное WebP/AVIF)

3. **Features Section** (3-4 карточки)
   - Icon + Title + Description для каждого feature
   - Примеры features: "AI Search", "Unlimited Collaboration", "Advanced Analytics", "Global Distribution"

4. **Pricing Preview** (мини-таблица)
   - 3 плана (Start, Pro, Enterprise)
   - Кнопка "Сравнить планы" → `/pricing`

5. **Social Proof** (опционально)
   - Логотипы клиентов (5-7)
   - Отзывы (2-3 карточки с котировками)

6. **CTA Section** (перед footer)
   - "Готовы начать?" + Primary button "Free Trial"

7. **Footer**
   - Links: Product | Pricing | Blog | About | Contact | Terms | Privacy
   - Соцсети: LinkedIn | Twitter | GitHub
   - Newsletter signup форма
   - Copyright © 2025 dam-brand

**API-запросы:**
```typescript
// Получить контент главной страницы (для заполнения sections)
GET /api/v4/public/pages/home/

// Получить тарифы для preview
GET /api/v4/public/plans/?limit=3

// Получить клиентов для social proof (опционально)
GET /api/v4/public/testimonials/?limit=3
```

**SEO-требования:**
- H1 только один (в Hero)
- Правильная иерархия: H1 → H2 (Features, Pricing) → H3 (Card titles)
- Все изображения с alt-текстом
- Heading в title в браузерной вкладке совпадает с h1 на странице

**Performance-требования:**
- Lighthouse LCP ≤ 2.5s
- Изображения: lazy-loaded (кроме hero), WebP + AVIF
- CSS: Tailwind (встроенный в bundle)
- JS: Минимален (только необходимые интеракции)

---

#### 3.2.2. Маршрут: `/pricing` (Тарифы)

**URL:** `https://dam-brand.com/pricing`  
**Режим рендеринга:** SSR (кешируется на 6 часов)  

**Компоненты:**

1. **Hero** (мини)
   - Title: "Выберите план, который подходит вам"
   - Subtitle: "SaaS или On-Premises — оба варианта доступны"

2. **Toggle: SaaS / Standalone** (опционально)
   - Переключатель между типами развертывания

3. **Pricing Cards** (3 основных плана)
   ```
   ┌─────────────────────┐
   │ START               │
   │ $29/month           │
   │ • 50 GB storage     │
   │ • 3 users           │
   │ • Basic AI Search   │
   │ [Try for Free]      │ ← кнопка
   └─────────────────────┘
   ```

4. **Comparison Table** (детальное сравнение всех features)
   | Feature | Start | Pro | Enterprise |
   |---------|-------|-----|------------|
   | Storage | 50 GB | 500 GB | Unlimited |
   | Users | 3 | 10 | Unlimited |
   | AI Features | Limited | Full | Full |
   | Support | Email | Priority | 24/7 |

5. **FAQ Section** (3-5 частых вопросов о тарифах)

**API-запросы:**
```typescript
GET /api/v4/public/plans/            // Все планы
GET /api/v4/public/faq/?section=pricing  // FAQ по тарифам
```

---

#### 3.2.3. Маршрут: `/blog` & `/blog/:slug` (Новости)

**Маршруты:**
- `/blog` — Список новостей (пагинация)
- `/blog/:slug` — Детальная страница поста (SSR для SEO)

**Компоненты `/blog` (список):**

1. **Search/Filter**
   - Поле поиска (query string: `?q=`)
   - Категория (filter: `?category=`)
   - Дата (опционально)

2. **Post Cards Grid** (3 столбца на десктопе, 1 на мобильном)
   ```
   ┌──────────────┐
   │   Image      │
   │   Title      │
   │   Excerpt    │
   │   Date, Tag  │
   │ [Read More]  │
   └──────────────┘
   ```

3. **Pagination**
   - Previous | 1 2 3 ... N | Next
   - 10 постов на странице (настраивается)

**Компоненты `/blog/:slug` (детальная):**

1. **Post Header**
   - Featured image (large, optimized)
   - Title (h1)
   - Author + date + reading time
   - Tags

2. **Post Content**
   - HTML-контент (с поддержкой markdown)
   - Встроенные images (lazy-loaded)
   - Встроенные code blocks (с highlight)

3. **Related Posts** (3-5 похожих статей в конце)

**Meta-теги для `/blog/:slug`:**
```html
<!-- Динамические теги из API ответа -->
<title>{{ post.seo_title }}</title>
<meta name="description" content="{{ post.seo_description }}">
<meta property="og:image" content="{{ post.featured_image }}">

<!-- Structured Data для новости -->
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "NewsArticle",
  "headline": "{{ post.title }}",
  "image": "{{ post.featured_image }}",
  "datePublished": "{{ post.published_at }}",
  "dateModified": "{{ post.updated_at }}",
  "author": {
    "@type": "Person",
    "name": "{{ post.author }}"
  }
}
</script>
```

**API-запросы:**
```typescript
GET /api/v4/public/posts/?page=1&limit=10&lang=ru  // Список
GET /api/v4/public/posts/{slug}/                   // Деталь
```

---

#### 3.2.4. Маршрут: `/auth/register` (Регистрация)

**URL:** `https://dam-brand.com/auth/register`  
**Режим:** SSR (без кеша, всегда свежая форма)  

**Форма:**

| Поле | Тип | Валидация | Обязательное |
|------|-----|-----------|-------------|
| Email | text | Email format, no duplicates | ✅ |
| Password | password | Min 8 chars, 1 digit, 1 special | ✅ |
| Org Name | text | Min 2 chars | ✅ |
| First Name | text | Min 2 chars | ❌ |
| Last Name | text | Min 2 chars | ❌ |
| Terms | checkbox | Must be checked | ✅ |

**Валидация (Zod Schema):**
```typescript
const registerSchema = z.object({
  email: z.string().email('Invalid email'),
  password: z.string()
    .min(8, 'Min 8 characters')
    .regex(/[0-9]/, 'Must include number')
    .regex(/[!@#$%^&*]/, 'Must include special char'),
  organization_name: z.string().min(2, 'Min 2 chars'),
  first_name: z.string().optional(),
  last_name: z.string().optional(),
  agree_terms: z.boolean().refine(v => v === true, 'Must agree')
});
```

**Flow:**
1. Пользователь заполняет форму
2. Клиентская валидация (Zod)
3. `POST /api/v4/public/auth/register/`
4. Успех: Email подтверждения отправлен → редирект на `/auth/register/sent`
5. Ошибка: Вывести ошибку (email exists, password weak, etc)

**Страница `/auth/register/sent`:**
- Сообщение: "Проверьте email для активации аккаунта"
- Ссылка: "Не получили письмо? Отправить ещё раз"

---

#### 3.2.5. Маршрут: `/auth/verify-email/:token` (Верификация)

**URL:** `https://dam-brand.com/auth/verify-email/[token]`  

**Flow:**
1. Пользователь кликает ссылку из письма
2. Frontend извлекает `:token` из URL
3. `POST /api/v4/public/auth/verify-email/` с token
4. Django проверяет токен и активирует аккаунт
5. Успех: Редирект на `https://app.dam-brand.com/login?success=verified`
6. Ошибка: Показать ошибку (expired token, invalid, etc)

---

#### 3.2.6. Маршруты: `/contact`, `/about`, `/terms`, `/privacy`

Все эти страницы получают контент из API через slug:
```typescript
GET /api/v4/public/pages/{slug}/
// Примеры: /contact/, /about/, /terms/, /privacy/
```

**Структура контента (для каждой страницы в Django CMS):**
```json
{
  "slug": "contact",
  "title": "Contact Us",
  "meta_title": "Contact dam-brand | Get in touch",
  "meta_description": "...",
  "sections": [
    {
      "type": "contact_form",
      "content": {
        "form_title": "Send us a message",
        "submit_button_text": "Send"
      }
    }
  ]
}
```

---

### 3.3. API-контракты (REST)

#### 3.3.1. Endpoint: `GET /api/v4/public/pages/{slug}/`

**Описание:** Получить контент страницы по slug (используется SSR).

**Request:**
```bash
GET /api/v4/public/pages/home/?lang=ru
Accept: application/json
Authorization: (не требуется)
```

**Response 200 OK:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "slug": "home",
  "title": "Главная",
  "meta_title": "DAM-система для управления медиафайлами | dam-brand",
  "meta_description": "Облачное хранилище и распределение контента с AI-поиском и аналитикой",
  "og_image": "https://cdn.dam-brand.com/og-home-ru.jpg",
  "canonical_url": "https://dam-brand.com/",
  "lang": "ru",
  "status": "published",
  "published_at": "2025-12-20T10:00:00Z",
  "updated_at": "2025-12-30T15:00:00Z",
  "sections": [
    {
      "id": "section-hero",
      "type": "hero",
      "order": 1,
      "content": {
        "heading": "Управляйте контентом быстрее",
        "subheading": "Облачное хранилище + AI-поиск + Аналитика",
        "cta_text": "Начать бесплатно",
        "cta_url": "/auth/register",
        "background_image": "https://cdn.dam-brand.com/hero-bg.jpg"
      }
    },
    {
      "id": "section-features",
      "type": "features",
      "order": 2,
      "content": [
        {
          "title": "AI Search",
          "description": "Найдите нужное за секунды",
          "icon": "search",
          "image": "https://cdn.dam-brand.com/feature-ai.jpg"
        }
      ]
    }
  ]
}
```

**Response 404 Not Found:**
```json
{
  "error": "not_found",
  "detail": "Page with slug 'unknown' not found"
}
```

---

#### 3.3.2. Endpoint: `GET /api/v4/public/posts/?page=1&limit=10&lang=ru`

**Описание:** Список опубликованных новостей с пагинацией.

**Query Parameters:**
- `page` (int, default 1) — номер страницы
- `limit` (int, default 10) — количество на странице (max 100)
- `lang` (string, default 'ru') — язык контента
- `search` (string, optional) — поиск по названию/содержанию
- `category` (string, optional) — фильтр по категории

**Request:**
```bash
GET /api/v4/public/posts/?page=1&limit=10&lang=ru
Authorization: (не требуется)
```

**Response 200 OK:**
```json
{
  "count": 47,
  "next": "https://api.dam-brand.com/api/v4/public/posts/?page=2&limit=10&lang=ru",
  "previous": null,
  "results": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "slug": "ai-search-release",
      "title": "Выпустили AI Search 2.0",
      "excerpt": "Новый поиск видит изображения и видео лучше чем когда-либо...",
      "featured_image": "https://cdn.dam-brand.com/news-ai-search.jpg",
      "category": "Product Updates",
      "author": {
        "name": "Ivan Petrov",
        "avatar": "https://cdn.dam-brand.com/avatar-ivan.jpg"
      },
      "published_at": "2025-12-28T12:00:00Z",
      "updated_at": "2025-12-30T10:00:00Z",
      "reading_time_minutes": 5,
      "tags": ["AI", "Search", "Feature Release"]
    }
  ]
}
```

---

#### 3.3.3. Endpoint: `GET /api/v4/public/posts/{slug}/`

**Описание:** Полная статья по slug (для SSR).

**Response 200 OK:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "slug": "ai-search-release",
  "title": "Выпустили AI Search 2.0",
  "content": "# Новая эра поиска\n\nМы гордимся представить...",
  "content_html": "<h1>Новая эра поиска</h1><p>Мы гордимся представить...</p>",
  "featured_image": "https://cdn.dam-brand.com/news-ai-search.jpg",
  "author": {
    "name": "Ivan Petrov",
    "bio": "Product Lead at dam-brand"
  },
  "category": "Product Updates",
  "tags": ["AI", "Search", "Feature Release"],
  "published_at": "2025-12-28T12:00:00Z",
  "updated_at": "2025-12-30T10:00:00Z",
  "reading_time_minutes": 5,
  "seo_title": "AI Search 2.0 выпущена | dam-brand",
  "seo_description": "Революционный AI-поиск для видео и изображений...",
  "og_image": "https://cdn.dam-brand.com/news-ai-search-og.jpg",
  "related_posts": [
    {
      "slug": "machine-learning-update",
      "title": "Обновление ML моделей",
      "featured_image": "https://cdn.dam-brand.com/news-ml.jpg"
    }
  ]
}
```

---

#### 3.3.4. Endpoint: `GET /api/v4/public/plans/`

**Описание:** Все тарифные планы (для страницы `/pricing`).

**Response 200 OK:**
```json
{
  "results": [
    {
      "id": "plan-start",
      "name": "Start",
      "description": "Для небольших команд",
      "price_monthly": 29,
      "price_yearly": 290,
      "currency": "USD",
      "billing_period": "month",
      "storage_gb": 50,
      "max_users": 3,
      "max_api_calls_monthly": 100000,
      "features": [
        "Basic AI Search",
        "Email Support",
        "Basic Analytics"
      ],
      "recommended": false,
      "type": "saas",
      "cta_text": "Try Free",
      "cta_url": "/auth/register?plan=start"
    },
    {
      "id": "plan-pro",
      "name": "Pro",
      "description": "Для растущих команд",
      "price_monthly": 99,
      "price_yearly": 990,
      "currency": "USD",
      "storage_gb": 500,
      "max_users": 10,
      "max_api_calls_monthly": 1000000,
      "features": [
        "Advanced AI Search",
        "Priority Support",
        "Full Analytics",
        "Custom Integrations"
      ],
      "recommended": true,
      "type": "saas"
    },
    {
      "id": "plan-enterprise",
      "name": "Enterprise",
      "description": "Для больших организаций",
      "price_monthly": null,
      "price_yearly": null,
      "currency": "USD",
      "storage_gb": null,
      "max_users": null,
      "features": [
        "Unlimited Everything",
        "Dedicated Support",
        "Custom Deployment",
        "SLA Guarantee"
      ],
      "recommended": false,
      "type": "both",
      "cta_text": "Contact Sales",
      "cta_url": "/contact"
    }
  ]
}
```

---

#### 3.3.5. Endpoint: `POST /api/v4/public/auth/register/`

**Описание:** Регистрация нового пользователя и организации.

**Request:**
```json
{
  "email": "cto@romashka.ru",
  "password": "SecurePass123!",
  "organization_name": "Ромашка ООО",
  "first_name": "Иван",
  "last_name": "Петров",
  "phone": "+7 (999) 123-45-67",
  "company_size": "50-200",
  "lang": "ru",
  "agree_terms": true
}
```

**Response 201 Created:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440002",
  "email": "cto@romashka.ru",
  "organization": {
    "id": "org-550e8400-e29b-41d4-a716-446655440003",
    "name": "Ромашка ООО",
    "slug": "romashka-ooo",
    "created_at": "2025-12-30T15:30:00Z"
  },
  "verification_required": true,
  "verification_email_sent": true,
  "next_step": "verify_email",
  "message": "На email отправлено письмо с ссылкой активации. Перейдите по ссылке для подтверждения адреса."
}
```

**Response 400 Bad Request (Email exists):**
```json
{
  "error": "validation_error",
  "details": {
    "email": ["Email уже зарегистрирован в системе"]
  }
}
```

**Response 400 Bad Request (Password weak):**
```json
{
  "error": "validation_error",
  "details": {
    "password": ["Пароль должен содержать минимум 8 символов, цифру и спецсимвол"]
  }
}
```

---

#### 3.3.6. Endpoint: `POST /api/v4/public/auth/verify-email/`

**Описание:** Верификация email по токену.

**Request:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJleHAiOjE3MDQwMDAwMDB9.ABC..."
}
```

**Response 200 OK:**
```json
{
  "success": true,
  "message": "Email успешно подтвержден. Вы можете войти в систему.",
  "redirect_url": "https://app.dam-brand.com/login?verified=true"
}
```

**Response 400 Bad Request (Token expired):**
```json
{
  "error": "token_expired",
  "message": "Ссылка активации истекла. Отправьте письмо снова.",
  "retry_url": "/auth/register/send-verification"
}
```

---

#### 3.3.7. Endpoint: `POST /api/v4/public/leads/`

**Описание:** Форма контакта (Lead capture).

**Request:**
```json
{
  "name": "Иван Петров",
  "email": "ivan@romashka.ru",
  "company": "Ромашка ООО",
  "message": "Заинтересованы в enterprise-версии с кастомной интеграцией",
  "phone": "+7 (999) 123-45-67",
  "subject": "Enterprise inquiry"
}
```

**Response 201 Created:**
```json
{
  "id": "lead-550e8400",
  "status": "new",
  "created_at": "2025-12-30T15:35:00Z",
  "message": "Спасибо! Мы получили ваше сообщение и свяжемся в течение 24 часов."
}
```

---

### 3.4. Многоязычность (i18n)

#### 3.4.1. Стратегия локализации

**Уровень URL (Nuxt i18n prefix strategy):**
```
/ru/                  → Русский (по умолчанию)
/en/                  → Английский
/ru/blog/             → /blog на русском
/en/blog/             → /blog на английском
```

**Конфигурация в nuxt.config.ts:**
```typescript
export default defineNuxtConfig({
  modules: ['@nuxtjs/i18n'],
  i18n: {
    locales: [
      {
        code: 'ru',
        iso: 'ru-RU',
        name: 'Русский',
        file: 'ru.json'
      },
      {
        code: 'en',
        iso: 'en-US',
        name: 'English',
        file: 'en.json'
      }
    ],
    defaultLocale: 'ru',
    strategy: 'prefix_except_default',  // /ru/, /en/ (но / = /ru/)
    baseUrl: 'https://dam-brand.com'
  }
})
```

#### 3.4.2. Backend API Localization

**Backend отдает локализованные данные:**
```json
{
  "title": {
    "ru": "Главная",
    "en": "Home"
  },
  "meta_title": {
    "ru": "DAM-система | dam-brand",
    "en": "DAM System | dam-brand"
  },
  "content": {
    "ru": "Добро пожаловать...",
    "en": "Welcome..."
  }
}
```

**Frontend выбирает правильный язык:**
```vue
<template>
  <h1>{{ page.title[$i18n.locale] }}</h1>
  <p>{{ page.content[$i18n.locale] }}</p>
</template>

<script setup lang="ts">
const { locale } = useI18n();
</script>
```

#### 3.4.3. UI-элементы (переключатель языка)

**Компонент LanguageSwitcher в Navigation:**
```vue
<template>
  <div class="language-switcher">
    <NuxtLink
      v-for="l in locales"
      :key="l.code"
      :to="switchLocalePath(l.code)"
      :class="{ active: locale === l.code }"
    >
      {{ l.name }}
    </NuxtLink>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n';
import { useSwitchLocalePath } from '#i18n';

const { locale, locales } = useI18n();
const switchLocalePath = useSwitchLocalePath();
</script>
```

---

### 3.5. Аналитика и Event Tracking

#### 3.5.1. События, которые нужно отслеживать

| Событие | Триггер | Параметры | Цель |
|---------|---------|-----------|------|
| `page_view` | При загрузке страницы | page, lang, source | Трафик |
| `cta_click` | Клик по CTA кнопке | button_text, page, section | Engagement |
| `form_submit` | Отправка формы | form_type, success | Conversions |
| `form_error` | Ошибка формы | field, error_type | UX insights |
| `pricing_view` | Просмотр `/pricing` | plans_viewed | Intent |
| `blog_read` | Прочитана новость | post_slug, reading_time | Content engagement |
| `signup_start` | Открыта форма `/register` | source | Funnel |
| `signup_complete` | Завершена регистрация | org_name, source | Conversion |
| `email_verify_click` | Клик на ссылку в письме | success | Activation |

#### 3.5.2. Реализация (Google Analytics + internal tracking)

```typescript
// composables/useAnalytics.ts
export function useAnalytics() {
  const router = useRouter();
  const route = useRoute();

  // Отправить событие в GA + backend
  const trackEvent = (event: string, params: Record<string, any>) => {
    // Google Analytics
    if (window.gtag) {
      window.gtag('event', event, params);
    }

    // Backend analytics (опционально)
    $fetch('/api/v4/public/analytics/events/', {
      method: 'POST',
      body: { event, ...params, timestamp: new Date().toISOString() }
    });
  };

  // Auto track page views
  watch(() => route.path, () => {
    trackEvent('page_view', {
      page: route.path,
      title: document.title,
      lang: useI18n().locale.value
    });
  });

  return { trackEvent };
}
```

---

## 4. НЕФУНКЦИОНАЛЬНЫЕ ТРЕБОВАНИЯ

### 4.1. Performance (Core Web Vitals)

| Метрика | Целевое значение | Инструмент |
|---------|-----------------|-----------|
| **LCP (Largest Contentful Paint)** | ≤ 2.5s | WebPageTest, Lighthouse |
| **FID (First Input Delay)** | ≤ 100ms | Chrome UX Report |
| **CLS (Cumulative Layout Shift)** | ≤ 0.1 | Lighthouse |
| **TTFB (Time to First Byte)** | ≤ 600ms | CDN monitoring |
| **JS Bundle Size** | ≤ 150 KB (gzip) | Rollup stats plugin |
| **CSS Bundle Size** | ≤ 30 KB (gzip) | PurgeCSS |
| **First Paint (FP)** | ≤ 1.5s | Lighthouse |
| **Largest Paint (LP)** | ≤ 3s | Lighthouse |

**Оптимизационные техники:**
- Image: WebP/AVIF + srcset, lazy-loading для below-the-fold
- Code splitting: Автоматически по роутам (Nuxt)
- CSS: Tailwind (встроен в build, PurgeCSS убирает неиспользованные стили)
- Fonts: Preload для primary font, font-display: swap
- Минификация: Vite по умолчанию

---

### 4.2. SEO

| Требование | Описание |
|-----------|---------|
| **Meta-теги** | Все страницы: `<title>`, `meta[description]`, `og:*`, `twitter:*` |
| **Structured Data** | JSON-LD для: SoftwareApplication (главная), NewsArticle (блог) |
| **Sitemap** | Автогенерация, обновление каждую ночь |
| **robots.txt** | Правильный (разрешить `/`, запретить `/admin`, `/api/`) |
| **Heading hierarchy** | H1 (только один) → H2 → H3, без пропусков |
| **Alt-text** | Все `<img>` имеют осмысленный alt |
| **Canonical URLs** | `<link rel="canonical">` на всех страницах |
| **Mobile-friendly** | 100% адаптивность, проходит мобильный test |
| **Page Speed** | Lighthouse ≥ 90 (performance score) |
| **Indexation** | Все публичные страницы индексируются (проверить в GSC) |

---

### 4.3. Security

| Требование | Описание |
|-----------|---------|
| **HTTPS** | Все ссылки HTTPS, HSTS (max-age=31536000) |
| **CSP (Content Security Policy)** | Минимальная политика (script-src: self, cdn; img-src: self, cdn) |
| **CORS** | Только api.dam-brand.com может отдавать ответы |
| **XSS Protection** | Все user input экранируется (Vue это делает автоматически) |
| **CSRF Protection** | Использовать CSRF tokens для форм (Django DRF поддерживает) |
| **Input Validation** | Клиентская (Zod) + серверная (Django) валидация |

---

### 4.4. Accessibility (WCAG 2.1 Level AA)

| Требование | Описание |
|-----------|---------|
| **Color Contrast** | 4.5:1 для обычного текста, 3:1 для большого (ಠ_ಠ) |
| **Keyboard Navigation** | Все интерактивные элементы доступны по Tab |
| **Focus Indicators** | Видимый focus ring для клавиатурной навигации |
| **Aria Labels** | Все иконки/кнопки имеют aria-label или title |
| **Form Labels** | Все `<input>` связаны с `<label>` |
| **Skip Links** | Skip-to-content ссылка (опционально) |
| **Responsive Text** | Текст читаемый без зума на 200% |

---

### 4.5. Browser Support

| Браузер | Версия | Поддержка |
|---------|--------|----------|
| Chrome | 90+ | ✅ Полная |
| Firefox | 88+ | ✅ Полная |
| Safari | 14+ | ✅ Полная |
| Edge | 90+ | ✅ Полная |
| IE 11 | — | ❌ Не поддерживается |

---

## 5. ТРЕБОВАНИЯ К ТЕСТИРОВАНИЮ

### 5.1. Unit-тесты (Vitest)

```typescript
// tests/unit/components/Button.spec.ts
import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import Button from '@/components/Button.vue';

describe('Button Component', () => {
  it('renders with primary variant', () => {
    const wrapper = mount(Button, {
      props: { variant: 'primary' },
      slots: { default: 'Click me' }
    });
    expect(wrapper.classes()).toContain('bg-blue-600');
  });

  it('emits click event', async () => {
    const wrapper = mount(Button);
    await wrapper.trigger('click');
    expect(wrapper.emitted('click')).toHaveLength(1);
  });

  it('is disabled when disabled prop is true', () => {
    const wrapper = mount(Button, {
      props: { disabled: true }
    });
    expect(wrapper.classes()).toContain('opacity-50');
  });
});
```

**Покрытие:** ≥ 80% по строкам для компонентов и utils.

---

### 5.2. Integration-тесты (Vitest + MSW)

```typescript
// tests/integration/api/pages.spec.ts
import { describe, it, expect, beforeAll } from 'vitest';
import { server } from '@/tests/mocks/server';

beforeAll(() => server.listen());

describe('Pages API', () => {
  it('fetches and renders home page', async () => {
    const data = await $fetch('/api/v4/public/pages/home/');
    expect(data.title).toBeDefined();
    expect(data.sections).toBeInstanceOf(Array);
  });

  it('handles 404 gracefully', async () => {
    try {
      await $fetch('/api/v4/public/pages/nonexistent/');
    } catch (error) {
      expect(error.statusCode).toBe(404);
    }
  });
});
```

---

### 5.3. E2E-тесты (Playwright)

```typescript
// tests/e2e/auth.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Registration Flow', () => {
  test('complete registration', async ({ page }) => {
    await page.goto('https://dam-brand.local/auth/register');

    // Fill form
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="password"]', 'TestPass123!');
    await page.fill('input[name="organization_name"]', 'Test Org');
    await page.check('input[name="agree_terms"]');

    // Submit
    await page.click('button[type="submit"]');

    // Expect redirect to verification page
    await expect(page).toHaveURL(/\/auth\/register\/sent/);
    await expect(page.locator('text=Check your email')).toBeVisible();
  });

  test('shows validation errors', async ({ page }) => {
    await page.goto('https://dam-brand.local/auth/register');
    await page.fill('input[name="email"]', 'invalid-email');
    await page.click('button[type="submit"]');
    await expect(page.locator('text=Invalid email')).toBeVisible();
  });
});
```

**Скрипт запуска:** `npm run test:e2e`

---

### 5.4. Performance-тесты

```bash
# Lighthouse CLI
npm install -g @lhci/cli@latest
lhci autorun

# Результаты сохраняются в временной шкале
```

**CI/CD интеграция:** GitHub Actions должен запускать Lighthouse после деплоя.

---

### 5.5. Чек-листы для QA

**Перед релизом проверить:**
- [ ] All pages load without console errors
- [ ] Meta tags are correct (title, description, OG)
- [ ] Images are optimized (WebP/AVIF)
- [ ] Forms submit and show success/error correctly
- [ ] Email verification flow works end-to-end
- [ ] Pagination works on `/blog`
- [ ] Language switcher switches content correctly
- [ ] Mobile view is responsive on 375px, 768px, 1920px
- [ ] All links (internal, external) work
- [ ] 404 page displays correctly
- [ ] Lighthouse scores ≥ 90 on all main pages
- [ ] Cross-browser testing (Chrome, Firefox, Safari, Edge)

---

## 6. ТРЕБОВАНИЯ К РАЗВЕРТЫВАНИЮ (DEPLOYMENT)

### 6.1. Build процесс

```bash
# Установка зависимостей
npm install

# Build production
npm run build
# Результат: .output/ директория с SSR app

# Локальное тестирование
npm run preview

# Production сервер
node .output/server/index.mjs
# Listen на http://localhost:3000
```

### 6.2. Docker

```dockerfile
# Dockerfile
FROM node:18-alpine

WORKDIR /app

# Copy manifests
COPY package*.json ./
RUN npm ci --only=production

# Copy built app
COPY .output ./

EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3000/', (r) => {if (r.statusCode !== 200) throw new Error(r.statusCode)})"

CMD ["node", ".output/server/index.mjs"]
```

### 6.3. Nginx конфигурация

```nginx
upstream nuxt_app {
  server nuxt:3000;
}

server {
  listen 80;
  server_name dam-brand.com www.dam-brand.com;

  # Redirect HTTP to HTTPS
  return 301 https://$server_name$request_uri;
}

server {
  listen 443 ssl http2;
  server_name dam-brand.com www.dam-brand.com;

  ssl_certificate /etc/letsencrypt/live/dam-brand.com/fullchain.pem;
  ssl_certificate_key /etc/letsencrypt/live/dam-brand.com/privkey.pem;

  # Security headers
  add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
  add_header X-Content-Type-Options "nosniff" always;
  add_header X-Frame-Options "SAMEORIGIN" always;
  add_header X-XSS-Protection "1; mode=block" always;

  # CSP
  add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' *.googletagmanager.com cdn.jsdelivr.net; img-src 'self' data: https: cdn.*; font-src 'self' fonts.googleapis.com fonts.gstatic.com;" always;

  # Gzip
  gzip on;
  gzip_comp_level 6;
  gzip_types text/plain text/css text/javascript application/javascript application/json;

  # Static files with long cache
  location ~* ^/(_nuxt|assets)/ {
    expires 1y;
    add_header Cache-Control "public, immutable";
  }

  # API proxy
  location /api {
    proxy_pass http://django:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
  }

  # Nuxt SSR
  location / {
    proxy_pass http://nuxt_app;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;

    # Кешировать HTML на 5 минут
    proxy_cache_valid 200 5m;
    proxy_cache_key "$scheme$request_method$host$request_uri";
    add_header X-Cache-Status $upstream_cache_status always;
  }
}
```

### 6.4. CI/CD Pipeline (GitHub Actions)

```yaml
# .github/workflows/deploy.yml
name: Deploy Nuxt App

on:
  push:
    branches:
      - main

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Setup Node
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Run tests
        run: npm run test

      - name: Build
        run: npm run build

      - name: Run Lighthouse CI
        run: npm run test:lighthouse

      - name: Build Docker image
        run: docker build -t dam-brand-public:latest .

      - name: Push to registry
        run: |
          echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
          docker push dam-brand-public:latest

      - name: Deploy to production
        run: |
          ssh deploy@prod-server 'cd /opt/dam-brand && docker-compose pull && docker-compose up -d'
```

---

## 7. РИСКИ И АРХИТЕКТУРНЫЕ РЕШЕНИЯ

### 7.1. Критические риски

| # | Риск | Вероятность | Вплив | Mitigation |
|---|------|-------------|------|-----------|
| 1 | API от Django медленный (timeout) | Medium | High | Rate limiting, кеширование (Redis) на уровне Nuxt |
| 2 | Контент на русском плохо индексируется | Medium | High | Структурированные данные (JSON-LD), XML sitemap, яндекс вебмастер |
| 3 | Мобильная версия неоптимизирована | Low | High | Mobile-first design, регулярный PageSpeed testing |
| 4 | Высокий bounce rate на лендинге | Medium | Medium | A/B-тестирование, тепловые карты (Hotjar), пользовательские интервью |
| 5 | DDoS атаки на публичный сайт | Low | High | Cloudflare DDoS protection, rate limiting на API |

### 7.2. Архитектурные решения (нужно согласовать до разработки)

1. **Кеширование API-ответов:**
   - На уровне Nuxt (Pinia store с TTL)?
   - На уровне Nginx (proxy_cache)?
   - На уровне Django (Redis)?
   - **Решение:** Все три уровня: Nginx (5 мин) → Pinia (во время сессии)

2. **Образ изображений (что использовать):**
   - Cloudinary (платный, но удобный)?
   - S3 + AVIF conversion на лету?
   - Django imagekit?
   - **Решение:** S3 + Cloudflare Image Optimization (бесплатен для Workers)

3. **Хостинг Nuxt приложения:**
   - Vercel (оптимально для Nuxt, но зависимость от сервиса)?
   - Self-hosted на выделенном VPS?
   - Kubernetes кластер?
   - **Решение:** Self-hosted Docker на одном VPS (для контроля) + Cloudflare CDN

4. **Обработка форм (где валидировать):**
   - Только клиент (Zod)?
   - Только сервер (Django)?
   - Оба (дублирование кода)?
   - **Решение:** Клиент (быстро), сервер (security).

5. **SEO: SSR vs SSG:**
   - SSR для всех страниц (свежий контент, но медленнее)?
   - SSG для статического контента + ISR для обновлений?
   - **Решение:** SSR для `/`, `/pricing`, `/blog` с кешированием; SSG для `/about`, `/privacy` (статичные).

---

## 8. ПЛАН РЕАЛИЗАЦИИ (ROADMAP)

### Sprint 1 (Неделя 1-2): Setup + Core Pages

- [ ] Setup Nuxt 3 проект, интеграция Tailwind
- [ ] Разработать Navigation, Footer компоненты
- [ ] Реализовать `/` (главная)
- [ ] Реализовать `/pricing` и `/about`
- [ ] Интеграция с API (страницы, планы)
- [ ] Базовая SEO (meta tags, sitemap)

### Sprint 2 (Неделя 3-4): Blog + Auth

- [ ] Реализовать `/blog` и `/blog/:slug`
- [ ] Реализовать `/auth/register` и `/auth/login`
- [ ] Email верификация flow
- [ ] Формы контакта и лидогенерация

### Sprint 3 (Неделя 5-6): Polish + Deploy

- [ ] i18n (RU/EN) для всех страниц
- [ ] Performance оптимизация (Lighthouse ≥ 95)
- [ ] Accessibility audit (WCAG 2.1 AA)
- [ ] E2E тесты (Playwright)
- [ ] Docker build + CI/CD pipeline
- [ ] Production deployment

---

## 9. ПРИЛОЖЕНИЯ

### Приложение A: Envs и конфигурация

```bash
# .env.example
NUXT_PUBLIC_API_URL=https://api.dam-brand.com
NUXT_PUBLIC_APP_URL=https://app.dam-brand.com
NUXT_PUBLIC_GA_ID=G-XXXXXXXXX  # Google Analytics
NUXT_PUBLIC_ENVIRONMENT=production
```

### Приложение B: Команды для разработки

```bash
# Dev server (http://localhost:3000)
npm run dev

# Build для production
npm run build

# Preview built app
npm run preview

# Lint
npm run lint

# Format
npm run format

# Tests
npm run test              # unit + integration
npm run test:e2e          # E2E (Playwright)
npm run test:lighthouse   # Performance
```

---

## 10. КОНТАКТЫ И ОТВЕТСТВЕННОСТЬ

| Роль | ФИО | Контакт | Ответственность |
|------|-----|---------|-----------------|
| **Frontend Lead** | — | — | Архитектура, code review |
| **Frontend Dev** | — | — | Компоненты, страницы |
| **DevOps** | — | — | Docker, CI/CD, infra |
| **QA** | — | — | Тестирование, checklist |

---

**Документ согласован:** ___________  
**Дата:** 30 декабря 2025  
**Версия:** 1.0  
