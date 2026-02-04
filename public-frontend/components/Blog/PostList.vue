<template>
  <div class="space-y-8">
    <!-- Loading State -->
    <div 
      v-if="loading"
      class="grid gap-8 md:grid-cols-2 lg:grid-cols-3"
    >
      <BlogPostCardSkeleton v-for="i in 6" :key="i" />
    </div>

    <!-- Posts Grid -->
    <div 
      v-else-if="posts.length" 
      class="grid gap-8 md:grid-cols-2 lg:grid-cols-3"
    >
      <BlogPostCard 
        v-for="post in posts" 
        :key="post.id" 
        :post="post" 
      />
    </div>

    <!-- Empty State -->
    <div 
      v-else 
      class="flex flex-col items-center justify-center rounded-2xl bg-neutral-50 py-16 text-center"
    >
      <DocumentTextIcon class="h-12 w-12 text-neutral-300" />
      <h3 class="mt-4 text-lg font-semibold text-neutral-900">Нет публикаций</h3>
      <p class="mt-2 text-sm text-neutral-600">
        Статьи скоро появятся. Подпишитесь на рассылку, чтобы не пропустить!
      </p>
    </div>

    <!-- Pagination -->
    <div v-if="totalPages > 1" class="flex items-center justify-center gap-2">
      <button
        :disabled="currentPage <= 1"
        class="flex h-10 w-10 items-center justify-center rounded-lg border border-neutral-200 text-neutral-600 transition hover:bg-neutral-50 disabled:cursor-not-allowed disabled:opacity-50"
        @click="$emit('page-change', currentPage - 1)"
        aria-label="Previous page"
      >
        <ChevronLeftIcon class="h-5 w-5" />
      </button>

      <div class="flex items-center gap-1">
        <button
          v-for="page in visiblePages"
          :key="page"
          class="flex h-10 min-w-[40px] items-center justify-center rounded-lg border px-3 text-sm font-medium transition"
          :class="page === currentPage 
            ? 'border-primary-600 bg-primary-600 text-white' 
            : 'border-neutral-200 text-neutral-600 hover:bg-neutral-50'"
          @click="$emit('page-change', page)"
        >
          {{ page }}
        </button>
      </div>

      <button
        :disabled="currentPage >= totalPages"
        class="flex h-10 w-10 items-center justify-center rounded-lg border border-neutral-200 text-neutral-600 transition hover:bg-neutral-50 disabled:cursor-not-allowed disabled:opacity-50"
        @click="$emit('page-change', currentPage + 1)"
        aria-label="Next page"
      >
        <ChevronRightIcon class="h-5 w-5" />
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { PublicPost } from '~/types/content'
import { 
  ChevronLeftIcon, 
  ChevronRightIcon,
  DocumentTextIcon 
} from '@heroicons/vue/24/outline'

const props = defineProps<{
  posts: PublicPost[]
  currentPage?: number
  totalPages?: number
  loading?: boolean
}>()

defineEmits<{
  (e: 'page-change', page: number): void
}>()

const visiblePages = computed(() => {
  const pages: number[] = []
  const total = props.totalPages || 1
  const current = props.currentPage || 1
  
  let start = Math.max(1, current - 2)
  let end = Math.min(total, current + 2)
  
  // Adjust if at edges
  if (current <= 2) {
    end = Math.min(5, total)
  }
  if (current >= total - 1) {
    start = Math.max(1, total - 4)
  }
  
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  
  return pages
})
</script>
