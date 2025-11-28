<template>
  <div class="collection-browser min-h-screen bg-neutral-50">
    <div class="container mx-auto px-4 py-6 max-w-7xl">
      <!-- Header -->
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
        <div>
          <h1 class="text-2xl font-bold text-neutral-900">{{ title }}</h1>
          <p v-if="subtitle" class="mt-1 text-sm text-neutral-600">{{ subtitle }}</p>
        </div>
        
        <!-- Header Actions Slot -->
        <slot name="header-actions">
          <div v-if="showUploadButton" class="flex items-center gap-3">
            <button
              type="button"
              class="inline-flex items-center gap-2 px-4 py-2.5 bg-primary-600 text-white text-sm font-semibold rounded-xl hover:bg-primary-700 transition-colors shadow-lg shadow-primary-600/25"
              @click="emit('upload')"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
              Загрузить
            </button>
          </div>
        </slot>
      </div>
      
      <!-- Stats Bar (optional) -->
      <div v-if="showStats && !isLoading && assets.length > 0" class="mb-6">
        <div class="inline-flex items-center gap-2 px-4 py-2 bg-white rounded-xl border border-neutral-200 text-sm text-neutral-600">
          <span class="font-medium text-neutral-900">{{ totalCount }}</span>
          <span>{{ pluralize(totalCount, 'файл', 'файла', 'файлов') }}</span>
        </div>
      </div>
      
      <!-- Loading State -->
      <div v-if="isLoading && assets.length === 0" class="py-12">
        <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
          <div
            v-for="i in 10"
            :key="i"
            class="bg-white rounded-xl border border-neutral-200 overflow-hidden animate-pulse"
          >
            <div class="aspect-video bg-neutral-200" />
            <div class="p-3 space-y-2">
              <div class="h-4 bg-neutral-200 rounded w-3/4" />
              <div class="flex justify-between">
                <div class="h-3 bg-neutral-200 rounded w-16" />
                <div class="h-3 bg-neutral-200 rounded w-20" />
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Empty State -->
      <div
        v-else-if="assets.length === 0 && !isLoading"
        class="flex items-center justify-center min-h-[60vh] p-8"
      >
        <div class="max-w-md text-center">
          <!-- Custom Empty State via Slot -->
          <slot name="empty-state">
            <div class="mx-auto w-24 h-24 rounded-full bg-gradient-to-br from-neutral-100 to-neutral-50 flex items-center justify-center mb-6">
              <component :is="emptyIcon" class="w-12 h-12 text-neutral-400" />
            </div>
            <h3 class="text-xl font-semibold text-neutral-800 mb-2">
              {{ emptyTitle }}
            </h3>
            <p class="text-neutral-500 mb-6">
              {{ emptyDescription }}
            </p>
            <slot name="empty-action">
              <router-link
                v-if="emptyActionLink"
                :to="emptyActionLink"
                class="inline-flex items-center gap-2 px-6 py-3 bg-primary-600 text-white font-medium rounded-xl
                       hover:bg-primary-700 focus:ring-2 focus:ring-primary-500 focus:ring-offset-2
                       transition-all shadow-lg shadow-primary-500/25"
              >
                {{ emptyActionText }}
              </router-link>
            </slot>
          </slot>
        </div>
      </div>
      
      <!-- Assets Grid -->
      <div v-else class="space-y-6">
        <!-- Time Groups (for Recent page) -->
        <template v-if="groupByTime">
          <div v-for="group in groupedAssets" :key="group.label" class="space-y-4">
            <h2 v-if="group.assets.length > 0" class="text-sm font-semibold text-neutral-600 uppercase tracking-wide">
              {{ group.label }}
            </h2>
            <div
              v-if="group.assets.length > 0"
              class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6"
            >
              <CollectionAssetCard
                v-for="asset in group.assets"
                :key="asset.id"
                :asset="asset"
                :show-favorite="showFavoriteButton"
                :show-owner="showOwner"
                @click="emit('asset-click', asset)"
                @favorite="emit('toggle-favorite', asset)"
                @preview="emit('preview', asset)"
                @download="emit('download', asset)"
                @share="emit('share', asset)"
              />
            </div>
          </div>
        </template>
        
        <!-- Regular Grid -->
        <div
          v-else
          class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6"
        >
          <CollectionAssetCard
            v-for="asset in assets"
            :key="asset.id"
            :asset="asset"
            :show-favorite="showFavoriteButton"
            :show-owner="showOwner"
            @click="emit('asset-click', asset)"
            @favorite="emit('toggle-favorite', asset)"
            @preview="emit('preview', asset)"
            @download="emit('download', asset)"
            @share="emit('share', asset)"
          />
        </div>
        
        <!-- Load More / Pagination -->
        <div v-if="hasMore" class="flex justify-center pt-6">
          <button
            type="button"
            class="px-6 py-3 text-sm font-medium text-primary-600 bg-primary-50 rounded-xl hover:bg-primary-100 transition-colors"
            :disabled="isLoadingMore"
            @click="emit('load-more')"
          >
            <span v-if="isLoadingMore" class="inline-flex items-center gap-2">
              <svg class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              Загрузка...
            </span>
            <span v-else>Показать ещё</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, h } from 'vue'
