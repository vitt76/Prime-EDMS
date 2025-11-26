<template>
  <div class="asset-grid">
    <!-- Loading State -->
    <div v-if="isLoading" class="asset-grid__loading" role="status" aria-live="polite">
      <div
        v-for="i in 8"
        :key="i"
        class="asset-grid__skeleton"
        :aria-label="`Loading asset ${i}`"
      />
    </div>

    <!-- Empty State -->
    <div
      v-else-if="assets.length === 0"
      class="asset-grid__empty"
      role="status"
      aria-live="polite"
    >
      <svg
        class="w-16 h-16 text-neutral-400"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
        aria-hidden="true"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
        />
      </svg>
      <p class="asset-grid__empty-text">No assets in this collection</p>
    </div>

    <!-- Assets Grid -->
    <div v-else class="asset-grid__grid" role="grid" aria-label="Collection assets">
      <div
        v-for="asset in assets"
        :key="asset.id"
        class="asset-grid__item"
        role="gridcell"
        @click="handleAssetClick(asset.id)"
        @keydown.enter="handleAssetClick(asset.id)"
        @keydown.space.prevent="handleAssetClick(asset.id)"
        tabindex="0"
        :aria-label="`Asset ${asset.label || asset.filename}`"
      >
        <div class="asset-grid__thumbnail">
          <img
            v-if="asset.thumbnail_url"
            :src="asset.thumbnail_url"
            :alt="asset.label || asset.filename"
            class="asset-grid__image"
            loading="lazy"
          />
          <div v-else class="asset-grid__placeholder">
            <svg
              class="w-12 h-12 text-neutral-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
              />
            </svg>
          </div>
        </div>
        <div class="asset-grid__info">
          <p class="asset-grid__name" :title="asset.label || asset.filename">
            {{ asset.label || asset.filename }}
          </p>
          <p class="asset-grid__meta">{{ formatFileSize(asset.size) }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { collectionsService } from '@/services/collectionsService'
import type { Asset } from '@/types/api'
import type { CollectionWithAssets } from '@/types/collections'

interface Props {
  collectionId: number | string
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'asset-click': [assetId: number]
}>()

const assets = ref<Asset[]>([])
const isLoading = ref(false)

const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i]
}

const loadAssets = async (): Promise<void> => {
  if (typeof props.collectionId !== 'number') {
    assets.value = []
    return
  }

  isLoading.value = true
  try {
    const collection = await collectionsService.getCollection(props.collectionId)
    assets.value = (collection as CollectionWithAssets).assets || []
  } catch (error) {
    console.error('Failed to load collection assets:', error)
    assets.value = []
  } finally {
    isLoading.value = false
  }
}

const handleAssetClick = (assetId: number): void => {
  emit('asset-click', assetId)
}

onMounted(() => {
  loadAssets()
})
</script>

<style scoped lang="css">
.asset-grid {
  width: 100%;
}

.asset-grid__loading {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
}

.asset-grid__skeleton {
  aspect-ratio: 1;
  background: var(--color-bg-1, #f9fafb);
  border-radius: var(--radius-base, 6px);
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@keyframes pulse {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.asset-grid__empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 64px 24px;
  color: var(--color-text-secondary, #6b7280);
  gap: 16px;
}

.asset-grid__empty-text {
  font-size: var(--font-size-base, 14px);
  margin: 0;
}

.asset-grid__grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
}

.asset-grid__item {
  display: flex;
  flex-direction: column;
  background: var(--color-surface, #ffffff);
  border: 1px solid var(--color-border, #e5e7eb);
  border-radius: var(--radius-base, 6px);
  overflow: hidden;
  cursor: pointer;
  transition: all 200ms ease;
}

.asset-grid__item:hover {
  border-color: var(--color-primary, #3b82f6);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.asset-grid__item:focus-visible {
  outline: 2px solid var(--color-primary, #3b82f6);
  outline-offset: 2px;
}

.asset-grid__thumbnail {
  width: 100%;
  aspect-ratio: 1;
  background: var(--color-bg-1, #f9fafb);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.asset-grid__image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.asset-grid__placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
}

.asset-grid__info {
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.asset-grid__name {
  font-size: var(--font-size-sm, 12px);
  font-weight: 500;
  color: var(--color-text, #111827);
  margin: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.asset-grid__meta {
  font-size: var(--font-size-xs, 11px);
  color: var(--color-text-secondary, #6b7280);
  margin: 0;
}

/* Responsive */
@media (max-width: 768px) {
  .asset-grid__grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 12px;
  }
}

@media (prefers-reduced-motion: reduce) {
  .asset-grid__item {
    transition: none;
  }

  .asset-grid__skeleton {
    animation: none;
  }
}
</style>



