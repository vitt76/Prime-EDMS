import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { assetService } from '@/services/assetService'
import type { Asset, SearchQuery, SearchResponse, Facets } from '@/types/api'
import { formatApiError } from '@/utils/errors'

export const useSearchStore = defineStore(
  'search',
  () => {
    // State
    const query = ref<string>('')
    const results = ref<Asset[]>([])
    const facets = ref<Facets>({})
    const totalCount = ref(0)
    const isLoading = ref(false)
    const error = ref<string | null>(null)
    const recentSearches = ref<string[]>([])
    const searchHistory = ref<Array<{ query: string; timestamp: Date }>>([])
    const lastSearchAnalytics = ref<{ search_query_id?: number | null; search_session_id?: string | null } | null>(null)
    const lastSearchStartedAt = ref<Date | null>(null)

    // Getters
    const hasResults = computed(() => results.value.length > 0)
    const resultCount = computed(() => totalCount.value)
    const facetsSummary = computed(() => {
      const summary: Record<string, number> = {}
      Object.keys(facets.value).forEach((key) => {
        const facet = facets.value[key]
        if (facet) {
          summary[key] = Object.values(facet).reduce((sum, count) => sum + count, 0)
        }
      })
      return summary
    })

    // Actions
    async function performSearch(searchQuery: string, limit: number = 8) {
      if (!searchQuery.trim() || searchQuery.length < 2) {
        results.value = []
        totalCount.value = 0
        facets.value = {}
        return
      }

      query.value = searchQuery.trim()
      isLoading.value = true
      error.value = null

      try {
        const searchParams: SearchQuery = {
          q: query.value,
          limit,
          offset: 0
        }

        lastSearchStartedAt.value = new Date()
        const response: SearchResponse = await assetService.searchAssets(searchParams)

        results.value = response.results
        totalCount.value = response.count
        facets.value = response.facets
        lastSearchAnalytics.value = response.analytics || null

        // Add to recent searches (max 5)
        addToRecent(query.value)

        // Add to search history
        searchHistory.value.unshift({
          query: query.value,
          timestamp: new Date()
        })
        if (searchHistory.value.length > 50) {
          searchHistory.value = searchHistory.value.slice(0, 50)
        }
      } catch (err) {
        error.value = formatApiError(err)
        results.value = []
        totalCount.value = 0
        facets.value = {}
        throw err
      } finally {
        isLoading.value = false
      }
    }

    async function advancedSearch(searchParams: SearchQuery) {
      isLoading.value = true
      error.value = null

      try {
        lastSearchStartedAt.value = new Date()
        const response: SearchResponse = await assetService.searchAssets(searchParams)

        results.value = response.results
        totalCount.value = response.count
        facets.value = response.facets
        lastSearchAnalytics.value = response.analytics || null

        if (searchParams.q) {
          query.value = searchParams.q
          addToRecent(searchParams.q)
        }
      } catch (err) {
        error.value = formatApiError(err)
        results.value = []
        totalCount.value = 0
        facets.value = {}
        throw err
      } finally {
        isLoading.value = false
      }
    }

    function clearSearch() {
      query.value = ''
      results.value = []
      totalCount.value = 0
      facets.value = {}
      error.value = null
    }

    function addToRecent(searchQuery: string) {
      // Remove if already exists
      const index = recentSearches.value.indexOf(searchQuery)
      if (index !== -1) {
        recentSearches.value.splice(index, 1)
      }

      // Add to beginning
      recentSearches.value.unshift(searchQuery)

      // Keep only last 5
      if (recentSearches.value.length > 5) {
        recentSearches.value = recentSearches.value.slice(0, 5)
      }

      // Persist to localStorage
      localStorage.setItem('recent_searches', JSON.stringify(recentSearches.value))
    }

    function loadRecentSearches() {
      try {
        const stored = localStorage.getItem('recent_searches')
        if (stored) {
          recentSearches.value = JSON.parse(stored)
        }
      } catch (err) {
        console.error('Failed to load recent searches:', err)
        recentSearches.value = []
      }
    }

    // Initialize on store creation
    loadRecentSearches()

    return {
      // State
      query,
      results,
      facets,
      totalCount,
      isLoading,
      error,
      recentSearches,
      searchHistory,
      lastSearchAnalytics,
      lastSearchStartedAt,
      // Getters
      hasResults,
      resultCount,
      facetsSummary,
      // Actions
      performSearch,
      advancedSearch,
      clearSearch,
      addToRecent,
      loadRecentSearches
    }
  },
  {
    persist: {
      paths: ['recentSearches']
    }
  }
)

