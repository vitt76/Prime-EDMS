<template>
  <nav
    class="flex items-center justify-between px-4 py-3 bg-neutral-0 dark:bg-neutral-0 border-t border-neutral-300 dark:border-neutral-300"
    aria-label="Pagination"
  >
    <div class="flex items-center gap-2">
      <span class="text-sm text-neutral-600 dark:text-neutral-600">
        Показано {{ startItem }}-{{ endItem }} из {{ total }}
      </span>
    </div>

    <div class="flex items-center gap-2">
      <!-- Previous Button -->
      <button
        :disabled="!hasPrevious"
        :class="[
          'px-3 py-2 text-sm font-medium rounded-md transition-colors',
          hasPrevious
            ? 'text-neutral-700 dark:text-neutral-700 bg-neutral-0 dark:bg-neutral-0 hover:bg-neutral-100 dark:hover:bg-neutral-100 border border-neutral-300 dark:border-neutral-300'
            : 'text-neutral-400 dark:text-neutral-400 bg-neutral-50 dark:bg-neutral-50 cursor-not-allowed border border-neutral-200 dark:border-neutral-200'
        ]"
        @click="handlePrevious"
        aria-label="Предыдущая страница"
      >
        <svg
          class="w-5 h-5"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M15 19l-7-7 7-7"
          />
        </svg>
      </button>

      <!-- Page Numbers -->
      <div class="flex items-center gap-1">
        <button
          v-for="page in visiblePages"
          :key="page"
          :class="[
            'px-3 py-2 text-sm font-medium rounded-md transition-colors',
            page === currentPage
              ? 'bg-primary-500 text-white hover:bg-primary-600'
              : 'text-neutral-700 dark:text-neutral-700 bg-neutral-0 dark:bg-neutral-0 hover:bg-neutral-100 dark:hover:bg-neutral-100 border border-neutral-300 dark:border-neutral-300'
          ]"
          @click="handlePageClick(page)"
          :aria-label="`Страница ${page}`"
          :aria-current="page === currentPage ? 'page' : undefined"
        >
          {{ page }}
        </button>
      </div>

      <!-- Next Button -->
      <button
        :disabled="!hasNext"
        :class="[
          'px-3 py-2 text-sm font-medium rounded-md transition-colors',
          hasNext
            ? 'text-neutral-700 dark:text-neutral-700 bg-neutral-0 dark:bg-neutral-0 hover:bg-neutral-100 dark:hover:bg-neutral-100 border border-neutral-300 dark:border-neutral-300'
            : 'text-neutral-400 dark:text-neutral-400 bg-neutral-50 dark:bg-neutral-50 cursor-not-allowed border border-neutral-200 dark:border-neutral-200'
        ]"
        @click="handleNext"
        aria-label="Следующая страница"
      >
        <svg
          class="w-5 h-5"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M9 5l7 7-7 7"
          />
        </svg>
      </button>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  currentPage: number
  totalItems: number
  pageSize: number
  maxVisiblePages?: number
}

const props = withDefaults(defineProps<Props>(), {
  maxVisiblePages: 5
})

const emit = defineEmits<{
  'update:currentPage': [page: number]
  'page-change': [page: number]
}>()

const totalPages = computed(() => Math.ceil(props.totalItems / props.pageSize))
const hasNext = computed(() => props.currentPage < totalPages.value)
const hasPrevious = computed(() => props.currentPage > 1)

const startItem = computed(() => {
  if (props.totalItems === 0) return 0
  return (props.currentPage - 1) * props.pageSize + 1
})

const endItem = computed(() => {
  const end = props.currentPage * props.pageSize
  return Math.min(end, props.totalItems)
})

const visiblePages = computed(() => {
  const pages: number[] = []
  const maxVisible = props.maxVisiblePages
  const total = totalPages.value
  const current = props.currentPage

  if (total <= maxVisible) {
    // Show all pages if total is less than max visible
    for (let i = 1; i <= total; i++) {
      pages.push(i)
    }
  } else {
    // Calculate start and end of visible range
    let start = Math.max(1, current - Math.floor(maxVisible / 2))
    let end = Math.min(total, start + maxVisible - 1)

    // Adjust start if we're near the end
    if (end - start < maxVisible - 1) {
      start = Math.max(1, end - maxVisible + 1)
    }

    for (let i = start; i <= end; i++) {
      pages.push(i)
    }
  }

  return pages
})

function handlePrevious() {
  if (hasPrevious.value) {
    const newPage = props.currentPage - 1
    emit('update:currentPage', newPage)
    emit('page-change', newPage)
  }
}

function handleNext() {
  if (hasNext.value) {
    const newPage = props.currentPage + 1
    emit('update:currentPage', newPage)
    emit('page-change', newPage)
  }
}

function handlePageClick(page: number) {
  if (page !== props.currentPage && page >= 1 && page <= totalPages.value) {
    emit('update:currentPage', page)
    emit('page-change', page)
  }
}
</script>

