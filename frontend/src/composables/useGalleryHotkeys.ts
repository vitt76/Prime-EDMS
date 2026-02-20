/**
 * Gallery hotkeys composable (Sprint 2 Productivity & UX).
 *
 * Binds F, Space, Delete, Backspace, Esc, Ctrl+A, Shift+? with:
 * - Ignore when focus is in input/textarea/contenteditable (no conflict with search).
 * - Optional modal-aware Esc (close preview/cheatsheet first, then clear selection).
 */

import { onMounted, onUnmounted } from 'vue'

function isEditableElement(target: EventTarget | null): boolean {
  if (!target || !(target instanceof HTMLElement)) return false
  const el = target as HTMLElement
  return !!(
    el.closest('input') ||
    el.closest('textarea') ||
    el.closest('[contenteditable="true"]')
  )
}

export interface UseGalleryHotkeysOptions {
  /** Current selection count (for F, Space, Delete, Backspace). */
  getSelectedCount: () => number
  /** Toggle favorite for selected assets. */
  onFavorite: () => void | Promise<void>
  /** Open preview for selected asset(s). */
  onPreview: () => void
  /** Open delete confirmation (e.g. BulkDeleteModal). */
  onDelete: () => void
  /** Clear selection. */
  onClearSelection: () => void
  /** Select all assets in current view. */
  onSelectAll: () => void
  /** Open keyboard shortcuts cheat sheet modal. */
  onOpenCheatSheet: () => void
  /** Whether preview modal is open (Esc closes it first). */
  isPreviewOpen?: () => boolean
  /** Whether cheat sheet modal is open (Esc closes it first). */
  isCheatSheetOpen?: () => boolean
  /** Close preview modal. */
  onClosePreview?: () => void
  /** Close cheat sheet modal. */
  onCloseCheatSheet?: () => void
}

export function useGalleryHotkeys(options: UseGalleryHotkeysOptions): void {
  const {
    getSelectedCount,
    onFavorite,
    onPreview,
    onDelete,
    onClearSelection,
    onSelectAll,
    onOpenCheatSheet,
    isPreviewOpen = () => false,
    isCheatSheetOpen = () => false,
    onClosePreview,
    onCloseCheatSheet
  } = options

  function handleKeydown(event: KeyboardEvent): void {
    const target = event.target as HTMLElement | null
    const inInput = isEditableElement(target)
    const selectedCount = getSelectedCount()

    // Shift+? or ? (with Shift) — open cheat sheet
    if (event.key === '?' && event.shiftKey) {
      event.preventDefault()
      onOpenCheatSheet()
      return
    }

    // Escape — close modals first, then clear selection
    if (event.key === 'Escape') {
      if (isPreviewOpen() && onClosePreview) {
        event.preventDefault()
        onClosePreview()
        return
      }
      if (isCheatSheetOpen() && onCloseCheatSheet) {
        event.preventDefault()
        onCloseCheatSheet()
        return
      }
      if (selectedCount > 0) {
        event.preventDefault()
        onClearSelection()
      }
      return
    }

    // Ctrl+A / Cmd+A — select all (only when not in input)
    if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'a') {
      if (!inInput) {
        event.preventDefault()
        onSelectAll()
      }
      return
    }

    // F — toggle favorite for selected (only when not in input)
    if (event.key === 'f' && !event.ctrlKey && !event.metaKey && !event.altKey) {
      if (!inInput && selectedCount > 0) {
        event.preventDefault()
        void onFavorite()
      }
      return
    }

    // Space — preview (only when selection; prevent page scroll)
    if (event.key === ' ') {
      if (!inInput && selectedCount > 0) {
        event.preventDefault()
        onPreview()
      }
      return
    }

    // Delete or Backspace — open delete modal (only when not in input)
    if (event.key === 'Delete' || event.key === 'Backspace') {
      if (!inInput && selectedCount > 0) {
        event.preventDefault()
        onDelete()
      }
    }
  }

  onMounted(() => {
    document.addEventListener('keydown', handleKeydown)
  })

  onUnmounted(() => {
    document.removeEventListener('keydown', handleKeydown)
  })
}
