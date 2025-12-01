<template>
  <div
    class="h-16 px-6 flex items-center justify-between border-b border-neutral-200 
           bg-white/90 backdrop-blur-sm sticky top-0 z-40"
  >
    <!-- ═══════════════════════════════════════════════════════════════════════
         ZONE 1: LEFT — Search & Context (Global Omnibox)
         ═══════════════════════════════════════════════════════════════════════ -->
    <div class="flex items-center gap-4">
      <div class="relative w-[400px]">
        <div
          class="flex items-center h-10 bg-gray-100 rounded-lg px-3 
                 focus-within:ring-2 focus-within:ring-indigo-500 focus-within:bg-white
                 transition-all duration-200"
        >
          <!-- Search Icon (Left) -->
          <svg
            class="w-5 h-5 text-gray-400 flex-shrink-0"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            />
          </svg>

          <!-- Search Input -->
          <input
            type="text"
            :value="searchQuery"
            @input="handleSearchInput"
            placeholder="Search assets, tags, metadata..."
            class="flex-1 h-full bg-transparent border-none outline-none px-3 
                   text-sm text-gray-900 placeholder-gray-500"
          />

          <!-- Filter Adjustment Icon (Right, inside input) -->
          <button
            type="button"
            class="p-1.5 rounded-md hover:bg-gray-200 transition-colors"
            @click="emit('toggleFilters')"
            title="Advanced filters"
          >
            <svg
              class="w-4 h-4 text-gray-500"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4"
              />
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- ═══════════════════════════════════════════════════════════════════════
         ZONE 2: RIGHT — Actions & View Controls
         ═══════════════════════════════════════════════════════════════════════ -->
    <div class="flex items-center gap-4">
      <!-- Group 1: View Controls (Segment Control) -->
      <div class="flex items-center bg-gray-100 p-1 rounded-lg">
        <button
          type="button"
          :class="[
            'flex items-center justify-center w-9 h-8 rounded-md transition-all duration-200',
            viewMode === 'grid'
              ? 'bg-white shadow-sm text-gray-900'
              : 'text-gray-500 hover:text-gray-700'
          ]"
          @click="setViewMode('grid')"
          title="Grid view"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z"
            />
          </svg>
        </button>
        <button
          type="button"
          :class="[
            'flex items-center justify-center w-9 h-8 rounded-md transition-all duration-200',
            viewMode === 'list'
              ? 'bg-white shadow-sm text-gray-900'
              : 'text-gray-500 hover:text-gray-700'
          ]"
          @click="setViewMode('list')"
          title="List view"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M4 6h16M4 10h16M4 14h16M4 18h16"
            />
          </svg>
        </button>
      </div>

      <!-- Group 2: Sorting Dropdown -->
      <div class="relative" ref="sortDropdownRef">
        <button
          type="button"
          class="flex items-center gap-1.5 text-sm text-gray-600 hover:text-gray-900 
                 transition-colors px-2 py-1.5 rounded-md hover:bg-gray-100"
          @click="toggleSortDropdown"
        >
          <span>Sort: {{ currentSortLabel }}</span>
          <svg
            class="w-4 h-4 transition-transform duration-200"
            :class="{ 'rotate-180': isSortDropdownOpen }"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
          </svg>
        </button>

        <!-- Dropdown Menu -->
        <Transition
          enter-active-class="transition ease-out duration-100"
          enter-from-class="transform opacity-0 scale-95"
          enter-to-class="transform opacity-100 scale-100"
          leave-active-class="transition ease-in duration-75"
          leave-from-class="transform opacity-100 scale-100"
          leave-to-class="transform opacity-0 scale-95"
        >
          <div
            v-if="isSortDropdownOpen"
            class="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 
                   py-1 z-50"
          >
            <button
              v-for="option in sortOptions"
              :key="option.value"
              type="button"
              class="w-full text-left px-4 py-2 text-sm hover:bg-gray-50 transition-colors"
              :class="[
                sortBy === option.value
                  ? 'text-indigo-600 bg-indigo-50 font-medium'
                  : 'text-gray-700'
              ]"
              @click="selectSort(option.value)"
            >
              {{ option.label }}
            </button>
          </div>
        </Transition>
      </div>

      <!-- Divider -->
      <div class="h-6 w-px bg-gray-200" />

      <!-- Group 3: Primary Action — Upload Media (THE STAR) -->
      <button
        type="button"
        class="inline-flex items-center gap-2 px-5 py-2.5 
               bg-indigo-600 hover:bg-indigo-700 
               text-white font-medium text-sm rounded-lg
               shadow-md hover:shadow-lg 
               transition-all duration-200
               focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
        @click="emit('upload')"
      >
        <!-- Cloud Arrow Up Icon -->
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
          />
        </svg>
        <span>Upload Media</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'

// ═══════════════════════════════════════════════════════════════════════════════
// Props
// ═══════════════════════════════════════════════════════════════════════════════
interface Props {
  searchQuery?: string
  viewMode?: 'grid' | 'list'
  sortBy?: string
}

const props = withDefaults(defineProps<Props>(), {
  searchQuery: '',
  viewMode: 'grid',
  sortBy: 'newest'
})

// ═══════════════════════════════════════════════════════════════════════════════
// Emits
// ═══════════════════════════════════════════════════════════════════════════════
const emit = defineEmits<{
  'update:searchQuery': [value: string]
  'update:viewMode': [value: 'grid' | 'list']
  'update:sortBy': [value: string]
  upload: []
  toggleFilters: []
}>()

// ═══════════════════════════════════════════════════════════════════════════════
// State
// ═══════════════════════════════════════════════════════════════════════════════
const isSortDropdownOpen = ref(false)
const sortDropdownRef = ref<HTMLElement | null>(null)

const sortOptions = [
  { value: 'newest', label: 'Newest first' },
  { value: 'oldest', label: 'Oldest first' },
  { value: 'name_asc', label: 'Name A → Z' },
  { value: 'name_desc', label: 'Name Z → A' },
  { value: 'size_desc', label: 'Largest first' },
  { value: 'size_asc', label: 'Smallest first' }
]

// ═══════════════════════════════════════════════════════════════════════════════
// Computed
// ═══════════════════════════════════════════════════════════════════════════════
const currentSortLabel = computed(() => {
  const option = sortOptions.find(o => o.value === props.sortBy)
  return option?.label ?? 'Newest'
})

// ═══════════════════════════════════════════════════════════════════════════════
// Handlers
// ═══════════════════════════════════════════════════════════════════════════════
function handleSearchInput(event: Event) {
  const target = event.target as HTMLInputElement
  emit('update:searchQuery', target.value)
}

function setViewMode(mode: 'grid' | 'list') {
  emit('update:viewMode', mode)
}

function toggleSortDropdown() {
  isSortDropdownOpen.value = !isSortDropdownOpen.value
}

function selectSort(value: string) {
  emit('update:sortBy', value)
  isSortDropdownOpen.value = false
}

// Close dropdown on outside click
function handleClickOutside(event: MouseEvent) {
  if (sortDropdownRef.value && !sortDropdownRef.value.contains(event.target as Node)) {
    isSortDropdownOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

