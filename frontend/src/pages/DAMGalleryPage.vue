<template>
  <div class="dam-gallery">
    <!-- Header -->
    <header class="dam-gallery__header">
      <div class="dam-gallery__header-left">
        <h1 class="dam-gallery__title">Галерея активов</h1>
        <p class="dam-gallery__subtitle">
          {{ assetStore.totalCount }} {{ pluralize(assetStore.totalCount, 'актив', 'актива', 'активов') }}
        </p>
      </div>
      
      <div class="dam-gallery__header-right">
        <!-- Search -->
        <div class="dam-gallery__search">
          <svg class="dam-gallery__search-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <input
            v-model="localSearch"
            type="text"
            placeholder="Поиск активов..."
            class="dam-gallery__search-input"
            @keydown.enter="handleSearch"
            @keydown.escape="clearSearch"
          />
          <button
            v-if="localSearch"
            @click="clearSearch"
            class="dam-gallery__search-clear"
            aria-label="Очистить поиск"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        <!-- View Toggle -->
        <div class="dam-gallery__view-toggle">
          <button
            @click="viewMode = 'grid'"
            :class="['dam-gallery__view-btn', viewMode === 'grid' && 'dam-gallery__view-btn--active']"
            aria-label="Сетка"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
            </svg>
          </button>
          <button
            @click="viewMode = 'list'"
            :class="['dam-gallery__view-btn', viewMode === 'list' && 'dam-gallery__view-btn--active']"
            aria-label="Список"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 10h16M4 14h16M4 18h16" />
            </svg>
          </button>
        </div>
        
        <!-- Sort -->
        <select
          v-model="sortOption"
          @change="handleSortChange"
          class="dam-gallery__sort-select"
        >
          <option value="date_added-desc">Новые</option>
          <option value="date_added-asc">Старые</option>
          <option value="name-asc">A → Я</option>
          <option value="name-desc">Я → A</option>
          <option value="size-desc">Большие</option>
          <option value="size-asc">Маленькие</option>
        </select>
        
        <!-- Filters Toggle -->
        <button
          @click="showFilters = !showFilters"
          :class="['dam-gallery__filter-btn', (showFilters || assetStore.hasActiveFilters) && 'dam-gallery__filter-btn--active']"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
          </svg>
          <span v-if="assetStore.hasActiveFilters" class="dam-gallery__filter-badge"></span>
        </button>
      </div>
    </header>
    
    <!-- Filters Panel -->
    <transition name="slide-down">
      <div v-if="showFilters" class="dam-gallery__filters">
        <div class="dam-gallery__filters-grid">
          <!-- Type Filter -->
          <div class="dam-gallery__filter-group">
            <label class="dam-gallery__filter-label">Тип файла</label>
            <div class="dam-gallery__filter-chips">
              <button
                v-for="type in fileTypes"
                :key="type.value"
                @click="toggleTypeFilter(type.value)"
                :class="['dam-gallery__chip', localFilters.type?.includes(type.value) && 'dam-gallery__chip--active']"
              >
                {{ type.label }}
                <span v-if="assetStore.typeCounts[type.value]" class="dam-gallery__chip-count">
                  {{ assetStore.typeCounts[type.value] }}
                </span>
              </button>
            </div>
          </div>
          
          <!-- Status Filter -->
          <div class="dam-gallery__filter-group">
            <label class="dam-gallery__filter-label">Статус</label>
            <div class="dam-gallery__filter-chips">
              <button
                v-for="status in statusOptions"
                :key="status.value"
                @click="toggleStatusFilter(status.value)"
                :class="['dam-gallery__chip', localFilters.status?.includes(status.value) && 'dam-gallery__chip--active']"
              >
                <span :class="['dam-gallery__status-dot', `dam-gallery__status-dot--${status.value}`]"></span>
                {{ status.label }}
              </button>
            </div>
          </div>
          
          <!-- Date Range -->
          <div class="dam-gallery__filter-group">
            <label class="dam-gallery__filter-label">Дата добавления</label>
            <div class="dam-gallery__date-range">
              <input
                v-model="localFilters.dateFrom"
                type="date"
                class="dam-gallery__date-input"
              />
              <span class="dam-gallery__date-separator">—</span>
              <input
                v-model="localFilters.dateTo"
                type="date"
                class="dam-gallery__date-input"
              />
            </div>
          </div>
          
          <!-- Tags -->
          <div class="dam-gallery__filter-group">
            <label class="dam-gallery__filter-label">Теги</label>
            <div class="dam-gallery__tags-input">
              <input
                v-model="tagInput"
                type="text"
                placeholder="Введите тег..."
                class="dam-gallery__tag-input"
                @keydown.enter.prevent="addTag"
              />
              <div v-if="localFilters.tags?.length" class="dam-gallery__selected-tags">
                <span
                  v-for="tag in localFilters.tags"
                  :key="tag"
                  class="dam-gallery__tag"
                >
                  {{ tag }}
                  <button @click="removeTag(tag)" class="dam-gallery__tag-remove">×</button>
                </span>
              </div>
            </div>
          </div>
        </div>
        
        <div class="dam-gallery__filters-actions">
          <button @click="clearAllFilters" class="dam-gallery__btn dam-gallery__btn--ghost">
            Сбросить
          </button>
          <button @click="applyFilters" class="dam-gallery__btn dam-gallery__btn--primary">
            Применить
          </button>
        </div>
      </div>
    </transition>
    
    <!-- Bulk Actions -->
    <transition name="slide-down">
      <div v-if="assetStore.hasSelection" class="dam-gallery__bulk-actions">
        <div class="dam-gallery__bulk-info">
          <span class="dam-gallery__bulk-count">
            Выбрано: {{ assetStore.selectedCount }}
          </span>
          <button @click="assetStore.clearSelection()" class="dam-gallery__bulk-clear">
            Снять выделение
          </button>
        </div>
        <div class="dam-gallery__bulk-buttons">
          <button @click="handleBulkDownload" class="dam-gallery__bulk-btn">
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
            Скачать
          </button>
          <button @click="handleBulkShare" class="dam-gallery__bulk-btn">
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.367 2.684 3 3 0 00-5.367-2.684z" />
            </svg>
            Поделиться
          </button>
          <button @click="handleBulkDelete" class="dam-gallery__bulk-btn dam-gallery__bulk-btn--danger">
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
            Удалить
          </button>
        </div>
      </div>
    </transition>
    
    <!-- Main Content -->
    <main class="dam-gallery__content">
      <!-- Loading State -->
      <div v-if="assetStore.isLoading && !assetStore.assets.length" class="dam-gallery__loading">
        <div class="dam-gallery__grid">
          <div
            v-for="i in 12"
            :key="i"
            class="dam-gallery__skeleton"
          >
            <div class="dam-gallery__skeleton-image"></div>
            <div class="dam-gallery__skeleton-text"></div>
            <div class="dam-gallery__skeleton-text dam-gallery__skeleton-text--short"></div>
          </div>
        </div>
      </div>
      
      <!-- Empty State -->
      <div
        v-else-if="!assetStore.assets.length && !assetStore.isLoading"
        class="dam-gallery__empty"
      >
        <div class="dam-gallery__empty-icon">
          <svg class="w-16 h-16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
        </div>
        <h3 class="dam-gallery__empty-title">
          {{ assetStore.hasActiveFilters ? 'Ничего не найдено' : 'Нет активов' }}
        </h3>
        <p class="dam-gallery__empty-text">
          {{ assetStore.hasActiveFilters 
            ? 'Попробуйте изменить параметры поиска или сбросить фильтры' 
            : 'Загрузите первый актив, чтобы начать работу' 
          }}
        </p>
        <button
          v-if="assetStore.hasActiveFilters"
          @click="clearAllFilters"
          class="dam-gallery__btn dam-gallery__btn--primary mt-4"
        >
          Сбросить фильтры
        </button>
      </div>
      
      <!-- Assets Grid -->
      <div
        v-else
        :class="['dam-gallery__grid', viewMode === 'list' && 'dam-gallery__grid--list']"
      >
        <AssetCardEnhanced
          v-for="asset in assetStore.assets"
          :key="asset.id"
          :asset="asset"
          :is-selected="assetStore.isSelected(asset.id)"
          :view-mode="viewMode"
          @select="handleAssetSelect"
          @open="handleAssetOpen"
          @preview="handleAssetPreview"
          @download="handleAssetDownload"
          @share="handleAssetShare"
          @delete="handleAssetDelete"
        />
      </div>
      
      <!-- Load More -->
      <div
        v-if="assetStore.hasNextPage"
        ref="loadMoreTrigger"
        class="dam-gallery__load-more"
      >
        <button
          v-if="!assetStore.isLoadingMore"
          @click="assetStore.loadMore()"
          class="dam-gallery__btn dam-gallery__btn--outline"
        >
          Загрузить ещё
        </button>
        <div v-else class="dam-gallery__loading-more">
          <svg class="animate-spin h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          Загрузка...
        </div>
      </div>
    </main>
    
    <!-- Quick View Modal -->
    <Teleport to="body">
      <transition name="modal">
        <div v-if="previewAsset" class="dam-gallery__modal-overlay" @click="closePreview">
          <div class="dam-gallery__modal" @click.stop>
            <button @click="closePreview" class="dam-gallery__modal-close">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
            
            <div class="dam-gallery__modal-content">
              <div class="dam-gallery__modal-image">
                <img
                  v-if="previewAssetSrc && !previewImageError"
                  :src="previewAssetSrc"
                  :alt="previewAsset.label"
                  @error="handlePreviewImageError"
                />
                <div
                  v-else
                  class="dam-gallery__modal-image-placeholder"
                  role="img"
                  aria-label="Нет предпросмотра"
                >
                  <svg class="w-12 h-12 text-neutral-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                  <p class="text-sm text-neutral-500 mt-2">Предпросмотр недоступен</p>
                </div>
                <button
                  v-if="previewAsset"
                  class="dam-gallery__modal-favorite"
                  :class="{ 'dam-gallery__modal-favorite--active': previewIsFavorite }"
                  @click.stop="togglePreviewFavorite"
                  aria-label="Добавить в избранное"
                  type="button"
                >
                  <svg class="w-5 h-5" :fill="previewIsFavorite ? 'currentColor' : 'none'" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                  </svg>
                </button>
              </div>
              
              <div class="dam-gallery__modal-info">
                <h2 class="dam-gallery__modal-title">{{ previewAsset.label }}</h2>
                
                <div class="dam-gallery__modal-meta">
                  <div class="dam-gallery__modal-meta-item">
                    <span class="dam-gallery__modal-meta-label">Размер:</span>
                    <span>{{ formatFileSize(previewAsset.size) }}</span>
                  </div>
                  <div class="dam-gallery__modal-meta-item">
                    <span class="dam-gallery__modal-meta-label">Тип:</span>
                    <span>{{ previewAsset.mime_type }}</span>
                  </div>
                  <div class="dam-gallery__modal-meta-item">
                    <span class="dam-gallery__modal-meta-label">Добавлен:</span>
                    <span>{{ formatDate(previewAsset.date_added) }}</span>
                  </div>
                  <div v-if="previewAsset.metadata?.status" class="dam-gallery__modal-meta-item">
                    <span class="dam-gallery__modal-meta-label">Статус:</span>
                    <span :class="['dam-gallery__status-badge', `dam-gallery__status-badge--${previewAsset.metadata.status}`]">
                      {{ previewAsset.metadata.status }}
                    </span>
                  </div>
                </div>
                
                <!-- AI Analysis -->
                <div v-if="previewAsset.ai_analysis?.status === 'completed'" class="dam-gallery__modal-ai">
                  <h3 class="dam-gallery__modal-section-title">AI Анализ</h3>
                  <p v-if="previewAsset.ai_analysis.ai_description" class="dam-gallery__modal-description">
                    {{ previewAsset.ai_analysis.ai_description }}
                  </p>
                  <div v-if="previewAsset.ai_analysis.tags?.length" class="dam-gallery__modal-tags">
                    <span
                      v-for="tag in previewAsset.ai_analysis.tags"
                      :key="tag"
                      class="dam-gallery__modal-tag"
                    >
                      {{ tag }}
                    </span>
                  </div>
                  <div v-if="previewAsset.ai_analysis.colors?.length" class="dam-gallery__modal-colors">
                    <span class="dam-gallery__modal-meta-label">Цвета:</span>
                    <div class="dam-gallery__color-swatches">
                      <span
                        v-for="color in previewAsset.ai_analysis.colors"
                        :key="color"
                        class="dam-gallery__color-swatch"
                        :style="{ backgroundColor: color }"
                        :title="color"
                      ></span>
                    </div>
                  </div>
                </div>
                
                <div class="dam-gallery__modal-actions">
                  <button @click="handleAssetDownload(previewAsset)" class="dam-gallery__btn dam-gallery__btn--primary">
                    Скачать
                  </button>
                  <button @click="handleAssetShare(previewAsset)" class="dam-gallery__btn dam-gallery__btn--outline">
                    Поделиться
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </transition>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAssetStore } from '@/stores/assetStore'
import { useFavoritesStore } from '@/stores/favoritesStore'
import { useFolderStore } from '@/stores/folderStore'
import { resolveAssetImageUrl } from '@/utils/imageUtils'
import { formatFileSize, formatDate } from '@/utils/formatters'
import AssetCardEnhanced from '@/components/DAM/AssetCardEnhanced.vue'
import type { Asset } from '@/types/api'
import { findFolderById } from '@/mocks/folders'

