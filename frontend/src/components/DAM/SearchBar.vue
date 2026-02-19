<template>
  <div class="relative" ref="searchContainer">
    <div class="relative">
      <input
        ref="searchInput"
        v-model="localQuery"
        type="text"
        :placeholder="placeholder"
        :class="[
          'w-full pl-10 pr-4 py-2 bg-neutral-100 dark:bg-neutral-100 border border-neutral-300 dark:border-neutral-300 rounded-md text-sm',
          'focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent',
          'transition-all duration-fast',
          isFocused ? 'ring-2 ring-primary-500' : ''
        ]"
        @input="handleInput"
        @focus="handleFocus"
        @blur="handleBlur"
        @keydown.esc="handleEscape"
        @keydown.arrow-down.prevent="handleArrowDown"
        @keydown.arrow-up.prevent="handleArrowUp"
        @keydown.enter.prevent="handleEnter"
        aria-label="Поиск активов"
        aria-autocomplete="list"
        :aria-expanded="showResults"
        :aria-controls="`search-results-${searchId}`"
      />
      <svg
        class="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-neutral-400 pointer-events-none"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
        aria-hidden="true"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
        />
      </svg>
      <button
        v-if="localQuery"
        class="absolute right-2 top-1/2 transform -translate-y-1/2 p-2 text-neutral-400 hover:text-neutral-600 dark:hover:text-neutral-600 rounded transition-colors min-w-[44px] min-h-[44px] flex items-center justify-center"
        @click="clearSearch"
        aria-label="Очистить поиск"
        type="button"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M6 18L18 6M6 6l12 12"
          />
        </svg>
      </button>
    </div>

    <!-- Instant Results Dropdown -->
    <Transition
      enter-active-class="transition ease-out duration-200"
      enter-from-class="opacity-0 scale-95"
      enter-to-class="opacity-100 scale-100"
      leave-active-class="transition ease-in duration-150"
      leave-from-class="opacity-100 scale-100"
      leave-to-class="opacity-0 scale-95"
    >
      <div
        v-if="showResults"
        :id="`search-results-${searchId}`"
        class="absolute z-50 mt-2 w-full bg-neutral-0 dark:bg-neutral-0 border border-neutral-300 dark:border-neutral-300 rounded-md shadow-lg max-h-96 overflow-y-auto"
        role="listbox"
        aria-label="Результаты поиска"
      >
        <!-- Loading State -->
        <div v-if="searchStore.isLoading" class="p-4 text-center">
          <div class="animate-spin h-6 w-6 mx-auto text-primary-500"></div>
          <p class="mt-2 text-sm text-neutral-600 dark:text-neutral-600">Поиск...</p>
        </div>

        <!-- Error State -->
        <div v-else-if="searchStore.error" class="p-4 text-center">
          <p class="text-sm text-error">{{ searchStore.error }}</p>
        </div>

        <!-- Results -->
        <div v-else-if="searchStore.hasResults">
          <SearchResults
            :results="searchStore.results"
            :selected-index="selectedIndex"
            :total-count="searchStore.totalCount"
            @select="handleResultSelect"
            @view-all="handleViewAll"
          />
        </div>

        <!-- No Results -->
        <div
          v-else-if="debouncedQuery && !searchStore.isLoading"
          class="p-4 text-center text-sm text-neutral-600 dark:text-neutral-600"
        >
          <p>Ничего не найдено</p>
          <p class="mt-1 text-xs">Попробуйте изменить запрос</p>
        </div>

        <!-- Recent Searches (when input is focused but empty) -->
        <div
          v-else-if="isFocused && !debouncedQuery && recentList.length > 0"
          class="p-2"
        >
          <div class="px-3 py-2 text-xs font-semibold text-neutral-500 uppercase tracking-wider">
            Недавние поиски
          </div>
          <button
            v-for="(recentQuery, index) in recentList"
            :key="index"
            :class="[
              'w-full text-left px-3 py-2 text-sm rounded-md transition-colors min-h-[44px]',
              'hover:bg-neutral-100 dark:hover:bg-neutral-100',
              'text-neutral-700 dark:text-neutral-700'
            ]"
            @click="selectRecentSearch(recentQuery)"
            type="button"
            :aria-label="`Выбрать поиск: ${recentQuery}`"
          >
            <div class="flex items-center gap-2">
              <svg class="w-4 h-4 text-neutral-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              <span>{{ recentQuery }}</span>
            </div>
          </button>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useSearchStore } from '@/stores/searchStore'
import { useDamSearchFilters } from '@/composables/useDamSearchFilters'
import { useDebounce } from '@/composables/useDebounce'
import { onClickOutside } from '@vueuse/core'
import SearchResults from './SearchResults.vue'

interface Props {
  placeholder?: string
  autofocus?: boolean
  /** When 'dam', recent list and submit use useDamSearchFilters (localStorage history); when 'searchStore' use searchStore (default). */
  historySource?: 'dam' | 'searchStore'
}

const props = withDefaults(defineProps<Props>(), {
  placeholder: 'Поиск... (Ctrl+K)',
  autofocus: false,
  historySource: 'searchStore'
})

const emit = defineEmits<{
  search: [query: string]
  'result-selected': [assetId: number]
}>()

const router = useRouter()
const searchStore = useSearchStore()
const damSearch = useDamSearchFilters()

