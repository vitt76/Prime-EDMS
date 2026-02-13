# SEO Best Practices — MADDAM Public Frontend (Nuxt 3)

Чеклист и конфигурация для индексации (Yandex, Google) и технического SEO.

---

## 1. robots.txt

- **Реализация:** Динамический ответ из `server/routes/robots.txt.get.ts`.
- **Переменная:** `NUXT_PUBLIC_SITE_URL` (production: `https://maddam.io`).
- **Проверить:**
  - [ ] `Allow` для `/`, `/pricing`, `/about`, `/blog`, `/contact`, `/privacy`, `/terms`, `/roadmap`, `/changelog`.
  - [ ] `Disallow` для `/auth/`, `/admin`, `/app/`, `/account/`, `/api/`, `/_nuxt/`.
  - [ ] Директива `Host:` для Yandex.
  - [ ] `Sitemap: {siteUrl}/sitemap.xml`.

---

## 2. Sitemap

- **Модуль:** `@nuxtjs/sitemap`, конфиг в `nuxt.config.ts` → `sitemap`.
- **Динамические URL:** Блог подтягивается из Django API через `sources: ['/api/sitemap-urls']` (см. `server/api/sitemap-urls.get.ts`).
- **Проверить:**
  - [ ] В production задан `NUXT_PUBLIC_SITE_URL`.
  - [ ] Доступен `https://maddam.io/sitemap.xml`.
  - [ ] В sitemap есть главная, pricing, about, blog (список), contact, legal, roadmap, changelog и все посты из API.

---

## 3. Meta и Open Graph

- **Глобально:** `nuxt.config.ts` → `app.head`: `description`, `og:type`, `og:site_name`, `og:image` (fallback `/og-default.png`), `twitter:card`.
- **По страницам:** Компонент `SEOPageMeta` + composable `useSeo()` → `setPageMeta({ title, description, ogImage, canonical, canonicalFromRoute })`.
- **Проверить:**
  - [ ] У каждой публичной страницы заданы `title` и `description`.
  - [ ] Для шаринга в соцсетях есть `og:title`, `og:description`, `og:image` (абсолютный URL через `siteUrl` в `useSeo`).
  - [ ] Канонический URL задаётся (по умолчанию `canonicalFromRoute: true` → `siteUrl + route.path`).
  - [ ] В `public/` лежит `og-default.png` (рекомендуемый размер для OG: 1200×630).

---

## 4. JSON-LD (Schema.org)

- **Composable:** `useJsonld()` в `composables/useJsonld.ts`: `organizationSchema()`, `softwareApplicationSchema()`, `setSchema()`, `siteUrl`.
- **Главная:** `Organization` + `SoftwareApplication` (через `@graph` в `pages/index.vue`).
- **Блог-пост:** `BlogPosting` в `pages/blog/[slug].vue` (с `siteUrl` для publisher и mainEntityOfPage).
- **Проверить:**
  - [ ] На главной в разметке есть и Organization, и SoftwareApplication.
  - [ ] В JSON-LD все URL абсолютные (`siteUrl` из runtimeConfig).

---

## 5. Производительность и техническое SEO

- **Изображения:** `@nuxt/image` с провайдером `ipx`, форматы webp/avif, пресеты (avatar, thumbnail, hero).
- **Аналитика:** Яндекс.Метрика подключается только после согласия (CookieConsentModal), скрипт не блокирует рендер.
- **SSR:** Включён (`ssr: true`), контент отдаётся для краулеров.
- **Кэширование:** `routeRules` с `swr` для главной, pricing, blog, статических и legal-страниц.
- **Проверить:**
  - [ ] LCP, FID, CLS в норме (Lighthouse / PageSpeed).
  - [ ] Критичный контент в первом экране без лишних блокирующих скриптов.

---

## 6. Production

- Задать в окружении:
  - `NUXT_PUBLIC_SITE_URL=https://maddam.io`
  - При необходимости `NUXT_PUBLIC_YM_ID` для Яндекс.Метрики.
- Добавить в `public/`:
  - `og-default.png` (1200×630) для OG по умолчанию.
  - `logo.png` для Schema.org (Organization, publisher).

---

## Краткий чеклист по проекту

| Элемент | Где | Статус |
|--------|-----|--------|
| robots.txt | `server/routes/robots.txt.get.ts` | Динамический, Host + Sitemap |
| sitemap.xml | @nuxtjs/sitemap | Статика + `/api/sitemap-urls` (блог) |
| Title/Description | SEOPageMeta, app.head | По страницам + дефолт |
| OG / Twitter | useSeo.setPageMeta, app.head | og:image абсолютный через siteUrl |
| Canonical | SEOPageMeta (canonicalFromRoute) | siteUrl + path |
| JSON-LD | useJsonld, index + blog/[slug] | Organization, SoftwareApplication, BlogPosting |
| Изображения | @nuxt/image | Оптимизация, пресеты |
