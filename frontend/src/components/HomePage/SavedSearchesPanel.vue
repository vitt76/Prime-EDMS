<template>
  <div class="saved-searches-panel bg-white dark:bg-white rounded-lg shadow-sm border border-neutral-100 p-5">
    <div class="flex justify-between items-center mb-4">
      <h2 class="text-lg font-semibold text-neutral-900 flex items-center gap-2">
        <span class="text-xl">🔖</span> Сохраненные поиски
      </h2>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="space-y-3">
      <div v-for="i in 3" :key="i" class="animate-pulse flex items-center gap-2">
        <div class="w-4 h-4 bg-neutral-200 rounded"></div>
        <div class="h-4 bg-neutral-200 rounded w-1/2"></div>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="text-sm text-error bg-error/10 p-2 rounded">
      {{ error }}
    </div>

    <!-- Empty State -->
    <div v-else-if="list.length === 0" class="text-sm text-neutral-500 text-center py-4">
      У вас пока нет сохраненных поисков.
    </div>

    <!-- List -->
    <div v-else class="flex flex-col gap-1">
      <button
        v-for="item in displayList"
        :key="item.id"
        @click="onRun(item)"
        class="w-full text-left px-3 py-2 rounded-md hover:bg-neutral-50 flex items-center gap-2 transition-colors text-sm text-neutral-700 dark:text-neutral-700 group"
      >
        <svg class="w-4 h-4 text-neutral-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
        <span class="truncate flex-1">{{ item.name }}</span>
        
        <!-- Run icon on hover -->
        <span class="opacity-0 group-hover:opacity-100 text-primary-500">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3" />
          </svg>
        </span>
      </button>
      
      <button 
        v-if="list.length > 5"
        @click="goToGallery" 
        class="text-xs text-primary-600 hover:text-primary-700 font-medium text-left px-3 mt-2"
      >
        Показать все ({{ list.length }})
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { listSavedSearches, type SavedSearch } from '@/services/savedSearchesService'
import { useDamSearchFilters } from '@/composables/useDamSearchFilters'

const router = useRouter()
const searchFilters = useDamSearchFilters()

const list = ref<SavedSearch[]>([])
const loading = ref(false)
const error = ref<string | null>(null)

const displayList = computed(() => list.value.slice(0, 5))

onMounted(() => {
  load()
})

function load() {
  loading.value = true
  error.value = null
  listSavedSearches()
    .then((data) => {
      list.value = data
    })
    .catch((e: any) => {
      error.value = e?.message || 'Ошибка загрузки'
    })
    .finally(() => {
      loading.value = false
    })
}

function onRun(item: SavedSearch) {
  // Use existing composable to apply filters and fetch
  searchFilters.applySavedSearch(item.query, item.filters)
  router.push({ name: 'dam' })
}

function goToGallery() {
  router.push({ name: 'dam' })
}
</script>