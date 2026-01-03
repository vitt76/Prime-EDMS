/**
 * Composition API hook for asset selection logic
 * 
 * Provides Google Photos-style selection with Shift+Click range selection,
 * keyboard shortcuts (Ctrl+A, Delete), and selection state management.
 * 
 * @example
 * ```vue
 * <script setup>
 * import { useAssetSelection } from '@/composables/useAssetSelection'
 * 
 * const { 
 *   selectedAssets, 
 *   isSelected, 
 *   toggleSelection, 
 *   selectRange,
 *   selectAll,
 *   clearSelection 
 * } = useAssetSelection(assets)
 * </script>
 * ```
 */

import { ref, computed, type Ref } from 'vue'
import type { Asset } from '@/types/api'

export interface UseAssetSelectionOptions {
  /**
   * Whether to enable keyboard shortcuts (Ctrl+A, Delete)
   * @default true
   */
  enableKeyboardShortcuts?: boolean
  
  /**
   * Callback when selection changes
   */
  onSelectionChange?: (selectedIds: Set<number>) => void
}

export function useAssetSelection(
  assets: Ref<Asset[]>,
  options: UseAssetSelectionOptions = {}
) {
  const {
    enableKeyboardShortcuts = true,
    onSelectionChange
  } = options

  // Selection state
  const selectedAssets = ref<Set<number>>(new Set())
  const lastSelectedIndex = ref<number | null>(null)

  // Computed
  const selectedCount = computed(() => selectedAssets.value.size)
  const hasSelection = computed(() => selectedAssets.value.size > 0)
  const allSelected = computed(() => 
    assets.value.length > 0 && selectedAssets.value.size === assets.value.length
  )
  const selectedAssetsList = computed(() =>
    assets.value.filter(asset => selectedAssets.value.has(asset.id))
  )

  // Selection methods
  function isSelected(assetId: number): boolean {
    return selectedAssets.value.has(assetId)
  }

  function toggleSelection(asset: Asset, index: number, event?: MouseEvent): void {
    const isShiftClick = event?.shiftKey && lastSelectedIndex.value !== null

    if (isShiftClick) {
      // Range selection
      selectRange(lastSelectedIndex.value!, index)
    } else {
      // Toggle single asset
      if (selectedAssets.value.has(asset.id)) {
        selectedAssets.value.delete(asset.id)
      } else {
        selectedAssets.value.add(asset.id)
      }
      
      // Force reactivity
      selectedAssets.value = new Set(selectedAssets.value)
      lastSelectedIndex.value = index
      
      // Notify change
      onSelectionChange?.(selectedAssets.value)
    }
  }

  function selectRange(startIndex: number, endIndex: number): void {
    const start = Math.min(startIndex, endIndex)
    const end = Math.max(startIndex, endIndex)
    
    for (let i = start; i <= end; i++) {
      const asset = assets.value[i]
      if (asset) {
        selectedAssets.value.add(asset.id)
      }
    }
    
    // Force reactivity
    selectedAssets.value = new Set(selectedAssets.value)
    lastSelectedIndex.value = endIndex
    
    // Notify change
    onSelectionChange?.(selectedAssets.value)
  }

  function selectAll(): void {
    assets.value.forEach(asset => {
      selectedAssets.value.add(asset.id)
    })
    
    // Force reactivity
    selectedAssets.value = new Set(selectedAssets.value)
    
    // Notify change
    onSelectionChange?.(selectedAssets.value)
  }

  function clearSelection(): void {
    selectedAssets.value.clear()
    lastSelectedIndex.value = null
    
    // Force reactivity
    selectedAssets.value = new Set(selectedAssets.value)
    
    // Notify change
    onSelectionChange?.(selectedAssets.value)
  }

  function selectAsset(assetId: number): void {
    selectedAssets.value.add(assetId)
    selectedAssets.value = new Set(selectedAssets.value)
    onSelectionChange?.(selectedAssets.value)
  }

  function deselectAsset(assetId: number): void {
    selectedAssets.value.delete(assetId)
    selectedAssets.value = new Set(selectedAssets.value)
    onSelectionChange?.(selectedAssets.value)
  }

  // Keyboard shortcuts handler
  function handleKeydown(event: KeyboardEvent): void {
    if (!enableKeyboardShortcuts) return

    // Ctrl+A / Cmd+A: Select all
    if ((event.ctrlKey || event.metaKey) && event.key === 'a') {
      event.preventDefault()
      selectAll()
      return
    }

    // Delete / Backspace: Delete selected assets (if handler provided)
    if ((event.key === 'Delete' || event.key === 'Backspace') && hasSelection.value) {
      // Don't prevent default here - let parent component handle deletion
      // This is just a notification that deletion was requested
      return
    }

    // Escape: Clear selection
    if (event.key === 'Escape' && hasSelection.value) {
      event.preventDefault()
      clearSelection()
    }
  }

  return {
    // State
    selectedAssets,
    lastSelectedIndex,
    
    // Computed
    selectedCount,
    hasSelection,
    allSelected,
    selectedAssetsList,
    
    // Methods
    isSelected,
    toggleSelection,
    selectRange,
    selectAll,
    clearSelection,
    selectAsset,
    deselectAsset,
    handleKeydown
  }
}