import CollectionAssetCard from './CollectionAssetCard.vue'
import type { ExtendedAsset } from '@/mocks/assets'

// ============================================================================
// PROPS
// ============================================================================

interface TimeGroup {
  label: string
  assets: ExtendedAsset[]
}

interface Props {
  title: string
  subtitle?: string
  assets: ExtendedAsset[]
  totalCount: number
  isLoading?: boolean
  isLoadingMore?: boolean
  hasMore?: boolean
  showStats?: boolean
  showUploadButton?: boolean
  showFavoriteButton?: boolean
  showOwner?: boolean
  groupByTime?: boolean
  groupedAssets?: TimeGroup[]
  
  // Empty state customization
  emptyTitle?: string
  emptyDescription?: string
  emptyActionText?: string
  emptyActionLink?: string
}

const props = withDefaults(defineProps<Props>(), {
  isLoading: false,
  isLoadingMore: false,
  hasMore: false,
  showStats: true,
  showUploadButton: false,
  showFavoriteButton: true,
  showOwner: false,
  groupByTime: false,
  groupedAssets: () => [],
  emptyTitle: 'Ничего не найдено',
  emptyDescription: 'В этой коллекции пока нет файлов',
  emptyActionText: 'Перейти в галерею',
  emptyActionLink: '/dam',
})

// ============================================================================
// EMITS
// ============================================================================

const emit = defineEmits<{
  'asset-click': [asset: ExtendedAsset]
  'toggle-favorite': [asset: ExtendedAsset]
  'preview': [asset: ExtendedAsset]
  'download': [asset: ExtendedAsset]
  'share': [asset: ExtendedAsset]
  'load-more': []
  'upload': []
}>()

// ============================================================================
// COMPUTED
// ============================================================================

// Default empty icon component
const emptyIcon = computed(() => ({
  render() {
    return h('svg', {
      fill: 'none',
      stroke: 'currentColor',
      viewBox: '0 0 24 24',
    }, [
      h('path', {
        'stroke-linecap': 'round',
        'stroke-linejoin': 'round',
        'stroke-width': '1.5',
        d: 'M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z',
      }),
    ])
  },
}))

// ============================================================================
// HELPERS
// ============================================================================

function pluralize(count: number, one: string, few: string, many: string): string {
  const mod10 = count % 10
  const mod100 = count % 100
  
  if (mod10 === 1 && mod100 !== 11) return one
  if (mod10 >= 2 && mod10 <= 4 && (mod100 < 10 || mod100 >= 20)) return few
  return many
}
</script>

<style scoped>
.collection-browser {
  padding-top: calc(var(--header-height, 64px));
}
</style>

