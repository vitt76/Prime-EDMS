// @ts-nocheck
<template>
  <div class="admin-dashboard space-y-4 sm:space-y-6">
    <!-- Page Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h1 class="text-xl sm:text-2xl font-semibold text-gray-900">Панель управления</h1>
        <p class="text-sm text-gray-600 mt-1">Обзор системы MADDAM</p>
      </div>
      <div class="flex items-center gap-3">
        <!-- Real-time Connection Status -->
        <div class="hidden sm:flex items-center gap-2 px-3 py-1.5 bg-gray-100 rounded-lg">
          <span
            :class="[
              'w-2 h-2 rounded-full',
              isConnected ? 'bg-emerald-500 animate-pulse' : 'bg-gray-400'
            ]"
          />
          <span class="text-xs font-medium text-gray-600">
            {{ isConnected ? 'Live' : 'Offline' }}
          </span>
        </div>
        <span class="hidden md:inline text-sm text-gray-500">
          Обновлено: {{ formatTime(lastUpdated) }}
        </span>
        <button
          type="button"
          class="inline-flex items-center gap-2 px-3 sm:px-4 py-2 bg-white border border-gray-200 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 shadow-sm transition-colors focus:outline-none focus:ring-2 focus:ring-violet-500 focus:ring-offset-2"
          @click="refreshData"
        >
          <svg class="w-4 h-4" :class="{ 'animate-spin': isRefreshing }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          <span class="hidden sm:inline">Обновить</span>
        </button>
      </div>
    </div>

    <!-- ═══════════════════════════════════════════════════════════════════════
         STATS CARDS ROW
         ═══════════════════════════════════════════════════════════════════════ -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
      <!-- Total Assets -->
      <div class="bg-white rounded-xl border border-gray-200 p-4 sm:p-5 shadow-sm hover:shadow-md transition-shadow">
        <div class="flex items-center justify-between">
          <div class="min-w-0">
            <p class="text-xs sm:text-sm font-medium text-gray-500 truncate">Всего активов</p>
            <p class="text-xl sm:text-2xl font-semibold text-gray-900 mt-1">{{ formatNumber(stats.total_assets) }}</p>
          </div>
          <div class="w-10 h-10 sm:w-12 sm:h-12 bg-violet-100 rounded-xl flex items-center justify-center flex-shrink-0">
            <svg class="w-5 h-5 sm:w-6 sm:h-6 text-violet-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          </div>
        </div>
      <div class="mt-3 flex items-center text-xs sm:text-sm">
        <span class="text-emerald-600 font-medium">{{ assetsGrowthLabel }}</span>
        <span class="text-gray-500 ml-2 truncate">за месяц</span>
      </div>
      </div>

      <!-- Total Users -->
      <div class="bg-white rounded-xl border border-gray-200 p-4 sm:p-5 shadow-sm hover:shadow-md transition-shadow">
        <div class="flex items-center justify-between">
          <div class="min-w-0">
            <p class="text-xs sm:text-sm font-medium text-gray-500 truncate">Пользователей</p>
            <p class="text-xl sm:text-2xl font-semibold text-gray-900 mt-1">{{ stats.total_users }}</p>
          </div>
          <div class="w-10 h-10 sm:w-12 sm:h-12 bg-blue-100 rounded-xl flex items-center justify-center flex-shrink-0">
            <svg class="w-5 h-5 sm:w-6 sm:h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
            </svg>
          </div>
        </div>
        <div class="mt-3 flex items-center text-xs sm:text-sm">
          <span class="text-gray-500 truncate">{{ stats.active_users }} активных</span>
          <span class="text-gray-300 mx-2">•</span>
          <span class="text-emerald-600 font-medium">{{ usersGrowthLabel }}</span>
          <span class="text-gray-500 ml-1 truncate">за месяц</span>
        </div>
      </div>

      <!-- Storage Used -->
      <div class="bg-white rounded-xl border border-gray-200 p-4 sm:p-5 shadow-sm hover:shadow-md transition-shadow">
        <div class="flex items-center justify-between">
          <div class="min-w-0">
            <p class="text-xs sm:text-sm font-medium text-gray-500 truncate">Хранилище</p>
            <p class="text-xl sm:text-2xl font-semibold text-gray-900 mt-1">{{ formatBytes(stats.storage_used_bytes) }}</p>
          </div>
          <div class="w-10 h-10 sm:w-12 sm:h-12 bg-amber-100 rounded-xl flex items-center justify-center flex-shrink-0">
            <svg class="w-5 h-5 sm:w-6 sm:h-6 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4" />
            </svg>
          </div>
        </div>
        <div class="mt-3">
          <div class="flex items-center justify-between text-xs sm:text-sm mb-1">
            <span class="text-gray-500">Занято</span>
            <span class="font-medium text-gray-700">{{ storagePercent === null ? '—' : `${storagePercent}%` }}</span>
          </div>
          <div class="h-1.5 sm:h-2 bg-gray-100 rounded-full overflow-hidden">
            <div
              class="h-full bg-amber-500 rounded-full transition-all duration-500"
              :style="{ width: `${storagePercent === null ? 0 : storagePercent}%` }"
            />
          </div>
        </div>
      </div>

      <!-- AI Queue -->
      <div class="bg-white rounded-xl border border-gray-200 p-4 sm:p-5 shadow-sm hover:shadow-md transition-shadow">
        <div class="flex items-center justify-between">
          <div class="min-w-0">
            <p class="text-xs sm:text-sm font-medium text-gray-500 truncate">AI-очередь</p>
            <p class="text-xl sm:text-2xl font-semibold text-gray-900 mt-1">{{ stats.ai_queue.pending + stats.ai_queue.processing }}</p>
          </div>
          <div class="w-10 h-10 sm:w-12 sm:h-12 bg-emerald-100 rounded-xl flex items-center justify-center flex-shrink-0">
            <svg class="w-5 h-5 sm:w-6 sm:h-6 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
          </div>
        </div>
        <div class="mt-3 flex flex-wrap items-center gap-2 sm:gap-4 text-xs sm:text-sm">
          <span class="flex items-center gap-1.5">
            <span class="w-2 h-2 bg-blue-500 rounded-full animate-pulse" />
            <span class="text-gray-500">{{ stats.ai_queue.processing }} в работе</span>
          </span>
          <span v-if="stats.ai_queue.failed > 0" class="flex items-center gap-1.5">
            <span class="w-2 h-2 bg-red-500 rounded-full" />
            <span class="text-red-600 font-medium">{{ stats.ai_queue.failed }} ошибок</span>
          </span>
        </div>
      </div>
    </div>

    <!-- ═══════════════════════════════════════════════════════════════════════
         SYSTEM HEALTH & ACTIVITY
         ═══════════════════════════════════════════════════════════════════════ -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-4 sm:gap-6">
      <!-- System Health -->
      <div class="bg-white rounded-xl border border-gray-200 shadow-sm">
        <div class="px-4 sm:px-5 py-3 sm:py-4 border-b border-gray-100">
          <h2 class="text-sm sm:text-base font-semibold text-gray-900">Состояние системы</h2>
        </div>
        <div class="p-4 sm:p-5 space-y-3 sm:space-y-4">
          <ServiceStatus
            label="База данных"
            :status="stats.system_health.database.status"
            :latency="stats.system_health.database.latency_ms"
          />
          <ServiceStatus
            label="Redis"
            :status="stats.system_health.redis.status"
            :latency="stats.system_health.redis.latency_ms"
          />
          <ServiceStatus
            label="Celery Workers"
            :status="stats.system_health.celery.status"
            :info="`${activeWorkers} активных`"
          />
          <ServiceStatus
            label="Поисковый индекс"
            :status="stats.system_health.search_index.status"
            :latency="stats.system_health.search_index.latency_ms"
          />
          <ServiceStatus
            label="Хранилище"
            :status="stats.system_health.storage.status"
            :info="`${storagePercent}%`"
          />
        </div>
      </div>

      <!-- Activity Feed -->
      <div class="lg:col-span-2 bg-white rounded-xl border border-gray-200 shadow-sm">
        <div class="px-4 sm:px-5 py-3 sm:py-4 border-b border-gray-100 flex items-center justify-between">
          <h2 class="text-sm sm:text-base font-semibold text-gray-900">Последняя активность</h2>
          <router-link
            to="/admin/logs"
            class="text-xs sm:text-sm text-violet-600 hover:text-violet-700 font-medium focus:outline-none focus:underline"
          >
            Все логи →
          </router-link>
        </div>
        <div class="divide-y divide-gray-100 max-h-[300px] sm:max-h-[400px] overflow-y-auto">
          <ActivityItem
            v-for="event in stats.recent_activity"
            :key="event.id"
            :event="event"
          />
          <div v-if="stats.recent_activity.length === 0" class="p-6 sm:p-8 text-center text-gray-500 text-sm">
            Нет недавней активности
          </div>
        </div>
      </div>
    </div>

    <!-- ═══════════════════════════════════════════════════════════════════════
         QUICK ACTIONS
         ═══════════════════════════════════════════════════════════════════════ -->
    <div class="bg-white rounded-xl border border-gray-200 p-4 sm:p-5 shadow-sm">
      <h2 class="text-sm sm:text-base font-semibold text-gray-900 mb-3 sm:mb-4">Быстрые действия</h2>
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-2 sm:gap-3">
        <router-link
          to="/admin/users"
          class="flex flex-col items-center gap-2 p-3 sm:p-4 rounded-xl border border-gray-200 hover:border-violet-300 hover:bg-violet-50 transition-all group focus:outline-none focus:ring-2 focus:ring-violet-500 focus:ring-offset-2"
        >
          <div class="w-9 h-9 sm:w-10 sm:h-10 bg-violet-100 rounded-lg flex items-center justify-center group-hover:bg-violet-200 transition-colors">
            <svg class="w-4 h-4 sm:w-5 sm:h-5 text-violet-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
            </svg>
          </div>
          <span class="text-xs sm:text-sm font-medium text-gray-700 text-center">Пригласить</span>
        </router-link>

        <router-link
          to="/admin/metadata"
          class="flex flex-col items-center gap-2 p-3 sm:p-4 rounded-xl border border-gray-200 hover:border-blue-300 hover:bg-blue-50 transition-all group focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
        >
          <div class="w-9 h-9 sm:w-10 sm:h-10 bg-blue-100 rounded-lg flex items-center justify-center group-hover:bg-blue-200 transition-colors">
            <svg class="w-4 h-4 sm:w-5 sm:h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
          </div>
          <span class="text-xs sm:text-sm font-medium text-gray-700 text-center">Создать схему</span>
        </router-link>

        <router-link
          to="/admin/ai-logs"
          class="flex flex-col items-center gap-2 p-3 sm:p-4 rounded-xl border border-gray-200 hover:border-amber-300 hover:bg-amber-50 transition-all group focus:outline-none focus:ring-2 focus:ring-amber-500 focus:ring-offset-2"
        >
          <div class="w-9 h-9 sm:w-10 sm:h-10 bg-amber-100 rounded-lg flex items-center justify-center group-hover:bg-amber-200 transition-colors">
            <svg class="w-4 h-4 sm:w-5 sm:h-5 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </div>
          <span class="text-xs sm:text-sm font-medium text-gray-700 text-center">Retry AI</span>
        </router-link>

        <router-link
          to="/admin/sources"
          class="flex flex-col items-center gap-2 p-3 sm:p-4 rounded-xl border border-gray-200 hover:border-emerald-300 hover:bg-emerald-50 transition-all group focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2"
        >
          <div class="w-9 h-9 sm:w-10 sm:h-10 bg-emerald-100 rounded-lg flex items-center justify-center group-hover:bg-emerald-200 transition-colors">
            <svg class="w-4 h-4 sm:w-5 sm:h-5 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10" />
            </svg>
          </div>
          <span class="text-xs sm:text-sm font-medium text-gray-700 text-center">Импорт</span>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// @ts-nocheck
