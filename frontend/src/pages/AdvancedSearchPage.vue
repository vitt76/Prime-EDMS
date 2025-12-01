<template>
  <div class="advanced-search-page">
    <div class="max-w-7xl mx-auto p-6">
      <!-- Search Header -->
      <div class="mb-6">
        <h1 class="text-2xl font-bold text-neutral-900 dark:text-neutral-900 mb-4">
          Расширенный поиск
        </h1>
        <SearchBar
          :placeholder="'Введите запрос для поиска...'"
          @search="handleSearch"
          @result-selected="handleResultSelected"
        />
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <!-- Filters Sidebar (Left) -->
        <div class="lg:col-span-1">
          <div class="bg-neutral-0 dark:bg-neutral-0 border border-neutral-300 dark:border-neutral-300 rounded-lg p-4 sticky top-4">
            <h2 class="text-sm font-semibold text-neutral-900 dark:text-neutral-900 mb-4">
              Фильтры
            </h2>
            <FiltersPanel
              :facets="searchStore.facets"
              :initial-filters="activeFilters"
              @apply="handleFiltersApply"
              @reset="handleFiltersReset"
            />
          </div>
        </div>

        <!-- Results Area (Right) -->
        <div class="lg:col-span-3">
          <!-- Results Header -->
          <div class="flex items-center justify-between mb-4">
            <div>
              <p class="text-sm text-neutral-600 dark:text-neutral-600">
                Найдено результатов: <span class="font-semibold">{{ searchStore.totalCount }}</span>
              </p>
            </div>
            <div class="flex items-center gap-2">
              <label class="text-sm text-neutral-600 dark:text-neutral-600">Сортировка:</label>
              <select
                v-model="sortBy"
                class="px-3 py-1 border border-neutral-300 dark:border-neutral-300 rounded-md text-sm bg-neutral-0 dark:bg-neutral-0 text-neutral-900 dark:text-neutral-900"
                @change="handleSortChange"
              >
                <option value="relevance">По релевантности</option>
                <option value="-date_added">Сначала новые</option>
                <option value="date_added">Сначала старые</option>
                <option value="label">По названию (А-Я)</option>
                <option value="-label">По названию (Я-А)</option>
                <option value="-size">По размеру (большие)</option>
                <option value="size">По размеру (маленькие)</option>
              </select>
            </div>
          </div>

          <!-- Loading State -->
          <div v-if="searchStore.isLoading" class="p-8 text-center">
            <div class="animate-spin h-8 w-8 mx-auto text-primary-500"></div>
            <p class="mt-4 text-neutral-600 dark:text-neutral-600">Поиск...</p>
          </div>

          <!-- Error State -->
          <div v-else-if="searchStore.error" class="p-8 text-center">
            <p class="text-error">{{ searchStore.error }}</p>
            <button
              class="mt-4 px-4 py-2 bg-primary-500 text-white rounded-md hover:bg-primary-600 transition-colors"
              @click="handleRetry"
            >
              Попробовать снова
            </button>
          </div>

          <!-- Results Grid -->
          <div v-else-if="searchStore.hasResults" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            <AssetCard
              v-for="asset in searchStore.results"
              :key="asset.id"
              :asset="asset"
              :is-selected="false"
              :show-checkbox="false"
              @open="handleAssetOpen"
            />
          </div>

          <!-- Empty State -->
          <div v-else class="p-8 text-center">
            <svg
              class="mx-auto h-12 w-12 text-neutral-400"
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
            <h3 class="mt-4 text-lg font-medium text-neutral-900 dark:text-neutral-900">
              Нет результатов
            </h3>
            <p class="mt-2 text-sm text-neutral-600 dark:text-neutral-600">
              Попробуйте изменить запрос или фильтры
            </p>
          </div>

          <!-- Pagination -->
          <Pagination
            v-if="searchStore.totalCount > 0"
            :current-page="currentPage"
            :total-items="searchStore.totalCount"
            :page-size="pageSize"
            @page-change="handlePageChange"
            class="mt-6"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useSearchStore } from '@/stores/searchStore'
import SearchBar from '@/components/DAM/SearchBar.vue'
import FiltersPanel from '@/components/DAM/FiltersPanel.vue'
import AssetCard from '@/components/DAM/AssetCard.vue'
import Pagination from '@/components/Common/Pagination.vue'
import type { SearchQuery, SearchFilters } from '@/types/api'

const route = useRoute()
const router = useRouter()
const searchStore = useSearchStore()

const sortBy = ref('relevance')
const currentPage = ref(1)
const pageSize = ref(50)
const activeFilters = ref<SearchFilters>({})

// Initialize search from query params
onMounted(() => {
  const query = route.query.q as string
  if (query) {
    const searchParams: SearchQuery = {
      q: query,
      sort: sortBy.value,
      limit: pageSize.value,
      offset: 0
    }
    searchStore.advancedSearch(searchParams)
  }
})

// Watch route query changes
watch(
  () => route.query.q,
  (newQuery) => {
    if (newQuery && typeof newQuery === 'string') {
      const searchParams: SearchQuery = {
        q: newQuery,
        filters: activeFilters.value,
        sort: sortBy.value,
        limit: pageSize.value,
        offset: (currentPage.value - 1) * pageSize.value
      }
      searchStore.advancedSearch(searchParams)
    }
  }
)

function handleSearch(query: string) {
  currentPage.value = 1
  router.push({
    path: '/dam/search',
    query: { q: query }
  })
}

function handleResultSelected(assetId: number) {
  router.push(`/dam/assets/${assetId}`)
}

function handleAssetOpen(asset: any) {
  router.push(`/dam/assets/${asset.id}`)
}

function handleFiltersApply(filters: SearchFilters) {
  activeFilters.value = filters
  currentPage.value = 1
  const query = route.query.q as string
  const searchParams: SearchQuery = {
    q: query || '',
    filters,
    sort: sortBy.value,
    limit: pageSize.value,
    offset: 0
  }
  searchStore.advancedSearch(searchParams)
}

function handleFiltersReset() {
  activeFilters.value = {}
  currentPage.value = 1
  const query = route.query.q as string
  if (query) {
    const searchParams: SearchQuery = {
      q: query,
      sort: sortBy.value,
      limit: pageSize.value,
      offset: 0
    }
    searchStore.advancedSearch(searchParams)
  } else {
    searchStore.clearSearch()
  }
}

function handleSortChange() {
  currentPage.value = 1
  const query = route.query.q as string
  const searchParams: SearchQuery = {
    q: query || '',
    sort: sortBy.value,
    limit: pageSize.value,
    offset: 0
  }
  searchStore.advancedSearch(searchParams)
}

function handlePageChange(page: number) {
  currentPage.value = page
  const query = route.query.q as string
  const searchParams: SearchQuery = {
    q: query || '',
    sort: sortBy.value,
    limit: pageSize.value,
    offset: (page - 1) * pageSize.value
  }
  searchStore.advancedSearch(searchParams)
}

function handleRetry() {
  const query = route.query.q as string
  if (query) {
    searchStore.performSearch(query, pageSize.value)
  }
}
</script>

<style scoped>
.advanced-search-page {
  min-height: calc(100vh - 4rem);
}
</style>

