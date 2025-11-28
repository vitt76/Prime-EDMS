<template>
  <div class="smart-search relative" ref="containerRef">
    <!-- Search Input -->
    <div 
      :class="[
        'relative flex items-center gap-2 bg-neutral-100 rounded-xl transition-all duration-200',
        isOpen ? 'ring-2 ring-primary-500 bg-white shadow-lg' : 'hover:bg-neutral-200'
      ]"
    >
      <!-- Search Icon -->
      <div class="pl-4 text-neutral-400">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
      </div>
      
      <!-- Active Filters (Pills) -->
      <div v-if="Object.keys(activeFilters).length > 0" class="flex items-center gap-1 py-1">
        <span
          v-for="(value, key) in activeFilters"
          :key="key"
          class="inline-flex items-center gap-1 px-2 py-0.5 bg-primary-100 text-primary-700 text-xs font-medium rounded-full"
        >
          {{ getFilterLabel(key as string, value) }}
          <button 
            type="button"
            @click.stop="removeFilter(key as string)"
            class="ml-0.5 hover:text-primary-900"
          >
            <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </span>
      </div>
      
      <!-- Input -->
      <input
        ref="inputRef"
        v-model="searchQuery"
        type="text"
        :placeholder="placeholder"
        class="flex-1 bg-transparent py-3 pr-4 text-sm text-neutral-900 placeholder-neutral-500 outline-none"
        @focus="handleFocus"
        @blur="handleBlur"
        @input="handleInput"
        @keydown="handleKeydown"
        autocomplete="off"
        role="combobox"
        :aria-expanded="isOpen"
        aria-haspopup="listbox"
        aria-autocomplete="list"
      />
      
      <!-- Filter Button -->
      <button
        type="button"
        @click.stop="toggleFiltersDropdown"
        :class="[
          'p-2 mr-1 rounded-lg transition-colors',
          showFiltersDropdown ? 'bg-primary-100 text-primary-600' : 'text-neutral-500 hover:bg-neutral-200 hover:text-neutral-700'
        ]"
        title="Фильтры"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
        </svg>
      </button>
      
      <!-- Keyboard Shortcut Hint -->
      <div v-if="!isOpen && !searchQuery" class="pr-3 text-neutral-400 text-xs hidden sm:flex items-center gap-1">
        <kbd class="px-1.5 py-0.5 bg-neutral-200 rounded text-[10px] font-mono">Ctrl</kbd>
        <span>+</span>
        <kbd class="px-1.5 py-0.5 bg-neutral-200 rounded text-[10px] font-mono">K</kbd>
      </div>
      
      <!-- Clear Button -->
      <button
        v-if="searchQuery || Object.keys(activeFilters).length > 0"
        type="button"
        @click.stop="clearAll"
        class="p-2 mr-1 text-neutral-400 hover:text-neutral-600 rounded-lg hover:bg-neutral-200 transition-colors"
        title="Очистить"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>
    
    <!-- Dropdown -->
    <Transition
      enter-active-class="transition ease-out duration-200"
      enter-from-class="opacity-0 translate-y-1"
      enter-to-class="opacity-100 translate-y-0"
      leave-active-class="transition ease-in duration-150"
      leave-from-class="opacity-100 translate-y-0"
      leave-to-class="opacity-0 translate-y-1"
    >
      <div
        v-if="isOpen"
        class="absolute top-full left-0 right-0 mt-2 bg-white rounded-xl shadow-2xl border border-neutral-200 overflow-hidden z-50"
        @mousedown.prevent
      >
        <!-- Filters Dropdown -->
        <div v-if="showFiltersDropdown" class="p-4 border-b border-neutral-100">
          <div class="grid grid-cols-2 sm:grid-cols-3 gap-3">
            <div v-for="filter in filters" :key="filter.key" class="space-y-1">
              <label class="block text-xs font-medium text-neutral-600">{{ filter.label }}</label>
              <select
                :value="activeFilters[filter.key] || ''"
                @change="setFilter(filter.key, ($event.target as HTMLSelectElement).value)"
                class="w-full px-2 py-1.5 text-sm border border-neutral-200 rounded-lg bg-white focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              >
                <option value="">Все</option>
                <option v-for="opt in filter.options" :key="opt.value" :value="opt.value">
                  {{ opt.label }}
                  <span v-if="opt.count">({{ opt.count }})</span>
                </option>
              </select>
            </div>
          </div>
        </div>
        
        <!-- Recent Searches -->
        <div v-if="!searchQuery && recentSearches.length > 0" class="p-2">
          <div class="flex items-center justify-between px-3 py-1.5">
            <span class="text-xs font-medium text-neutral-500 uppercase tracking-wider">Недавние поиски</span>
            <button 
              type="button"
              @click="clearRecentSearches"
              class="text-xs text-neutral-400 hover:text-neutral-600"
            >
              Очистить
            </button>
          </div>
          <ul role="listbox">
            <li
              v-for="(item, index) in recentSearches"
              :key="item.id"
              :class="[
                'flex items-center gap-3 px-3 py-2 rounded-lg cursor-pointer transition-colors',
                highlightedIndex === index ? 'bg-primary-50 text-primary-700' : 'hover:bg-neutral-50'
              ]"
              @click="selectRecentSearch(item)"
              @mouseenter="highlightedIndex = index"
              role="option"
              :aria-selected="highlightedIndex === index"
            >
              <svg class="w-4 h-4 text-neutral-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span class="flex-1 text-sm">{{ item.query }}</span>
              <span class="text-xs text-neutral-400">{{ item.resultCount }} рез.</span>
              <button 
                type="button"
                @click.stop="removeRecentSearchItem(item.id)"
                class="p-1 text-neutral-300 hover:text-neutral-500 rounded"
              >
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </li>
          </ul>
        </div>
        
        <!-- Suggestions -->
        <div v-else-if="suggestions.length > 0" class="p-2 max-h-[400px] overflow-y-auto">
          <ul role="listbox">
            <li
              v-for="(item, index) in suggestions"
              :key="item.id"
              :class="[
                'flex items-center gap-3 px-3 py-2 rounded-lg cursor-pointer transition-colors',
                highlightedIndex === index ? 'bg-primary-50' : 'hover:bg-neutral-50'
              ]"
              @click="selectSuggestion(item)"
              @mouseenter="highlightedIndex = index"
              role="option"
              :aria-selected="highlightedIndex === index"
            >
              <!-- Icon or Thumbnail -->
              <div class="flex-shrink-0">
                <img
                  v-if="item.thumbnail"
                  :src="item.thumbnail"
                  :alt="item.label"
                  class="w-8 h-8 rounded object-cover"
                />
                <div v-else :class="getSuggestionIconClass(item.type)">
                  <component :is="getSuggestionIcon(item.type)" class="w-4 h-4" />
                </div>
              </div>
              
              <!-- Content -->
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-neutral-900 truncate">{{ item.label }}</p>
                <p v-if="item.subtitle" class="text-xs text-neutral-500 truncate">{{ item.subtitle }}</p>
              </div>
              
              <!-- Type Badge -->
              <span :class="getSuggestionBadgeClass(item.type)">
                {{ getSuggestionTypeLabel(item.type) }}
              </span>
            </li>
          </ul>
        </div>
        
        <!-- Empty State -->
        <div v-else-if="searchQuery && searchQuery.length >= 2" class="p-8 text-center">
          <svg class="w-12 h-12 mx-auto text-neutral-300 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <p class="text-sm text-neutral-500">Нет предложений для "{{ searchQuery }}"</p>
          <p class="text-xs text-neutral-400 mt-1">Нажмите Enter для поиска</p>
        </div>
        
        <!-- Help Hint -->
        <div v-else-if="!searchQuery" class="p-4 text-center border-t border-neutral-100">
          <p class="text-xs text-neutral-400">
            Начните вводить для поиска • Используйте <kbd class="px-1 py-0.5 bg-neutral-100 rounded text-[10px]">↑</kbd> <kbd class="px-1 py-0.5 bg-neutral-100 rounded text-[10px]">↓</kbd> для навигации • <kbd class="px-1 py-0.5 bg-neutral-100 rounded text-[10px]">Enter</kbd> для выбора
          </p>
        </div>
        
        <!-- Footer with Search Button -->
        <div v-if="searchQuery" class="p-2 border-t border-neutral-100 bg-neutral-50">
          <button
            type="button"
            @click="executeSearch"
            class="w-full flex items-center justify-center gap-2 px-4 py-2 bg-primary-600 text-white text-sm font-medium rounded-lg hover:bg-primary-700 transition-colors"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            Искать "{{ searchQuery }}"
          </button>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useDebounceFn, onClickOutside, onKeyStroke } from '@vueuse/core'
