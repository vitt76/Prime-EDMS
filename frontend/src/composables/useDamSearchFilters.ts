import { computed, reactive, watch } from 'vue'
import { useDebounceFn } from '@vueuse/core'
import { useRoute, useRouter } from 'vue-router'
import { useAssetStore } from '@/stores/assetStore'
import { useUIStore } from '@/stores/uiStore'

type Density = 'compact' | 'comfortable'
type Layout = 'grid' | 'masonry'
type Sort = 'date' | 'name' | 'size'

export interface DamFiltersState {
  type: string[]
  tags: string[]
  status: string[]
  dateFrom?: string
  dateTo?: string
  sizeMin?: number
  sizeMax?: number
}

export interface DamSearchState {
  q: string
  density: Density
  layout: Layout
  sort: Sort
  filters: DamFiltersState
}

let _state: DamSearchState | null = null
let _initialized = false
let _isUpdatingRoute = false
let _routeWatchRegistered = false

function _parseCsv(value: unknown): string[] {
  if (!value) return []
  return String(value)
    .split(',')
    .map((s) => s.trim())
    .filter(Boolean)
}

function _toIsoDateString(value: string | undefined): string | undefined {
  if (!value) return undefined
  // accept YYYY-MM-DD or full ISO; pass through as-is (backend side decides)
  return value
}

/**
 * Single Source of Truth for DAM search + filters + URL sync.
 *
 * Responsibilities:
 * - Holds state: q/sort/layout/density/filters
 * - Reads from URL query on init and on back/forward
 * - Writes to URL query on state change
 * - Debounced fetchAssets() (300ms) for q/filters/sort changes
 */
