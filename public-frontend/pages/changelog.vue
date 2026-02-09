<template>
  <div>
    <SEOPageMeta
      title="Changelog | MADDAM"
      description="История изменений MADDAM — новые функции, улучшения и исправления."
    />

    <!-- Hero -->
    <section class="bg-gradient-to-b from-primary-50 to-white py-16 lg:py-20 dark:from-neutral-900 dark:to-neutral-950">
      <div class="mx-auto max-w-container px-4 text-center">
        <div class="inline-flex items-center gap-2 rounded-full bg-primary-100 px-4 py-1.5 text-sm font-medium text-primary-700 dark:bg-primary-900/40 dark:text-primary-300">
          <DocumentTextIcon class="h-4 w-4" />
          <span>Changelog</span>
        </div>
        <h1 class="mt-6 text-4xl font-bold tracking-tight text-neutral-900 md:text-5xl dark:text-white">
          История изменений
        </h1>
        <p class="mx-auto mt-4 max-w-2xl text-lg text-neutral-600 dark:text-neutral-400">
          Все обновления, улучшения и исправления в одном месте.
        </p>
      </div>
    </section>

    <!-- Changelog Entries -->
    <section class="py-16 lg:py-20">
      <div class="mx-auto max-w-3xl px-4">
        <div class="space-y-12">
          <article
            v-for="release in releases"
            :key="release.version"
            class="relative"
          >
            <!-- Version Header -->
            <div class="flex flex-wrap items-center gap-3">
              <h2 class="text-2xl font-bold text-neutral-900 dark:text-white">
                v{{ release.version }}
              </h2>
              <span
                v-if="release.latest"
                class="rounded-full bg-success/10 px-3 py-0.5 text-xs font-semibold text-success"
              >
                Последний
              </span>
              <span class="text-sm text-neutral-500 dark:text-neutral-400">
                {{ release.date }}
              </span>
            </div>

            <p v-if="release.summary" class="mt-2 text-neutral-600 dark:text-neutral-400">
              {{ release.summary }}
            </p>

            <!-- Change Categories -->
            <div class="mt-6 space-y-4">
              <div v-for="category in release.changes" :key="category.type">
                <div class="flex items-center gap-2">
                  <span
                    class="rounded px-2 py-0.5 text-xs font-semibold"
                    :class="changeBadgeClass(category.type)"
                  >
                    {{ changeLabel(category.type) }}
                  </span>
                </div>
                <ul class="mt-2 space-y-1.5 pl-4">
                  <li
                    v-for="item in category.items"
                    :key="item"
                    class="flex items-start gap-2 text-sm text-neutral-700 dark:text-neutral-300"
                  >
                    <span class="mt-1.5 h-1.5 w-1.5 flex-shrink-0 rounded-full bg-neutral-400 dark:bg-neutral-500"></span>
                    {{ item }}
                  </li>
                </ul>
              </div>
            </div>

            <!-- Divider -->
            <div class="mt-8 border-b border-neutral-200 dark:border-neutral-700"></div>
          </article>
        </div>

        <!-- Subscribe CTA -->
        <div class="mt-16 rounded-2xl bg-neutral-50 p-8 text-center dark:bg-neutral-800">
          <h3 class="text-xl font-bold text-neutral-900 dark:text-white">Будьте в курсе обновлений</h3>
          <p class="mt-2 text-neutral-600 dark:text-neutral-400">
            Подпишитесь на рассылку, чтобы первыми узнавать о новых функциях.
          </p>
          <NuxtLink
            to="/contact"
            class="mt-6 inline-flex items-center gap-2 rounded-xl bg-primary-600 px-6 py-3 text-sm font-semibold text-white shadow-lg transition hover:bg-primary-700"
          >
            Подписаться на обновления
          </NuxtLink>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { DocumentTextIcon } from '@heroicons/vue/24/outline'

type ChangeType = 'added' | 'improved' | 'fixed' | 'security'

interface ChangeCategory {
  type: ChangeType
  items: string[]
}

interface Release {
  version: string
  date: string
  summary?: string
  latest?: boolean
  changes: ChangeCategory[]
}

const releases: Release[] = [
  {
    version: '0.5.0',
    date: '5 февраля 2026',
    summary: 'Публичный фронтенд, Marketing CMS и улучшения UI.',
    latest: true,
    changes: [
      {
        type: 'added',
        items: [
          'Публичный сайт на Nuxt 3 (SSR/SSG) с SEO-оптимизацией',
          'Marketing CMS модуль для управления контентом страниц',
          'Immersive Grid в стиле Google Photos для галереи активов',
          'Компонент GalleryHeaderActions с Teleport',
          'YouTube Analytics интеграция с OAuth2'
        ]
      },
      {
        type: 'improved',
        items: [
          'Рефакторинг FiltersPanel на v-model two-way binding',
          'Централизация логики фильтров в useDamSearchFilters composable',
          'Lazy loading для share links (загрузка по требованию)',
          'Multi-tenancy WebSocket groups для аналитики',
          'Оптимизация notification fetching (предотвращение дубликатов)'
        ]
      },
      {
        type: 'fixed',
        items: [
          'Предотвращение N+1 queries при загрузке активов',
          'Non-fatal error handling в distribution store',
          'Централизация debug telemetry в API service',
          'Исправлена обработка corrupted notifications'
        ]
      }
    ]
  },
  {
    version: '0.4.0',
    date: '15 декабря 2025',
    summary: 'Модуль аналитики и система распространения контента.',
    changes: [
      {
        type: 'added',
        items: [
          'Analytics Module: Asset Bank, Campaign, User Activity, Search, Distribution, Content Intelligence dashboards',
          'Distribution Module: Publications, Renditions, Share Links, Recipient Lists',
          'Real-time обновления через WebSocket (Daphne)',
          'Image Editor с версионированием'
        ]
      },
      {
        type: 'improved',
        items: [
          'Расширенный AI-анализ: категории, люди, локации, доминирующие цвета',
          'Оптимизация полнотекстового поиска через GIN индексы',
          'Улучшенный error handling в Celery tasks'
        ]
      }
    ]
  },
  {
    version: '0.3.0',
    date: '1 октября 2025',
    summary: 'AI-обогащение метаданных и Vue 3 фронтенд.',
    changes: [
      {
        type: 'added',
        items: [
          'DAM Module с AI-анализом через YandexGPT, GigaChat, OpenAI',
          'Vue 3 SPA фронтенд с TypeScript и Pinia',
          'Headless API для фронтенда',
          'Интеграция с Яндекс.Диск для импорта файлов',
          'S3 Storage backend (Beget)'
        ]
      },
      {
        type: 'security',
        items: [
          'Token-based аутентификация (JWT)',
          'Интеграция с RBAC системой Mayan EDMS',
          'CORS и CSRF защита для API'
        ]
      }
    ]
  }
]

const changeBadgeClass = (type: ChangeType) => {
  switch (type) {
    case 'added':
      return 'bg-success/10 text-success'
    case 'improved':
      return 'bg-primary-100 text-primary-700 dark:bg-primary-900/40 dark:text-primary-300'
    case 'fixed':
      return 'bg-warning/10 text-warning-700 dark:text-warning-500'
    case 'security':
      return 'bg-error/10 text-error-700 dark:text-error'
    default:
      return 'bg-neutral-100 text-neutral-600'
  }
}

const changeLabel = (type: ChangeType) => {
  switch (type) {
    case 'added':
      return 'Добавлено'
    case 'improved':
      return 'Улучшено'
    case 'fixed':
      return 'Исправлено'
    case 'security':
      return 'Безопасность'
    default:
      return type
  }
}
</script>