// ============================================================================
// COMPOSABLES
// ============================================================================

const router = useRouter()
const route = useRoute()
const assetStore = useAssetStore()
const favoritesStore = useFavoritesStore()
const folderStore = useFolderStore()

// ============================================================================
// STATE
// ============================================================================

const viewMode = ref<'grid' | 'list'>('grid')
const showFilters = ref(false)
const localSearch = ref('')
const tagInput = ref('')
const sortOption = ref('date_added-desc')
const previewAsset = ref<Asset | null>(null)
const previewImageError = ref(false)
const loadMoreTrigger = ref<HTMLElement | null>(null)
const previewAssetSrc = computed(() => resolveAssetImageUrl(previewAsset.value))
const previewIsFavorite = computed(() => {
  const asset = previewAsset.value
  if (!asset) return false
  return favoritesStore.isFavorite(asset.id) || asset.is_favorite === true || asset.isFavorite === true
})

// Local filters (applied on button click)
const localFilters = ref({
  type: [] as string[],
  status: [] as string[],
  tags: [] as string[],
  dateFrom: '',
  dateTo: '',
})

// ============================================================================
// CONSTANTS
// ============================================================================

const fileTypes = [
  { value: 'image', label: 'Изображения' },
  { value: 'video', label: 'Видео' },
  { value: 'document', label: 'Документы' },
  { value: 'audio', label: 'Аудио' },
]

