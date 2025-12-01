<template>
  <Modal
    :is-open="isOpen"
    size="md"
    @close="$emit('close')"
  >
    <template #header>
      <h2 class="text-lg font-semibold text-neutral-900 dark:text-neutral-900">
        Переместить активы
      </h2>
    </template>

    <template #default>
      <div class="space-y-4">
        <!-- Collection Selector -->
        <div>
          <label class="block text-sm font-medium text-neutral-900 dark:text-neutral-900 mb-2">
            Коллекция назначения
          </label>
          <select
            v-model="selectedCollection"
            class="w-full px-3 py-2 border border-neutral-300 dark:border-neutral-300 rounded-md text-sm bg-neutral-0 dark:bg-neutral-0 text-neutral-900 dark:text-neutral-900 focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="">Выберите коллекцию...</option>
            <option v-for="collection in collections" :key="collection.id" :value="collection.id">
              {{ collection.name }}
            </option>
          </select>
        </div>

        <!-- Create New Collection Option -->
        <div>
          <button
            class="text-sm text-primary-500 hover:text-primary-600 transition-colors"
            @click="showNewCollectionInput = !showNewCollectionInput"
          >
            + Создать новую коллекцию
          </button>
          <input
            v-if="showNewCollectionInput"
            v-model="newCollectionName"
            type="text"
            placeholder="Название коллекции"
            class="mt-2 w-full px-3 py-2 border border-neutral-300 dark:border-neutral-300 rounded-md text-sm bg-neutral-0 dark:bg-neutral-0 text-neutral-900 dark:text-neutral-900 focus:outline-none focus:ring-2 focus:ring-primary-500"
            @keydown.enter="createAndSelectCollection"
          />
        </div>

        <!-- Info -->
        <div class="p-3 bg-neutral-50 dark:bg-neutral-50 rounded-md">
          <p class="text-sm text-neutral-600 dark:text-neutral-600">
            <strong>{{ selectedCount }}</strong> активов будет перемещено в выбранную коллекцию.
          </p>
        </div>

        <!-- Progress -->
        <div v-if="isProcessing" class="space-y-2">
          <div class="flex items-center justify-between text-sm">
            <span class="text-neutral-600 dark:text-neutral-600">Перемещение...</span>
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
          @click="handleMove"
          :disabled="!selectedCollection || isProcessing"
        >
          <span v-if="!isProcessing">Переместить</span>
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
import { assetService } from '@/services/assetService'
import { formatApiError } from '@/utils/errors'

interface Collection {
  id: number
  name: string
}

interface Props {
  isOpen: boolean
  selectedIds: number[]
  collections?: Collection[]
}

const props = withDefaults(defineProps<Props>(), {
  collections: () => []
})

const emit = defineEmits<{
  close: []
  success: [result: { updated: number; failed: number }]
}>()

const selectedCollection = ref<number | ''>('')
const showNewCollectionInput = ref(false)
const newCollectionName = ref('')
const isProcessing = ref(false)
const processedCount = ref(0)
const errors = ref<string[]>([])

const selectedCount = computed(() => props.selectedIds.length)

// Reset on open
watch(
  () => props.isOpen,
  (isOpen) => {
    if (isOpen) {
      selectedCollection.value = ''
      showNewCollectionInput.value = false
      newCollectionName.value = ''
      isProcessing.value = false
      processedCount.value = 0
      errors.value = []
    }
  }
)

function createAndSelectCollection() {
  if (newCollectionName.value.trim()) {
    // TODO: Create collection via API
    // For now, just use the name as a placeholder
    selectedCollection.value = -1 // Temporary ID
    showNewCollectionInput.value = false
  }
}

async function handleMove() {
  if (!selectedCollection.value) return

  isProcessing.value = true
  processedCount.value = 0
  errors.value = []

  try {
    const collectionId = selectedCollection.value === -1 ? newCollectionName.value : selectedCollection.value

    const result = await assetService.bulkOperation({
      ids: props.selectedIds,
      action: 'move',
      data: { collection_id: collectionId }
    })

    if (result.success) {
      processedCount.value = result.updated
      if (result.errors && result.errors.length > 0) {
        errors.value = result.errors.map((e) => `Asset ${e.id}: ${e.error}`)
      }
      emit('success', { updated: result.updated, failed: result.failed })
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

