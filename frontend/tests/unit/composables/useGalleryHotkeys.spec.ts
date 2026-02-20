import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { defineComponent, h } from 'vue'
import { useGalleryHotkeys } from '@/composables/useGalleryHotkeys'

describe('useGalleryHotkeys', () => {
  const defaultOptions = () => ({
    getSelectedCount: vi.fn(() => 1),
    onFavorite: vi.fn(),
    onPreview: vi.fn(),
    onDelete: vi.fn(),
    onClearSelection: vi.fn(),
    onSelectAll: vi.fn(),
    onOpenCheatSheet: vi.fn(),
    isPreviewOpen: vi.fn(() => false),
    isCheatSheetOpen: vi.fn(() => false),
    onClosePreview: vi.fn(),
    onCloseCheatSheet: vi.fn()
  })

  /** Mount a component that calls useGalleryHotkeys so the listener is registered. */
  function mountWithHotkeys(options: ReturnType<typeof defaultOptions>) {
    return mount(
      defineComponent({
        setup() {
          useGalleryHotkeys(options)
          return () => h('div', { 'data-testid': 'gallery' })
        }
      }),
      { attachTo: document.body }
    )
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    document.body.innerHTML = ''
  })

  it('calls onFavorite when F is pressed and selection exists and focus not in input', async () => {
    const options = defaultOptions()
    mountWithHotkeys(options)

    const ev = new KeyboardEvent('keydown', { key: 'f', bubbles: true })
    document.dispatchEvent(ev)

    expect(options.onFavorite).toHaveBeenCalledTimes(1)
  })

  it('does not call onFavorite when F is pressed but focus is in input', async () => {
    const options = defaultOptions()
    mountWithHotkeys(options)

    const input = document.createElement('input')
    input.setAttribute('type', 'text')
    document.body.appendChild(input)
    input.focus()

    const ev = new KeyboardEvent('keydown', { key: 'f', bubbles: true })
    input.dispatchEvent(ev)

    expect(options.onFavorite).not.toHaveBeenCalled()
  })

  it('does not call onFavorite when selection is zero', async () => {
    const options = defaultOptions()
    options.getSelectedCount.mockReturnValue(0)
    mountWithHotkeys(options)

    const ev = new KeyboardEvent('keydown', { key: 'f', bubbles: true })
    document.dispatchEvent(ev)

    expect(options.onFavorite).not.toHaveBeenCalled()
  })

  it('calls onPreview when Space is pressed with selection and not in input', async () => {
    const options = defaultOptions()
    mountWithHotkeys(options)

    const ev = new KeyboardEvent('keydown', { key: ' ', bubbles: true })
    document.dispatchEvent(ev)

    expect(options.onPreview).toHaveBeenCalledTimes(1)
  })

  it('calls onDelete when Delete is pressed with selection and not in input', async () => {
    const options = defaultOptions()
    mountWithHotkeys(options)

    const ev = new KeyboardEvent('keydown', { key: 'Delete', bubbles: true })
    document.dispatchEvent(ev)

    expect(options.onDelete).toHaveBeenCalledTimes(1)
  })

  it('calls onOpenCheatSheet when Shift+? is pressed', async () => {
    const options = defaultOptions()
    mountWithHotkeys(options)

    const ev = new KeyboardEvent('keydown', { key: '?', shiftKey: true, bubbles: true })
    document.dispatchEvent(ev)

    expect(options.onOpenCheatSheet).toHaveBeenCalledTimes(1)
  })

  it('calls onClearSelection when Escape is pressed with selection and no modals open', async () => {
    const options = defaultOptions()
    mountWithHotkeys(options)

    const ev = new KeyboardEvent('keydown', { key: 'Escape', bubbles: true })
    document.dispatchEvent(ev)

    expect(options.onClearSelection).toHaveBeenCalledTimes(1)
  })

  it('calls onClosePreview when Escape is pressed and preview is open', async () => {
    const options = defaultOptions()
    options.isPreviewOpen.mockReturnValue(true)
    mountWithHotkeys(options)

    const ev = new KeyboardEvent('keydown', { key: 'Escape', bubbles: true })
    document.dispatchEvent(ev)

    expect(options.onClosePreview).toHaveBeenCalledTimes(1)
    expect(options.onClearSelection).not.toHaveBeenCalled()
  })

  it('calls onSelectAll when Ctrl+A is pressed and not in input', async () => {
    const options = defaultOptions()
    mountWithHotkeys(options)

    const ev = new KeyboardEvent('keydown', {
      key: 'a',
      ctrlKey: true,
      bubbles: true
    })
    document.dispatchEvent(ev)

    expect(options.onSelectAll).toHaveBeenCalledTimes(1)
  })
})