const statusOptions = [
  { value: 'approved', label: 'Одобрено' },
  { value: 'pending', label: 'На проверке' },
  { value: 'draft', label: 'Черновик' },
  { value: 'rejected', label: 'Отклонено' },
]

// ============================================================================
// HELPERS
// ============================================================================

function pluralize(count: number, one: string, few: string, many: string): string {
  const mod10 = count % 10
  const mod100 = count % 100
  
  if (mod100 >= 11 && mod100 <= 14) return many
  if (mod10 === 1) return one
  if (mod10 >= 2 && mod10 <= 4) return few
  return many
}

function applyFolderFilterFromRoute(): void {
  const folderId = route.query.folder as string | undefined

  if (!folderId) {
    assetStore.setFolderFilter(null, null)
    assetStore.fetchAssets()
    return
  }

  // Try to resolve folder type to ensure we filter only system folders
  const systemSection = folderStore.sections.find(section => section.type === 'local')
  const foundFolder = systemSection
    ? findFolderById(systemSection.folders, folderId) 
    : null

  // #region agent log
  fetch('http://127.0.0.1:7242/ingest/e2a91df7-36f3-4ec3-8d36-7745f17b1cac', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      id: `log_applyFolderFilter_${Date.now()}`,
      timestamp: Date.now(),
      sessionId: 'debug-session',
      runId: 'post-fix',
      hypothesisId: 'H-folder',
      location: 'DAMGalleryPage:applyFolderFilterFromRoute',
      message: 'Applying folder filter from route',
      data: {
        folderId,
        found: !!foundFolder,
        folderType: foundFolder?.type || null,
        systemSectionExists: !!systemSection
      }
    })
  }).catch(() => {})
  // #endregion agent log

  assetStore.setFolderFilter(
    foundFolder ? folderId : null,
    foundFolder?.type || null
  )

  if (foundFolder) {
    folderStore.selectFolder(folderId)
  }

  assetStore.fetchAssets({ page: 1 })
}