export function useDamSearchFilters() {
  const route = useRoute()
  const router = useRouter()
  const assetStore = useAssetStore()
  const uiStore = useUIStore()

  if (!_state) {
    _state = reactive<DamSearchState>({
      q: '',
      density: uiStore.damGalleryDensity,
      layout: uiStore.damGalleryLayout,
      sort: uiStore.damGallerySort,
      filters: {
        type: [],
        tags: [],
        status: [],
        dateFrom: undefined,
        dateTo: undefined,
        sizeMin: undefined,
        sizeMax: undefined
      }
    })
  }

  const state = _state

  const activeFiltersCount = computed(() => {
    let count = 0
    if (state.filters.type.length) count++
    if (state.filters.tags.length) count++
    if (state.filters.status.length) count++
    if (state.filters.dateFrom || state.filters.dateTo) count++
    if (typeof state.filters.sizeMin === 'number' || typeof state.filters.sizeMax === 'number') count++
    return count
  })

  function readFromUrl(): void {
    state.q = String(route.query.q || '')
    state.sort = (route.query.sort as Sort) || uiStore.damGallerySort
    state.layout = (route.query.layout as Layout) || uiStore.damGalleryLayout
    state.density = (route.query.density as Density) || uiStore.damGalleryDensity

    state.filters.type = _parseCsv(route.query.type)
    state.filters.tags = _parseCsv(route.query.tags)
    state.filters.status = _parseCsv(route.query.status)

    state.filters.dateFrom = _toIsoDateString(route.query.dateFrom as string | undefined)
    state.filters.dateTo = _toIsoDateString(route.query.dateTo as string | undefined)

    state.filters.sizeMin = route.query.sizeMin ? Number(route.query.sizeMin) : undefined
    state.filters.sizeMax = route.query.sizeMax ? Number(route.query.sizeMax) : undefined
  }

  function writeToUrl(): void {
    _isUpdatingRoute = true
    void router
      .replace({
        query: {
          ...route.query,
          q: state.q || undefined,
          sort: state.sort,
          layout: state.layout,
          density: state.density,
          type: state.filters.type.length ? state.filters.type.join(',') : undefined,
          tags: state.filters.tags.length ? state.filters.tags.join(',') : undefined,
          status: state.filters.status.length ? state.filters.status.join(',') : undefined,
          dateFrom: state.filters.dateFrom || undefined,
          dateTo: state.filters.dateTo || undefined,
          sizeMin: typeof state.filters.sizeMin === 'number' ? String(state.filters.sizeMin) : undefined,
          sizeMax: typeof state.filters.sizeMax === 'number' ? String(state.filters.sizeMax) : undefined
        }
      })
      .finally(() => {
        _isUpdatingRoute = false
      })
  }

  function applyToStoreParams(): void {
    // Store no longer auto-fetches on setters; composable is responsible.
    assetStore.setSearchQuery(state.q)
    assetStore.setSortBy(
      state.sort === 'date' ? 'date_added' : state.sort === 'name' ? 'name' : 'size',
      state.sort === 'name' ? 'asc' : 'desc'
    )
    assetStore.applyFilters({
      type: state.filters.type,
      tags: state.filters.tags,
      status: state.filters.status,
      dateFrom: state.filters.dateFrom,
      dateTo: state.filters.dateTo,
      sizeMin: state.filters.sizeMin,
      sizeMax: state.filters.sizeMax
    })

    uiStore.setDamGalleryDensity(state.density)
    uiStore.setDamGalleryLayout(state.layout)
    uiStore.setDamGallerySort(state.sort)
  }

  const debouncedSyncAndFetch = useDebounceFn(() => {
    writeToUrl()
    applyToStoreParams()
    assetStore.fetchAssets()
  }, 300)

  function ensureDamRoute(): void {
    // Search-first UX: if user searches from anywhere — switch to DAM.
    // Keep URL query synced (the actual fetch is controlled by this composable).
    if (!router.currentRoute.value.path.startsWith('/dam')) {
      void router.push({ path: '/dam', query: router.currentRoute.value.query })
    }
  }

  function scheduleFetch(): void {
    // Trigger debounced URL sync + store params update + fetch
    debouncedSyncAndFetch()
  }

  function fetchNow(): void {
    debouncedSyncAndFetch.cancel()
    writeToUrl()
    applyToStoreParams()
    assetStore.fetchAssets()
  }

  function setSearch(value: string): void {
    state.q = value
    ensureDamRoute()
    scheduleFetch()
  }

  function submitSearchNow(): void {
    ensureDamRoute()
    fetchNow()
  }

  function setSort(value: Sort): void {
    state.sort = value
    scheduleFetch()
  }

  function setView(value: { density?: Density; layout?: Layout }): void {
    if (value.density) state.density = value.density
    if (value.layout) state.layout = value.layout
    // View changes should be reflected in URL/persisted, but do not need refetch.
    writeToUrl()
    uiStore.setDamGalleryDensity(state.density)
    uiStore.setDamGalleryLayout(state.layout)
  }

  function toggleFilter<K extends keyof DamFiltersState>(key: K, value: string): void {
    const list = state.filters[key]
    if (!Array.isArray(list)) return
    const idx = list.indexOf(value)
    if (idx === -1) list.push(value)
    else list.splice(idx, 1)
    scheduleFetch()
  }

  function resetFilters(): void {
    state.filters.type = []
    state.filters.tags = []
    state.filters.status = []
    state.filters.dateFrom = undefined
    state.filters.dateTo = undefined
    state.filters.sizeMin = undefined
    state.filters.sizeMax = undefined
    scheduleFetch()
  }

  // Init: read URL once, then fetch.
  if (!_initialized) {
    _initialized = true
    readFromUrl()
    applyToStoreParams()
    assetStore.fetchAssets()
  }

  // Back/forward support
  if (!_routeWatchRegistered) {
    _routeWatchRegistered = true
    watch(
      () => route.query,
      () => {
        if (_isUpdatingRoute) {
          return
        }
        readFromUrl()
        applyToStoreParams()
        assetStore.fetchAssets()
      }
    )
  }

  return {
    state,
    q: computed({
      get: () => state.q,
      set: (v) => setSearch(v)
    }),
    activeFiltersCount,
    setSearch,
    submitSearchNow,
    setSort,
    setView,
    toggleFilter,
    resetFilters,
    scheduleFetch,
    fetchNow
  }
}


