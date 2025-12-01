<template>
  <div class="admin-ai-logs space-y-4 sm:space-y-6">
    <!-- Page Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h1 class="text-xl sm:text-2xl font-semibold text-gray-900">AI-обработка</h1>
        <p class="text-sm text-gray-600 mt-1">Мониторинг задач AI-анализа и OCR</p>
      </div>
      <button
        type="button"
        class="inline-flex items-center justify-center gap-2 px-4 py-2 border border-gray-200 rounded-lg text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 shadow-sm transition-colors focus:outline-none focus:ring-2 focus:ring-violet-500 focus:ring-offset-2 disabled:opacity-50"
        @click="retryAllFailed"
        :disabled="failedTasks.length === 0"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
        <span class="hidden sm:inline">Повторить все</span>
        <span class="sm:hidden">Retry</span>
        ({{ failedTasks.length }})
      </button>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
      <div class="bg-white rounded-xl border border-gray-200 p-3 sm:p-4 shadow-sm">
        <div class="flex items-center gap-2 sm:gap-3">
          <div class="w-9 h-9 sm:w-10 sm:h-10 bg-blue-100 rounded-lg flex items-center justify-center flex-shrink-0">
            <svg class="w-4 h-4 sm:w-5 sm:h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div class="min-w-0">
            <p class="text-xl sm:text-2xl font-semibold text-gray-900">{{ stats.pending }}</p>
            <p class="text-xs sm:text-sm text-gray-500 truncate">В очереди</p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-xl border border-gray-200 p-3 sm:p-4 shadow-sm">
        <div class="flex items-center gap-2 sm:gap-3">
          <div class="w-9 h-9 sm:w-10 sm:h-10 bg-amber-100 rounded-lg flex items-center justify-center flex-shrink-0">
            <svg class="w-4 h-4 sm:w-5 sm:h-5 text-amber-600 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </div>
          <div class="min-w-0">
            <p class="text-xl sm:text-2xl font-semibold text-gray-900">{{ stats.processing }}</p>
            <p class="text-xs sm:text-sm text-gray-500 truncate">В работе</p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-xl border border-gray-200 p-3 sm:p-4 shadow-sm">
        <div class="flex items-center gap-2 sm:gap-3">
          <div class="w-9 h-9 sm:w-10 sm:h-10 bg-emerald-100 rounded-lg flex items-center justify-center flex-shrink-0">
            <svg class="w-4 h-4 sm:w-5 sm:h-5 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div class="min-w-0">
            <p class="text-xl sm:text-2xl font-semibold text-gray-900">{{ stats.completed_today }}</p>
            <p class="text-xs sm:text-sm text-gray-500 truncate">Готово</p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-xl border border-gray-200 p-3 sm:p-4 shadow-sm">
        <div class="flex items-center gap-2 sm:gap-3">
          <div class="w-9 h-9 sm:w-10 sm:h-10 bg-red-100 rounded-lg flex items-center justify-center flex-shrink-0">
            <svg class="w-4 h-4 sm:w-5 sm:h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div class="min-w-0">
            <p class="text-xl sm:text-2xl font-semibold text-gray-900">{{ stats.failed }}</p>
            <p class="text-xs sm:text-sm text-gray-500 truncate">Ошибок</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Provider Status -->
    <div class="bg-white rounded-xl border border-gray-200 shadow-sm">
      <div class="px-4 sm:px-5 py-3 sm:py-4 border-b border-gray-100">
        <h2 class="text-sm sm:text-base font-semibold text-gray-900">AI-провайдеры</h2>
      </div>
      <div class="p-3 sm:p-5 grid grid-cols-2 lg:grid-cols-4 gap-2 sm:gap-4">
        <div
          v-for="provider in providers"
          :key="provider.provider"
          :class="[
            'p-3 sm:p-4 rounded-xl border-2 transition-colors',
            provider.healthy
              ? 'border-emerald-200 bg-emerald-50/50'
              : 'border-red-200 bg-red-50/50'
          ]"
        >
          <div class="flex items-center justify-between mb-2">
            <span class="text-xs sm:text-sm font-medium text-gray-900 truncate">{{ provider.label }}</span>
            <span
              :class="[
                'w-2 h-2 sm:w-2.5 sm:h-2.5 rounded-full flex-shrink-0',
                provider.healthy ? 'bg-emerald-500' : 'bg-red-500'
              ]"
            />
          </div>
          <div class="space-y-0.5 sm:space-y-1 text-[10px] sm:text-xs text-gray-500">
            <p>{{ provider.requests_today }} запр.</p>
            <p>~{{ provider.avg_response_ms }}ms</p>
            <p v-if="provider.errors_today > 0" class="text-red-600 font-medium">
              {{ provider.errors_today }} ошибок
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Tasks Table -->
    <div class="bg-white rounded-xl border border-gray-200 shadow-sm">
      <div class="px-4 sm:px-5 py-3 sm:py-4 border-b border-gray-100">
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
          <h2 class="text-sm sm:text-base font-semibold text-gray-900">Задачи обработки</h2>
          
          <div class="flex items-center gap-2 sm:gap-3">
            <!-- Status Filter -->
            <select
              v-model="statusFilter"
              class="flex-1 sm:flex-none px-2 sm:px-3 py-1.5 sm:py-2 bg-gray-50 border border-gray-200 rounded-lg text-xs sm:text-sm focus:outline-none focus:ring-2 focus:ring-violet-500"
            >
              <option value="">Статус</option>
              <option value="pending">В очереди</option>
              <option value="processing">В работе</option>
              <option value="completed">Готово</option>
              <option value="failed">Ошибка</option>
            </select>

            <!-- Task Type Filter -->
            <select
              v-model="taskTypeFilter"
              class="flex-1 sm:flex-none px-2 sm:px-3 py-1.5 sm:py-2 bg-gray-50 border border-gray-200 rounded-lg text-xs sm:text-sm focus:outline-none focus:ring-2 focus:ring-violet-500"
            >
              <option value="">Тип</option>
              <option value="image_analysis">Изображения</option>
              <option value="ocr">OCR</option>
              <option value="tag_extraction">Теги</option>
              <option value="color_analysis">Цвета</option>
            </select>
          </div>
        </div>
      </div>

      <!-- Desktop Table -->
      <div class="hidden lg:block overflow-x-auto">
        <table class="w-full">
          <thead>
            <tr class="bg-gray-50 border-b border-gray-100">
              <th class="px-5 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                Документ
              </th>
              <th class="px-5 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                Тип
              </th>
              <th class="px-5 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                Провайдер
              </th>
              <th class="px-5 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                Время
              </th>
              <th class="px-5 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                Токены
              </th>
              <th class="px-5 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                Статус
              </th>
              <th class="px-5 py-3 text-right text-xs font-semibold text-gray-500 uppercase tracking-wider">
                
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <tr
              v-for="task in filteredTasks"
              :key="task.id"
              class="hover:bg-gray-50 transition-colors"
            >
              <td class="px-5 py-4">
                <div class="flex items-center gap-3">
                  <div
                    v-if="task.thumbnail_url"
                    class="w-10 h-10 rounded-lg bg-gray-100 overflow-hidden flex-shrink-0 shadow-sm"
                  >
                    <img
                      :src="task.thumbnail_url"
                      :alt="task.document_label"
                      class="w-full h-full object-cover"
                    />
                  </div>
                  <div v-else class="w-10 h-10 rounded-lg bg-gray-100 flex items-center justify-center flex-shrink-0">
                    <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  </div>
                  <div class="min-w-0">
                    <p class="text-sm font-medium text-gray-900 truncate max-w-[200px]">
                      {{ task.document_label }}
                    </p>
                    <p class="text-xs text-gray-500">ID: {{ task.document_id }}</p>
                  </div>
                </div>
              </td>
              <td class="px-5 py-4">
                <span
                  :class="[
                    'inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-medium',
                    taskTypeStyles[task.task_type] || 'bg-gray-100 text-gray-700'
                  ]"
                >
                  {{ taskTypeLabels[task.task_type] || task.task_type }}
                </span>
              </td>
              <td class="px-5 py-4">
                <span class="text-sm text-gray-700">{{ providerLabels[task.provider] || task.provider }}</span>
              </td>
              <td class="px-5 py-4">
                <span v-if="task.duration_ms" class="text-sm text-gray-700">
                  {{ formatDuration(task.duration_ms) }}
                </span>
                <span v-else-if="task.status === 'processing'" class="text-sm text-amber-600">
                  ...
                </span>
                <span v-else class="text-sm text-gray-400">—</span>
              </td>
              <td class="px-5 py-4">
                <div v-if="task.tokens_used" class="text-sm">
                  <span class="text-gray-700">{{ formatNumber(task.tokens_used) }}</span>
                  <span v-if="task.cost_estimate" class="text-gray-400 text-xs ml-1">
                    ${{ task.cost_estimate.toFixed(3) }}
                  </span>
                </div>
                <span v-else class="text-sm text-gray-400">—</span>
              </td>
              <td class="px-5 py-4">
                <span
                  :class="[
                    'inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium',
                    statusStyles[task.status]
                  ]"
                >
                  <span
                    :class="[
                      'w-1.5 h-1.5 rounded-full',
                      task.status === 'completed' ? 'bg-emerald-500' :
                      task.status === 'processing' ? 'bg-amber-500 animate-pulse' :
                      task.status === 'failed' ? 'bg-red-500' : 'bg-blue-500'
                    ]"
                  />
                  {{ statusLabels[task.status] }}
                </span>
              </td>
              <td class="px-5 py-4 text-right">
                <div class="flex items-center justify-end gap-1">
                  <button
                    v-if="task.status === 'failed'"
                    type="button"
                    class="p-2 text-gray-400 hover:text-violet-600 hover:bg-violet-50 rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-violet-500"
                    title="Повторить"
                    @click="retryTask(task)"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                    </svg>
                  </button>
                  <button
                    type="button"
                    class="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-gray-500"
                    title="Детали"
                    @click="showTaskDetails(task)"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                  </button>
                  <button
                    v-if="task.status === 'pending'"
                    type="button"
                    class="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                    title="Отменить"
                    @click="cancelTask(task)"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Mobile Card View -->
      <div class="lg:hidden divide-y divide-gray-100">
        <div
          v-for="task in filteredTasks"
          :key="task.id"
          class="p-4 hover:bg-gray-50 transition-colors"
        >
          <div class="flex items-start gap-3">
            <div
              v-if="task.thumbnail_url"
              class="w-12 h-12 rounded-lg bg-gray-100 overflow-hidden flex-shrink-0 shadow-sm"
            >
              <img
                :src="task.thumbnail_url"
                :alt="task.document_label"
                class="w-full h-full object-cover"
              />
            </div>
            <div v-else class="w-12 h-12 rounded-lg bg-gray-100 flex items-center justify-center flex-shrink-0">
              <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <div class="flex-1 min-w-0">
              <div class="flex items-start justify-between gap-2">
                <p class="text-sm font-medium text-gray-900 truncate">
                  {{ task.document_label }}
                </p>
                <span
                  :class="[
                    'inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-medium flex-shrink-0',
                    statusStyles[task.status]
                  ]"
                >
                  <span
                    :class="[
                      'w-1.5 h-1.5 rounded-full',
                      task.status === 'completed' ? 'bg-emerald-500' :
                      task.status === 'processing' ? 'bg-amber-500 animate-pulse' :
                      task.status === 'failed' ? 'bg-red-500' : 'bg-blue-500'
                    ]"
                  />
                  {{ statusLabels[task.status] }}
                </span>
              </div>
              <div class="flex flex-wrap items-center gap-1.5 mt-1.5 text-xs text-gray-500">
                <span
                  :class="[
                    'inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-medium',
                    taskTypeStyles[task.task_type] || 'bg-gray-100 text-gray-700'
                  ]"
                >
                  {{ taskTypeLabels[task.task_type] || task.task_type }}
                </span>
                <span class="text-gray-300">•</span>
                <span>{{ providerLabels[task.provider] || task.provider }}</span>
                <span v-if="task.duration_ms" class="text-gray-400">
                  {{ formatDuration(task.duration_ms) }}
                </span>
              </div>
              <div v-if="task.error_message" class="mt-2 p-2 bg-red-50 rounded text-xs text-red-600 line-clamp-2">
                {{ task.error_message }}
              </div>
            </div>
          </div>
          <div class="flex items-center justify-end gap-1 mt-3 pt-3 border-t border-gray-100">
            <button
              v-if="task.status === 'failed'"
              type="button"
              class="p-2 text-gray-400 hover:text-violet-600 hover:bg-violet-50 rounded-lg transition-colors"
              @click="retryTask(task)"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
            </button>
            <button
              type="button"
              class="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
              @click="showTaskDetails(task)"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
            </button>
            <button
              v-if="task.status === 'pending'"
              type="button"
              class="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
              @click="cancelTask(task)"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
      </div>

      <div v-if="filteredTasks.length === 0" class="px-4 sm:px-5 py-8 sm:py-12 text-center">
        <svg class="mx-auto w-12 h-12 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
        </svg>
        <p class="mt-4 text-sm text-gray-500">Задачи не найдены</p>
      </div>
    </div>

    <!-- Task Details Modal -->
    <Teleport to="body">
      <div
        v-if="selectedTask"
        class="fixed inset-0 z-50 flex items-center justify-center"
      >
        <div class="absolute inset-0 bg-black/50" @click="selectedTask = null" />
        <div class="relative bg-white rounded-2xl shadow-xl w-full max-w-lg mx-4 max-h-[80vh] overflow-hidden flex flex-col">
          <div class="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
            <h2 class="text-lg font-semibold text-gray-900">Детали задачи</h2>
            <button
              type="button"
              class="p-1.5 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
              @click="selectedTask = null"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          
          <div class="flex-1 overflow-y-auto p-6 space-y-4">
            <div class="grid grid-cols-2 gap-4">
              <div>
                <p class="text-xs text-gray-500 mb-1">ID задачи</p>
                <p class="text-sm font-mono text-gray-900">{{ selectedTask.id }}</p>
              </div>
              <div>
                <p class="text-xs text-gray-500 mb-1">Статус</p>
                <span
                  :class="[
                    'inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium',
                    statusStyles[selectedTask.status]
                  ]"
                >
                  {{ statusLabels[selectedTask.status] }}
                </span>
              </div>
              <div>
                <p class="text-xs text-gray-500 mb-1">Тип</p>
                <p class="text-sm text-gray-900">{{ taskTypeLabels[selectedTask.task_type] }}</p>
              </div>
              <div>
                <p class="text-xs text-gray-500 mb-1">Провайдер</p>
                <p class="text-sm text-gray-900">{{ providerLabels[selectedTask.provider] }}</p>
              </div>
              <div>
                <p class="text-xs text-gray-500 mb-1">Создано</p>
                <p class="text-sm text-gray-900">{{ formatDateTime(selectedTask.created_at) }}</p>
              </div>
              <div>
                <p class="text-xs text-gray-500 mb-1">Попыток</p>
                <p class="text-sm text-gray-900">{{ selectedTask.retries }} / {{ selectedTask.max_retries }}</p>
              </div>
            </div>

            <div v-if="selectedTask.error_message" class="mt-4">
              <p class="text-xs text-gray-500 mb-1">Сообщение об ошибке</p>
              <div class="p-3 bg-red-50 border border-red-200 rounded-lg">
                <p class="text-sm text-red-700 font-mono whitespace-pre-wrap">{{ selectedTask.error_message }}</p>
              </div>
            </div>

            <div v-if="selectedTask.result_summary" class="mt-4">
              <p class="text-xs text-gray-500 mb-1">Результат</p>
              <div class="p-3 bg-gray-50 border border-gray-200 rounded-lg">
                <p class="text-sm text-gray-700">{{ selectedTask.result_summary }}</p>
              </div>
            </div>
          </div>

          <div class="px-6 py-4 border-t border-gray-100 flex justify-end gap-3">
            <button
              type="button"
              class="px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
              @click="selectedTask = null"
            >
              Закрыть
            </button>
            <button
              v-if="selectedTask.status === 'failed'"
              type="button"
              class="px-4 py-2 bg-violet-600 text-white rounded-lg text-sm font-medium hover:bg-violet-700 transition-colors"
              @click="retryTask(selectedTask); selectedTask = null"
            >
              Повторить задачу
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { AITask, AITaskStatus, AITaskType, AIProvider, AIProviderStatus } from '@/types/admin'

