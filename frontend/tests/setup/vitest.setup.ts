import { expect, afterEach, beforeEach } from 'vitest'
import { cleanup } from '@testing-library/vue'
import '@testing-library/jest-dom/vitest'
import { toHaveNoViolations } from 'vitest-axe'
import * as axe from 'axe-core'

// Extend Vitest matchers with axe
expect.extend(toHaveNoViolations)

// Make axe available globally for tests
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


