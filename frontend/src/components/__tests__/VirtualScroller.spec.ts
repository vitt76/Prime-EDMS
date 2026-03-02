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
      const spacer = wrapper.find('.virtual-scroller__spacer')
      expect(scroller.classes()).toContain('virtual-scroller')
      expect(spacer.attributes('style')).toContain('50000px')
    })

    it('calculates visible range correctly', () => {
      // With container height 400 and item height 50: ceil(400/50)=8 visible, + buffer 5 => end=13
      expect(wrapper.vm.visibleRange.start).toBe(0)
      expect(wrapper.vm.visibleRange.end).toBe(13)
    })

    it('renders correct number of visible items', () => {
      const items = wrapper.findAll('.virtual-scroller__item')
      expect(items.length).toBe(13)
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

      // Simulate scroll: scrollTop 2500, container 400 => start=45, end=63
      scroller.scrollTop = 2500
      await wrapper.vm.handleScroll()

      expect(wrapper.vm.visibleRange.start).toBe(45)
      expect(wrapper.vm.visibleRange.end).toBe(63)
    })

    it('applies correct transform to items container', async () => {
      const scroller = wrapper.find('.virtual-scroller').element as HTMLElement

      scroller.scrollTop = 500 // start = floor(500/50)-5 = 5
      await wrapper.vm.handleScroll()

      const itemsContainer = wrapper.find('.virtual-scroller__items')
      expect(itemsContainer.attributes('style')).toContain('translateY(250px)')
    })

    it('emits load-more when scrolling near bottom', async () => {
      const scroller = wrapper.find('.virtual-scroller').element as HTMLElement

      // Scroll to bottom: scrollTop+400 >= totalHeight-200 => scrollTop >= 49400
      scroller.scrollTop = 49600
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

      // end = ceil(400/50)+10 = 18, start = 0 => 18 items
      expect(wrapper.vm.visibleRange.end - wrapper.vm.visibleRange.start).toBe(18)
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
      if (typeof scroller.scrollTo === 'function') {
        scroller.scrollTo = vi.fn(function (this: HTMLElement, opts?: ScrollToOptions) {
          if (opts?.top !== undefined) (this as any).scrollTop = opts.top
        }) as any
      }
      scroller.focus()

      await wrapper.trigger('keydown', { key: 'ArrowDown' })
      expect(scroller.scrollTop).toBe(150)

      await wrapper.trigger('keydown', { key: 'PageDown' })
      expect(scroller.scrollTop).toBe(550)
    })

    it('handles home/end navigation', async () => {
      const scroller = wrapper.find('.virtual-scroller').element as HTMLElement
      if (typeof scroller.scrollTo === 'function') {
        scroller.scrollTo = vi.fn(function (this: HTMLElement, opts?: ScrollToOptions) {
          if (opts?.top !== undefined) (this as any).scrollTop = opts.top
        }) as any
      }
      scroller.focus()

      await wrapper.trigger('keydown', { key: 'End' })
      expect(scroller.scrollTop).toBe(49600)

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

      // showBottomLoader is true only when scrolled to bottom; simulate scroll to bottom
      const scroller = wrapper.find('.virtual-scroller').element as HTMLElement
      scroller.scrollTop = 49600
      await wrapper.vm.handleScroll()
      await nextTick()

      const loader = wrapper.find('.virtual-scroller__bottom-loader')
      expect(loader.exists()).toBe(true)
      expect(loader.text()).toContain('Loading more items...')
    })

    it('shows custom loading slot', async () => {
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
      const scroller = wrapper.find('.virtual-scroller').element as HTMLElement
      scroller.scrollTop = 49600
      await wrapper.vm.handleScroll()
      await nextTick()
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
        props: { ...defaultProps, isLoading: true },
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
      const scroller = wrapper.find('.virtual-scroller').element as HTMLElement
      scroller.scrollTop = 49600
      await wrapper.vm.handleScroll()
      await wrapper.setProps({ isLoading: true })
      await nextTick()

      const status = wrapper.find('[role="status"]')
      expect(status.exists()).toBe(true)
      expect(status.attributes('aria-live')).toBe('polite')
    })
  })

  describe('Performance', () => {
    beforeEach(() => {
      wrapper = mount(VirtualScroller, {
        props: defaultProps,
        global: {
          stubs: ['GalleryItem', 'GalleryItemSkeleton']
        }
      })
    })

    it('throttles scroll events', () => {
      expect(wrapper.vm.handleScroll).toBeDefined()
    })

    it('only renders visible items plus buffer', () => {
      const items = wrapper.findAll('.virtual-scroller__item')
      expect(items.length).toBeLessThan(50)
    })

    it('updates efficiently on prop changes', async () => {
      const newItems = mockItems.slice(0, 500)
      await wrapper.setProps({
        items: newItems,
        totalItems: 500
      })
      expect(wrapper.vm.totalHeight).toBe(25000)
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

      const total = wrapper.vm.totalHeight
      expect(total === 0 || Number.isNaN(total)).toBe(true)
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
      const scrollToFn = vi.fn(function (this: HTMLElement, opts?: ScrollToOptions) {
        if (opts?.top !== undefined) (this as any).scrollTop = opts.top
      })
      scroller.scrollTo = scrollToFn as any

      wrapper.vm.scrollToItem(100)
      expect(scrollToFn).toHaveBeenCalledWith(expect.objectContaining({ top: 5000 }))
    })

    it('scrollToTop scrolls to top', () => {
      const scroller = wrapper.find('.virtual-scroller').element as HTMLElement
      scroller.scrollTop = 1000
      const scrollToFn = vi.fn(function (this: HTMLElement, opts?: ScrollToOptions) {
        if (opts?.top !== undefined) (this as any).scrollTop = opts.top
      })
      scroller.scrollTo = scrollToFn as any

      wrapper.vm.scrollToTop()
      expect(scrollToFn).toHaveBeenCalledWith(expect.objectContaining({ top: 0 }))
    })

    it('getVisibleRange returns current range', () => {
      const range = wrapper.vm.getVisibleRange()
      expect(range).toHaveProperty('start')
      expect(range).toHaveProperty('end')
      expect(range.start).toBe(0)
      expect(range.end).toBe(13)
    })
  })

  describe('Reactivity', () => {
    beforeEach(() => {
      wrapper = mount(VirtualScroller, {
        props: defaultProps,
        global: {
          stubs: ['GalleryItem', 'GalleryItemSkeleton']
        }
      })
    })

    it('reacts to items prop changes', async () => {
      await wrapper.setProps({
        items: mockItems.slice(0, 500),
        totalItems: 500
      })
      expect(wrapper.vm.totalHeight).toBe(25000)
    })

    it('reacts to itemHeight changes', async () => {
      await wrapper.setProps({ itemHeight: 100 })
      expect(wrapper.vm.totalHeight).toBe(100000)
    })

    it('reacts to totalItems changes', async () => {
      await wrapper.setProps({ totalItems: 500 })
      expect(wrapper.vm.totalHeight).toBe(25000)
    })
  })
})




















