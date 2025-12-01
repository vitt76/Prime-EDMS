<template>
  <div class="admin-health space-y-6">
    <!-- Page Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-semibold text-gray-900">Мониторинг системы</h1>
        <p class="text-sm text-gray-500 mt-1">Состояние сервисов и ресурсов</p>
      </div>
      <div class="flex items-center gap-3">
        <span class="text-sm text-gray-500">
          Обновлено: {{ formatTime(lastUpdated) }}
        </span>
        <button
          type="button"
          class="inline-flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
          @click="refreshHealth"
        >
          <svg class="w-4 h-4" :class="{ 'animate-spin': isRefreshing }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Обновить
        </button>
      </div>
    </div>

    <!-- Overall Status -->
    <div
      :class="[
        'rounded-xl border-2 p-6',
        overallHealthy
          ? 'bg-emerald-50 border-emerald-200'
          : 'bg-red-50 border-red-200'
      ]"
    >
      <div class="flex items-center gap-4">
        <div
          :class="[
            'w-16 h-16 rounded-2xl flex items-center justify-center',
            overallHealthy ? 'bg-emerald-100' : 'bg-red-100'
          ]"
        >
          <svg
            v-if="overallHealthy"
            class="w-8 h-8 text-emerald-600"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
          </svg>
          <svg
            v-else
            class="w-8 h-8 text-red-600"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        </div>
        <div>
          <h2
            :class="[
              'text-xl font-semibold',
              overallHealthy ? 'text-emerald-900' : 'text-red-900'
            ]"
          >
            {{ overallHealthy ? 'Все системы работают нормально' : 'Обнаружены проблемы' }}
          </h2>
          <p
            :class="[
              'text-sm mt-1',
              overallHealthy ? 'text-emerald-700' : 'text-red-700'
            ]"
          >
            {{ healthySystems }}/{{ totalSystems }} сервисов в норме
          </p>
        </div>
      </div>
    </div>

    <!-- Services Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <!-- Database -->
      <ServiceCard
        title="База данных (PostgreSQL)"
        :status="health.database.status"
        :latency="health.database.latency_ms"
        icon="database"
      />

      <!-- Redis -->
      <ServiceCard
        title="Redis"
        :status="health.redis.status"
        :latency="health.redis.latency_ms"
        icon="memory"
      />

      <!-- Search Index -->
      <ServiceCard
        title="Поисковый индекс"
        :status="health.search_index.status"
        :latency="health.search_index.latency_ms"
        icon="search"
      />
    </div>

    <!-- Celery Workers -->
    <div class="bg-white rounded-xl border border-gray-200">
      <div class="px-5 py-4 border-b border-gray-100">
        <h2 class="font-semibold text-gray-900">Celery Workers</h2>
      </div>
      <div class="divide-y divide-gray-100">
        <div
          v-for="worker in health.celery.workers"
          :key="worker.name"
          class="px-5 py-4 flex items-center justify-between"
        >
          <div class="flex items-center gap-3">
            <span
              :class="[
                'w-3 h-3 rounded-full',
                worker.status === 'healthy' ? 'bg-emerald-500' :
                worker.status === 'degraded' ? 'bg-amber-500' : 'bg-red-500'
              ]"
            />
            <div>
              <p class="text-sm font-medium text-gray-900">{{ worker.name }}</p>
              <p class="text-xs text-gray-500">
                Последний heartbeat: {{ formatTime(worker.last_heartbeat) }}
              </p>
            </div>
          </div>
          <div class="flex items-center gap-6 text-sm">
            <div class="text-center">
              <p class="font-semibold text-gray-900">{{ worker.active_tasks }}</p>
              <p class="text-xs text-gray-500">активных</p>
            </div>
            <div class="text-center">
              <p class="font-semibold text-gray-900">{{ formatNumber(worker.processed_total) }}</p>
              <p class="text-xs text-gray-500">обработано</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Storage -->
    <div class="bg-white rounded-xl border border-gray-200 p-5">
      <h2 class="font-semibold text-gray-900 mb-4">Хранилище</h2>
      <div class="flex items-center gap-6">
        <div class="flex-1">
          <div class="flex items-center justify-between text-sm mb-2">
            <span class="text-gray-600">Использовано</span>
            <span class="font-medium text-gray-900">
              {{ formatBytes(health.storage.used_bytes) }} / {{ formatBytes(health.storage.total_bytes) }}
            </span>
          </div>
          <div class="h-4 bg-gray-100 rounded-full overflow-hidden">
            <div
              :class="[
                'h-full rounded-full transition-all duration-500',
                health.storage.usage_percent > 90 ? 'bg-red-500' :
                health.storage.usage_percent > 70 ? 'bg-amber-500' : 'bg-emerald-500'
              ]"
              :style="{ width: `${health.storage.usage_percent}%` }"
            />
          </div>
        </div>
        <div class="text-center px-4 border-l border-gray-200">
          <p class="text-3xl font-semibold text-gray-900">{{ health.storage.usage_percent.toFixed(1) }}%</p>
          <p class="text-xs text-gray-500">использовано</p>
        </div>
      </div>
      <div class="mt-4 grid grid-cols-3 gap-4 text-center">
        <div class="p-3 bg-gray-50 rounded-lg">
          <p class="text-lg font-semibold text-gray-900">{{ formatBytes(health.storage.total_bytes) }}</p>
          <p class="text-xs text-gray-500">Всего</p>
        </div>
        <div class="p-3 bg-gray-50 rounded-lg">
          <p class="text-lg font-semibold text-gray-900">{{ formatBytes(health.storage.used_bytes) }}</p>
          <p class="text-xs text-gray-500">Использовано</p>
        </div>
        <div class="p-3 bg-gray-50 rounded-lg">
          <p class="text-lg font-semibold text-emerald-600">{{ formatBytes(health.storage.free_bytes) }}</p>
          <p class="text-xs text-gray-500">Свободно</p>
        </div>
      </div>
    </div>

    <!-- Celery Queues -->
    <div class="bg-white rounded-xl border border-gray-200">
      <div class="px-5 py-4 border-b border-gray-100">
        <h2 class="font-semibold text-gray-900">Очереди задач</h2>
      </div>
      <div class="p-5 grid grid-cols-1 md:grid-cols-3 gap-4">
        <div
          v-for="queue in queues"
          :key="queue.name"
          class="p-4 bg-gray-50 rounded-xl border border-gray-200"
        >
          <div class="flex items-center justify-between mb-3">
            <span class="text-sm font-medium text-gray-900">{{ queue.name }}</span>
            <span
              :class="[
                'w-2.5 h-2.5 rounded-full',
                queue.pending > 100 ? 'bg-amber-500' :
                queue.failed > 0 ? 'bg-red-500' : 'bg-emerald-500'
              ]"
            />
          </div>
          <div class="space-y-2">
            <div class="flex items-center justify-between text-sm">
              <span class="text-gray-500">В очереди:</span>
              <span class="font-medium text-gray-900">{{ queue.pending }}</span>
            </div>
            <div class="flex items-center justify-between text-sm">
              <span class="text-gray-500">Активных:</span>
              <span class="font-medium text-gray-900">{{ queue.active }}</span>
            </div>
            <div class="flex items-center justify-between text-sm">
              <span class="text-gray-500">Ошибок:</span>
              <span :class="queue.failed > 0 ? 'font-medium text-red-600' : 'text-gray-900'">
                {{ queue.failed }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, h } from 'vue'
