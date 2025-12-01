<template>
  <Modal
    :is-open="isOpen"
    size="md"
    @close="$emit('close')"
  >
    <template #header>
      <h2 class="text-lg font-semibold text-neutral-900 dark:text-neutral-900">
        Удаление активов
      </h2>
    </template>

    <template #default>
      <div class="space-y-4">
        <!-- Warning -->
        <div class="p-4 bg-error-50 dark:bg-error-50 rounded-md border border-error-200 dark:border-error-200">
          <div class="flex items-start gap-3">
            <svg
              class="w-6 h-6 text-error flex-shrink-0 mt-0.5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
              />
            </svg>
            <div>
              <p class="text-sm font-medium text-error mb-1">
                Внимание! Это действие нельзя отменить.
              </p>
              <p class="text-sm text-error">
                Вы собираетесь удалить <strong>{{ selectedCount }}</strong> активов. Это действие
                необратимо.
              </p>
            </div>
          </div>
        </div>

        <!-- Confirmation Checkbox -->
        <div class="flex items-start gap-2">
          <input
            id="confirm-delete"
            v-model="confirmed"
            type="checkbox"
            class="mt-1 w-4 h-4 rounded border-neutral-300 text-error focus:ring-error"
          />
          <label for="confirm-delete" class="text-sm text-neutral-700 dark:text-neutral-700">
            Я понимаю, что это действие нельзя отменить
          </label>
        </div>

        <!-- Progress -->
        <div v-if="isProcessing" class="space-y-2">
          <div class="flex items-center justify-between text-sm">
            <span class="text-neutral-600 dark:text-neutral-600">Удаление...</span>
            <span class="text-neutral-900 dark:text-neutral-900 font-medium">
              {{ processedCount }} / {{ selectedCount }}
            </span>
          </div>
          <div class="w-full bg-neutral-200 dark:bg-neutral-200 rounded-full h-2">
            <div
              class="bg-error h-2 rounded-full transition-all duration-300"
              :style="{ width: `${(processedCount / selectedCount) * 100}%` }"
            ></div>
          </div>
        </div>

        <!-- Error Display -->
        <div v-if="errors.length > 0" class="p-3 bg-error-50 dark:bg-error-50 rounded-md">
          <p class="text-sm font-medium text-error mb-2">Ошибки:</p>
          <ul class="text-sm text-error space-y-1">
            <li v-for="(error, index) in errors" :key="index">
              {{ error }}
            </li>
          </ul>
        </div>
      </div>
    </template>

    <template #footer>
      <div class="flex justify-end gap-2">
        <Button
          variant="outline"
          size="md"
          @click="$emit('close')"
          :disabled="isProcessing"
        >
          Отмена
        </Button>
        <Button
          variant="danger"
          size="md"
          @click="handleDelete"
          :disabled="!confirmed || isProcessing"
        >
          <span v-if="!isProcessing">Удалить навсегда</span>
          <span v-else>Удаление...</span>
        </Button>
      </div>
    </template>
  </Modal>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import Modal from '@/components/Common/Modal.vue'
import Button from '@/components/Common/Button.vue'
import { useAssetStore } from '@/stores/assetStore'
import { formatApiError } from '@/utils/errors'

interface Props {
  isOpen: boolean
  selectedIds: number[]
}

const props = defineProps<Props>()

const emit = defineEmits<{
  close: []
  success: [result: { updated: number; failed: number }]
}>()

const assetStore = useAssetStore()

const confirmed = ref(false)
const isProcessing = ref(false)
const processedCount = ref(0)
const errors = ref<string[]>([])

const selectedCount = computed(() => props.selectedIds.length)

// Reset on open
watch(
  () => props.isOpen,
  (isOpen) => {
    if (isOpen) {
      confirmed.value = false
      isProcessing.value = false
      processedCount.value = 0
      errors.value = []
    }
  }
)

async function handleDelete() {
  if (!confirmed.value) return

  isProcessing.value = true
  processedCount.value = 0
  errors.value = []

  try {
    // Use assetStore.bulkDelete which properly handles mock mode
    const deletedCount = await assetStore.bulkDelete(props.selectedIds)
    
    processedCount.value = deletedCount
    
    const failedCount = props.selectedIds.length - deletedCount
    if (failedCount > 0) {
      errors.value = [`Не удалось удалить ${failedCount} активов`]
    }
    
    emit('success', { updated: deletedCount, failed: failedCount })
    
    // Close modal after short delay to show completion
    setTimeout(() => {
      emit('close')
    }, 500)
  } catch (err) {
    errors.value = [formatApiError(err)]
  } finally {
    isProcessing.value = false
  }
}
</script>