// ═══════════════════════════════════════════════════════════════════════════════
// State
// ═══════════════════════════════════════════════════════════════════════════════
const statusFilter = ref('')
const taskTypeFilter = ref('')
const selectedTask = ref<AITask | null>(null)

const statusStyles: Record<AITaskStatus, string> = {
  pending: 'bg-blue-50 text-blue-700',
  processing: 'bg-amber-50 text-amber-700',
  completed: 'bg-emerald-50 text-emerald-700',
  failed: 'bg-red-50 text-red-700',
  cancelled: 'bg-gray-100 text-gray-600'
}

const statusLabels: Record<AITaskStatus, string> = {
  pending: 'В очереди',
  processing: 'Обработка',
  completed: 'Выполнено',
  failed: 'Ошибка',
  cancelled: 'Отменено'
}

const taskTypeStyles: Record<AITaskType, string> = {
  image_analysis: 'bg-violet-100 text-violet-700',
  ocr: 'bg-blue-100 text-blue-700',
  tag_extraction: 'bg-emerald-100 text-emerald-700',
  color_analysis: 'bg-amber-100 text-amber-700',
  face_detection: 'bg-pink-100 text-pink-700',
  content_moderation: 'bg-red-100 text-red-700'
}

const taskTypeLabels: Record<AITaskType, string> = {
  image_analysis: 'Анализ изображения',
  ocr: 'OCR',
  tag_extraction: 'Извлечение тегов',
  color_analysis: 'Анализ цветов',
  face_detection: 'Распознавание лиц',
  content_moderation: 'Модерация контента'
}

