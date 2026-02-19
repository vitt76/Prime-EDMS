<template>
  <Teleport to="body">
    <div
      class="fixed inset-0 z-[1100] flex items-center justify-center p-4 bg-black/50"
      role="dialog"
      aria-modal="true"
      aria-labelledby="add-to-collection-title"
      @click.self="emit('close')"
    >
      <div
        class="bg-white dark:bg-neutral-800 rounded-xl shadow-xl max-w-md w-full max-h-[80vh] flex flex-col"
        @keydown.escape="emit('close')"
      >
        <div class="p-4 border-b border-neutral-200 dark:border-neutral-700">
          <h2 id="add-to-collection-title" class="text-lg font-semibold text-neutral-900 dark:text-white">
            Добавить в коллекцию
          </h2>
          <p class="mt-1 text-sm text-neutral-500 dark:text-neutral-400">
            Выбрано активов: {{ selectedIds.length }}
          </p>
        </div>
        <div class="flex-1 overflow-y-auto p-4">
          <div v-if="loading" class="flex justify-center py-8">
            <div class="animate-spin rounded-full h-8 w-8 border-2 border-primary-500 border-t-transparent" />
          </div>
          <div v-else-if="collections.length === 0" class="py-8 text-center text-neutral-500 dark:text-neutral-400">
            Нет коллекций. Создайте коллекцию на странице «Коллекции».
          </div>
          <ul v-else class="space-y-1" role="listbox" aria-label="Список коллекций">
            <li
              v-for="c in collections"
              :key="c.id"
              role="option"
              :aria-selected="selectedId === c.id"
              class="flex items-center gap-3 px-3 py-2.5 rounded-lg cursor-pointer transition-colors
                     hover:bg-neutral-100 dark:hover:bg-neutral-700
                     focus:bg-neutral-100 dark:focus:bg-neutral-700 focus:outline-none"
              :class="{ 'bg-primary-50 dark:bg-primary-900/30 ring-1 ring-primary-500': selectedId === c.id }"
              @click="selectedId = c.id"
            >
              <span class="flex-1 font-medium text-neutral-900 dark:text-white">{{ c.name }}</span>
              <span class="text-sm text-neutral-500 dark:text-neutral-400">{{ c.asset_count ?? 0 }} активов</span>
            </li>
          </ul>
        </div>
        <div class="p-4 border-t border-neutral-200 dark:border-neutral-700 flex justify-end gap-2">
          <button
            type="button"
            class="px-4 py-2 rounded-lg text-neutral-700 dark:text-neutral-300 hover:bg-neutral-100 dark:hover:bg-neutral-700"
            @click="emit('close')"
          >
            Отмена
          </button>
          <button
            type="button"
            class="px-4 py-2 rounded-lg bg-primary-600 text-white hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
            :disabled="!selectedId || submitting"
            @click="handleAdd"
          >
            {{ submitting ? 'Добавление…' : 'Добавить' }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { collectionsService } from '@/services/collectionsService'
import type { Collection } from '@/types/collections'

const props = defineProps<{
  selectedIds: number[]
}>()

const emit = defineEmits<{
  close: []
  done: []
}>()

const loading = ref(true)
const submitting = ref(false)
const collections = ref<Collection[]>([])
const selectedId = ref<number | null>(null)

onMounted(async () => {
  try {
    const res = await collectionsService.getCollections({})
    collections.value = res.results
    if (collections.value.length > 0 && !selectedId.value) {
      selectedId.value = collections.value[0].id
    }
  } catch {
    collections.value = []
  } finally {
    loading.value = false
  }
})

async function handleAdd() {
  if (!selectedId.value || props.selectedIds.length === 0) return
  submitting.value = true
  try {
    await collectionsService.addAssetsToCollection(
      String(selectedId.value),
      props.selectedIds.map(String)
    )
    emit('done')
    emit('close')
  } finally {
    submitting.value = false
  }
}
</script>
