<template>
  <div class="admin-logs space-y-6">
    <!-- Page Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-semibold text-gray-900">Системные логи</h1>
        <p class="text-sm text-gray-500 mt-1">История событий и ошибок</p>
      </div>
      <div class="flex items-center gap-3">
        <button
          type="button"
          class="inline-flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
          Экспорт
        </button>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white rounded-xl border border-gray-200 p-4">
      <div class="flex flex-wrap items-center gap-4">
        <div class="flex-1 min-w-[200px]">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Поиск в логах..."
            class="w-full px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-violet-500"
          />
        </div>
        <label class="inline-flex items-center gap-2 text-sm text-gray-700 cursor-pointer select-none">
          <input v-model="showSystemEvents" type="checkbox" class="rounded border-gray-300 text-violet-600 focus:ring-violet-500" />
          Показывать системные события
        </label>
        <div class="text-sm text-gray-500">
          Всего: {{ totalCount }}
        </div>
      </div>
    </div>

    <!-- Logs Table -->
    <div class="bg-white rounded-xl border border-gray-200">
      <div v-if="loadError" class="px-5 py-4 border-b border-gray-100">
        <div class="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800">
          {{ loadError }}
        </div>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead>
            <tr class="bg-gray-50 border-b border-gray-100">
              <th class="px-5 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider w-40">
                Время
              </th>
              <th class="px-5 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider w-32">
                Пользователь
              </th>
              <th class="px-5 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                Событие
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100 text-sm">
            <tr
              v-for="log in filteredLogs"
              :key="log.id"
              class="hover:bg-gray-50 transition-colors cursor-pointer"
              @click="showLogDetail(log)"
            >
              <td class="px-5 py-3 text-gray-500">
                {{ formatDateTime(log.datetime) }}
              </td>
              <td class="px-5 py-3 text-gray-700 font-mono">
                {{ log.actor?.full_name || log.actor?.username || 'Система' }}
              </td>
              <td class="px-5 py-3 text-gray-900">
                <div class="font-medium">{{ log.description }}</div>
                <div class="text-xs text-gray-500 font-mono mt-0.5">
                  {{ log.verb_code }}<span v-if="log.target?.label"> • {{ log.target.label }}</span>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="filteredLogs.length === 0" class="px-5 py-12 text-center">
        <svg class="mx-auto w-12 h-12 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        <p class="mt-4 text-sm text-gray-500">
          {{ loadError ? 'Не удалось загрузить логи' : 'Логи не найдены' }}
        </p>
      </div>
    </div>

    <!-- Pagination -->
    <div class="flex items-center justify-between">
      <div class="text-sm text-gray-500">
        Страница {{ currentPage }} из {{ totalPages }}
      </div>
      <div class="flex items-center gap-2">
        <button
          type="button"
          class="px-3 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          :disabled="!canGoPrev || isLoading"
          @click="handlePrevPage"
        >
          Назад
        </button>
        <button
          type="button"
          class="px-3 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          :disabled="!canGoNext || isLoading"
          @click="handleNextPage"
        >
          Вперёд
        </button>
      </div>
    </div>

    <!-- Log Detail Modal -->
    <Teleport to="body">
      <div
        v-if="selectedLog"
        class="fixed inset-0 z-50 flex items-center justify-center"
      >
        <div class="absolute inset-0 bg-black/50" @click="selectedLog = null" />
        <div class="relative bg-white rounded-2xl shadow-xl w-full max-w-2xl mx-4 max-h-[80vh] overflow-hidden flex flex-col">
          <div class="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
            <div class="flex items-center gap-3">
              <span class="text-sm text-gray-500 font-mono">{{ selectedLog.actor?.full_name || selectedLog.actor?.username || 'Система' }}</span>
              <span class="text-sm text-gray-300">•</span>
              <span class="text-sm text-gray-500 font-mono">{{ selectedLog.verb_code }}</span>
            </div>
            <button
              type="button"
              class="p-1.5 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
              @click="selectedLog = null"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          
          <div class="flex-1 overflow-y-auto p-6">
            <div class="mb-4">
              <p class="text-xs text-gray-500 mb-1">Время</p>
              <p class="text-sm font-mono text-gray-900">{{ formatDateTime(selectedLog.datetime) }}</p>
            </div>
            <div class="mb-4">
              <p class="text-xs text-gray-500 mb-1">Сообщение</p>
              <p class="text-sm text-gray-900">{{ selectedLog.description }}</p>
            </div>
            <div v-if="selectedLog.target?.label">
              <p class="text-xs text-gray-500 mb-1">Объект</p>
              <p class="text-sm text-gray-900">{{ selectedLog.target.label }}</p>
            </div>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { apiService } from '@/services/apiService'

