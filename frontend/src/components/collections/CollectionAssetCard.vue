<template>
  <div
    class="collection-asset-card group relative bg-white rounded-xl border border-neutral-200 overflow-hidden cursor-pointer transition-all duration-200 hover:shadow-lg hover:border-primary-200 hover:-translate-y-0.5"
    @click="emit('click', asset)"
  >
    <!-- Thumbnail -->
    <div class="relative aspect-video bg-neutral-100 overflow-hidden">
      <img
        v-if="asset.thumbnail_url"
        :src="asset.thumbnail_url"
        :alt="asset.label"
        class="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
        loading="lazy"
      />
      <div
        v-else
        class="w-full h-full flex items-center justify-center text-neutral-400"
      >
        <svg class="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
      </div>
      
      <!-- Type Badge -->
      <span
        v-if="assetType"
        class="absolute top-2 left-2 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wider bg-black/50 text-white rounded backdrop-blur-sm"
      >
        {{ assetType }}
      </span>
      
      <!-- Favorite Button -->
      <button
        v-if="showFavorite"
        type="button"
        class="absolute top-2 right-2 p-1.5 rounded-full transition-all duration-200"
        :class="[
          asset.isFavorite
            ? 'bg-error-500 text-white shadow-lg'
            : 'bg-black/30 text-white/80 hover:bg-black/50 hover:text-white opacity-0 group-hover:opacity-100'
        ]"
        @click.stop="emit('favorite', asset)"
        :title="asset.isFavorite ? 'Убрать из избранного' : 'Добавить в избранное'"
      >
        <svg class="w-4 h-4" :fill="asset.isFavorite ? 'currentColor' : 'none'" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
        </svg>
      </button>
      
      <!-- Owner Avatar (for SharedWithMe) -->
      <div
        v-if="showOwner && asset.sharedBy"
        class="absolute bottom-2 left-2 flex items-center gap-1.5 px-2 py-1 bg-black/50 backdrop-blur-sm rounded-full"
      >
        <img
          v-if="asset.sharedBy.avatar_url"
          :src="asset.sharedBy.avatar_url"
          :alt="asset.sharedBy.first_name"
          class="w-5 h-5 rounded-full object-cover border border-white/30"
        />
        <span
          v-else
          class="w-5 h-5 rounded-full bg-primary-500 text-white text-[10px] font-bold flex items-center justify-center"
        >
          {{ asset.sharedBy.first_name[0] }}{{ asset.sharedBy.last_name[0] }}
        </span>
        <span class="text-[10px] text-white font-medium">
          {{ asset.sharedBy.first_name }}
        </span>
      </div>
      
      <!-- Hover Actions Overlay -->
      <div class="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-200">
        <div class="absolute bottom-2 right-2 flex items-center gap-1">
          <button
            type="button"
            class="p-2 bg-white/90 rounded-lg hover:bg-white transition-colors"
            @click.stop="emit('preview', asset)"
            title="Предпросмотр"
          >
            <svg class="w-4 h-4 text-neutral-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
            </svg>
          </button>
          <button
            type="button"
            class="p-2 bg-white/90 rounded-lg hover:bg-white transition-colors"
            @click.stop="emit('download', asset)"
            title="Скачать"
          >
            <svg class="w-4 h-4 text-neutral-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
          </button>
          <button
            type="button"
            class="p-2 bg-white/90 rounded-lg hover:bg-white transition-colors"
            @click.stop="emit('share', asset)"
            title="Поделиться"
          >
            <svg class="w-4 h-4 text-neutral-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
            </svg>
          </button>
        </div>
      </div>
    </div>
    
    <!-- Info -->
    <div class="p-3">
      <h3 class="text-sm font-medium text-neutral-900 truncate" :title="asset.label">
        {{ asset.label }}
      </h3>
      <div class="flex items-center justify-between mt-1.5">
        <span class="text-xs text-neutral-500">
          {{ formatFileSize(asset.size) }}
        </span>
        <span class="text-xs text-neutral-500">
          {{ formatDate(asset.date_added) }}
        </span>
      </div>
      
      <!-- Last Accessed (for Recent) -->
      <p v-if="showLastAccessed" class="text-[10px] text-neutral-400 mt-1">
        Открыт {{ formatRelativeTime(asset.lastAccessedAt) }}
      </p>
      
      <!-- Shared At (for SharedWithMe) -->
      <p v-if="showOwner && asset.sharedAt" class="text-[10px] text-neutral-400 mt-1">
        Расшарено {{ formatRelativeTime(asset.sharedAt) }}
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { ExtendedAsset } from '@/mocks/assets'

// ============================================================================
// PROPS
// ============================================================================

interface Props {
  asset: ExtendedAsset
  showFavorite?: boolean
  showOwner?: boolean
  showLastAccessed?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  showFavorite: true,
  showOwner: false,
  showLastAccessed: false,
})

// ============================================================================
// EMITS
// ============================================================================

const emit = defineEmits<{
  'click': [asset: ExtendedAsset]
  'favorite': [asset: ExtendedAsset]
  'preview': [asset: ExtendedAsset]
  'download': [asset: ExtendedAsset]
  'share': [asset: ExtendedAsset]
}>()

// ============================================================================
// COMPUTED
// ============================================================================

const assetType = computed(() => {
  const type = props.asset.metadata?.type as string
  if (!type) return null
  
  const typeMap: Record<string, string> = {
    image: 'IMG',
    video: 'VIDEO',
    document: 'DOC',
    audio: 'AUDIO',
  }
  
  return typeMap[type] || type.toUpperCase().slice(0, 4)
})

// ============================================================================
// FORMATTERS
// ============================================================================

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  if (bytes < 1024 * 1024 * 1024) return (bytes / 1024 / 1024).toFixed(1) + ' MB'
  return (bytes / 1024 / 1024 / 1024).toFixed(1) + ' GB'
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'short',
  })
}

function formatRelativeTime(dateStr: string): string {
  const now = new Date()
  const date = new Date(dateStr)
  const diffMs = now.getTime() - date.getTime()
  const diffSec = Math.floor(diffMs / 1000)
  const diffMin = Math.floor(diffSec / 60)
  const diffHours = Math.floor(diffMin / 60)
  const diffDays = Math.floor(diffHours / 24)
  
  if (diffSec < 60) return 'только что'
  if (diffMin < 60) return `${diffMin} мин. назад`
  if (diffHours < 24) return `${diffHours} ч. назад`
  if (diffDays === 1) return 'вчера'
  if (diffDays < 7) return `${diffDays} дн. назад`
  
  return formatDate(dateStr)
}
</script>

<style scoped>
.collection-asset-card {
  will-change: transform, box-shadow;
}
</style>