import { ref, computed, onMounted, h, watch } from 'vue'
import type { AdminDashboardStats, ActivityEvent, ServiceStatus as ServiceStatusType } from '@/types/admin'
import { useAdminWebSocket } from '@/composables/useAdminWebSocket'
import { apiService } from '@/services/apiService'

// Real-time updates
const { 
  isConnected, 
  connectionStatus, 
  systemStats: wsStats, 
  recentEvents,
  notifications 
} = useAdminWebSocket()

// ═══════════════════════════════════════════════════════════════════════════════
// Sub-components (inline for simplicity)
// ═══════════════════════════════════════════════════════════════════════════════

const ServiceStatus = {
  props: {
    label: String,
    status: String,
    latency: Number,
    info: String
  },
  setup(props: { label: string; status: string; latency?: number; info?: string }) {
    const statusConfig = computed(() => {
      switch (props.status) {
        case 'healthy':
          return { color: 'bg-emerald-500', text: 'text-emerald-600', label: 'OK' }
        case 'degraded':
          return { color: 'bg-amber-500', text: 'text-amber-600', label: 'Медленно' }
        case 'down':
          return { color: 'bg-red-500', text: 'text-red-600', label: 'Ошибка' }
        default:
          return { color: 'bg-gray-400', text: 'text-gray-500', label: '?' }
      }
    })

    return () => h('div', { class: 'flex items-center justify-between py-1' }, [
      h('div', { class: 'flex items-center gap-2 sm:gap-3 min-w-0' }, [
        h('span', { class: `w-2 h-2 sm:w-2.5 sm:h-2.5 rounded-full flex-shrink-0 ${statusConfig.value.color}` }),
        h('span', { class: 'text-xs sm:text-sm text-gray-700 truncate' }, props.label)
      ]),
      h('div', { class: 'flex items-center gap-1 sm:gap-2 flex-shrink-0' }, [
        props.latency !== undefined && h('span', { class: 'text-[10px] sm:text-xs text-gray-400' }, `${props.latency}ms`),
        props.info && h('span', { class: 'text-[10px] sm:text-xs text-gray-400' }, props.info),
        h('span', { class: `text-[10px] sm:text-xs font-medium ${statusConfig.value.text}` }, statusConfig.value.label)
      ])
    ])
  }
}