// ============================================================================
// HANDLERS - SEARCH & FILTERS
// ============================================================================

function handleSearch(): void {
  assetStore.setSearchQuery(localSearch.value)
}

function clearSearch(): void {
  localSearch.value = ''
  assetStore.setSearchQuery('')
}

function handleSortChange(): void {
  const [field, direction] = sortOption.value.split('-') as ['date_added' | 'name' | 'size' | 'type', 'asc' | 'desc']
  assetStore.setSort({ field, direction })
}

function toggleTypeFilter(type: string): void {
  const index = localFilters.value.type.indexOf(type)
  if (index === -1) {
    localFilters.value.type.push(type)
  } else {
    localFilters.value.type.splice(index, 1)
  }
}

function toggleStatusFilter(status: string): void {
  const index = localFilters.value.status.indexOf(status)
  if (index === -1) {
    localFilters.value.status.push(status)
  } else {
    localFilters.value.status.splice(index, 1)
  }
}

function addTag(): void {
  const tag = tagInput.value.trim()
  if (tag && !localFilters.value.tags.includes(tag)) {
    localFilters.value.tags.push(tag)
    tagInput.value = ''
  }
}

function removeTag(tag: string): void {
  const index = localFilters.value.tags.indexOf(tag)
  if (index !== -1) {
    localFilters.value.tags.splice(index, 1)
  }
}