import {
  getSearchSuggestions,
  getRecentSearches,
  addRecentSearch,
  clearRecentSearches as clearRecent,
  removeRecentSearch,
  SEARCH_FILTERS,
  buildSearchUrl,
  type SearchSuggestion,
  type RecentSearch,
  type SearchFilter
} from '@/mocks/search'

// ============================================================================
// PROPS & EMITS
// ============================================================================

interface Props {
  placeholder?: string
  initialQuery?: string
  initialFilters?: Record<string, string>
}

const props = withDefaults(defineProps<Props>(), {
  placeholder: 'Поиск... (Ctrl+K)',
  initialQuery: '',
  initialFilters: () => ({})
})

const emit = defineEmits<{
  search: [query: string, filters: Record<string, string>]
  resultSelected: [result: SearchSuggestion]
}>()

// ============================================================================
// REFS & STATE
// ============================================================================

const router = useRouter()
const containerRef = ref<HTMLElement | null>(null)
const inputRef = ref<HTMLInputElement | null>(null)

const searchQuery = ref(props.initialQuery)
const activeFilters = ref<Record<string, string>>({ ...props.initialFilters })
const isOpen = ref(false)
const showFiltersDropdown = ref(false)
const highlightedIndex = ref(-1)

const suggestions = ref<SearchSuggestion[]>([])
const recentSearches = ref<RecentSearch[]>([])
const filters = ref<SearchFilter[]>(SEARCH_FILTERS)