const ActivityItem = {
  props: {
    event: Object as () => ActivityEvent
  },
  setup(props: { event: ActivityEvent }) {
    const iconConfig = computed(() => {
      switch (props.event.type) {
        case 'document_created':
        case 'document_updated':
          return { bg: 'bg-blue-100', color: 'text-blue-600', icon: 'M9 13h6m-3-3v6m5 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z' }
        case 'document_deleted':
          return { bg: 'bg-red-100', color: 'text-red-600', icon: 'M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16' }
        case 'user_login':
        case 'user_created':
          return { bg: 'bg-emerald-100', color: 'text-emerald-600', icon: 'M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z' }
        case 'import_started':
        case 'import_completed':
          return { bg: 'bg-violet-100', color: 'text-violet-600', icon: 'M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12' }
        case 'ai_analysis_completed':
          return { bg: 'bg-amber-100', color: 'text-amber-600', icon: 'M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z' }
        default:
          return { bg: 'bg-gray-100', color: 'text-gray-600', icon: 'M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z' }
      }
    })

    const formatTime = (iso: string) => {
      const date = new Date(iso)
      const now = new Date()
      const diffMs = now.getTime() - date.getTime()
      const diffMins = Math.floor(diffMs / 60000)
      
      if (diffMins < 1) return 'сейчас'
      if (diffMins < 60) return `${diffMins}м`
      if (diffMins < 1440) return `${Math.floor(diffMins / 60)}ч`
      return date.toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' })
    }

    return () => h('div', { class: 'flex items-start gap-2 sm:gap-3 px-4 sm:px-5 py-3 sm:py-4 hover:bg-gray-50 transition-colors cursor-pointer' }, [
      h('div', { class: `w-7 h-7 sm:w-8 sm:h-8 rounded-lg ${iconConfig.value.bg} flex items-center justify-center flex-shrink-0` }, [
        h('svg', { class: `w-3.5 h-3.5 sm:w-4 sm:h-4 ${iconConfig.value.color}`, fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
          h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: iconConfig.value.icon })
        ])
      ]),
      h('div', { class: 'flex-1 min-w-0' }, [
        h('p', { class: 'text-xs sm:text-sm text-gray-900 line-clamp-2' }, props.event.description),
        h('div', { class: 'flex items-center gap-1.5 sm:gap-2 mt-1' }, [
          h('span', { class: 'text-[10px] sm:text-xs text-gray-500' }, props.event.actor.username),
          h('span', { class: 'text-[10px] sm:text-xs text-gray-300' }, '•'),
          h('span', { class: 'text-[10px] sm:text-xs text-gray-400' }, formatTime(props.event.timestamp))
        ])
      ])
    ])
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// State
// ═══════════════════════════════════════════════════════════════════════════════
const isRefreshing = ref(false)
const lastUpdated = ref(new Date().toISOString())
const assetsGrowthLabel = ref('0%')
const usersGrowthLabel = ref('0%')

