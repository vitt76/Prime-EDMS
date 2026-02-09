<template>
  <div>
    <SEOPageMeta
      title="Roadmap | MADDAM"
      description="План развития MADDAM — функции, над которыми мы работаем и что планируем."
    />

    <!-- Hero -->
    <section class="bg-gradient-to-b from-primary-50 to-white py-16 lg:py-20 dark:from-neutral-900 dark:to-neutral-950">
      <div class="mx-auto max-w-container px-4 text-center">
        <div class="inline-flex items-center gap-2 rounded-full bg-primary-100 px-4 py-1.5 text-sm font-medium text-primary-700 dark:bg-primary-900/40 dark:text-primary-300">
          <MapIcon class="h-4 w-4" />
          <span>Roadmap</span>
        </div>
        <h1 class="mt-6 text-4xl font-bold tracking-tight text-neutral-900 md:text-5xl dark:text-white">
          План развития продукта
        </h1>
        <p class="mx-auto mt-4 max-w-2xl text-lg text-neutral-600 dark:text-neutral-400">
          Мы открыто делимся тем, над чем работаем и что планируем. Ваши отзывы помогают нам расставить приоритеты.
        </p>
      </div>
    </section>

    <!-- Timeline -->
    <section class="py-16 lg:py-20">
      <div class="mx-auto max-w-3xl px-4">
        <div class="space-y-12">
          <div v-for="(quarter, idx) in roadmapData" :key="idx">
            <!-- Quarter Header -->
            <div class="flex items-center gap-4">
              <div
                class="flex h-10 w-10 items-center justify-center rounded-full text-sm font-bold"
                :class="quarterBadgeClass(quarter.status)"
              >
                <CheckIcon v-if="quarter.status === 'done'" class="h-5 w-5" />
                <ArrowPathIcon v-else-if="quarter.status === 'in-progress'" class="h-5 w-5" />
                <ClockIcon v-else class="h-5 w-5" />
              </div>
              <div>
                <h2 class="text-xl font-bold text-neutral-900 dark:text-white">{{ quarter.title }}</h2>
                <span
                  class="text-sm font-medium"
                  :class="statusTextClass(quarter.status)"
                >
                  {{ statusLabel(quarter.status) }}
                </span>
              </div>
            </div>

            <!-- Features -->
            <div class="ml-5 border-l-2 border-neutral-200 pl-9 dark:border-neutral-700">
              <ul class="space-y-4">
                <li
                  v-for="feature in quarter.features"
                  :key="feature"
                  class="flex items-start gap-3"
                >
                  <span
                    class="mt-1.5 h-2 w-2 flex-shrink-0 rounded-full"
                    :class="dotClass(quarter.status)"
                  ></span>
                  <span class="text-neutral-700 dark:text-neutral-300">{{ feature }}</span>
                </li>
              </ul>
            </div>
          </div>
        </div>

        <!-- Feedback CTA -->
        <div class="mt-16 rounded-2xl bg-primary-50 p-8 text-center dark:bg-primary-900/20">
          <h3 class="text-xl font-bold text-neutral-900 dark:text-white">Хотите повлиять на Roadmap?</h3>
          <p class="mt-2 text-neutral-600 dark:text-neutral-400">
            Мы всегда открыты к обратной связи. Расскажите нам, какие функции для вас приоритетны.
          </p>
          <NuxtLink
            to="/contact"
            class="mt-6 inline-flex items-center gap-2 rounded-xl bg-primary-600 px-6 py-3 text-sm font-semibold text-white shadow-lg transition hover:bg-primary-700"
          >
            Оставить пожелание
            <ArrowRightIcon class="h-4 w-4" />
          </NuxtLink>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import {
  MapIcon,
  CheckIcon,
  ArrowPathIcon,
  ClockIcon,
  ArrowRightIcon
} from '@heroicons/vue/24/outline'

type QuarterStatus = 'done' | 'in-progress' | 'planned'

interface RoadmapQuarter {
  title: string
  status: QuarterStatus
  features: string[]
}

const roadmapData: RoadmapQuarter[] = [
  {
    title: 'Q4 2025 — Фундамент',
    status: 'done',
    features: [
      'AI-обогащение метаданных (YandexGPT, GigaChat, OpenAI)',
      'Модуль аналитики (Asset Bank, Campaign Performance, Search Analytics)',
      'Система распространения контента (Publications, Share Links)',
      'Публичный сайт на Nuxt 3 с SEO-оптимизацией',
      'Marketing CMS модуль для управления контентом'
    ]
  },
  {
    title: 'Q1 2026 — AI и UX',
    status: 'in-progress',
    features: [
      'Immersive Grid в стиле Google Photos / Pinterest',
      'Расширенный поиск с фасетными фильтрами',
      'Claude и Gemini AI-провайдеры',
      'YouTube Analytics интеграция',
      'Оптимизация производительности для больших коллекций'
    ]
  },
  {
    title: 'Q2 2026 — Multi-tenancy',
    status: 'planned',
    features: [
      'Multi-tenancy архитектура (SaaS и Standalone режимы)',
      'Модуль Organizations с тарифными планами',
      'Кастомные домены для SaaS-клиентов',
      'Биллинг и управление подписками',
      'Миграция данных к tenant-aware моделям'
    ]
  },
  {
    title: 'Q3-Q4 2026 — Масштабирование',
    status: 'planned',
    features: [
      'Мобильное приложение (PWA)',
      'Predictive Analytics и AI-рекомендации',
      'Расширенные интеграции (Slack, Teams, n8n)',
      'Video Intelligence (распознавание сцен)',
      'White-label решение для партнёров'
    ]
  }
]

const quarterBadgeClass = (status: QuarterStatus) => {
  switch (status) {
    case 'done':
      return 'bg-success/10 text-success'
    case 'in-progress':
      return 'bg-primary-100 text-primary-600 dark:bg-primary-900/40 dark:text-primary-400'
    default:
      return 'bg-neutral-100 text-neutral-500 dark:bg-neutral-800 dark:text-neutral-400'
  }
}

const statusTextClass = (status: QuarterStatus) => {
  switch (status) {
    case 'done':
      return 'text-success'
    case 'in-progress':
      return 'text-primary-600 dark:text-primary-400'
    default:
      return 'text-neutral-500 dark:text-neutral-400'
  }
}

const statusLabel = (status: QuarterStatus) => {
  switch (status) {
    case 'done':
      return 'Завершено'
    case 'in-progress':
      return 'В работе'
    default:
      return 'Планируется'
  }
}

const dotClass = (status: QuarterStatus) => {
  switch (status) {
    case 'done':
      return 'bg-success'
    case 'in-progress':
      return 'bg-primary-500'
    default:
      return 'bg-neutral-300 dark:bg-neutral-600'
  }
}
</script>