// ============================================================================
// COMPUTED
// ============================================================================

const totalItems = computed(() => {
  if (searchQuery.value) {
    return suggestions.value.length
  }
  return recentSearches.value.length
})

// ============================================================================
// METHODS
// ============================================================================

function handleFocus() {
  isOpen.value = true
  highlightedIndex.value = -1
  
  if (!searchQuery.value) {
    recentSearches.value = getRecentSearches()
  }
}

function handleBlur() {
  // Delay close to allow click events
  setTimeout(() => {
    // Only close if click wasn't inside dropdown
  }, 200)
}

const handleInput = useDebounceFn(() => {
  if (searchQuery.value && searchQuery.value.length >= 2) {
    suggestions.value = getSearchSuggestions(searchQuery.value)
  } else {
    suggestions.value = []
    recentSearches.value = getRecentSearches()
  }
  highlightedIndex.value = -1
}, 150)

function handleKeydown(event: KeyboardEvent) {
  switch (event.key) {
    case 'ArrowDown':
      event.preventDefault()
      if (highlightedIndex.value < totalItems.value - 1) {
        highlightedIndex.value++
      } else {
        highlightedIndex.value = 0
      }
      break
      
    case 'ArrowUp':
      event.preventDefault()
      if (highlightedIndex.value > 0) {
        highlightedIndex.value--
      } else {
        highlightedIndex.value = totalItems.value - 1
      }
      break
      
    case 'Enter':
      event.preventDefault()
      if (highlightedIndex.value >= 0) {
        if (searchQuery.value && suggestions.value[highlightedIndex.value]) {
          selectSuggestion(suggestions.value[highlightedIndex.value])
        } else if (!searchQuery.value && recentSearches.value[highlightedIndex.value]) {
          selectRecentSearch(recentSearches.value[highlightedIndex.value])
        }
      } else if (searchQuery.value) {
        executeSearch()
      }
      break
      
    case 'Escape':
      event.preventDefault()
      isOpen.value = false
      showFiltersDropdown.value = false
      inputRef.value?.blur()
      break
      
    case 'Tab':
      if (showFiltersDropdown.value) {
        // Allow tab navigation in filters
      } else {
        isOpen.value = false
      }
      break
  }
}

function selectSuggestion(item: SearchSuggestion) {
  if (item.type === 'filter' && item.filter) {
    setFilter(item.filter.key, item.filter.value)
    searchQuery.value = ''
  } else if (item.type === 'asset') {
    // Navigate to asset detail
    router.push(`/dam/assets/${item.id.replace('a', '')}`)
    isOpen.value = false
  } else if (item.type === 'collection') {
    // Navigate to collection
    router.push(`/collections/${item.id.replace('c', '')}`)
    isOpen.value = false
  } else {
    searchQuery.value = item.label
    executeSearch()
  }
  
  emit('resultSelected', item)
}

function selectRecentSearch(item: RecentSearch) {
  searchQuery.value = item.query
  executeSearch()
}

function executeSearch() {
  if (!searchQuery.value && Object.keys(activeFilters.value).length === 0) {
    return
  }
  
  addRecentSearch(searchQuery.value, Math.floor(Math.random() * 500) + 10)
  
  const url = buildSearchUrl(searchQuery.value, activeFilters.value)
  router.push(url)
  
  isOpen.value = false
  emit('search', searchQuery.value, activeFilters.value)
}

