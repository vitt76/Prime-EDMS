/**
 * VirtualScroller Component Tests
 *
 * Tests for high-performance virtual scrolling with buffer management,
 * infinite scroll, keyboard navigation, and accessibility.
 */

import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { mount, VueWrapper } from '@vue/test-utils'
import { nextTick } from 'vue'
import VirtualScroller from '../VirtualScroller.vue'

// Mock lodash throttle
vi.mock('lodash-es', () => ({
  throttle: (fn: Function) => fn
}))

describe('VirtualScroller', () => {
  let wrapper: VueWrapper<any>
  const mockItems = Array.from({ length: 1000 }, (_, i) => ({
    id: `item-${i}`,
    name: `Item ${i}`,
    value: i
  }))

  const defaultProps = {
    items: mockItems,
    totalItems: 1000,
    itemHeight: 50,
    containerHeight: 400
  }

  beforeEach(() => {
    // Mock IntersectionObserver
    global.IntersectionObserver = vi.fn().mockImplementation(() => ({
      observe: vi.fn(),
      unobserve: vi.fn(),
      disconnect: vi.fn()
    }))

    // Mock ResizeObserver
    global.ResizeObserver = vi.fn().mockImplementation(() => ({
      observe: vi.fn(),
      unobserve: vi.fn(),
      disconnect: vi.fn()
    }))
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  describe('Initialization', () => {
    beforeEach(() => {
      wrapper = mount(VirtualScroller, {
        props: defaultProps,
        global: {
          stubs: ['GalleryItem', 'GalleryItemSkeleton']
        }
      })
    })

    it('renders correctly with default props', () => {
      expect(wrapper.exists()).toBe(true)
      expect(wrapper.find('.virtual-scroller').exists()).toBe(true)
    })

    it('sets correct container height', () => {
      const scroller = wrapper.find('.virtual-scroller')
      expect(scroller.attributes('style')).toContain('height: 400px')
    })

    it('calculates visible range correctly', () => {
      // With container height 400 and item height 50, should show 8 items (400/50)
      // Plus buffer of 5 above and below = visible range of 0-18
      expect(wrapper.vm.visibleRange.start).toBe(0)
      expect(wrapper.vm.visibleRange.end).toBe(18)
    })

    it('renders correct number of visible items', () => {
      const items = wrapper.findAll('.virtual-scroller__item')
      expect(items.length).toBe(18) // 8 visible + 5 buffer above + 5 buffer below
    })

    it('sets correct spacer height', () => {
      const spacer = wrapper.find('.virtual-scroller__spacer')
      expect(spacer.attributes('style')).toContain('height: 50000px') // 1000 * 50
    })
  })

  describe('Virtual Scrolling', () => {
    beforeEach(() => {
      wrapper = mount(VirtualScroller, {
        props: defaultProps,
        global: {
          stubs: ['GalleryItem', 'GalleryItemSkeleton']
        }
      })
    })

    it('updates visible range on scroll', async () => {
      const scroller = wrapper.find('.virtual-scroller').element as HTMLElement

      // Simulate scroll to show items 50-68
      scroller.scrollTop = 2500 // 50 * 50px
      await wrapper.vm.handleScroll()

      expect(wrapper.vm.visibleRange.start).toBe(45) // 50 - 5 buffer
      expect(wrapper.vm.visibleRange.end).toBe(73)  // 68 + 5 buffer
    })

    it('applies correct transform to items container', async () => {
      const scroller = wrapper.find('.virtual-scroller').element as HTMLElement

      scroller.scrollTop = 500 // 10 * 50px
      await wrapper.vm.handleScroll()

      const itemsContainer = wrapper.find('.virtual-scroller__items')
      expect(itemsContainer.attributes('style')).toContain('translateY(250px)') // 5 * 50px (buffer start)
    })

    it('emits load-more when scrolling near bottom', async () => {
      const scroller = wrapper.find('.virtual-scroller').element as HTMLElement

      // Scroll to near bottom (within loadMoreThreshold)
      scroller.scrollTop = 48500 // Close to 50000 total height
      await wrapper.vm.handleScroll()

      expect(wrapper.emitted('load-more')).toBeTruthy()
    })

    it('does not emit load-more when already loading', async () => {
      await wrapper.setProps({ isLoading: true })
      const scroller = wrapper.find('.virtual-scroller').element as HTMLElement

      scroller.scrollTop = 48500
      await wrapper.vm.handleScroll()

      expect(wrapper.emitted('load-more')).toBeFalsy()
    })
  })

  describe('Buffer Management', () => {
    it('respects custom buffer size', () => {
      wrapper = mount(VirtualScroller, {
        props: {
          ...defaultProps,
          bufferSize: 10
        },
        global: {
          stubs: ['GalleryItem', 'GalleryItemSkeleton']
        }
      })

      // Should show 8 visible + 10 buffer above + 10 buffer below = 28 items
      expect(wrapper.vm.visibleRange.end - wrapper.vm.visibleRange.start).toBe(28)
    })

    it('handles edge cases with small datasets', () => {
      const smallItems = mockItems.slice(0, 5)

      wrapper = mount(VirtualScroller, {
        props: {
          ...defaultProps,
          items: smallItems,
          totalItems: 5
        },
        global: {
          stubs: ['GalleryItem', 'GalleryItemSkeleton']
        }
      })

      expect(wrapper.vm.visibleRange.start).toBe(0)
      expect(wrapper.vm.visibleRange.end).toBe(5) // Don't exceed total items
    })
  })

  describe('Keyboard Navigation', () => {
    beforeEach(() => {
      wrapper = mount(VirtualScroller, {
        props: defaultProps,
        global: {
          stubs: ['GalleryItem', 'GalleryItemSkeleton']
        }
      })
    })

    it('handles arrow key navigation', async () => {
      const scroller = wrapper.find('.virtual-scroller').element as HTMLElement

      // Focus the scroller
      scroller.focus()

      // Simulate arrow down
      await wrapper.trigger('keydown', { key: 'ArrowDown' })
      expect(scroller.scrollTop).toBe(50) // One item height

      // Simulate page down
      await wrapper.trigger('keydown', { key: 'PageDown' })
      expect(scroller.scrollTop).toBe(450) // 50 + container height
    })

    it('handles home/end navigation', async () => {
      const scroller = wrapper.find('.virtual-scroller').element as HTMLElement

      scroller.focus()

      // End key
      await wrapper.trigger('keydown', { key: 'End' })
      expect(scroller.scrollTop).toBe(49600) // Total height - container height

      // Home key
      await wrapper.trigger('keydown', { key: 'Home' })
      expect(scroller.scrollTop).toBe(0)
    })

    it('ignores keyboard events when not focused', async () => {
      const scroller = wrapper.find('.virtual-scroller').element as HTMLElement

      // Don't focus
      await wrapper.trigger('keydown', { key: 'ArrowDown' })
      expect(scroller.scrollTop).toBe(0)
    })
  })

  describe('Loading States', () => {
    it('shows loading indicator when isLoading is true', async () => {
      wrapper = mount(VirtualScroller, {
        props: {
          ...defaultProps,
          isLoading: true
        },
        global: {
          stubs: ['GalleryItem', 'GalleryItemSkeleton']
        }
      })

      const loader = wrapper.find('.virtual-scroller__bottom-loader')
      expect(loader.exists()).toBe(true)
      expect(loader.text()).toContain('Loading more items...')
    })

    it('shows custom loading slot', () => {
      wrapper = mount(VirtualScroller, {
        props: {
          ...defaultProps,
          isLoading: true
        },
        slots: {
          loading: '<div>Custom loading...</div>'
        },
        global: {
          stubs: ['GalleryItem', 'GalleryItemSkeleton']
        }
      })

      expect(wrapper.text()).toContain('Custom loading...')
    })

    it('shows error state', () => {
      wrapper = mount(VirtualScroller, {
        props: {
          ...defaultProps,
          error: 'Failed to load items'
        },
        global: {
          stubs: ['GalleryItem', 'GalleryItemSkeleton']
        }
      })

      const errorDiv = wrapper.find('.virtual-scroller__error')
      expect(errorDiv.exists()).toBe(true)
      expect(errorDiv.text()).toContain('Failed to load items')
    })

    it('shows empty state when no items', () => {
      wrapper = mount(VirtualScroller, {
        props: {
          ...defaultProps,
          items: [],
          totalItems: 0
        },
        global: {
          stubs: ['GalleryItem', 'GalleryItemSkeleton']
        }
      })

      const emptyDiv = wrapper.find('.virtual-scroller__empty')
      expect(emptyDiv.exists()).toBe(true)
      expect(emptyDiv.text()).toContain('No items found')
    })

    it('shows custom empty slot', () => {
      wrapper = mount(VirtualScroller, {
        props: {
          ...defaultProps,
          items: [],
          totalItems: 0
        },
        slots: {
          empty: '<div>Custom empty state</div>'
        },
        global: {
          stubs: ['GalleryItem', 'GalleryItemSkeleton']
        }
      })

      expect(wrapper.text()).toContain('Custom empty state')
    })
  })

  describe('Skeletons', () => {
    it('renders correct number of skeleton items when loading', () => {
      wrapper = mount(VirtualScroller, {
        props: {
          ...defaultProps,
          isLoading: true
        },
        global: {
          stubs: ['GalleryItem', 'GalleryItemSkeleton']
        }
      })

      const skeletons = wrapper.findAll('.virtual-scroller__item--skeleton')
      expect(skeletons.length).toBe(wrapper.vm.loadingItemsCount)
    })

    it('passes correct props to skeleton slot', () => {
      let skeletonProps: any = null

      wrapper = mount(VirtualScroller, {
        props: defaultProps,
        slots: {
          skeleton: (props: any) => {
            skeletonProps = props
            return '<div>Skeleton</div>'
          }
        },
        global: {
          stubs: ['GalleryItem']
        }
      })

      expect(skeletonProps).toBeDefined()
      expect(skeletonProps.index).toBeGreaterThanOrEqual(0)
    })
  })

  describe('Accessibility', () => {
    beforeEach(() => {
      wrapper = mount(VirtualScroller, {
        props: {
          ...defaultProps,
          ariaLabel: 'Test gallery'
        },
        global: {
          stubs: ['GalleryItem', 'GalleryItemSkeleton']
        }
      })
    })

    it('has correct ARIA attributes', () => {
      const scroller = wrapper.find('.virtual-scroller')
      expect(scroller.attributes('role')).toBe('list')
      expect(scroller.attributes('aria-label')).toBe('Test gallery')
    })

    it('has correct ARIA attributes on list items', () => {
      const items = wrapper.findAll('.virtual-scroller__item')
      items.forEach(item => {
        expect(item.attributes('role')).toBe('listitem')
      })
    })

    it('is keyboard focusable', () => {
      const scroller = wrapper.find('.virtual-scroller')
      expect(scroller.attributes('tabindex')).toBe('0')
    })

    it('has screen reader status for loading', async () => {
      await wrapper.setProps({ isLoading: true })

      const status = wrapper.find('[role="status"]')
      expect(status.exists()).toBe(true)
      expect(status.attributes('aria-live')).toBe('polite')
    })
  })

  describe('Performance', () => {
    it('throttles scroll events', () => {
      const mockThrottle = vi.fn()
      vi.mocked(require('lodash-es').throttle).mockReturnValue(mockThrottle)

      wrapper = mount(VirtualScroller, {
        props: defaultProps,
        global: {
          stubs: ['GalleryItem', 'GalleryItemSkeleton']
        }
      })

      // Should use throttled version
      expect(vi.mocked(require('lodash-es').throttle)).toHaveBeenCalled()
    })

    it('only renders visible items plus buffer', () => {
      // With 1000 items, should only render ~18 items (8 visible + 10 buffer)
      const items = wrapper.findAll('.virtual-scroller__item')
      expect(items.length).toBeLessThan(50) // Much less than total
    })

    it('updates efficiently on prop changes', async () => {
      const newItems = mockItems.slice(0, 500)

      await wrapper.setProps({
        items: newItems,
        totalItems: 500
      })

      // Should recalculate visible range
      expect(wrapper.vm.totalHeight).toBe(25000) // 500 * 50
    })
  })

  describe('Edge Cases', () => {
    it('handles zero item height gracefully', () => {
      wrapper = mount(VirtualScroller, {
        props: {
          ...defaultProps,
          itemHeight: 0
        },
        global: {
          stubs: ['GalleryItem', 'GalleryItemSkeleton']
        }
      })

      expect(wrapper.vm.totalHeight).toBe(0)
      expect(wrapper.vm.visibleRange.start).toBe(0)
      expect(wrapper.vm.visibleRange.end).toBe(0)
    })

    it('handles negative scroll positions', async () => {
      const scroller = wrapper.find('.virtual-scroller').element as HTMLElement

      scroller.scrollTop = -100
      await wrapper.vm.handleScroll()

      expect(wrapper.vm.visibleRange.start).toBeGreaterThanOrEqual(0)
    })

    it('handles very large datasets', () => {
      wrapper = mount(VirtualScroller, {
        props: {
          ...defaultProps,
          totalItems: 1000000 // 1 million items
        },
        global: {
          stubs: ['GalleryItem', 'GalleryItemSkeleton']
        }
      })

      expect(wrapper.vm.totalHeight).toBe(50000000) // 1M * 50px
      expect(wrapper.vm.visibleRange.end).toBeLessThan(100) // Still reasonable visible count
    })

    it('handles dynamic container height changes', async () => {
      await wrapper.setProps({ containerHeight: 800 })

      // Should show more items (800/50 = 16 visible + buffers)
      expect(wrapper.vm.visibleRange.end - wrapper.vm.visibleRange.start).toBeGreaterThan(20)
    })
  })

  describe('Exposed Methods', () => {
    beforeEach(() => {
      wrapper = mount(VirtualScroller, {
        props: defaultProps,
        global: {
          stubs: ['GalleryItem', 'GalleryItemSkeleton']
        }
      })
    })

    it('exposes scrollToItem method', () => {
      expect(typeof wrapper.vm.scrollToItem).toBe('function')
    })

    it('exposes scrollToTop method', () => {
      expect(typeof wrapper.vm.scrollToTop).toBe('function')
    })

    it('exposes getVisibleRange method', () => {
      expect(typeof wrapper.vm.getVisibleRange).toBe('function')
    })

    it('scrollToItem scrolls to correct position', async () => {
      const scroller = wrapper.find('.virtual-scroller').element as HTMLElement

      wrapper.vm.scrollToItem(100) // Scroll to item at index 100

      expect(scroller.scrollTop).toBe(5000) // 100 * 50px
    })

    it('scrollToTop scrolls to top', () => {
      const scroller = wrapper.find('.virtual-scroller').element as HTMLElement

      // First scroll down
      scroller.scrollTop = 1000
      wrapper.vm.scrollToTop()

      expect(scroller.scrollTop).toBe(0)
    })

    it('getVisibleRange returns current range', () => {
      const range = wrapper.vm.getVisibleRange()
      expect(range).toHaveProperty('start')
      expect(range).toHaveProperty('end')
      expect(range.start).toBe(0)
      expect(range.end).toBe(18)
    })
  })

  describe('Reactivity', () => {
    it('reacts to items prop changes', async () => {
      const newItems = mockItems.slice(0, 500)

      await wrapper.setProps({
        items: newItems,
        totalItems: 500
      })

      expect(wrapper.vm.totalHeight).toBe(25000) // 500 * 50
    })

    it('reacts to itemHeight changes', async () => {
      await wrapper.setProps({ itemHeight: 100 })

      expect(wrapper.vm.totalHeight).toBe(100000) // 1000 * 100
    })

    it('reacts to totalItems changes', async () => {
      await wrapper.setProps({ totalItems: 500 })

      expect(wrapper.vm.totalHeight).toBe(25000) // 500 * 50
    })
  })
})


