import type { SystemHealth, ServiceStatus } from '@/types/admin'

// ═══════════════════════════════════════════════════════════════════════════════
// Sub-components
// ═══════════════════════════════════════════════════════════════════════════════
const ServiceCard = {
  props: {
    title: String,
    status: String,
    latency: Number,
    icon: String
  },
  setup(props: { title: string; status: ServiceStatus; latency?: number; icon: string }) {
    const statusConfig = computed(() => {
      switch (props.status) {
        case 'healthy':
          return { bg: 'bg-emerald-50', border: 'border-emerald-200', dot: 'bg-emerald-500', text: 'text-emerald-700', label: 'Работает' }
        case 'degraded':
          return { bg: 'bg-amber-50', border: 'border-amber-200', dot: 'bg-amber-500', text: 'text-amber-700', label: 'Замедление' }
        case 'down':
          return { bg: 'bg-red-50', border: 'border-red-200', dot: 'bg-red-500', text: 'text-red-700', label: 'Недоступен' }
        default:
          return { bg: 'bg-gray-50', border: 'border-gray-200', dot: 'bg-gray-400', text: 'text-gray-600', label: 'Неизвестно' }
      }
    })

    const iconPath = computed(() => {
      switch (props.icon) {
        case 'database':
          return 'M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4'
        case 'memory':
          return 'M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z'
        case 'search':
          return 'M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z'
        default:
          return 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z'
      }
    })

    return () => h('div', {
      class: `p-5 rounded-xl border-2 ${statusConfig.value.bg} ${statusConfig.value.border}`
    }, [
      h('div', { class: 'flex items-center justify-between mb-3' }, [
        h('span', { class: `w-3 h-3 rounded-full ${statusConfig.value.dot}` }),
        h('span', { class: `text-xs font-medium ${statusConfig.value.text}` }, statusConfig.value.label)
      ]),
      h('div', { class: 'flex items-center gap-3' }, [
        h('svg', { class: 'w-8 h-8 text-gray-400', fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
          h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '1.5', d: iconPath.value })
        ]),
        h('div', {}, [
          h('p', { class: 'text-sm font-medium text-gray-900' }, props.title),
          props.latency !== undefined && h('p', { class: 'text-xs text-gray-500' }, `Latency: ${props.latency}ms`)
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

const health = ref<SystemHealth>({
  database: { status: 'healthy', latency_ms: 12, last_check: new Date().toISOString() },
  redis: { status: 'healthy', latency_ms: 2, last_check: new Date().toISOString() },
  celery: {
    status: 'healthy',
    workers: [
      { name: 'celery@worker-documents-1', status: 'healthy', active_tasks: 3, processed_total: 12450, last_heartbeat: new Date().toISOString() },
      { name: 'celery@worker-documents-2', status: 'healthy', active_tasks: 2, processed_total: 11890, last_heartbeat: new Date().toISOString() },
      { name: 'celery@worker-converter-1', status: 'healthy', active_tasks: 1, processed_total: 8234, last_heartbeat: new Date().toISOString() },
      { name: 'celery@worker-distribution-1', status: 'healthy', active_tasks: 0, processed_total: 3421, last_heartbeat: new Date().toISOString() }
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
})

const queues = ref([
  { name: 'documents', pending: 12, active: 5, failed: 0 },
  { name: 'converter', pending: 3, active: 1, failed: 0 },
  { name: 'distribution', pending: 0, active: 0, failed: 0 }
])

// ═══════════════════════════════════════════════════════════════════════════════
// Computed
// ═══════════════════════════════════════════════════════════════════════════════
const totalSystems = computed(() => 5) // database, redis, celery, storage, search

const healthySystems = computed(() => {
  let count = 0
  if (health.value.database.status === 'healthy') count++
  if (health.value.redis.status === 'healthy') count++
  if (health.value.celery.status === 'healthy') count++
  if (health.value.storage.status === 'healthy') count++
  if (health.value.search_index.status === 'healthy') count++
  return count
})

const overallHealthy = computed(() => healthySystems.value === totalSystems.value)

// ═══════════════════════════════════════════════════════════════════════════════
// Methods
// ═══════════════════════════════════════════════════════════════════════════════
function formatTime(iso: string): string {
  return new Date(iso).toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
}

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

async function refreshHealth() {
  isRefreshing.value = true
  await new Promise(resolve => setTimeout(resolve, 1000))
  lastUpdated.value = new Date().toISOString()
  isRefreshing.value = false
}
</script>

