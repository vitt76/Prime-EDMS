import '@testing-library/jest-dom/vitest'
import 'vitest-axe/extend-expect'
import * as axe from 'axe-core'
import { vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'

// Make axe available globally for tests that use it
if (typeof window !== 'undefined') {
  ;(window as any).axe = axe
}

// Global Pinia for components that use stores (e.g. BulkTagModal, GalleryView)
beforeEach(() => {
  setActivePinia(createPinia())
})

// Mock vue-router so useRouter() / useRoute() work in components
vi.mock('vue-router', async (importOriginal) => {
  const actual = await importOriginal() as object
  return {
    ...actual,
    useRouter: () => ({
      push: vi.fn(),
      replace: vi.fn(),
      go: vi.fn(),
      back: vi.fn(),
      forward: vi.fn(),
      currentRoute: { value: { path: '/', params: {}, query: {} } }
    }),
    useRoute: () => ({
      path: '/',
      params: {},
      query: {},
      fullPath: '/'
    })
  }
})

// Canvas getContext for Chart.js and similar (jsdom has no real canvas)
if (typeof HTMLCanvasElement !== 'undefined') {
  const mockContext = {
    fillRect: vi.fn(),
    clearRect: vi.fn(),
    getImageData: vi.fn(),
    putImageData: vi.fn(),
    createImageData: vi.fn(),
    setTransform: vi.fn(),
    drawImage: vi.fn(),
    save: vi.fn(),
    restore: vi.fn(),
    beginPath: vi.fn(),
    moveTo: vi.fn(),
    lineTo: vi.fn(),
    closePath: vi.fn(),
    stroke: vi.fn(),
    fill: vi.fn(),
    measureText: vi.fn(() => ({ width: 0 })),
    transform: vi.fn(),
    translate: vi.fn(),
    scale: vi.fn(),
    rotate: vi.fn(),
    arc: vi.fn(),
    fillText: vi.fn(),
    strokeText: vi.fn(),
    createLinearGradient: vi.fn(),
    createPattern: vi.fn(),
    createRadialGradient: vi.fn(),
    clip: vi.fn(),
    isPointInPath: vi.fn(),
    isPointInStroke: vi.fn()
  }
  HTMLCanvasElement.prototype.getContext = vi.fn().mockReturnValue(mockContext)
}

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation((query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn()
  }))
})

// IntersectionObserver (jsdom does not provide it). Must be a constructor (not arrow fn).
class IntersectionObserverMock {
  observe = vi.fn()
  unobserve = vi.fn()
  disconnect = vi.fn()
  takeRecords = vi.fn(() => [])
  constructor(
    public _callback?: (entries: IntersectionObserverEntry[]) => void,
    public _options?: IntersectionObserverInit
  ) {}
}
vi.stubGlobal('IntersectionObserver', IntersectionObserverMock)

// ResizeObserver — constructor
class ResizeObserverMock {
  observe = vi.fn()
  unobserve = vi.fn()
  disconnect = vi.fn()
  constructor(public _callback?: (entries: unknown) => void) {}
}
vi.stubGlobal('ResizeObserver', ResizeObserverMock)

// DragEvent (jsdom does not provide it)
if (typeof globalThis.DragEvent === 'undefined') {
  ;(globalThis as any).DragEvent = class DragEvent extends Event {
    dataTransfer: unknown = null
    constructor(type: string, options?: { dataTransfer?: unknown }) {
      super(type, options as EventInit)
      this.dataTransfer = options?.dataTransfer ?? null
    }
  }
}

// scrollTo / scrollIntoView (Element.prototype.scrollTo for virtual scroller, etc.)
if (typeof window !== 'undefined') {
  window.scrollTo = vi.fn()
  Element.prototype.scrollIntoView = vi.fn()
  const scrollToImpl = function (this: Element, options?: ScrollToOptions) {
    const el = this as HTMLElement
    if (el && typeof (el as any).scrollTop !== 'undefined' && options?.top !== undefined) {
      (el as any).scrollTop = options.top
    }
  }
  if (typeof Element !== 'undefined' && !(Element.prototype as any).scrollTo) {
    ;(Element.prototype as any).scrollTo = scrollToImpl
  }
}

// URL.createObjectURL / revokeObjectURL (for blob thumbnails)
if (typeof globalThis.URL !== 'undefined') {
  globalThis.URL.createObjectURL = vi.fn(() => 'blob:mock-url')
  globalThis.URL.revokeObjectURL = vi.fn()
}


