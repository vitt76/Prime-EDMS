import { describe, it, expect, beforeEach, vi } from 'vitest'
import { ref, nextTick } from 'vue'
import { useIntersectionObserver } from '@/composables/useIntersectionObserver'

describe('useIntersectionObserver', () => {
  let mockObserver: {
    observe: ReturnType<typeof vi.fn>
    disconnect: ReturnType<typeof vi.fn>
    unobserve: ReturnType<typeof vi.fn>
  }
  let observerCallback: (entries: IntersectionObserverEntry[]) => void

  beforeEach(() => {
    mockObserver = {
      observe: vi.fn(),
      disconnect: vi.fn(),
      unobserve: vi.fn()
    }

    // Mock IntersectionObserver
    global.IntersectionObserver = vi.fn().mockImplementation((callback) => {
      observerCallback = callback
      return {
        observe: mockObserver.observe,
        disconnect: mockObserver.disconnect,
        unobserve: mockObserver.unobserve
      }
    }) as any
  })

  it('creates observer and observes target element', async () => {
    const target = ref<HTMLElement | null>(document.createElement('div'))
    const { hasIntersected, isIntersecting } = useIntersectionObserver(target)

    await nextTick()

    expect(global.IntersectionObserver).toHaveBeenCalled()
    expect(mockObserver.observe).toHaveBeenCalledWith(target.value)
    expect(hasIntersected.value).toBe(false)
    expect(isIntersecting.value).toBe(false)
  })

  it('does not create observer if target is null', async () => {
    const target = ref<HTMLElement | null>(null)
    const { hasIntersected } = useIntersectionObserver(target)

    await nextTick()

    expect(mockObserver.observe).not.toHaveBeenCalled()
    expect(hasIntersected.value).toBe(false)
  })

  it('sets hasIntersected to true when element intersects', async () => {
    const target = ref<HTMLElement | null>(document.createElement('div'))
    const { hasIntersected, isIntersecting } = useIntersectionObserver(target)

    await nextTick()

    // Simulate intersection
    const mockEntry = {
      isIntersecting: true,
      target: target.value!,
      boundingClientRect: {} as DOMRectReadOnly,
      intersectionRatio: 1,
      intersectionRect: {} as DOMRectReadOnly,
      rootBounds: null,
      time: 0
    } as IntersectionObserverEntry

    observerCallback([mockEntry])

    expect(hasIntersected.value).toBe(true)
    expect(isIntersecting.value).toBe(true)
  })

  it('updates isIntersecting when element leaves viewport', async () => {
    const target = ref<HTMLElement | null>(document.createElement('div'))
    const { isIntersecting } = useIntersectionObserver(target)

    await nextTick()

    // Simulate intersection
    observerCallback([
      {
        isIntersecting: true,
        target: target.value!,
        boundingClientRect: {} as DOMRectReadOnly,
        intersectionRatio: 1,
        intersectionRect: {} as DOMRectReadOnly,
        rootBounds: null,
        time: 0
      } as IntersectionObserverEntry
    ])

    expect(isIntersecting.value).toBe(true)

    // Simulate leaving viewport
    observerCallback([
      {
        isIntersecting: false,
        target: target.value!,
        boundingClientRect: {} as DOMRectReadOnly,
        intersectionRatio: 0,
        intersectionRect: {} as DOMRectReadOnly,
        rootBounds: null,
        time: 0
      } as IntersectionObserverEntry
    ])

    expect(isIntersecting.value).toBe(false)
  })

  it('accepts custom options', async () => {
    const target = ref<HTMLElement | null>(document.createElement('div'))
    const options = {
      rootMargin: '100px',
      threshold: 0.5
    }

    useIntersectionObserver(target, options)

    await nextTick()

    expect(global.IntersectionObserver).toHaveBeenCalledWith(
      expect.any(Function),
      expect.objectContaining({
        rootMargin: '100px',
        threshold: 0.5
      })
    )
  })
})
