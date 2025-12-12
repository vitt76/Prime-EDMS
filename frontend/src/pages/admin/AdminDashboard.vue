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
          <span class="text-emerald-600 font-medium">+12%</span>
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
            <span class="font-medium text-gray-700">{{ storagePercent }}%</span>
          </div>
          <div class="h-1.5 sm:h-2 bg-gray-100 rounded-full overflow-hidden">
            <div
              class="h-full bg-amber-500 rounded-full transition-all duration-500"
              :style="{ width: `${storagePercent}%` }"
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

// Mock data
const stats = ref<AdminDashboardStats>({
  total_assets: 15847,
  total_users: 24,
  active_users: 8,
  storage_used_bytes: 128_000_000_000,
  storage_total_bytes: 500_000_000_000,
  ai_queue: {
    pending: 12,
    processing: 3,
    failed: 2,
    completed_today: 156
  },
  recent_activity: [
    {
      id: '1',
      type: 'document_created',
      actor: { id: 1, username: 'admin' },
      description: 'Загружено 45 новых файлов в папку "Маркетинг Q4"',
      metadata: {},
      timestamp: new Date(Date.now() - 5 * 60000).toISOString()
    },
    {
      id: '2',
      type: 'user_created',
      actor: { id: 1, username: 'admin' },
      description: 'Приглашён новый пользователь maria@company.ru',
      metadata: {},
      timestamp: new Date(Date.now() - 25 * 60000).toISOString()
    },
    {
      id: '3',
      type: 'import_completed',
      actor: { id: 2, username: 'system' },
      description: 'Импорт из Яндекс.Диска завершён: 234 файла',
      metadata: {},
      timestamp: new Date(Date.now() - 2 * 3600000).toISOString()
    },
    {
      id: '4',
      type: 'ai_analysis_completed',
      actor: { id: 2, username: 'system' },
      description: 'AI-анализ завершён для 89 изображений',
      metadata: {},
      timestamp: new Date(Date.now() - 4 * 3600000).toISOString()
    },
    {
      id: '5',
      type: 'document_deleted',
      actor: { id: 3, username: 'editor' },
      description: 'Удалено 12 устаревших документов',
      metadata: {},
      timestamp: new Date(Date.now() - 24 * 3600000).toISOString()
    }
  ],
  system_health: {
    database: { status: 'healthy', latency_ms: 12, last_check: new Date().toISOString() },
    redis: { status: 'healthy', latency_ms: 2, last_check: new Date().toISOString() },
    celery: {
      status: 'healthy',
      workers: [
        { name: 'worker_a', status: 'healthy', active_tasks: 3, processed_total: 12450, last_heartbeat: new Date().toISOString() },
        { name: 'worker_b', status: 'healthy', active_tasks: 2, processed_total: 11890, last_heartbeat: new Date().toISOString() }
      ],
      queues: []
    },
    storage: {
      status: 'healthy',
      total_bytes: 500_000_000_000,
      used_bytes: 128_000_000_000,
      free_bytes: 372_000_000_000,
      usage_percent: 25.6
    },
    search_index: { status: 'healthy', latency_ms: 45, last_check: new Date().toISOString() }
  }
})

// ═══════════════════════════════════════════════════════════════════════════════
// Computed
// ═══════════════════════════════════════════════════════════════════════════════
const storagePercent = computed(() => {
  return Math.round((stats.value.storage_used_bytes / stats.value.storage_total_bytes) * 100)
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
  await new Promise(resolve => setTimeout(resolve, 1000))
  lastUpdated.value = new Date().toISOString()
  isRefreshing.value = false
}

onMounted(() => {
  // Initial data load
})

// Watch WebSocket data for real-time updates
watch(() => wsStats.activeUsers, (val) => {
  stats.value.active_users = val
})

watch(() => wsStats.aiQueueSize, (val) => {
  stats.value.ai_queue_size = val
})

watch(() => wsStats.storageUsedPercent, (val) => {
  stats.value.storage_used_percent = parseFloat(val.toFixed(1))
})

watch(() => wsStats.cpuUsage, () => {
  // Update services status based on CPU usage
  if (wsStats.cpuUsage > 80) {
    const web = services.value.find(s => s.label === 'Web Server')
    if (web) web.status = 'degraded'
  }
})

// Merge WebSocket events with existing activity
watch(recentEvents, (events) => {
  if (events.length > 0 && events[0]) {
    const latestEvent = events[0]
    const newActivity: ActivityEvent = {
      id: latestEvent.id,
      type: mapEventType(latestEvent.type),
      description: latestEvent.description,
      actor: latestEvent.actor || 'System',
      timestamp: latestEvent.timestamp
    }
    // Add to beginning and keep max 20 items
    stats.value.recent_activity.unshift(newActivity)
    if (stats.value.recent_activity.length > 20) {
      stats.value.recent_activity.pop()
    }
  }
}, { deep: true })

function mapEventType(wsType: string): ActivityEvent['type'] {
  const mapping: Record<string, ActivityEvent['type']> = {
    'user_login': 'user_login',
    'document_upload': 'document_created',
    'ai_completed': 'ai_analysis_completed',
    'storage_warning': 'document_deleted',
    'system_update': 'import_completed'
  }
  return mapping[wsType] || 'document_created'
}
</script>
