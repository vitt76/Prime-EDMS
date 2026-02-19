import '@testing-library/jest-dom/vitest'
import 'vitest-axe/extend-expect'
import * as axe from 'axe-core'

// Make axe available globally for tests that use it
if (typeof window !== 'undefined') {
  ;(window as any).axe = axe
}

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: (query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: () => {},
    removeListener: () => {},
    addEventListener: () => {},
    removeEventListener: () => {},
    dispatchEvent: () => {}
  })
})