const providerLabels: Record<AIProvider, string> = {
  qwenlocal: 'Qwen Local',
  gigachat: 'GigaChat',
  openai: 'OpenAI',
  claude: 'Claude',
  gemini: 'Gemini',
  yandexgpt: 'YandexGPT',
  kieai: 'Kie.ai'
}

// Mock data
const stats = ref({
  pending: 12,
  processing: 3,
  completed_today: 156,
  failed: 2
})

const providers = ref<AIProviderStatus[]>([
  { provider: 'qwenlocal', label: 'Qwen Local', enabled: true, healthy: true, last_check: new Date().toISOString(), requests_today: 89, errors_today: 0, avg_response_ms: 1200 },
  { provider: 'gigachat', label: 'GigaChat', enabled: true, healthy: true, last_check: new Date().toISOString(), requests_today: 45, errors_today: 2, avg_response_ms: 2100 },
  { provider: 'openai', label: 'OpenAI', enabled: false, healthy: false, last_check: new Date().toISOString(), requests_today: 0, errors_today: 0, avg_response_ms: 0 },
  { provider: 'yandexgpt', label: 'YandexGPT', enabled: true, healthy: true, last_check: new Date().toISOString(), requests_today: 22, errors_today: 0, avg_response_ms: 1800 }
])