function toggleFiltersDropdown() {
  showFiltersDropdown.value = !showFiltersDropdown.value
  if (showFiltersDropdown.value) {
    isOpen.value = true
  }
}

function setFilter(key: string, value: string) {
  if (value) {
    activeFilters.value[key] = value
  } else {
    delete activeFilters.value[key]
  }
}

function removeFilter(key: string) {
  delete activeFilters.value[key]
  activeFilters.value = { ...activeFilters.value }
}

function clearAll() {
  searchQuery.value = ''
  activeFilters.value = {}
  suggestions.value = []
  recentSearches.value = getRecentSearches()
  highlightedIndex.value = -1
  inputRef.value?.focus()
}

function clearRecentSearches() {
  clearRecent()
  recentSearches.value = []
}

function removeRecentSearchItem(id: string) {
  removeRecentSearch(id)
  recentSearches.value = getRecentSearches()
}

function getFilterLabel(key: string, value: string): string {
  const filter = filters.value.find(f => f.key === key)
  const option = filter?.options?.find(o => o.value === value)
  return option?.label || `${key}: ${value}`
}

function getSuggestionIcon(type: SearchSuggestion['type']) {
  const icons = {
    query: { template: '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>' },
    tag: { template: '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" /></svg>' },
    collection: { template: '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" /></svg>' },
    asset: { template: '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>' },
    filter: { template: '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" /></svg>' }
  }
  return icons[type] || icons.query
}

function getSuggestionIconClass(type: SearchSuggestion['type']): string {
  const classes = {
    query: 'w-8 h-8 rounded-lg bg-neutral-100 text-neutral-500 flex items-center justify-center',
    tag: 'w-8 h-8 rounded-lg bg-purple-100 text-purple-600 flex items-center justify-center',
    collection: 'w-8 h-8 rounded-lg bg-blue-100 text-blue-600 flex items-center justify-center',
    asset: 'w-8 h-8 rounded-lg bg-green-100 text-green-600 flex items-center justify-center',
    filter: 'w-8 h-8 rounded-lg bg-amber-100 text-amber-600 flex items-center justify-center'
  }
  return classes[type] || classes.query
}

function getSuggestionBadgeClass(type: SearchSuggestion['type']): string {
  const classes = {
    query: 'px-2 py-0.5 text-[10px] font-medium rounded bg-neutral-100 text-neutral-600',
    tag: 'px-2 py-0.5 text-[10px] font-medium rounded bg-purple-100 text-purple-700',
    collection: 'px-2 py-0.5 text-[10px] font-medium rounded bg-blue-100 text-blue-700',
    asset: 'px-2 py-0.5 text-[10px] font-medium rounded bg-green-100 text-green-700',
    filter: 'px-2 py-0.5 text-[10px] font-medium rounded bg-amber-100 text-amber-700'
  }
  return classes[type] || classes.query
}

function getSuggestionTypeLabel(type: SearchSuggestion['type']): string {
  const labels = {
    query: 'Запрос',
    tag: 'Тег',
    collection: 'Коллекция',
    asset: 'Актив',
    filter: 'Фильтр'
  }
  return labels[type] || type
}

// ============================================================================
// GLOBAL KEYBOARD SHORTCUT
// ============================================================================

function handleGlobalKeydown(event: KeyboardEvent) {
  // Ctrl+K or Cmd+K to focus search
  if ((event.ctrlKey || event.metaKey) && event.key === 'k') {
    event.preventDefault()
    inputRef.value?.focus()
    isOpen.value = true
  }
}

// Click outside to close
onClickOutside(containerRef, () => {
  isOpen.value = false
  showFiltersDropdown.value = false
})

// ============================================================================
// LIFECYCLE
// ============================================================================

onMounted(() => {
  document.addEventListener('keydown', handleGlobalKeydown)
  recentSearches.value = getRecentSearches()
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleGlobalKeydown)
})

// Watch for prop changes
watch(() => props.initialQuery, (val) => {
  searchQuery.value = val
})

watch(() => props.initialFilters, (val) => {
  activeFilters.value = { ...val }
}, { deep: true })
</script>

<style scoped>
.smart-search {
  width: 100%;
}

/* Custom scrollbar for suggestions */
.smart-search ::-webkit-scrollbar {
  width: 6px;
}

.smart-search ::-webkit-scrollbar-track {
  background: transparent;
}

.smart-search ::-webkit-scrollbar-thumb {
  background: #e5e7eb;
  border-radius: 3px;
}

.smart-search ::-webkit-scrollbar-thumb:hover {
  background: #d1d5db;
}
</style>

