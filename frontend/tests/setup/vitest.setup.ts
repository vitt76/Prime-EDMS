import '@testing-library/jest-dom/vitest'
import 'vitest-axe/extend-expect'
import * as axe from 'axe-core'
import { vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { defineComponent, h } from 'vue'
import { config, RouterLinkStub } from '@vue/test-utils'

// Make axe available globally for tests that use it
if (typeof window !== 'undefined') {
  ;(window as any).axe = axe
}

// Global Pinia for components that use stores (e.g. BulkTagModal, GalleryView)
beforeEach(() => {
  vi.clearAllMocks()
  setActivePinia(createPinia())
  document.body.innerHTML = '<div id="header-actions"></div><div id="header-search-actions"></div>'
})

config.global.stubs = {
  teleport: true,
  'router-link': RouterLinkStub,
  RouterLink: RouterLinkStub,
  RouterView: true
}

// Mock vue-router so useRouter() / useRoute() work in components
vi.mock('vue-router', async (importOriginal) => {
  const actual = await importOriginal() as object
  return {
    ...actual,
    RouterLink: defineComponent({
      name: 'RouterLink',
      props: {
        to: {
          type: [String, Object],
          required: false,
          default: '/'
        }
      },
      setup(props, { slots, attrs }) {
        return () => h('a', { ...attrs, href: typeof props.to === 'string' ? props.to : '#' }, slots.default?.())
      }
    }),
    RouterView: defineComponent({
      name: 'RouterView',
      setup(_, { slots }) {
        return () => slots.default?.()
      }
    }),
    useRouter: () => ({
      push: vi.fn(),
      replace: vi.fn(),
      go: vi.fn(),
      back: vi.fn(),
      forward: vi.fn(),
      currentRoute: {
        value: {
          name: 'root',
          path: '/',
          fullPath: '/',
          params: {},
          query: {},
          hash: '',
          meta: {},
          matched: []
        }
      }
    }),
    useRoute: () => ({
      name: 'root',
      path: '/',
      params: {},
      query: {},
      fullPath: '/',
      hash: '',
      meta: {},
      matched: []
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
  HTMLCanvasElement.prototype.toDataURL = vi.fn(() => 'data:image/png;base64,mock')
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

class MutationObserverMock {
  observe = vi.fn()
  disconnect = vi.fn()
  takeRecords = vi.fn(() => [])
  constructor(public _callback?: MutationCallback) {}
}
vi.stubGlobal('MutationObserver', MutationObserverMock)

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
  window.open = vi.fn()
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

if (typeof globalThis.requestAnimationFrame === 'undefined') {
  vi.stubGlobal('requestAnimationFrame', (callback: FrameRequestCallback) => {
    return window.setTimeout(() => callback(performance.now()), 0)
  })
}

if (typeof globalThis.cancelAnimationFrame === 'undefined') {
  vi.stubGlobal('cancelAnimationFrame', (handle: number) => {
    window.clearTimeout(handle)
  })
}

if (typeof globalThis.DOMRect === 'undefined') {
  vi.stubGlobal(
    'DOMRect',
    class DOMRectMock {
      x = 0
      y = 0
      width = 0
      height = 0
      top = 0
      right = 0
      bottom = 0
      left = 0

      constructor(x = 0, y = 0, width = 0, height = 0) {
        this.x = x
        this.y = y
        this.width = width
        this.height = height
        this.top = y
        this.left = x
        this.right = x + width
        this.bottom = y + height
      }

      toJSON() {
        return {
          x: this.x,
          y: this.y,
          width: this.width,
          height: this.height,
          top: this.top,
          right: this.right,
          bottom: this.bottom,
          left: this.left
        }
      }
    }
  )
}