function applyFilters(): void {
  assetStore.setFilters({
    type: localFilters.value.type.length ? localFilters.value.type : undefined,
    status: localFilters.value.status.length ? localFilters.value.status : undefined,
    tags: localFilters.value.tags.length ? localFilters.value.tags : undefined,
    dateFrom: localFilters.value.dateFrom || undefined,
    dateTo: localFilters.value.dateTo || undefined,
  })
  showFilters.value = false
}

function clearAllFilters(): void {
  localFilters.value = {
    type: [],
    status: [],
    tags: [],
    dateFrom: '',
    dateTo: '',
  }
  localSearch.value = ''
  assetStore.clearFilters()
  showFilters.value = false
}

// ============================================================================
// HANDLERS - ASSET ACTIONS
// ============================================================================

function handleAssetSelect(asset: Asset): void {
  assetStore.toggleSelection(asset.id)
}

function handleAssetOpen(asset: Asset): void {
  router.push(`/dam/assets/${asset.id}`)
}

function handleAssetPreview(asset: Asset): void {
  previewImageError.value = false
  previewAsset.value = asset
}

function closePreview(): void {
  previewAsset.value = null
  previewImageError.value = false
}

function handleAssetDownload(asset: Asset): void {
  console.log('Download:', asset.label)
  // TODO: Implement download
}

function handleAssetShare(asset: Asset): void {
  console.log('Share:', asset.label)
  // TODO: Open share modal
}

async function togglePreviewFavorite(): Promise<void> {
  if (!previewAsset.value) return
  try {
    const favorited = await favoritesStore.toggleFavorite(previewAsset.value.id)
    previewAsset.value.is_favorite = favorited
  } catch (error) {
    // ignore, store will revert on failure
  }
}

function handlePreviewImageError(): void {
  previewImageError.value = true
}

function handleAssetDelete(asset: Asset): void {
  if (confirm(`Удалить "${asset.label}"?`)) {
    assetStore.deleteAsset(asset.id)
  }
}

// ============================================================================
// HANDLERS - BULK ACTIONS
// ============================================================================

function handleBulkDownload(): void {
  console.log('Bulk download:', assetStore.selectedAssetsList)
  // TODO: Implement bulk download
}

function handleBulkShare(): void {
  console.log('Bulk share:', assetStore.selectedAssetsList)
  // TODO: Open bulk share modal
}

function handleBulkDelete(): void {
  const count = assetStore.selectedCount
  if (confirm(`Удалить ${count} ${pluralize(count, 'актив', 'актива', 'активов')}?`)) {
    const ids = Array.from(assetStore.selectedAssets)
    assetStore.bulkDelete(ids)
  }
}

// ============================================================================
// INFINITE SCROLL
// ============================================================================

let observer: IntersectionObserver | null = null

