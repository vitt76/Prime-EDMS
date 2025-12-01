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
        <select
          v-model="levelFilter"
          class="px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-violet-500"
        >
          <option value="">Все уровни</option>
          <option value="error">Ошибки</option>
          <option value="warning">Предупреждения</option>
          <option value="info">Информация</option>
          <option value="debug">Отладка</option>
        </select>
        <select
          v-model="appFilter"
          class="px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-violet-500"
        >
          <option value="">Все приложения</option>
          <option value="documents">Документы</option>
          <option value="dam">DAM</option>
          <option value="distribution">Распространение</option>
          <option value="converter">Конвертер</option>
        </select>
      </div>
    </div>

    <!-- Logs Table -->
    <div class="bg-white rounded-xl border border-gray-200">
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead>
            <tr class="bg-gray-50 border-b border-gray-100">
              <th class="px-5 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider w-40">
                Время
              </th>
              <th class="px-5 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider w-24">
                Уровень
              </th>
              <th class="px-5 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider w-32">
                Приложение
              </th>
              <th class="px-5 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                Сообщение
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100 font-mono text-sm">
            <tr
              v-for="log in filteredLogs"
              :key="log.id"
              :class="[
                'hover:bg-gray-50 transition-colors cursor-pointer',
                log.level === 'error' ? 'bg-red-50/50' :
                log.level === 'warning' ? 'bg-amber-50/50' : ''
              ]"
              @click="showLogDetail(log)"
            >
              <td class="px-5 py-3 text-gray-500">
                {{ formatDateTime(log.datetime) }}
              </td>
              <td class="px-5 py-3">
                <span
                  :class="[
                    'inline-flex items-center px-2 py-0.5 rounded text-xs font-medium',
                    levelStyles[log.level]
                  ]"
                >
                  {{ log.level.toUpperCase() }}
                </span>
              </td>
              <td class="px-5 py-3 text-gray-700">
                {{ log.app_label }}
              </td>
              <td class="px-5 py-3 text-gray-900 truncate max-w-md">
                {{ log.message }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="filteredLogs.length === 0" class="px-5 py-12 text-center">
        <svg class="mx-auto w-12 h-12 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        <p class="mt-4 text-sm text-gray-500">Логи не найдены</p>
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
              <span
                :class="[
                  'px-2.5 py-1 rounded text-xs font-medium',
                  levelStyles[selectedLog.level]
                ]"
              >
                {{ selectedLog.level.toUpperCase() }}
              </span>
              <span class="text-sm text-gray-500">{{ selectedLog.app_label }}</span>
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
              <p class="text-sm text-gray-900">{{ selectedLog.message }}</p>
            </div>
            <div v-if="selectedLog.traceback">
              <p class="text-xs text-gray-500 mb-1">Traceback</p>
              <pre class="p-4 bg-gray-900 text-gray-100 rounded-lg text-xs overflow-x-auto">{{ selectedLog.traceback }}</pre>
            </div>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { ErrorLogEntry } from '@/types/admin'

// State
const searchQuery = ref('')
const levelFilter = ref('')
const appFilter = ref('')
const selectedLog = ref<ErrorLogEntry | null>(null)

const levelStyles: Record<string, string> = {
  error: 'bg-red-100 text-red-700',
  warning: 'bg-amber-100 text-amber-700',
  info: 'bg-blue-100 text-blue-700',
  debug: 'bg-gray-100 text-gray-700',
  critical: 'bg-red-200 text-red-800'
}

// Mock logs
const logs = ref<ErrorLogEntry[]>([
  {
    id: 1,
    datetime: new Date(Date.now() - 5 * 60000).toISOString(),
    app_label: 'dam',
    name: 'ai_analysis',
    level: 'error',
    message: 'AI analysis failed for document 1234: Rate limit exceeded',
    traceback: 'Traceback (most recent call last):\n  File "mayan/apps/dam/tasks.py", line 45, in analyze_document\n    result = provider.analyze(image)\n  File "mayan/apps/dam/providers/gigachat.py", line 78, in analyze\n    raise RateLimitError("Rate limit exceeded")\nRateLimitError: Rate limit exceeded'
  },
  {
    id: 2,
    datetime: new Date(Date.now() - 15 * 60000).toISOString(),
    app_label: 'documents',
    name: 'document_upload',
    level: 'info',
    message: 'Document uploaded successfully: product_catalog_2024.pdf'
  },
  {
    id: 3,
    datetime: new Date(Date.now() - 30 * 60000).toISOString(),
    app_label: 'distribution',
    name: 'rendition_generation',
    level: 'warning',
    message: 'Slow rendition generation detected: took 45s for document 5678'
  },
  {
    id: 4,
    datetime: new Date(Date.now() - 60 * 60000).toISOString(),
    app_label: 'converter',
    name: 'pdf_conversion',
    level: 'info',
    message: 'PDF converted to images: 24 pages processed'
  },
  {
    id: 5,
    datetime: new Date(Date.now() - 2 * 3600000).toISOString(),
    app_label: 'dam',
    name: 'yandex_sync',
    level: 'info',
    message: 'Yandex Disk sync completed: 45 new files imported'
  }
])

// Computed
const filteredLogs = computed(() => {
  return logs.value.filter(log => {
    const matchesSearch = !searchQuery.value ||
      log.message.toLowerCase().includes(searchQuery.value.toLowerCase())
    const matchesLevel = !levelFilter.value || log.level === levelFilter.value
    const matchesApp = !appFilter.value || log.app_label === appFilter.value
    return matchesSearch && matchesLevel && matchesApp
  })
})

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

function showLogDetail(log: ErrorLogEntry): void {
  selectedLog.value = log
}
</script>