const searchContainer = ref<HTMLElement | null>(null)
const searchInput = ref<HTMLInputElement | null>(null)
const localQuery = ref('')
const isFocused = ref(false)
const selectedIndex = ref(-1)

// Unique ID for accessibility
const searchId = ref(`search-${Math.random().toString(36).substring(2, 9)}`)

// Debounce search query (300ms)
const debouncedQuery = useDebounce(localQuery, 300)

// Recent list: from DAM localStorage when historySource is 'dam', else from searchStore
const recentList = computed(() =>
  props.historySource === 'dam' ? damSearch.getSearchHistory() : searchStore.recentSearches
)

// Show results when there's a query and input is focused. In DAM mode only show dropdown for recent list (no instant results).
const showResults = computed(() => {
  if (!isFocused.value || searchStore.error) return false
  if (props.historySource === 'dam') {
    return recentList.value.length > 0 && !debouncedQuery.value
  }
  return debouncedQuery.value.length >= 2 || recentList.value.length > 0
})

// When DAM mode: sync query to composable (gallery updates). When searchStore: perform instant search.
watch(debouncedQuery, async (newQuery) => {
  if (props.historySource === 'dam') {
    damSearch.setSearch(newQuery || '')
    if (newQuery) emit('search', newQuery)
    return
  }
  if (newQuery && newQuery.length >= 2) {
    await searchStore.performSearch(newQuery, 8) // Limit to 8 for instant results
    emit('search', newQuery)
  } else {
    searchStore.clearSearch()
  }
})

// Initialize with store query if exists
watch(
  () => searchStore.query,
  (newQuery) => {
    if (newQuery && !localQuery.value) {
      localQuery.value = newQuery
    }
  },
  { immediate: true }
)

function handleInput() {
  selectedIndex.value = -1
}

function handleFocus() {
  isFocused.value = true
  if (!debouncedQuery.value && props.historySource === 'searchStore') {
    searchStore.loadRecentSearches()
  }
}

function handleBlur() {
  // Delay to allow click events on results
  setTimeout(() => {
    isFocused.value = false
  }, 200)
}

function handleEscape() {
  localQuery.value = ''
  searchStore.clearSearch()
  searchInput.value?.blur()
  isFocused.value = false
}

function clearSearch() {
  localQuery.value = ''
  searchStore.clearSearch()
  searchInput.value?.focus()
}

function handleArrowDown() {
  if (!showResults.value || searchStore.results.length === 0) return

  selectedIndex.value = Math.min(selectedIndex.value + 1, searchStore.results.length - 1)
  scrollToSelected()
}

function handleArrowUp() {
  if (!showResults.value) return

  if (selectedIndex.value <= 0) {
    selectedIndex.value = -1
  } else {
    selectedIndex.value--
    scrollToSelected()
  }
}

function handleEnter() {
  if (selectedIndex.value >= 0 && selectedIndex.value < searchStore.results.length) {
    handleResultSelect(searchStore.results[selectedIndex.value].id)
  } else if (debouncedQuery.value) {
    if (props.historySource === 'dam') {
      damSearch.setSearch(localQuery.value)
      damSearch.submitSearchNow()
      router.push({ path: '/dam', query: { ...router.currentRoute.value.query, q: localQuery.value } })
    } else {
      handleViewAll()
    }
    isFocused.value = false
    searchInput.value?.blur()
  }
}

function handleResultSelect(assetId: number) {
  emit('result-selected', assetId)
  router.push(`/dam/assets/${assetId}`)
  localQuery.value = ''
  searchStore.clearSearch()
  isFocused.value = false
  searchInput.value?.blur()
}

function handleViewAll() {
  if (!debouncedQuery.value) return
  if (props.historySource === 'dam') {
    damSearch.setSearch(localQuery.value)
    damSearch.submitSearchNow()
    router.push({ path: '/dam', query: { ...router.currentRoute.value.query, q: localQuery.value } })
  } else {
    router.push({
      path: '/dam/search',
      query: { q: debouncedQuery.value }
    })
  }
  isFocused.value = false
  searchInput.value?.blur()
}

function selectRecentSearch(query: string) {
  localQuery.value = query
  if (props.historySource === 'dam') {
    damSearch.applySearchFromHistory(query)
  }
  searchInput.value?.focus()
}

function scrollToSelected() {
  nextTick(() => {
    const resultsContainer = document.getElementById(`search-results-${searchId.value}`)
    if (resultsContainer && selectedIndex.value >= 0) {
      const selectedElement = resultsContainer.querySelector(
        `[data-result-index="${selectedIndex.value}"]`
      )
      if (selectedElement) {
        selectedElement.scrollIntoView({ block: 'nearest', behavior: 'smooth' })
      }
    }
  })
}

// Keyboard shortcut: Ctrl+K
function handleKeyDown(event: KeyboardEvent) {
  if ((event.ctrlKey || event.metaKey) && event.key === 'k') {
    event.preventDefault()
    searchInput.value?.focus()
  }
}

// Click outside to close
onClickOutside(searchContainer, () => {
  isFocused.value = false
})

onMounted(() => {
  document.addEventListener('keydown', handleKeyDown)
  if (props.autofocus) {
    searchInput.value?.focus()
  }
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeyDown)
})
</script>

<style scoped>
/* Additional styles if needed */
</style>

