<template>
  <div class="mx-auto max-w-container px-4 py-12 lg:py-16">
    <SEOPageMeta 
      title="Блог | MADDAM" 
      description="Статьи, руководства и новости о управлении цифровыми активами"
    />

    <!-- Header -->
    <div class="mb-12 text-center">
      <h1 class="text-4xl font-bold text-neutral-900 md:text-5xl">Блог</h1>
      <p class="mt-4 text-lg text-neutral-600">
        Статьи, руководства и новости о управлении цифровыми активами
      </p>
    </div>

    <!-- Search & Filters -->
    <div class="mb-10 rounded-2xl bg-neutral-50 p-6">
      <div class="flex flex-col gap-4 md:flex-row md:items-center">
        <!-- Search Input -->
        <div class="relative flex-1">
          <MagnifyingGlassIcon class="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-neutral-400" />
          <input 
            v-model="searchQuery" 
            type="search"
            class="w-full rounded-xl border-neutral-200 py-3 pl-10 pr-4 text-sm shadow-sm transition focus:border-primary-500 focus:ring-primary-500" 
            placeholder="Поиск статей..."
            @keyup.enter="applySearch"
          />
        </div>

        <!-- Search Button -->
        <button 
          class="inline-flex items-center justify-center gap-2 rounded-xl bg-primary-600 px-6 py-3 text-sm font-medium text-white shadow-sm transition hover:bg-primary-700"
          @click="applySearch"
        >
          <MagnifyingGlassIcon class="h-4 w-4" />
          Найти
        </button>
      </div>

      <!-- Active Search Tag -->
      <div v-if="search" class="mt-4 flex items-center gap-2">
        <span class="text-sm text-neutral-600">Результаты для:</span>
        <span class="inline-flex items-center gap-1 rounded-full bg-primary-100 px-3 py-1 text-sm font-medium text-primary-700">
          {{ search }}
          <button @click="clearSearch" class="ml-1 hover:text-primary-900">
            <XMarkIcon class="h-4 w-4" />
          </button>
        </span>
      </div>
    </div>

    <div class="mb-10 flex flex-wrap gap-3">
      <button
        @click="selectedCategory = null"
        :class="selectedCategory === null 
          ? 'bg-primary-600 text-white' 
          : 'bg-white text-neutral-700 ring-1 ring-neutral-200 hover:bg-neutral-50'"
        class="rounded-lg px-4 py-2 text-sm font-medium transition"
      >
        Все
      </button>
      <button
        v-for="cat in categories"
        :key="cat"
        @click="selectedCategory = cat"
        :class="selectedCategory === cat 
          ? 'bg-primary-600 text-white' 
          : 'bg-white text-neutral-700 ring-1 ring-neutral-200 hover:bg-neutral-50'"
        class="rounded-lg px-4 py-2 text-sm font-medium transition"
      >
        {{ cat }}
      </button>
    </div>

    <!-- Results Count -->
    <div v-if="posts?.count" class="mb-6 text-sm text-neutral-600">
      Найдено статей: <span class="font-semibold text-neutral-900">{{ posts.count }}</span>
    </div>

    <!-- Posts List with built-in pagination -->
    <BlogPostList 
      :posts="posts?.results || []" 
      :current-page="page"
      :total-pages="totalPages"
      :loading="pending"
      @page-change="changePage"
    />

    <!-- Empty State -->
    <div 
      v-if="!posts?.results?.length && !pending" 
      class="rounded-2xl bg-neutral-50 py-16 text-center"
    >
      <DocumentTextIcon class="mx-auto h-12 w-12 text-neutral-300" />
      <h3 class="mt-4 text-lg font-semibold text-neutral-900">Ничего не найдено</h3>
      <p class="mt-2 text-sm text-neutral-600">
        Попробуйте изменить поисковый запрос
      </p>
      <button 
        v-if="search"
        class="mt-4 text-sm font-medium text-primary-600 hover:text-primary-700"
        @click="clearSearch"
      >
        Сбросить поиск
      </button>
    </div>

  </div>
</template>

<script setup lang="ts">
import type { PaginatedResponse } from '~/types/api'
import type { PublicPost } from '~/types/content'
import { MagnifyingGlassIcon, XMarkIcon, DocumentTextIcon } from '@heroicons/vue/24/outline'

const route = useRoute()
const router = useRouter()
const { locale } = useI18n()
const { getPosts } = useApi()

const searchQuery = ref((route.query.q as string) || '')
const search = ref((route.query.q as string) || '')
const page = computed(() => Number(route.query.page || 1))
const selectedCategory = ref<string | null>(null)
const categories = ref(['Product Updates', 'Tutorials', 'Case Studies', 'Industry News'])

const { data: posts, pending, refresh } = await useAsyncData<PaginatedResponse<PublicPost>>(
  `blog-${locale.value}-${page.value}-${search.value}-${selectedCategory.value || 'all'}`,
  () =>
    getPosts({
      page: page.value,
      limit: 9,
      lang: locale.value,
      search: search.value || undefined,
      category: selectedCategory.value || undefined
    }),
  { watch: [locale, page, search, selectedCategory] }
)

const totalPages = computed(() => {
  const count = posts.value?.count || 0
  return Math.max(1, Math.ceil(count / 9))
})

const applySearch = () => {
  search.value = searchQuery.value
  router.push({ 
    query: { 
      ...route.query, 
      q: searchQuery.value || undefined,
      page: 1 
    } 
  })
}

const clearSearch = () => {
  searchQuery.value = ''
  search.value = ''
  router.push({ 
    query: { 
      ...route.query, 
      q: undefined,
      page: 1 
    } 
  })
}

const changePage = (newPage: number) => {
  router.push({ query: { ...route.query, page: newPage } })
}

watch(selectedCategory, () => {
  refresh()
})
</script>
