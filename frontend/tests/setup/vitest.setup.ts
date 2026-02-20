import '@testing-library/jest-dom/vitest'
import 'vitest-axe/extend-expect'
import * as axe from 'axe-core'
import { vi } from 'vitest'

// Make axe available globally for tests that use it
if (typeof window !== 'undefined') {
  ;(window as any).axe = axe
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

// scrollTo / scrollIntoView
if (typeof window !== 'undefined') {
  window.scrollTo = vi.fn()
  Element.prototype.scrollIntoView = vi.fn()
}

// URL.createObjectURL / revokeObjectURL (for blob thumbnails)
if (typeof globalThis.URL !== 'undefined') {
  globalThis.URL.createObjectURL = vi.fn(() => 'blob:mock-url')
  globalThis.URL.revokeObjectURL = vi.fn()
}