const tasks = ref<AITask[]>([
  {
    id: 'task-001',
    document_id: 1234,
    document_label: 'product_photo_01.jpg',
    thumbnail_url: 'https://picsum.photos/seed/1/100/100',
    task_type: 'image_analysis',
    provider: 'qwenlocal',
    status: 'completed',
    created_at: new Date(Date.now() - 5 * 60000).toISOString(),
    started_at: new Date(Date.now() - 4 * 60000).toISOString(),
    completed_at: new Date(Date.now() - 3 * 60000).toISOString(),
    duration_ms: 1245,
    tokens_used: 892,
    cost_estimate: 0.0012,
    result_summary: 'Обнаружено: продукт, упаковка, белый фон',
    retries: 0,
    max_retries: 3
  },
  {
    id: 'task-002',
    document_id: 1235,
    document_label: 'contract_2024_final.pdf',
    task_type: 'ocr',
    provider: 'kieai',
    status: 'processing',
    created_at: new Date(Date.now() - 2 * 60000).toISOString(),
    started_at: new Date(Date.now() - 1 * 60000).toISOString(),
    retries: 0,
    max_retries: 3
  },
  {
    id: 'task-003',
    document_id: 1236,
    document_label: 'banner_campaign_winter.png',
    thumbnail_url: 'https://picsum.photos/seed/2/100/100',
    task_type: 'color_analysis',
    provider: 'qwenlocal',
    status: 'pending',
    created_at: new Date(Date.now() - 1 * 60000).toISOString(),
    retries: 0,
    max_retries: 3
  },
  {
    id: 'task-004',
    document_id: 1237,
    document_label: 'team_photo_event.jpg',
    thumbnail_url: 'https://picsum.photos/seed/3/100/100',
    task_type: 'face_detection',
    provider: 'gigachat',
    status: 'failed',
    created_at: new Date(Date.now() - 30 * 60000).toISOString(),
    started_at: new Date(Date.now() - 29 * 60000).toISOString(),
    completed_at: new Date(Date.now() - 28 * 60000).toISOString(),
    duration_ms: 45000,
    error_message: 'Rate limit exceeded. Please retry after 60 seconds.',
    retries: 2,
    max_retries: 3
  },
  {
    id: 'task-005',
    document_id: 1238,
    document_label: 'presentation_q4.pptx',
    task_type: 'tag_extraction',
    provider: 'yandexgpt',
    status: 'completed',
    created_at: new Date(Date.now() - 60 * 60000).toISOString(),
    started_at: new Date(Date.now() - 59 * 60000).toISOString(),
    completed_at: new Date(Date.now() - 58 * 60000).toISOString(),
    duration_ms: 2340,
    tokens_used: 1456,
    cost_estimate: 0.0023,
    result_summary: 'Теги: маркетинг, Q4, отчёт, презентация',
    retries: 0,
    max_retries: 3
  }
])

