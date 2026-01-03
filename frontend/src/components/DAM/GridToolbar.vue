<template>
  <div
    class="sticky top-0 z-40 bg-neutral-0/95 backdrop-blur-md border-b border-neutral-200"
    role="toolbar"
    aria-label="Панель управления видом"
  >
    <div class="flex items-center justify-between gap-4 px-4 py-3">
      <!-- Left: View controls -->
      <div class="flex items-center gap-3">
        <!-- Density switcher -->
        <div class="inline-flex rounded-xl bg-neutral-100 p-1" aria-label="Плотность">
          <button
            type="button"
            class="px-3 py-1.5 text-sm font-medium rounded-lg transition-colors"
            :class="density === 'compact' ? 'bg-white text-neutral-900 shadow-sm' : 'text-neutral-600 hover:text-neutral-900'"
            @click="$emit('update:density', 'compact')"
          >
            Compact
          </button>
          <button
            type="button"
            class="px-3 py-1.5 text-sm font-medium rounded-lg transition-colors"
            :class="density === 'comfortable' ? 'bg-white text-neutral-900 shadow-sm' : 'text-neutral-600 hover:text-neutral-900'"
            @click="$emit('update:density', 'comfortable')"
          >
            Comfortable
          </button>
        </div>

        <!-- Layout switcher -->
        <div class="inline-flex rounded-xl bg-neutral-100 p-1" aria-label="Раскладка">
          <button
            type="button"
            class="w-10 h-9 rounded-lg transition-colors flex items-center justify-center"
            :class="layout === 'grid' ? 'bg-white text-neutral-900 shadow-sm' : 'text-neutral-600 hover:text-neutral-900'"
            @click="$emit('update:layout', 'grid')"
            title="Grid"
            aria-label="Grid"
          >
            <Squares2X2Icon class="w-5 h-5" />
          </button>
          <button
            type="button"
            class="w-10 h-9 rounded-lg transition-colors flex items-center justify-center"
            :class="layout === 'masonry' ? 'bg-white text-neutral-900 shadow-sm' : 'text-neutral-600 hover:text-neutral-900'"
            @click="$emit('update:layout', 'masonry')"
            title="Masonry"
            aria-label="Masonry"
          >
            <ViewColumnsIcon class="w-5 h-5" />
          </button>
          <button
            type="button"
            class="w-10 h-9 rounded-lg transition-colors flex items-center justify-center opacity-50 cursor-not-allowed"
            title="List (скоро)"
            aria-label="List (скоро)"
            disabled
          >
            <Bars3Icon class="w-5 h-5" />
          </button>
        </div>
      </div>

      <!-- Right: Sort + count -->
      <div class="flex items-center gap-3">
        <div class="text-sm text-neutral-600">
          Показано <span class="font-semibold text-neutral-900">{{ shownCount }}</span>
          <span v-if="typeof totalCount === 'number'"> из <span class="font-semibold text-neutral-900">{{ totalCount }}</span></span>
        </div>

        <!-- Sort dropdown -->
        <div class="relative" ref="sortRef">
          <button
            type="button"
            class="inline-flex items-center gap-2 px-3 py-2 rounded-xl bg-neutral-100 hover:bg-neutral-200
                   text-sm font-medium text-neutral-800 transition-colors"
            @click="toggleSort"
            :aria-expanded="isSortOpen"
            aria-label="Сортировка"
          >
            <ArrowsUpDownIcon class="w-4 h-4 text-neutral-500" />
            <span class="hidden sm:inline">{{ sortLabel }}</span>
            <ChevronDownIcon class="w-4 h-4 text-neutral-500 transition-transform" :class="isSortOpen ? 'rotate-180' : ''" />
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
              class="absolute right-0 mt-2 w-48 bg-white rounded-xl shadow-lg border border-neutral-200 z-50 overflow-hidden"
            >
              <button
                v-for="opt in sortOptions"
                :key="opt.value"
                type="button"
                class="w-full px-4 py-2.5 text-left text-sm transition-colors flex items-center justify-between"
                :class="sort === opt.value ? 'bg-primary-50 text-primary-700 font-semibold' : 'hover:bg-neutral-50 text-neutral-800'"
                @click="selectSort(opt.value)"
              >
                <span>{{ opt.label }}</span>
                <CheckIcon v-if="sort === opt.value" class="w-4 h-4" />
              </button>
            </div>
          </Transition>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onBeforeUnmount, ref } from 'vue'
import {
  Squares2X2Icon,
  ViewColumnsIcon,
  Bars3Icon,
  ChevronDownIcon,
  ArrowsUpDownIcon,
  CheckIcon
} from '@heroicons/vue/24/outline'

type Density = 'compact' | 'comfortable'
type Layout = 'grid' | 'masonry' | 'list'
type Sort = 'date' | 'name' | 'size'

interface Props {
  density: Density
  layout: Exclude<Layout, 'list'> // list reserved for future
  sort: Sort
  shownCount: number
  totalCount?: number
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:density': [value: Density]
  'update:layout': [value: Exclude<Layout, 'list'>]
  'update:sort': [value: Sort]
}>()

const isSortOpen = ref(false)
const sortRef = ref<HTMLElement | null>(null)

const sortOptions = [
  { value: 'date' as const, label: 'По дате' },
  { value: 'name' as const, label: 'По имени' },
  { value: 'size' as const, label: 'По размеру' }
]

const sortLabel = computed(() => {
  return sortOptions.find(o => o.value === props.sort)?.label ?? 'Сортировка'
})

function toggleSort() {
  isSortOpen.value = !isSortOpen.value
}

function selectSort(value: Sort) {
  isSortOpen.value = false
  emit('update:sort', value)
}

function onGlobalClick(e: MouseEvent) {
  if (!isSortOpen.value) return
  const target = e.target as Node
  if (sortRef.value && !sortRef.value.contains(target)) {
    isSortOpen.value = false
  }
}

onMounted(() => {
  window.addEventListener('click', onGlobalClick, true)
})

onBeforeUnmount(() => {
  window.removeEventListener('click', onGlobalClick, true)
})

const density = computed(() => props.density)
const layout = computed(() => props.layout)
const sort = computed(() => props.sort)
const shownCount = computed(() => props.shownCount)
const totalCount = computed(() => props.totalCount)
</script>

