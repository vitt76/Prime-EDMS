<template>
  <!-- Filter button variant (placed next to search) -->
  <button
    v-if="variant === 'filter'"
    type="button"
    class="relative text-gray-500 hover:text-gray-900 hover:bg-gray-100 rounded-lg p-2 transition-colors"
    :aria-label="`Фильтры${activeFiltersCount > 0 ? ` (${activeFiltersCount})` : ''}`"
    @click="$emit('toggle-filters')"
    title="Фильтры"
  >
    <FunnelIcon class="w-5 h-5" />
    <span
      v-if="activeFiltersCount > 0"
      class="absolute -top-0.5 -right-0.5 min-w-4 h-4 px-1 rounded-full
             bg-red-500 text-white text-[10px] font-semibold leading-4 text-center"
    >
      {{ activeFiltersCount > 9 ? '9+' : activeFiltersCount }}
    </span>
  </button>

  <!-- Controls variant (placed in header right actions) -->
  <div v-else class="flex items-center gap-1">
    <!-- View options -->
    <div class="relative" ref="viewRef">
      <button
        type="button"
        class="text-gray-500 hover:text-gray-900 hover:bg-gray-100 rounded-lg p-2 transition-colors"
        :class="isViewOpen ? 'bg-gray-100 text-gray-900' : ''"
        aria-label="Параметры вида"
        @click="toggleView"
        title="Параметры вида"
      >
        <AdjustmentsHorizontalIcon class="w-5 h-5" />
      </button>

      <Transition
        enter-active-class="transition ease-out duration-100"
        enter-from-class="transform opacity-0 scale-95"
        enter-to-class="transform opacity-100 scale-100"
        leave-active-class="transition ease-in duration-75"
        leave-from-class="transform opacity-100 scale-100"
        leave-to-class="transform opacity-0 scale-95"
      >
        <div
          v-if="isViewOpen"
          class="absolute right-0 mt-2 w-[min(16rem,calc(100vw-1rem))] bg-white rounded-xl shadow-lg border border-gray-200 z-50
                 max-h-[calc(100vh-6rem)] overflow-auto"
        >
          <div class="px-4 py-3 border-b border-gray-100">
            <p class="text-xs font-semibold text-gray-500 uppercase tracking-wide">Плотность</p>
            <div class="mt-2 inline-flex rounded-lg bg-gray-100 p-1">
              <button
                type="button"
                class="px-3 py-1.5 text-sm font-medium rounded-md transition-colors"
                :class="density === 'compact' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-600 hover:text-gray-900'"
                @click="$emit('update:density', 'compact')"
              >
                Компактно
              </button>
              <button
                type="button"
                class="px-3 py-1.5 text-sm font-medium rounded-md transition-colors"
                :class="density === 'comfortable' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-600 hover:text-gray-900'"
                @click="$emit('update:density', 'comfortable')"
              >
                Комфортно
              </button>
            </div>
          </div>

          <div class="px-4 py-3">
            <p class="text-xs font-semibold text-gray-500 uppercase tracking-wide">Раскладка</p>
            <div class="mt-2 grid grid-cols-2 gap-2">
              <button
                type="button"
                class="flex items-center gap-2 px-3 py-2 rounded-lg border text-sm transition-colors"
                :class="layout === 'grid' ? 'border-indigo-200 bg-indigo-50 text-indigo-700' : 'border-gray-200 text-gray-700 hover:bg-gray-50'"
                @click="$emit('update:layout', 'grid')"
              >
                <Squares2X2Icon class="w-4 h-4" />
                Сетка
              </button>
              <button
                type="button"
                class="flex items-center gap-2 px-3 py-2 rounded-lg border text-sm transition-colors"
                :class="layout === 'masonry' ? 'border-indigo-200 bg-indigo-50 text-indigo-700' : 'border-gray-200 text-gray-700 hover:bg-gray-50'"
                @click="$emit('update:layout', 'masonry')"
              >
                <ViewColumnsIcon class="w-4 h-4" />
                Мозаика
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </div>

    <!-- Sort dropdown -->
    <div class="relative" ref="sortRef">
      <button
        type="button"
        class="flex items-center gap-2 text-gray-500 hover:text-gray-900 hover:bg-gray-100 rounded-lg p-2 transition-colors"
        :class="isSortOpen ? 'bg-gray-100 text-gray-900' : ''"
        aria-label="Сортировка"
        @click="toggleSort"
        title="Сортировка"
      >
        <ArrowsUpDownIcon class="w-5 h-5" />
        <span class="hidden lg:inline text-sm font-medium">
          Сортировка: {{ sortLabel }}
        </span>
        <ChevronDownIcon class="w-4 h-4 hidden lg:inline transition-transform" :class="isSortOpen ? 'rotate-180' : ''" />
      </button>

      <Transition
        enter-active-class="transition ease-out duration-100"
        enter-from-class="transform opacity-0 scale-95"
        enter-to-class="transform opacity-100 scale-100"
        leave-active-class="transition ease-in duration-75"
        leave-from-class="transform opacity-100 scale-100"
        leave-to-class="transform opacity-0 scale-95"
      >
        <div
          v-if="isSortOpen"
          class="absolute right-0 mt-2 w-48 bg-white rounded-xl shadow-lg border border-gray-200 z-50 overflow-hidden"
        >
          <button
            v-for="opt in sortOptions"
            :key="opt.value"
            type="button"
            class="w-full px-4 py-2.5 text-left text-sm transition-colors flex items-center justify-between"
            :class="sort === opt.value ? 'bg-indigo-50 text-indigo-700 font-semibold' : 'hover:bg-gray-50 text-gray-800'"
            @click="selectSort(opt.value)"
          >
            <span>{{ opt.label }}</span>
            <CheckIcon v-if="sort === opt.value" class="w-4 h-4" />
          </button>
        </div>
      </Transition>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import {
  AdjustmentsHorizontalIcon,
  FunnelIcon,
  ArrowsUpDownIcon,
  ChevronDownIcon,
  CheckIcon,
  Squares2X2Icon,
  ViewColumnsIcon
} from '@heroicons/vue/24/outline'

