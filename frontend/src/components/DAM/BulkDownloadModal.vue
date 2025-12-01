<template>
  <Modal
    :is-open="isOpen"
    size="md"
    @close="$emit('close')"
  >
    <template #header>
      <h2 class="text-lg font-semibold text-neutral-900 dark:text-neutral-900">
        Скачать активы
      </h2>
    </template>

    <template #default>
      <div class="space-y-4">
        <!-- Format Selection -->
        <div>
          <label class="block text-sm font-medium text-neutral-900 dark:text-neutral-900 mb-2">
            Формат архива
          </label>
          <select
            v-model="format"
            class="w-full px-3 py-2 border border-neutral-300 dark:border-neutral-300 rounded-md text-sm bg-neutral-0 dark:bg-neutral-0 text-neutral-900 dark:text-neutral-900 focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="zip">ZIP архив</option>
            <option value="tar">TAR архив</option>
          </select>
        </div>

        <!-- Options -->
        <div class="space-y-2">
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              v-model="includeMetadata"
              type="checkbox"
              class="w-4 h-4 rounded border-neutral-300 text-primary-500 focus:ring-primary-500"
            />
            <span class="text-sm text-neutral-700 dark:text-neutral-700">
              Включить метаданные (JSON файл)
            </span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              v-model="preserveStructure"
              type="checkbox"
              class="w-4 h-4 rounded border-neutral-300 text-primary-500 focus:ring-primary-500"
            />
            <span class="text-sm text-neutral-700 dark:text-neutral-700">
              Сохранить структуру папок
            </span>
          </label>
        </div>

        <!-- Info -->
        <div class="p-3 bg-neutral-50 dark:bg-neutral-50 rounded-md">
          <p class="text-sm text-neutral-600 dark:text-neutral-600">
            Будет создан архив с <strong>{{ selectedCount }}</strong> активами.
          </p>
          <p class="text-xs text-neutral-500 dark:text-neutral-500 mt-1">
            После создания архива начнется автоматическая загрузка.
          </p>
        </div>

        <!-- Progress -->
        <div v-if="isProcessing" class="space-y-2">
          <div class="flex items-center justify-between text-sm">
            <span class="text-neutral-600 dark:text-neutral-600">{{ progressMessage }}</span>
            <span v-if="progressPercent > 0" class="text-neutral-900 dark:text-neutral-900 font-medium">
              {{ progressPercent }}%
            </span>
          </div>
          <div class="w-full bg-neutral-200 dark:bg-neutral-200 rounded-full h-2">
            <div
              class="bg-primary-500 h-2 rounded-full transition-all duration-300"
              :style="{ width: `${progressPercent}%` }"
            ></div>
          </div>
        </div>

        <!-- Download Link (when ready) -->
        <div v-if="downloadUrl" class="p-3 bg-primary-50 dark:bg-primary-50 rounded-md">
          <p class="text-sm text-neutral-900 dark:text-neutral-900 mb-2">
            Архив готов к скачиванию!
          </p>
          <Button
            variant="primary"
            size="sm"
            @click="handleDownload"
            class="w-full"
          >
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
              />
            </svg>
            Скачать архив
          </Button>
        </div>

        <!-- Error Display -->
        <div v-if="error" class="p-3 bg-error-50 dark:bg-error-50 rounded-md">
          <p class="text-sm font-medium text-error">{{ error }}</p>
        </div>
      </div>
    </template>

    <template #footer>
      <div class="flex justify-end gap-2">
        <Button
          variant="outline"
          size="md"
          @click="$emit('close')"
          :disabled="isProcessing && !downloadUrl"
        >
          {{ downloadUrl ? 'Закрыть' : 'Отмена' }}
        </Button>
        <Button
          v-if="!downloadUrl"
          variant="primary"
          size="md"
          @click="handleStartDownload"
          :disabled="isProcessing"
        >
          <span v-if="!isProcessing">Создать архив</span>
          <span v-else>Создание...</span>
        </Button>
      </div>
    </template>
  </Modal>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import Modal from '@/components/Common/Modal.vue'
import Button from '@/components/Common/Button.vue'
import { assetService } from '@/services/assetService'
import { formatApiError } from '@/utils/errors'

interface Props {
  isOpen: boolean
  selectedIds: number[]
}

const props = defineProps<Props>()

const emit = defineEmits<{
  close: []
  success: []
}>()

const format = ref<'zip' | 'tar'>('zip')
const includeMetadata = ref(true)
const preserveStructure = ref(false)
const isProcessing = ref(false)
const progressPercent = ref(0)
const progressMessage = ref('')
const downloadUrl = ref<string | null>(null)
const error = ref<string | null>(null)

const selectedCount = computed(() => props.selectedIds.length)

// Reset on open
watch(
  () => props.isOpen,
  (isOpen) => {
    if (isOpen) {
      format.value = 'zip'
      includeMetadata.value = true
      preserveStructure.value = false
      isProcessing.value = false
      progressPercent.value = 0
      progressMessage.value = ''
      downloadUrl.value = null
      error.value = null
    }
  }
)

async function handleStartDownload() {
  isProcessing.value = true
  progressPercent.value = 0
  progressMessage.value = 'Создание архива...'
  error.value = null

  try {
    const result = await assetService.bulkOperation({
      ids: props.selectedIds,
      action: 'export',
      data: {
        format: format.value,
        include_metadata: includeMetadata.value,
        preserve_structure: preserveStructure.value
      }
    })

    if (result.success) {
      progressPercent.value = 100
      progressMessage.value = 'Архив создан!'
      // In real implementation, downloadUrl would come from API response
      // For now, simulate with a placeholder
      downloadUrl.value = `/api/v4/dam/assets/export/${result.updated}/download/`
      emit('success')
    } else {
      error.value = 'Не удалось создать архив'
    }
  } catch (err) {
    error.value = formatApiError(err)
  } finally {
    isProcessing.value = false
  }
}

function handleDownload() {
  if (downloadUrl.value) {
    window.open(downloadUrl.value, '_blank')
    emit('close')
  }
}
</script>