function setupInfiniteScroll(): void {
  if (observer) observer.disconnect()
  
  observer = new IntersectionObserver(
    (entries) => {
      const first = entries[0]
      if (first?.isIntersecting && assetStore.hasNextPage && !assetStore.isLoadingMore) {
        assetStore.loadMore()
      }
    },
    { rootMargin: '200px' }
  )
  
  if (loadMoreTrigger.value) {
    observer.observe(loadMoreTrigger.value)
  }
}

watch(loadMoreTrigger, () => {
  if (loadMoreTrigger.value) {
    setupInfiniteScroll()
  }
})

// ============================================================================
// LIFECYCLE
// ============================================================================

onMounted(() => {
  // Apply folder filter from route (if present)
  applyFolderFilterFromRoute()
  favoritesStore.fetchFavorites().catch(() => {})
})

watch(
  () => route.query.folder,
  () => {
    applyFolderFilterFromRoute()
  }
)
</script>

<style scoped>
/* ============================================================================
   BASE STYLES
   ============================================================================ */

.dam-gallery {
  @apply min-h-screen bg-neutral-50;
}

/* ============================================================================
   HEADER
   ============================================================================ */

.dam-gallery__header {
  @apply sticky top-0 z-30 bg-white border-b border-neutral-200 px-6 py-4;
  @apply flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4;
}

.dam-gallery__header-left {
  @apply flex-shrink-0;
}

.dam-gallery__title {
  @apply text-2xl font-bold text-neutral-900;
}

.dam-gallery__subtitle {
  @apply text-sm text-neutral-500 mt-1;
}

.dam-gallery__header-right {
  @apply flex items-center gap-3 flex-wrap;
}

/* Search */
.dam-gallery__search {
  @apply relative flex-1 min-w-[200px] max-w-md;
}

.dam-gallery__search-icon {
  @apply absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-neutral-400;
}

.dam-gallery__search-input {
  @apply w-full pl-10 pr-10 py-2.5 bg-neutral-100 border-0 rounded-lg;
  @apply text-sm placeholder-neutral-500;
  @apply focus:bg-white focus:ring-2 focus:ring-primary-500 transition-all;
}

.dam-gallery__search-clear {
  @apply absolute right-3 top-1/2 -translate-y-1/2 text-neutral-400 hover:text-neutral-600;
}

/* View Toggle */
.dam-gallery__view-toggle {
  @apply flex bg-neutral-100 rounded-lg p-1;
}

.dam-gallery__view-btn {
  @apply p-2 rounded-md text-neutral-500 hover:text-neutral-700 transition-colors;
}

.dam-gallery__view-btn--active {
  @apply bg-white text-primary-600 shadow-sm;
}

/* Sort */
.dam-gallery__sort-select {
  @apply px-3 py-2.5 bg-neutral-100 border-0 rounded-lg text-sm;
  @apply focus:ring-2 focus:ring-primary-500;
}

/* Filter Button */
.dam-gallery__filter-btn {
  @apply relative p-2.5 bg-neutral-100 rounded-lg text-neutral-500;
  @apply hover:bg-neutral-200 hover:text-neutral-700 transition-colors;
}

.dam-gallery__filter-btn--active {
  @apply bg-primary-100 text-primary-600;
}

.dam-gallery__filter-badge {
  @apply absolute -top-1 -right-1 w-3 h-3 bg-primary-500 rounded-full;
}

/* ============================================================================
   FILTERS PANEL
   ============================================================================ */

.dam-gallery__filters {
  @apply bg-white border-b border-neutral-200 px-6 py-5;
}

.dam-gallery__filters-grid {
  @apply grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6;
}

.dam-gallery__filter-group {
  @apply space-y-2;
}

.dam-gallery__filter-label {
  @apply block text-sm font-medium text-neutral-700;
}

.dam-gallery__filter-chips {
  @apply flex flex-wrap gap-2;
}

.dam-gallery__chip {
  @apply inline-flex items-center px-3 py-1.5 rounded-full text-sm;
  @apply bg-neutral-100 text-neutral-700 hover:bg-neutral-200 transition-colors;
}

.dam-gallery__chip--active {
  @apply bg-primary-100 text-primary-600;
}

.dam-gallery__chip-count {
  @apply ml-1.5 text-xs text-neutral-500;
}

.dam-gallery__status-dot {
  @apply w-2 h-2 rounded-full mr-2;
}