// State
const searchQuery = ref('')
const selectedLog = ref<ActivityLogEntry | null>(null)
const currentPage = ref(1)
const pageSize = ref(50)
const totalCount = ref(0)
const totalPages = ref(1)
const isLoading = ref(false)
const showSystemEvents = ref(false)
const loadError = ref<string>('')

type ActivityActor = {
  id: number | null
  username: string
  full_name?: string
}

type ActivityTarget = {
  id: number
  type: string
  label: string
  url?: string | null
}

type ActivityLogEntry = {
  id: number
  datetime: string
  actor: ActivityActor
  verb_code: string
  verb: string
  target?: ActivityTarget | null
  description: string
}

type ActivityFeedResponse = {
  count: number
  page: number
  page_size: number
  total_pages: number
  results: Array<{
    id: number
    timestamp: string
    actor: ActivityActor
    verb: string
    verb_code: string
    target?: ActivityTarget | null
    description: string
  }>
}

const logs = ref<ActivityLogEntry[]>([])

async function loadLogs(page = 1): Promise<void> {
  isLoading.value = true
  loadError.value = ''
  try {
    const data = await apiService.get<ActivityFeedResponse>(
      '/api/v4/headless/admin/logs/',
      {
        params: {
          page,
          page_size: pageSize.value,
          // Default (toggle OFF): show only meaningful events and hide system noise.
          // Toggle ON: show everything (including system/technical events).
          important: showSystemEvents.value ? 0 : 1,
          system: showSystemEvents.value ? 1 : 0
        }
      } as any,
      false
    )

    totalCount.value = data.count || 0
    currentPage.value = data.page || page
    totalPages.value = data.total_pages || 1
    logs.value = (data.results || []).map((r) => ({
      id: r.id,
      datetime: r.timestamp,
      actor: r.actor,
      verb: r.verb,
      verb_code: r.verb_code,
      target: r.target || null,
      description: r.description
    }))
  } catch (err) {
    console.warn('[AdminLogs] Failed to load activity logs', err)
    totalCount.value = 0
    logs.value = []
    const anyErr = err as any
    const status = anyErr?.response?.status ?? anyErr?.details?.status
    if (status === 401 || status === 403) {
      loadError.value = 'Недостаточно прав для просмотра системных логов.'
    } else if (status === 404) {
      loadError.value = 'Endpoint системных логов недоступен (404). Проверьте, что бэкенд перезапущен и URL зарегистрирован.'
    } else {
      loadError.value = 'Ошибка загрузки логов.'
    }
  } finally {
    isLoading.value = false
  }
}

// Computed
const filteredLogs = computed(() => {
  return logs.value.filter(log => {
    const q = searchQuery.value.trim().toLowerCase()
    if (!q) return true
    return (
      log.description.toLowerCase().includes(q) ||
      log.verb_code.toLowerCase().includes(q) ||
      (log.actor?.username || '').toLowerCase().includes(q) ||
      (log.target?.label || '').toLowerCase().includes(q)
    )
  })
})

const canGoPrev = computed(() => currentPage.value > 1)
const canGoNext = computed(() => currentPage.value < totalPages.value)

function handlePrevPage(): void {
  if (!canGoPrev.value || isLoading.value) return
  loadLogs(currentPage.value - 1)
}

function handleNextPage(): void {
  if (!canGoNext.value || isLoading.value) return
  loadLogs(currentPage.value + 1)
}

// Methods
function formatDateTime(iso: string): string {
  return new Date(iso).toLocaleString('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

function showLogDetail(log: ActivityLogEntry): void {
  selectedLog.value = log
}

watch(pageSize, () => loadLogs(1))
watch(showSystemEvents, () => loadLogs(1))
onMounted(() => loadLogs(1))
</script>

