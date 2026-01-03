<template>
  <div
    :class="gridClasses"
    role="grid"
    :aria-label="`Галерея активов (${density} density)`"
  >
    <AssetCard
      v-for="(asset, index) in assets"
      :key="asset.id"
      :asset="asset"
      :is-selected="isAssetSelected(asset)"
      :is-shared="isAssetShared(asset.id)"
      :show-checkbox="true"
      :density="density"
      :data-index="index"
      @select="(asset, event) => handleAssetSelect(asset, index, event)"
      @open="handleAssetOpen"
      @preview="handleAssetPreview"
      @download="handleAssetDownload"
      @share="handleAssetShare"
      @delete="handleAssetDelete"
      @add-tags="handleAssetAddTags"
      @move="handleAssetMove"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import AssetCard from './AssetCard.vue'
import type { Asset } from '@/types/api'
import { useAssetStore } from '@/stores/assetStore'

interface Props {
  assets: Asset[]
  density?: 'compact' | 'comfortable'
  layout?: 'grid' | 'masonry'
}

const props = withDefaults(defineProps<Props>(), {
  density: 'comfortable',
  layout: 'grid'
})

const emit = defineEmits<{
  'asset-select': [asset: Asset, index: number]
  'asset-open': [asset: Asset]
  'asset-preview': [asset: Asset]
  'asset-download': [asset: Asset]
  'asset-share': [asset: Asset]
  'asset-delete': [asset: Asset]
  'asset-add-tags': [asset: Asset]
  'asset-move': [asset: Asset]
}>()

const assetStore = useAssetStore()

// Selection state for Shift+Click range selection
const lastSelectedIndex = ref<number | null>(null)

// Grid classes based on density
const gridClasses = computed(() => {
  const base = ['w-full']
  
  if (props.layout === 'masonry') {
    // Masonry layout using CSS columns (fallback, not perfect but works)
    base.push('columns-auto')
    if (props.density === 'compact') {
      base.push('columns-[180px]', 'gap-2')
    } else {
      base.push('columns-[240px]', 'gap-4')
    }
  } else {
    // CSS Grid layout
    base.push('grid')
    if (props.density === 'compact') {
      base.push(
        'grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 2xl:grid-cols-8',
        'gap-2'
      )
    } else {
      base.push(
        'grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 2xl:grid-cols-6',
        'gap-4 sm:gap-6'
      )
    }
  }
  
  return base.join(' ')
})

// Check if asset is selected
function isAssetSelected(asset: Asset): boolean {
  return assetStore.selectedAssets.has(asset.id)
}

// Check if asset is shared
function isAssetShared(assetId: number): boolean {
  // TODO: Implement shared assets check
  return false
}

// Selection handler with Shift+Click support
function handleAssetSelect(asset: Asset, index: number, event?: MouseEvent) {
  const isShiftClick = event?.shiftKey && lastSelectedIndex.value !== null
  
  if (isShiftClick) {
    // Range selection: select all assets between lastSelectedIndex and current index
    const start = Math.min(lastSelectedIndex.value!, index)
    const end = Math.max(lastSelectedIndex.value!, index)
    
    for (let i = start; i <= end; i++) {
      const rangeAsset = props.assets[i]
      if (rangeAsset) {
        if (!assetStore.selectedAssets.has(rangeAsset.id)) {
          assetStore.toggleSelection(rangeAsset.id)
        }
      }
    }
  } else {
    // Toggle single asset (multi-select)
    assetStore.selectAsset(asset, true)
    
    // Update last selected index for future Shift+Click
    lastSelectedIndex.value = index
  }
  
  emit('asset-select', asset, index)
}

function handleAssetOpen(asset: Asset) {
  emit('asset-open', asset)
}

function handleAssetPreview(asset: Asset) {
  emit('asset-preview', asset)
}

function handleAssetDownload(asset: Asset) {
  emit('asset-download', asset)
}

function handleAssetShare(asset: Asset) {
  emit('asset-share', asset)
}

function handleAssetDelete(asset: Asset) {
  emit('asset-delete', asset)
}

function handleAssetAddTags(asset: Asset) {
  emit('asset-add-tags', asset)
}

function handleAssetMove(asset: Asset) {
  emit('asset-move', asset)
}
</script>

<style scoped>
/* Masonry layout fallback using CSS columns */
.columns-auto {
  column-fill: balance;
}

.columns-auto > * {
  break-inside: avoid;
  margin-bottom: var(--gap, 1rem);
}

/* Ensure cards don't break across columns */
.columns-auto > * {
  page-break-inside: avoid;
  break-inside: avoid;
}
</style>