.dam-gallery__status-dot--approved { @apply bg-green-500; }
.dam-gallery__status-dot--pending { @apply bg-yellow-500; }
.dam-gallery__status-dot--draft { @apply bg-neutral-400; }
.dam-gallery__status-dot--rejected { @apply bg-red-500; }

.dam-gallery__date-range {
  @apply flex items-center gap-2;
}

.dam-gallery__date-input {
  @apply flex-1 px-3 py-2 bg-neutral-100 border-0 rounded-lg text-sm;
  @apply focus:ring-2 focus:ring-primary-500;
}

.dam-gallery__date-separator {
  @apply text-neutral-400;
}

.dam-gallery__tags-input {
  @apply space-y-2;
}

.dam-gallery__tag-input {
  @apply w-full px-3 py-2 bg-neutral-100 border-0 rounded-lg text-sm;
  @apply focus:ring-2 focus:ring-primary-500;
}

.dam-gallery__selected-tags {
  @apply flex flex-wrap gap-2;
}

.dam-gallery__tag {
  @apply inline-flex items-center px-2.5 py-1 bg-primary-100 text-primary-600 rounded-full text-sm;
}

.dam-gallery__tag-remove {
  @apply ml-1.5 text-primary-500 hover:text-primary-600;
}

.dam-gallery__filters-actions {
  @apply flex justify-end gap-3 mt-6 pt-4 border-t border-neutral-100;
}

/* ============================================================================
   BULK ACTIONS
   ============================================================================ */

.dam-gallery__bulk-actions {
  @apply bg-primary-50 border-b border-primary-100 px-6 py-3;
  @apply flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3;
}

.dam-gallery__bulk-info {
  @apply flex items-center gap-4;
}

.dam-gallery__bulk-count {
  @apply text-sm font-medium text-primary-600;
}

.dam-gallery__bulk-clear {
  @apply text-sm text-primary-600 hover:text-primary-600 underline;
}

.dam-gallery__bulk-buttons {
  @apply flex items-center gap-2;
}

.dam-gallery__bulk-btn {
  @apply inline-flex items-center px-3 py-2 text-sm font-medium rounded-lg;
  @apply bg-white text-neutral-700 hover:bg-neutral-50 border border-neutral-300;
  @apply transition-colors;
}

.dam-gallery__bulk-btn--danger {
  @apply text-red-600 hover:bg-red-50 border-red-200;
}

/* ============================================================================
   CONTENT
   ============================================================================ */

.dam-gallery__content {
  @apply p-6;
}

/* Grid */
.dam-gallery__grid {
  @apply grid gap-4;
  grid-template-columns: repeat(2, 1fr);
}