type Density = 'compact' | 'comfortable'
type Layout = 'grid' | 'masonry'
type Sort = 'date' | 'name' | 'size'

interface Props {
  variant: 'filter' | 'controls'
  density: Density
  layout: Layout
  sort: Sort
  activeFiltersCount: number
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:density': [value: Density]
  'update:layout': [value: Layout]
  'update:sort': [value: Sort]
  'toggle-filters': []
}>()

const isViewOpen = ref(false)
const isSortOpen = ref(false)
const viewRef = ref<HTMLElement | null>(null)
const sortRef = ref<HTMLElement | null>(null)

const sortOptions = [
  { value: 'date' as const, label: 'Дата (сначала новые)' },
  { value: 'name' as const, label: 'Имя (А → Я)' },
  { value: 'size' as const, label: 'Размер (сначала большие)' }
]

const sortLabel = computed(() => {
  return sortOptions.find(o => o.value === props.sort)?.label ?? 'Дата'
})

const density = computed(() => props.density)
const layout = computed(() => props.layout)
const sort = computed(() => props.sort)
const activeFiltersCount = computed(() => props.activeFiltersCount)

function toggleView() {
  isViewOpen.value = !isViewOpen.value
  if (isViewOpen.value) isSortOpen.value = false
}

function toggleSort() {
  isSortOpen.value = !isSortOpen.value
  if (isSortOpen.value) isViewOpen.value = false
}

function selectSort(value: Sort) {
  isSortOpen.value = false
  emit('update:sort', value)
}

function onGlobalClick(e: MouseEvent) {
  const target = e.target as Node
  if (isViewOpen.value && viewRef.value && !viewRef.value.contains(target)) {
    isViewOpen.value = false
  }
  if (isSortOpen.value && sortRef.value && !sortRef.value.contains(target)) {
    isSortOpen.value = false
  }
}

onMounted(() => {
  // IMPORTANT: bubble phase is enough and avoids closing dropdowns before inner clicks run.
  window.addEventListener('click', onGlobalClick)
})

onBeforeUnmount(() => {
  window.removeEventListener('click', onGlobalClick)
})
</script>

