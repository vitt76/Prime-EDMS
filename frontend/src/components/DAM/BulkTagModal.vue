<template>
  <Modal
    :is-open="isOpen"
    size="md"
    @close="$emit('close')"
  >
    <template #header>
      <h2 class="text-lg font-semibold text-neutral-900 dark:text-neutral-900">
        Массовое добавление тегов
      </h2>
    </template>

    <template #default>
      <div class="space-y-4">
        <!-- Operation Selector -->
        <div>
          <label class="block text-sm font-medium text-neutral-900 dark:text-neutral-900 mb-2">
            Операция
          </label>
          <select
            v-model="operation"
            class="w-full px-3 py-2 border border-neutral-300 dark:border-neutral-300 rounded-md text-sm bg-neutral-0 dark:bg-neutral-0 text-neutral-900 dark:text-neutral-900 focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="add">Добавить теги</option>
            <option value="remove">Удалить теги</option>
            <option value="replace">Заменить все теги</option>
          </select>
        </div>

        <!-- Tag Input -->
        <div>
          <label class="block text-sm font-medium text-neutral-900 dark:text-neutral-900 mb-2">
            Теги
          </label>
          <TagInput
            v-model="tags"
            :suggestions="tagSuggestions"
            placeholder="Введите теги..."
            :allow-custom="true"
          />
        </div>

        <!-- Info -->
        <div class="p-3 bg-neutral-50 dark:bg-neutral-50 rounded-md">
          <p class="text-sm text-neutral-600 dark:text-neutral-600">
            Операция будет применена к <strong>{{ selectedCount }}</strong> выбранным активам.
          </p>
        </div>

        <!-- Progress (if processing) -->
        <div v-if="isProcessing" class="space-y-2">
          <div class="flex items-center justify-between text-sm">
            <span class="text-neutral-600 dark:text-neutral-600">Обработка...</span>
            <span class="text-neutral-900 dark:text-neutral-900 font-medium">
              {{ processedCount }} / {{ selectedCount }}
            </span>
          </div>
          <div class="w-full bg-neutral-200 dark:bg-neutral-200 rounded-full h-2">
            <div
              class="bg-primary-500 h-2 rounded-full transition-all duration-300"
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
          variant="primary"
          size="md"
          @click="handleApply"
          :disabled="tags.length === 0 || isProcessing"
        >
          <span v-if="!isProcessing">Применить</span>
          <span v-else>Обработка...</span>
        </Button>
      </div>
    </template>
  </Modal>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import Modal from '@/components/Common/Modal.vue'
import Button from '@/components/Common/Button.vue'
import TagInput from '@/components/Common/TagInput.vue'
import { assetService } from '@/services/assetService'
import { formatApiError } from '@/utils/errors'

interface Props {
  isOpen: boolean
  selectedIds: number[]
  tagSuggestions?: string[]
}

const props = withDefaults(defineProps<Props>(), {
  tagSuggestions: () => []
})

const emit = defineEmits<{
  close: []
  success: [result: { updated: number; failed: number }]
}>()

const operation = ref<'add' | 'remove' | 'replace'>('add')
const tags = ref<string[]>([])
const isProcessing = ref(false)
const processedCount = ref(0)
const errors = ref<string[]>([])

const selectedCount = computed(() => props.selectedIds.length)

// Reset on open
watch(
  () => props.isOpen,
  (isOpen) => {
    if (isOpen) {
      operation.value = 'add'
      tags.value = []
      isProcessing.value = false
      processedCount.value = 0
      errors.value = []
    }
  }
)

async function handleApply() {
  if (tags.value.length === 0) return

  isProcessing.value = true
  processedCount.value = 0
  errors.value = []

  try {
    const action = operation.value === 'add' ? 'add_tags' : operation.value === 'remove' ? 'remove_tags' : 'add_tags'
    const data = operation.value === 'replace' ? { tags: tags.value, replace: true } : { tags: tags.value }

    const result = await assetService.bulkOperation({
      ids: props.selectedIds,
      action: action as 'add_tags' | 'remove_tags',
      data
    })

    if (result.success) {
      processedCount.value = result.updated
      if (result.errors && result.errors.length > 0) {
        errors.value = result.errors.map((e) => `Asset ${e.id}: ${e.error}`)
      }
      emit('success', { updated: result.updated, failed: result.failed })
      // Close modal after short delay to show success
      setTimeout(() => {
        emit('close')
      }, 1000)
    } else {
      errors.value = ['Операция не удалась']
    }
  } catch (err) {
    errors.value = [formatApiError(err)]
  } finally {
    isProcessing.value = false
  }
}
</script>