@media (min-width: 640px) {
  .dam-gallery__grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (min-width: 768px) {
  .dam-gallery__grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

@media (min-width: 1024px) {
  .dam-gallery__grid {
    grid-template-columns: repeat(5, 1fr);
  }
}

@media (min-width: 1280px) {
  .dam-gallery__grid {
    grid-template-columns: repeat(6, 1fr);
  }
}

.dam-gallery__grid--list {
  @apply grid-cols-1 gap-2;
}

/* Skeleton Loading */
.dam-gallery__skeleton {
  @apply bg-white rounded-xl overflow-hidden animate-pulse;
}

.dam-gallery__skeleton-image {
  @apply w-full aspect-square bg-neutral-200;
}

.dam-gallery__skeleton-text {
  @apply h-4 bg-neutral-200 rounded m-3;
}

.dam-gallery__skeleton-text--short {
  @apply w-2/3;
}

/* Empty State */
.dam-gallery__empty {
  @apply flex flex-col items-center justify-center py-20 text-center;
}

.dam-gallery__empty-icon {
  @apply text-neutral-300 mb-4;
}

.dam-gallery__empty-title {
  @apply text-xl font-semibold text-neutral-900 mb-2;
}

.dam-gallery__empty-text {
  @apply text-neutral-500 max-w-md;
}

/* Load More */
.dam-gallery__load-more {
  @apply flex justify-center py-8;
}

.dam-gallery__loading-more {
  @apply flex items-center text-neutral-500;
}

/* ============================================================================
   BUTTONS
   ============================================================================ */

.dam-gallery__btn {
  @apply inline-flex items-center justify-center px-4 py-2.5 text-sm font-medium rounded-lg;
  @apply transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2;
}

.dam-gallery__btn--primary {
  @apply bg-primary-600 text-white hover:bg-primary-600 focus:ring-primary-500;
}

.dam-gallery__btn--outline {
  @apply bg-white text-neutral-700 border border-neutral-300 hover:bg-neutral-50 focus:ring-primary-500;
}

.dam-gallery__btn--ghost {
  @apply text-neutral-600 hover:text-neutral-900 hover:bg-neutral-100;
}

/* ============================================================================
   MODAL
   ============================================================================ */

.dam-gallery__modal-overlay {
  @apply fixed inset-0 z-50 bg-black/60 backdrop-blur-sm;
  @apply flex items-center justify-center p-4;
}

.dam-gallery__modal {
  @apply relative bg-white rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden;
}

.dam-gallery__modal-close {
  @apply absolute top-4 right-4 z-10 p-2 bg-white/80 rounded-full;
  @apply text-neutral-500 hover:text-neutral-900 hover:bg-white transition-colors;
}

.dam-gallery__modal-content {
  @apply flex flex-col md:flex-row;
}

.dam-gallery__modal-image {
  @apply relative md:w-1/2 bg-neutral-100 flex items-center justify-center;
}

.dam-gallery__modal-image img {
  @apply max-w-full max-h-[50vh] md:max-h-[70vh] object-contain;
}

.dam-gallery__modal-image-placeholder {
  @apply flex flex-col items-center justify-center text-center text-neutral-500;
}

.dam-gallery__modal-favorite {
  @apply absolute top-4 left-4 p-2.5 bg-white/95 rounded-full shadow-lg transition-all duration-200;
  @apply text-neutral-700 hover:bg-white hover:scale-105;
}

.dam-gallery__modal-favorite--active {
  @apply text-red-500;
}

.dam-gallery__modal-info {
  @apply md:w-1/2 p-6 overflow-y-auto max-h-[40vh] md:max-h-[70vh];
}

.dam-gallery__modal-title {
  @apply text-xl font-bold text-neutral-900 mb-4;
}

.dam-gallery__modal-meta {
  @apply space-y-2 mb-6;
}

.dam-gallery__modal-meta-item {
  @apply flex items-center text-sm;
}

.dam-gallery__modal-meta-label {
  @apply text-neutral-500 w-24 flex-shrink-0;
}

.dam-gallery__status-badge {
  @apply inline-flex px-2 py-0.5 rounded-full text-xs font-medium;
}

.dam-gallery__status-badge--approved { @apply bg-green-100 text-green-800; }
.dam-gallery__status-badge--pending { @apply bg-yellow-100 text-yellow-800; }
.dam-gallery__status-badge--draft { @apply bg-neutral-100 text-neutral-800; }
.dam-gallery__status-badge--rejected { @apply bg-red-100 text-red-800; }

.dam-gallery__modal-ai {
  @apply bg-neutral-50 rounded-lg p-4 mb-6;
}

.dam-gallery__modal-section-title {
  @apply text-sm font-semibold text-neutral-900 mb-2;
}

.dam-gallery__modal-description {
  @apply text-sm text-neutral-600 mb-3;
}

.dam-gallery__modal-tags {
  @apply flex flex-wrap gap-1.5 mb-3;
}

.dam-gallery__modal-tag {
  @apply px-2 py-0.5 bg-white rounded text-xs text-neutral-700;
}

.dam-gallery__modal-colors {
  @apply flex items-center gap-2;
}

.dam-gallery__color-swatches {
  @apply flex gap-1;
}

.dam-gallery__color-swatch {
  @apply w-5 h-5 rounded-full border border-neutral-200;
}

.dam-gallery__modal-actions {
  @apply flex gap-3;
}

/* ============================================================================
   TRANSITIONS
   ============================================================================ */

.slide-down-enter-active,
.slide-down-leave-active {
  @apply transition-all duration-300 ease-out;
}

.slide-down-enter-from,
.slide-down-leave-to {
  @apply opacity-0 -translate-y-2;
}

.modal-enter-active,
.modal-leave-active {
  @apply transition-all duration-300 ease-out;
}

.modal-enter-from,
.modal-leave-to {
  @apply opacity-0;
}

.modal-enter-from .dam-gallery__modal,
.modal-leave-to .dam-gallery__modal {
  @apply scale-95;
}
</style>

