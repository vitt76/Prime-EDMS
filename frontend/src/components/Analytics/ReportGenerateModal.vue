<template>
  <Modal :is-open="isOpen" title="Сформировать отчёт" @close="handleClose">
    <div class="space-y-4">
      <div v-if="!reportTaskId" class="space-y-4">
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-neutral-700 mb-1">Дата с</label>
            <input
              v-model="dateFrom"
              type="date"
              class="w-full px-3 py-2 border border-neutral-300 rounded-md"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-neutral-700 mb-1">Дата по</label>
            <input
              v-model="dateTo"
              type="date"
              class="w-full px-3 py-2 border border-neutral-300 rounded-md"
            />
          </div>
        </div>
        <div>
          <label class="block text-sm font-medium text-neutral-700 mb-1">Тип отчёта</label>
          <select v-model="reportType" class="w-full px-3 py-2 border border-neutral-300 rounded-md">
            <option value="asset_usage">Использование активов</option>
            <option value="user_activity">Активность пользователей</option>
            <option value="campaign_roi">ROI кампаний</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-neutral-700 mb-1">Формат</label>
          <select v-model="exportFormat" class="w-full px-3 py-2 border border-neutral-300 rounded-md">
            <option value="json">JSON</option>
          </select>
        </div>
        <p v-if="submitError" class="text-sm text-red-600">{{ submitError }}</p>
        <div class="flex justify-end gap-2 pt-2">
          <button
            type="button"
            class="px-4 py-2 border border-neutral-300 rounded-md hover:bg-neutral-50"
            @click="handleClose"
          >
            Отмена
          </button>
          <button
            type="button"
            class="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 disabled:opacity-50"
            :disabled="isSubmitting"
            @click="submit"
          >
            {{ isSubmitting ? 'Запуск…' : 'Сформировать' }}
          </button>
        </div>
      </div>

      <div v-else class="space-y-4">
        <p v-if="reportTaskStatus === 'processing' || reportTaskStatus === 'pending'" class="text-sm text-neutral-600">
          Формирование отчёта…
        </p>
        <p v-else-if="reportTaskStatus === 'failed'" class="text-sm text-red-600">
          Ошибка формирования отчёта.
        </p>
        <p v-else-if="reportTaskStatus === 'completed'" class="text-sm text-neutral-600">
          Отчёт готов.
        </p>
        <div class="flex justify-end gap-2 pt-2">
          <button
            v-if="reportTaskStatus === 'completed'"
            type="button"
            class="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700"
            :disabled="isDownloading"
            @click="download"
          >
            {{ isDownloading ? 'Скачивание…' : 'Скачать' }}
          </button>
          <button
            type="button"
            class="px-4 py-2 border border-neutral-300 rounded-md hover:bg-neutral-50"
            @click="handleClose"
          >
            Закрыть
          </button>
        </div>
      </div>
    </div>
  </Modal>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import Modal from '@/components/Common/Modal.vue'
import { analyticsService } from '@/services/analyticsService'
import { useAnalyticsStore } from '@/stores/analyticsStore'

const props = defineProps<{ isOpen: boolean }>()
const emit = defineEmits<{ close: [] }>()

const analyticsStore = useAnalyticsStore()

const dateFrom = ref('')
const dateTo = ref('')
const reportType = ref('asset_usage')
const exportFormat = ref('json')
const isSubmitting = ref(false)
const submitError = ref<string | null>(null)
const isDownloading = ref(false)

const reportTaskId = computed(() => analyticsStore.reportTaskId)
const reportTaskStatus = computed(() => analyticsStore.reportTaskStatus)

const POLL_INTERVAL_MS = 2500

let pollTimer: ReturnType<typeof setInterval> | null = null

function setDefaultDates(): void {
  const end = new Date()
  const start = new Date()
  start.setDate(start.getDate() - 30)
  dateFrom.value = start.toISOString().slice(0, 10)
  dateTo.value = end.toISOString().slice(0, 10)
}

async function submit(): Promise<void> {
  isSubmitting.value = true
  submitError.value = null
  try {
    const taskId = await analyticsStore.createReport({
      report_type: reportType.value,
      date_range: {
        from: dateFrom.value || undefined,
        to: dateTo.value || undefined,
      },
      export_format: exportFormat.value,
    })
    if (taskId != null) {
      await analyticsStore.pollReportStatus(taskId)
      if (analyticsStore.reportTaskStatus !== 'completed' && analyticsStore.reportTaskStatus !== 'failed') {
        startPolling()
      }
    }
  } finally {
    isSubmitting.value = false
  }
}

function startPolling(): void {
  if (pollTimer) clearInterval(pollTimer)
  pollTimer = setInterval(async () => {
    const id = analyticsStore.reportTaskId
    if (id == null) return
    const { status } = await analyticsStore.pollReportStatus(id)
    if (status === 'completed' || status === 'failed') {
      if (pollTimer) {
        clearInterval(pollTimer)
        pollTimer = null
      }
    }
  }, POLL_INTERVAL_MS)
}

async function download(): Promise<void> {
  const id = analyticsStore.reportTaskId
  if (id == null) return
  isDownloading.value = true
  try {
    const blob = await analyticsService.downloadReportBlob(id)
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `report-${id}.json`
    a.click()
    URL.revokeObjectURL(url)
  } catch (e: any) {
    submitError.value = e?.message || 'Не удалось скачать отчёт'
  } finally {
    isDownloading.value = false
  }
}

function handleClose(): void {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
  analyticsStore.resetReportState()
  submitError.value = null
  emit('close')
}

watch(
  () => props.isOpen,
  (open) => {
    if (open) {
      setDefaultDates()
      analyticsStore.resetReportState()
    }
  }
)
</script>