// Initial data (will be replaced by real data on mount)
const stats = ref<AdminDashboardStats>({
  total_assets: 0,
  total_users: 0,
  active_users: 0,
  storage_used_bytes: 0,
  storage_total_bytes: 0,
  ai_queue: {
    pending: 0,
    processing: 0,
    failed: 0,
    completed_today: 0
  },
  recent_activity: [],
  system_health: {
    database: { status: 'unknown', latency_ms: 0, last_check: new Date().toISOString() },
    redis: { status: 'unknown', latency_ms: 0, last_check: new Date().toISOString() },
    celery: {
      status: 'unknown',
      workers: [],
      queues: []
    },
    storage: {
      status: 'unknown',
      total_bytes: 0,
      used_bytes: 0,
      free_bytes: 0,
      usage_percent: 0
    },
    search_index: { status: 'unknown', latency_ms: 0, last_check: new Date().toISOString() }
  }
})

type PaginatedResponse<T> = {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

// ═══════════════════════════════════════════════════════════════════════════════
// Computed
// ═══════════════════════════════════════════════════════════════════════════════
const storagePercent = computed(() => {
  const total = Number(stats.value.storage_total_bytes || 0)
  const used = Number(stats.value.storage_used_bytes || 0)
  if (!total || total <= 0) return null
  return Math.round((used / total) * 100)
})

const activeWorkers = computed(() => {
  return stats.value.system_health.celery.workers.filter(w => w.status === 'healthy').length
})

// ═══════════════════════════════════════════════════════════════════════════════
// Methods
// ═══════════════════════════════════════════════════════════════════════════════
function formatNumber(num: number): string {
  return new Intl.NumberFormat('ru-RU').format(num)
}

async function fetchTotalAssetsCount(): Promise<number | null> {
  // "Активы" в текущей системе — это документы Mayan, поэтому предпочитаем документы.
  // Некоторые окружения имеют /assets/ эндпоинт, но он может быть пустым — используем его только как fallback.
  const candidates = [
    '/api/v4/documents/optimized/', // Prime-EDMS optimized documents endpoint
    '/api/v4/documents/', // Mayan standard documents endpoint
    '/api/v4/assets/' // custom DAM endpoint (if available)
  ]

  let bestCount: number | null = null

  for (const url of candidates) {
    try {
      // (debug ingest removed)

      const response = await apiService.get<PaginatedResponse<unknown>>(
        url,
        { params: { page_size: 1 } } as any,
        false
      )

      if (typeof response?.count === 'number') {
        // (debug ingest removed)
        bestCount = bestCount === null ? response.count : Math.max(bestCount, response.count)
        // If we found a non-zero count, we can stop early (real data is present).
        if (response.count > 0) {
          return response.count
        }
      }
    } catch (err) {
      // (debug ingest removed)
    }
  }

  return bestCount
}

async function fetchMonthlyGrowth(): Promise<{ total: number; growth_label: string } | null> {
  try {
    const data = await apiService.get<any>(
      '/api/v4/headless/dashboard/stats/',
      undefined,
      false
    )

    if (typeof data?.documents?.total === 'number') {
      // Update users too (no mocks)
      if (typeof data?.users?.total === 'number') {
        stats.value.total_users = data.users.total
      }
      if (typeof data?.users?.active_total === 'number') {
        stats.value.active_users = data.users.active_total
      }
      usersGrowthLabel.value = String(data?.users?.growth_label ?? '0%')

      // Update storage too (no mocks)
      if (typeof data?.storage?.used_bytes === 'number') {
        stats.value.storage_used_bytes = data.storage.used_bytes
      }
      if (typeof data?.storage?.total_bytes === 'number') {
        stats.value.storage_total_bytes = data.storage.total_bytes
      }

      return {
        total: data.documents.total,
        growth_label: String(data.documents.growth_label ?? '0%')
      }
    }
  } catch {
    // ignore
  }
  return null
}

async function loadRealDashboardStats(): Promise<void> {
  // (debug ingest removed)

  // Prefer headless dashboard stats (includes growth); fallback to count endpoints.
  const dash = await fetchMonthlyGrowth()
  if (dash) {
    stats.value.total_assets = dash.total
    assetsGrowthLabel.value = dash.growth_label
  } else {
    const totalAssets = await fetchTotalAssetsCount()
    if (typeof totalAssets === 'number') {
      stats.value.total_assets = totalAssets
    }
    assetsGrowthLabel.value = '0%'
  }

  lastUpdated.value = new Date().toISOString()
}

function mapVerbCodeToActivityType(verbCode: string): ActivityEvent['type'] {
  const mapping: Record<string, ActivityEvent['type']> = {
    // Documents
    'documents.document_create': 'document_created',
    'documents.document_file_created': 'document_created',
    'documents.document_version_created': 'document_updated',
    'documents.document_properties_edited': 'document_updated',
    'documents.document_file_downloaded': 'document_downloaded',
    'documents.document_deleted': 'document_deleted',
    // Users / auth
    'authentication.user_logged_in': 'user_login',
    'authentication.user_logged_out': 'user_login',
  }
  return mapping[verbCode] || 'document_updated'
}

async function loadRecentActivity(): Promise<void> {
  try {
    // Admin sees all, non-admin falls back server-side to my_documents.
    const data = await apiService.get<any>(
      '/api/v4/headless/activity/feed/',
      { params: { filter: 'all', page_size: 4, important: 1 } } as any,
      false
    )

    const results = Array.isArray(data?.results) ? data.results : []
    stats.value.recent_activity = results.map((item: any) => ({
      id: String(item.id),
      type: mapVerbCodeToActivityType(String(item.verb_code || '')),
      actor: item.actor || { id: null, username: 'system' },
      description: String(item.description || ''),
      metadata: {},
      timestamp: String(item.timestamp || new Date().toISOString())
    }))
  } catch (err) {
    console.warn('[AdminDashboard] Failed to load activity feed', err)
    stats.value.recent_activity = []
  }
}

function formatBytes(bytes: number): string {
  const units = ['B', 'KB', 'MB', 'GB', 'TB']
  let unitIndex = 0
  let size = bytes

  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024
    unitIndex++
  }

  return `${size.toFixed(1)} ${units[unitIndex]}`
}

function formatTime(iso: string): string {
  return new Date(iso).toLocaleTimeString('ru-RU', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

async function refreshData() {
  isRefreshing.value = true
  try {
    await loadRealDashboardStats()
    await loadRecentActivity()
  } finally {
    isRefreshing.value = false
  }
}

onMounted(() => {
  // Initial data load
  loadRealDashboardStats()
  loadRecentActivity()
})

// WebSocket stats are intentionally NOT used to overwrite dashboard numeric KPIs.
// The admin dashboard must be "no mocks" and sources of truth are backend endpoints.
// If we later implement a real WS feed from backend, we can re-enable these with strict validation.

// NOTE: Removed broken watcher referencing undefined `services`.
// This caused the entire dashboard to crash and trip the global ErrorBoundary.

// Do not merge websocket events into dashboard activity feed.
// Dashboard activity is sourced from backend and ACL-filtered.
</script>
