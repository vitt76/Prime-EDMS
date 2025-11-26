/**
 * ErrorBoundary Component Tests
 *
 * Tests error catching, retry logic, development vs production modes,
 * accessibility, and user interactions.
 */

import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { mount, VueWrapper } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import ErrorBoundary from '../ErrorBoundary.vue'

// Mock composables
vi.mock('@/composables/useErrorBoundary', () => ({
  logError: vi.fn(),
  shouldRetry: vi.fn(() => true)
}))

// Mock clipboard API
Object.assign(navigator, {
  clipboard: {
    writeText: vi.fn().mockResolvedValue(undefined)
  }
})

// Mock window methods
Object.assign(window, {
  location: {
    reload: vi.fn()
  }
})

describe('ErrorBoundary', () => {
  let wrapper: VueWrapper<any>
  let mockLogError: any
  let mockShouldRetry: any

  beforeEach(() => {
    setActivePinia(createPinia())

    // Reset mocks
    mockLogError = vi.fn()
    mockShouldRetry = vi.fn(() => true)

    // Mount component
    wrapper = mount(ErrorBoundary, {
      global: {
        plugins: [createRouter({ history: createWebHistory(), routes: [] })],
        stubs: ['Card', 'Button']
      },
      props: {
        maxRetries: 3,
        autoRetryDelay: 5
      }
    })
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  describe('Normal Operation', () => {
    it('renders slot content when no error', () => {
      expect(wrapper.text()).toContain('test content')
      expect(wrapper.find('.error-boundary').exists()).toBe(false)
    })

    it('passes through slot props correctly', () => {
      const slotContent = wrapper.find('slot')
      expect(slotContent.exists()).toBe(true)
    })
  })

  describe('Error Catching', () => {
    it('catches component errors and shows error UI', async () => {
      const error = new Error('Test component error')

      // Trigger error
      await wrapper.vm.errorCaptured(error, { $: { type: { name: 'TestComponent' } } }, 'render')

      await wrapper.vm.$nextTick()

      expect(wrapper.vm.hasError).toBe(true)
      expect(wrapper.find('.error-boundary').exists()).toBe(true)
      expect(mockLogError).toHaveBeenCalledWith(error, expect.any(Object))
    })

    it('shows generic error message in production', async () => {
      // Mock production environment
      vi.mocked(import.meta.env).DEV = false

      const error = new Error('Detailed technical error')

      await wrapper.vm.errorCaptured(error, {}, '')

      await wrapper.vm.$nextTick()

      expect(wrapper.text()).toContain('Something went wrong')
      expect(wrapper.text()).not.toContain('Detailed technical error')
    })

    it('shows detailed error in development', async () => {
      // Mock development environment
      vi.mocked(import.meta.env).DEV = true

      const error = new Error('Detailed technical error')

      await wrapper.vm.errorCaptured(error, {}, '')

      await wrapper.vm.$nextTick()

      expect(wrapper.text()).toContain('Detailed technical error')
    })

    it('emits error event with correct data', async () => {
      const error = new Error('Test error')
      const instance = { component: 'Test' }
      const info = 'render error'

      await wrapper.vm.errorCaptured(error, instance, info)

      expect(wrapper.emitted('error')).toBeTruthy()
      expect(wrapper.emitted('error')![0]).toEqual([error, instance, info])
    })
  })

  describe('Retry Logic', () => {
    beforeEach(async () => {
      const error = new Error('Retryable error')
      await wrapper.vm.errorCaptured(error, {}, '')
      await wrapper.vm.$nextTick()
    })

    it('shows retry button', () => {
      const retryButton = wrapper.find('button')
      expect(retryButton.text()).toContain('Try Again')
    })

    it('increments retry count on retry', async () => {
      const retryButton = wrapper.find('button')

      await retryButton.trigger('click')

      expect(wrapper.vm.retryCount).toBe(1)
      expect(wrapper.emitted('retry')).toBeTruthy()
      expect(wrapper.emitted('retry')![0]).toEqual([1])
    })

    it('disables retry after max attempts', async () => {
      // Exhaust retries
      wrapper.vm.retryCount = 3
      await wrapper.vm.$nextTick()

      const retryButton = wrapper.find('button')
      expect(retryButton.attributes('disabled')).toBeDefined()
      expect(retryButton.text()).toContain('Max Retries Reached')
    })

    it('shows retry progress', async () => {
      wrapper.vm.retrying = true
      wrapper.vm.retryCount = 2
      await wrapper.vm.$nextTick()

      expect(wrapper.text()).toContain('Retrying...')
      expect(wrapper.text()).toContain('(2/3)')
    })

    it('reloads page when no custom retry handler', async () => {
      const retryButton = wrapper.find('button')

      await retryButton.trigger('click')

      expect(window.location.reload).toHaveBeenCalled()
    })

    it('calls custom retry handler when provided', async () => {
      const customRetry = vi.fn().mockResolvedValue(undefined)

      await wrapper.setProps({ onRetry: customRetry })

      const retryButton = wrapper.find('button')
      await retryButton.trigger('click')

      expect(customRetry).toHaveBeenCalled()
      expect(window.location.reload).not.toHaveBeenCalled()
    })
  })

  describe('Auto Retry', () => {
    beforeEach(async () => {
      vi.useFakeTimers()

      const error = new Error('Network error')
      mockShouldRetry.mockReturnValue(true)

      await wrapper.vm.errorCaptured(error, {}, '')
      await wrapper.vm.$nextTick()
    })

    afterEach(() => {
      vi.useRealTimers()
    })

    it('starts auto-retry countdown for retryable errors', () => {
      expect(wrapper.vm.autoRetryCountdown).toBe(5)
    })

    it('shows auto-retry countdown', () => {
      expect(wrapper.text()).toContain('Auto-retrying in 5s...')
    })

    it('counts down automatically', async () => {
      vi.advanceTimersByTime(2000)
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.autoRetryCountdown).toBe(3)
      expect(wrapper.text()).toContain('Auto-retrying in 3s...')
    })

    it('auto-retries when countdown reaches zero', async () => {
      vi.advanceTimersByTime(5000)
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.retryCount).toBe(1)
    })

    it('cancels auto-retry on manual retry', async () => {
      const retryButton = wrapper.find('button')
      await retryButton.trigger('click')

      expect(wrapper.vm.autoRetryCountdown).toBe(0)
    })
  })

  describe('Error Details (Development)', () => {
    beforeEach(async () => {
      vi.mocked(import.meta.env).DEV = true

      const error = new Error('Test error with stack')
      error.stack = 'Error stack trace'

      await wrapper.vm.errorCaptured(error, { $: { type: { name: 'TestComponent' } } }, 'render')
      await wrapper.vm.$nextTick()
    })

    it('shows error details section', () => {
      const details = wrapper.find('details')
      expect(details.exists()).toBe(true)
      expect(details.text()).toContain('Error Details (Development)')
    })

    it('includes error stack and context', () => {
      const details = wrapper.find('details pre')
      expect(details.text()).toContain('Test error with stack')
      expect(details.text()).toContain('TestComponent')
      expect(details.text()).toContain('render')
    })

    it('shows report error button', () => {
      const reportButton = wrapper.findAll('button').find(btn =>
        btn.text().includes('Report Issue')
      )
      expect(reportButton).toBeDefined()
    })

    it('copies error details to clipboard on report', async () => {
      const reportButton = wrapper.findAll('button').find(btn =>
        btn.text().includes('Report Issue')
      )

      await reportButton!.trigger('click')

      expect(navigator.clipboard.writeText).toHaveBeenCalled()
    })
  })

  describe('Recovery', () => {
    it('emits recovered event when error is reset', async () => {
      // First trigger error
      await wrapper.vm.errorCaptured(new Error('Test'), {}, '')
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.hasError).toBe(true)

      // Reset error
      wrapper.vm.resetError()
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.hasError).toBe(false)
      expect(wrapper.emitted('recovered')).toBeTruthy()
    })

    it('reloads page on reload button click', async () => {
      // Trigger error first
      await wrapper.vm.errorCaptured(new Error('Test'), {}, '')
      await wrapper.vm.$nextTick()

      const reloadButton = wrapper.findAll('button').find(btn =>
        btn.text().includes('Reload Page')
      )

      await reloadButton!.trigger('click')

      expect(window.location.reload).toHaveBeenCalled()
    })
  })

  describe('Accessibility', () => {
    it('has proper ARIA attributes', async () => {
      await wrapper.vm.errorCaptured(new Error('Test'), {}, '')
      await wrapper.vm.$nextTick()

      const errorBoundary = wrapper.find('.error-boundary')
      expect(errorBoundary.attributes('role')).toBe('alert')
      expect(errorBoundary.attributes('aria-live')).toBe('assertive')
      expect(errorBoundary.attributes('tabindex')).toBe('-1')
    })

    it('focuses error container when error occurs', async () => {
      const focusSpy = vi.fn()
      wrapper.vm.$refs.errorContainer = { focus: focusSpy }

      await wrapper.vm.errorCaptured(new Error('Test'), {}, '')

      expect(focusSpy).toHaveBeenCalled()
    })

    it('has keyboard accessible buttons', async () => {
      await wrapper.vm.errorCaptured(new Error('Test'), {}, '')
      await wrapper.vm.$nextTick()

      const buttons = wrapper.findAll('button')
      buttons.forEach(button => {
        expect(button.attributes('type')).toBeDefined()
      })
    })
  })

  describe('Customization', () => {
    it('accepts custom error title and message', async () => {
      await wrapper.setProps({
        title: 'Custom Error Title',
        message: 'Custom error message'
      })

      await wrapper.vm.errorCaptured(new Error('Test'), {}, '')
      await wrapper.vm.$nextTick()

      expect(wrapper.text()).toContain('Custom Error Title')
      expect(wrapper.text()).toContain('Custom error message')
    })

    it('calls custom error handler', async () => {
      const customHandler = vi.fn()

      await wrapper.setProps({
        onError: customHandler
      })

      const error = new Error('Test')
      await wrapper.vm.errorCaptured(error, {}, 'test')

      expect(customHandler).toHaveBeenCalledWith(error, {}, 'test')
    })

    it('respects max retries setting', async () => {
      await wrapper.setProps({ maxRetries: 5 })

      // Trigger error
      await wrapper.vm.errorCaptured(new Error('Test'), {}, '')
      await wrapper.vm.$nextTick()

      // Should allow up to 5 retries
      for (let i = 1; i <= 5; i++) {
        expect(wrapper.vm.retryCount).toBeLessThanOrEqual(5)
        if (i < 5) {
          await wrapper.find('button').trigger('click')
        }
      }
    })
  })

  describe('Lifecycle', () => {
    it('cleans up auto-retry timer on unmount', () => {
      const clearIntervalSpy = vi.spyOn(window, 'clearInterval')

      wrapper.vm.autoRetryTimer = 123
      wrapper.unmount()

      expect(clearIntervalSpy).toHaveBeenCalledWith(123)
    })

    it('exposes error state via ref', async () => {
      await wrapper.vm.errorCaptured(new Error('Test'), {}, '')

      expect(wrapper.vm.hasError).toBe(true)
      expect(wrapper.vm.error).toBeInstanceOf(Error)
      expect(wrapper.vm.retryCount).toBe(0)
    })
  })
})