// ═══════════════════════════════════════════════════════════════════════════════
// Computed
// ═══════════════════════════════════════════════════════════════════════════════
const filteredTasks = computed(() => {
  return tasks.value.filter(task => {
    const matchesStatus = !statusFilter.value || task.status === statusFilter.value
    const matchesType = !taskTypeFilter.value || task.task_type === taskTypeFilter.value
    return matchesStatus && matchesType
  })
})

const failedTasks = computed(() => {
  return tasks.value.filter(t => t.status === 'failed')
})

// ═══════════════════════════════════════════════════════════════════════════════
// Methods
// ═══════════════════════════════════════════════════════════════════════════════
function formatNumber(num: number): string {
  return new Intl.NumberFormat('ru-RU').format(num)
}

function formatDuration(ms: number): string {
  if (ms < 1000) return `${ms}ms`
  if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`
  return `${Math.floor(ms / 60000)}m ${Math.floor((ms % 60000) / 1000)}s`
}

function formatDateTime(iso: string): string {
  return new Date(iso).toLocaleString('ru-RU')
}

function retryTask(task: AITask): void {
  console.log('Retrying task:', task.id)
  task.status = 'pending'
  task.retries++
}

function retryAllFailed(): void {
  failedTasks.value.forEach(task => {
    task.status = 'pending'
    task.retries++
  })
}

function cancelTask(task: AITask): void {
  console.log('Cancelling task:', task.id)
  task.status = 'cancelled'
}

function showTaskDetails(task: AITask): void {
  selectedTask.value = task
}
</script>

