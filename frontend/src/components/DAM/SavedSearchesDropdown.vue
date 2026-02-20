<template>
  <div class="relative" ref="containerRef">
    <button
      type="button"
      class="inline-flex items-center gap-2 px-3 py-2 text-sm font-medium text-neutral-700 dark:text-neutral-300 bg-white dark:bg-neutral-800 border border-neutral-300 dark:border-neutral-600 rounded-lg hover:bg-neutral-50 dark:hover:bg-neutral-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
      :aria-expanded="isOpen"
      aria-haspopup="listbox"
      aria-label="Сохранённые поиски"
      @click="toggle"
    >
      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
      </svg>
      <span>Сохранённые поиски</span>
      <svg
        class="w-4 h-4 transition-transform"
        :class="isOpen && 'rotate-180'"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
      </svg>
    </button>

    <Transition name="dropdown">
      <div
        v-if="isOpen"
        class="absolute left-0 top-full mt-1 w-72 rounded-lg border border-neutral-200 dark:border-neutral-600 bg-white dark:bg-neutral-800 shadow-lg z-50 py-1 max-h-80 overflow-auto"
        role="listbox"
        aria-label="Список сохранённых поисков"
      >
        <button
          type="button"
          class="w-full px-4 py-2.5 text-left text-sm text-primary-600 dark:text-primary-400 hover:bg-neutral-100 dark:hover:bg-neutral-700 flex items-center gap-2"
          role="option"
          aria-label="Сохранить текущий поиск"
          @click="onSaveCurrent"
        >
          <svg class="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          Сохранить текущий поиск
        </button>
        <div class="border-t border-neutral-200 dark:border-neutral-600 my-1" />
        <div v-if="loading" class="px-4 py-3 text-sm text-neutral-500">
          Загрузка…
        </div>
        <div v-else-if="error" class="px-4 py-3 text-sm text-red-600 dark:text-red-400">
          {{ error }}
        </div>
        <div v-else-if="list.length === 0" class="px-4 py-3 text-sm text-neutral-500">
          Нет сохранённых поисков
        </div>
        <template v-else>
          <button
            v-for="item in list"
            :key="item.id"
            type="button"
            class="w-full px-4 py-2 text-left text-sm text-neutral-800 dark:text-neutral-200 hover:bg-neutral-100 dark:hover:bg-neutral-700 group flex items-center gap-2"
            role="option"
            :aria-label="`Выполнить поиск: ${item.name}`"
            @click.stop
          >
            <span class="flex-1 truncate">{{ item.name }}</span>
            <div class="flex items-center gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity">
              <button
                type="button"
                class="p-1 rounded hover:bg-neutral-200 dark:hover:bg-neutral-600 text-neutral-600 dark:text-neutral-400"
                aria-label="Выполнить"
                title="Выполнить"
                @click="onRun(item)"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </button>
              <button
                type="button"
                class="p-1 rounded hover:bg-neutral-200 dark:hover:bg-neutral-600 text-neutral-600 dark:text-neutral-400"
                aria-label="Переименовать"
                title="Переименовать"
                @click="onEdit(item)"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
              </button>
              <button
                type="button"
                class="p-1 rounded hover:bg-neutral-200 dark:hover:bg-neutral-600 text-red-600 dark:text-red-400"
                aria-label="Удалить"
                title="Удалить"
                @click="onDelete(item.id)"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            </div>
          </button>
        </template>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { onClickOutside } from '@vueuse/core'
import {
  listSavedSearches,
  deleteSavedSearch,
  type SavedSearch
} from '@/services/savedSearchesService'

const emit = defineEmits<{
  saveCurrent: []
  run: [item: SavedSearch]
  edit: [item: SavedSearch]
  delete: [id: number]
}>()

const containerRef = ref<HTMLElement | null>(null)
const isOpen = ref(false)
const list = ref<SavedSearch[]>([])
const loading = ref(false)
const error = ref<string | null>(null)

function toggle() {
  isOpen.value = !isOpen.value
  if (isOpen.value) load()
}

function load() {
  loading.value = true
  error.value = null
  listSavedSearches()
    .then((data) => {
      list.value = data
    })
    .catch((e: unknown) => {
      const msg = e && typeof e === 'object' && 'message' in e ? String((e as Error).message) : 'Ошибка загрузки'
      error.value = msg
      list.value = []
    })
    .finally(() => {
      loading.value = false
    })
}

onClickOutside(containerRef, () => {
  isOpen.value = false
})

function onSaveCurrent() {
  isOpen.value = false
  emit('saveCurrent')
}

function onRun(item: SavedSearch) {
  isOpen.value = false
  emit('run', item)
}

function onEdit(item: SavedSearch) {
  emit('edit', item)
}

function onDelete(id: number) {
  isOpen.value = false
  emit('delete', id)
}

defineExpose({
  refresh: load
})
</script>

<style scoped>
.dropdown-enter-active,
.dropdown-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}
.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>
