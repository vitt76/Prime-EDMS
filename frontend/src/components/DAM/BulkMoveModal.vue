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
        <!-- Folder (Cabinet) Selector -->
        <div>
          <label class="block text-sm font-medium text-neutral-900 dark:text-neutral-900 mb-2">
            Папка назначения
          </label>
          <select
            v-model="selectedFolderId"
            class="w-full px-3 py-2 border border-neutral-300 dark:border-neutral-300 rounded-md text-sm bg-neutral-0 dark:bg-neutral-0 text-neutral-900 dark:text-neutral-900 focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="">Выберите папку...</option>
            <option v-for="folder in folderOptions" :key="folder.id" :value="folder.id">
              {{ folder.label }}
            </option>
          </select>
        </div>

        <!-- Info -->
        <div class="p-3 bg-neutral-50 dark:bg-neutral-50 rounded-md">
          <p class="text-sm text-neutral-600 dark:text-neutral-600">
            <strong>{{ selectedCount }}</strong> активов будет перемещено в выбранную папку.
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
          :disabled="!selectedFolderId || isProcessing"
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
import { useFolderStore } from '@/stores/folderStore'
import { formatApiError } from '@/utils/errors'
import type { FolderNode } from '@/mocks/folders'

interface Props {
  isOpen: boolean
  selectedIds: number[]
}

const props = defineProps<Props>()

const emit = defineEmits<{
  close: []
  success: [result: { updated: number; failed: number }]
}>()

const folderStore = useFolderStore()
const selectedFolderId = ref<string>('')
const isProcessing = ref(false)
const processedCount = ref(0)
const errors = ref<string[]>([])

const selectedCount = computed(() => props.selectedIds.length)

function flattenFolders(
  folders: FolderNode[],
  depth = 0,
  acc: Array<{ id: string; label: string }> = []
): Array<{ id: string; label: string }> {
  for (const folder of folders) {
    const prefix = depth > 0 ? `${'— '.repeat(depth)}` : ''
    acc.push({ id: folder.id, label: `${prefix}${folder.name}` })
    if (folder.children?.length) {
      flattenFolders(folder.children, depth + 1, acc)
    }
  }
  return acc
}

const folderOptions = computed(() => {
  return flattenFolders(folderStore.systemFolders)
})

// Reset on open
watch(
  () => props.isOpen,
  async (isOpen) => {
    if (isOpen) {
      selectedFolderId.value = ''
      isProcessing.value = false
      processedCount.value = 0
      errors.value = []

      // Ensure system folders are loaded from backend
      await folderStore.refreshFolders(true)
    }
  }
)

async function handleMove() {
  if (!selectedFolderId.value) return

  isProcessing.value = true
  processedCount.value = 0
  errors.value = []

  try {
    const result = await folderStore.handleBulkAssetDrop(
      props.selectedIds,
      selectedFolderId.value
    )

    if (result.success > 0) {
      processedCount.value = result.success
      emit('success', { updated: result.success, failed: result.failed })
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

