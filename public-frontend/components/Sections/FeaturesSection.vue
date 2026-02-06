<template>
  <section id="features" class="mx-auto max-w-container px-4 py-20 lg:py-28">
    <!-- Section Header -->
    <div class="mx-auto max-w-2xl text-center">
      <div class="inline-flex items-center gap-2 rounded-full bg-primary-100 px-4 py-1.5 text-sm font-medium text-primary-700">
        <CubeTransparentIcon class="h-4 w-4" />
        <span>{{ sectionBadge }}</span>
      </div>
      <h2 class="mt-4 text-3xl font-bold tracking-tight text-neutral-900 md:text-4xl">
        {{ title }}
      </h2>
      <p class="mt-4 text-lg leading-relaxed text-neutral-600">
        {{ subtitle }}
      </p>
    </div>

    <!-- Features Grid -->
    <div class="mt-16 grid gap-6 md:grid-cols-2 lg:grid-cols-4">
      <div 
        v-for="(item, idx) in featuresData" 
        :key="idx"
        class="group relative overflow-hidden rounded-2xl bg-white p-6 shadow-sm ring-1 ring-neutral-200/80 transition-all duration-300 hover:-translate-y-1 hover:shadow-xl hover:ring-primary-200"
      >
        <!-- Icon -->
        <div class="mb-5 inline-flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-primary-100 to-primary-50 text-primary-600 transition-transform duration-300 group-hover:scale-110">
          <component :is="item.icon" class="h-6 w-6" />
        </div>

        <!-- Content -->
        <h3 class="text-lg font-semibold text-neutral-900">{{ item.title }}</h3>
        <p class="mt-2 text-sm leading-relaxed text-neutral-600">{{ item.description }}</p>

        <!-- Hover Indicator -->
        <div class="absolute inset-x-0 bottom-0 h-1 origin-left scale-x-0 bg-gradient-to-r from-primary-500 to-primary-600 transition-transform duration-300 group-hover:scale-x-100"></div>
      </div>
    </div>

    <!-- Optional: Feature Highlights -->
    <div v-if="showHighlights" class="mt-20 rounded-2xl bg-gradient-to-br from-primary-600 to-primary-700 p-8 text-white md:p-12">
      <div class="grid gap-8 md:grid-cols-3">
        <div v-for="stat in statsData" :key="stat.label" class="text-center">
          <div class="text-4xl font-bold md:text-5xl">{{ stat.value }}</div>
          <div class="mt-2 text-sm text-primary-100">{{ stat.label }}</div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { 
  MagnifyingGlassIcon, 
  UsersIcon, 
  ChartBarIcon, 
  GlobeAltIcon,
  CubeTransparentIcon,
  ShieldCheckIcon,
  BoltIcon,
  CloudArrowUpIcon
} from '@heroicons/vue/24/outline'
import type { Component } from 'vue'

interface FeatureItem {
  icon: Component
  title: string
  description: string
}

interface StatItem {
  value: string
  label: string
}

const props = withDefaults(
  defineProps<{
    title?: string
    subtitle?: string
    sectionBadge?: string
    items?: FeatureItem[]
    showHighlights?: boolean
  }>(),
  {
    title: 'Почему выбирают MADDAM',
    subtitle: 'Все инструменты для эффективного управления контентом в одном месте',
    sectionBadge: 'Возможности',
    showHighlights: true
  }
)

// Default features if not provided
const defaultFeatures: FeatureItem[] = [
  {
    icon: MagnifyingGlassIcon,
    title: 'AI Search',
    description: 'Найдите нужный файл за секунды с помощью умного поиска по содержимому и метаданным'
  },
  {
    icon: UsersIcon,
    title: 'Командная работа',
    description: 'Приглашайте коллег, настраивайте права доступа и работайте над проектами вместе'
  },
  {
    icon: ChartBarIcon,
    title: 'Аналитика',
    description: 'Отслеживайте использование контента, популярность файлов и эффективность команды'
  },
  {
    icon: GlobeAltIcon,
    title: 'CDN дистрибуция',
    description: 'Мгновенная доставка контента по всему миру через глобальную сеть серверов'
  }
]

const featuresData = computed(() => props.items || defaultFeatures)

const statsData: StatItem[] = [
  { value: '10M+', label: 'Файлов обработано' },
  { value: '99.9%', label: 'Uptime SLA' },
  { value: '<100ms', label: 'Время отклика API' }
]
</script>
