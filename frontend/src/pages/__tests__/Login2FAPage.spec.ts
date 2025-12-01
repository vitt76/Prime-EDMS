/**
 * Login2FAPage Component Tests
 *
 * Tests 2FA setup and verification flows including:
 * - TOTP QR code setup
 * - Backup codes generation
 * - Code verification
 * - Error handling
 * - Accessibility
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import Login2FAPage from '../Login2FAPage.vue'
import { useAuthStore } from '@/stores/authStore'

// Mock dependencies
vi.mock('@/stores/authStore')
vi.mock('vue-router')

describe('Login2FAPage', () => {
  let wrapper: any
  let authStore: any
  let router: any

  beforeEach(() => {
    // Setup Pinia
    setActivePinia(createPinia())

    // Setup router mock
    router = {
      push: vi.fn(),
      currentRoute: {
        value: {
          query: {}
        }
      }
    }

    // Setup auth store mock
    authStore = {
      twoFactorSetup: {
        secret: 'JBSWY3DPEHPK3PXP',
        qr_code_url: 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...',
        backup_codes: ['12345678', '87654321', '11111111', '22222222']
      },
      twoFactorStatus: { enabled: false },
      twoFactorPending: false,
      checkTwoFactorStatus: vi.fn(),
      enableTwoFactor: vi.fn(),
      verifyTwoFactor: vi.fn(),
      regenerateBackupCodes: vi.fn()
    }

    // Mock the composables
    vi.mocked(useAuthStore).mockReturnValue(authStore)
  })

  describe('Setup Mode', () => {
    beforeEach(async () => {
      authStore.twoFactorStatus = { enabled: false }
      authStore.twoFactorPending = false

      wrapper = mount(Login2FAPage, {
        global: {
          plugins: [createRouter({ history: createWebHistory(), routes: [] })],
          stubs: ['Card', 'Input', 'Button', 'Spinner', 'Alert']
        }
      })

      await wrapper.vm.$nextTick()
    })

    it('shows QR code and setup instructions', () => {
      expect(wrapper.text()).toContain('Set up your authenticator app')
      expect(wrapper.find('img')).toBeTruthy()
    })

    it('displays manual secret code', () => {
      const secretElement = wrapper.find('code')
      expect(secretElement.text()).toContain('JBSWY3DPEHPK3PXP')
    })

    it('shows backup codes', () => {
      const codes = wrapper.findAll('code')
      expect(codes.length).toBeGreaterThan(1)
      expect(wrapper.text()).toContain('12345678')
    })

    it('completes setup when QR code scanned', async () => {
      const completeButton = wrapper.find('button')
      await completeButton.trigger('click')

      expect(wrapper.vm.isSetupMode).toBe(false)
      expect(wrapper.text()).toContain('Enter your authentication code')
    })

    it('regenerates backup codes', async () => {
      authStore.regenerateBackupCodes.mockResolvedValue({
        backup_codes: ['newcode1', 'newcode2']
      })

      const regenerateButton = wrapper.findAll('button').find((btn: any) =>
        btn.text().includes('Regenerate')
      )
      await regenerateButton.trigger('click')

      expect(authStore.regenerateBackupCodes).toHaveBeenCalled()
    })
  })

  describe('Verification Mode', () => {
    beforeEach(async () => {
      authStore.twoFactorStatus = { enabled: true }
      authStore.twoFactorPending = true

      wrapper = mount(Login2FAPage, {
        global: {
          plugins: [createRouter({ history: createWebHistory(), routes: [] })],
          stubs: ['Card', 'Input', 'Button', 'Spinner', 'Alert']
        }
      })

      await wrapper.vm.$nextTick()
    })

    it('shows verification form', () => {
      expect(wrapper.text()).toContain('Enter your authentication code')
      expect(wrapper.find('input')).toBeTruthy()
    })

    it('validates 6-digit code requirement', async () => {
      const form = wrapper.find('form')
      await form.trigger('submit')

      expect(wrapper.vm.codeError).toBe('Please enter a valid 6-digit code')
    })

    it('verifies valid TOTP code', async () => {
      authStore.verifyTwoFactor.mockResolvedValue({
        success: true,
        user: { id: 1, email: 'test@example.com' }
      })

      const input = wrapper.find('input')
      await input.setValue('123456')

      const form = wrapper.find('form')
      await form.trigger('submit')

      expect(authStore.verifyTwoFactor).toHaveBeenCalledWith('123456', 'totp')
      expect(router.push).toHaveBeenCalled()
    })

    it('handles invalid code', async () => {
      authStore.verifyTwoFactor.mockRejectedValue({
        response: { status: 401 }
      })

      const input = wrapper.find('input')
      await input.setValue('123456')

      const form = wrapper.find('form')
      await form.trigger('submit')

      expect(wrapper.vm.codeError).toContain('Invalid code')
    })

    it('handles rate limiting', async () => {
      authStore.verifyTwoFactor.mockRejectedValue({
        response: { status: 429 }
      })

      const input = wrapper.find('input')
      await input.setValue('123456')

      const form = wrapper.find('form')
      await form.trigger('submit')

      expect(wrapper.vm.error).toContain('Too many attempts')
    })

    it('switches to backup code mode', async () => {
      const backupLink = wrapper.find('button')
      await backupLink.trigger('click')

      expect(wrapper.vm.useBackupCode).toBe(true)
    })

    it('verifies backup code', async () => {
      wrapper.vm.useBackupCode = true
      authStore.verifyTwoFactor.mockResolvedValue({
        success: true,
        user: { id: 1, email: 'test@example.com' }
      })

      const input = wrapper.find('input')
      await input.setValue('12345678')

      const form = wrapper.find('form')
      await form.trigger('submit')

      expect(authStore.verifyTwoFactor).toHaveBeenCalledWith('12345678', 'backup_code')
    })
  })

  describe('Error Handling', () => {
    it('shows initialization error', async () => {
      authStore.checkTwoFactorStatus.mockRejectedValue(new Error('API Error'))

      wrapper = mount(Login2FAPage, {
        global: {
          plugins: [createRouter({ history: createWebHistory(), routes: [] })],
          stubs: ['Card', 'Input', 'Button', 'Spinner', 'Alert']
        }
      })

      await wrapper.vm.$nextTick()

      expect(wrapper.vm.error).toContain('Failed to initialize')
    })

    it('handles network errors during verification', async () => {
      authStore.twoFactorStatus = { enabled: true }
      authStore.twoFactorPending = true
      authStore.verifyTwoFactor.mockRejectedValue(new Error('Network error'))

      wrapper = mount(Login2FAPage, {
        global: {
          plugins: [createRouter({ history: createWebHistory(), routes: [] })],
          stubs: ['Card', 'Input', 'Button', 'Spinner', 'Alert']
        }
      })

      const input = wrapper.find('input')
      await input.setValue('123456')

      const form = wrapper.find('form')
      await form.trigger('submit')

      expect(wrapper.vm.error).toContain('Verification failed')
    })
  })

  describe('Accessibility', () => {
    it('has proper ARIA labels', () => {
      const inputs = wrapper.findAll('input')
      inputs.forEach((input: any) => {
        expect(input.attributes('aria-label')).toBeTruthy()
      })
    })

    it('supports keyboard navigation', () => {
      const buttons = wrapper.findAll('button')
      expect(buttons.length).toBeGreaterThan(0)

      buttons.forEach((button: any) => {
        expect(button.attributes('tabindex')).not.toBe('-1')
      })
    })

    it('has descriptive alt text for QR code', () => {
      const qrImage = wrapper.find('img')
      expect(qrImage.attributes('alt')).toContain('QR Code')
    })
  })

  describe('Security', () => {
    it('clears sensitive data on unmount', async () => {
      wrapper.unmount()
      // Verify no sensitive data remains in component
      expect(wrapper.vm.secret).toBe('')
    })

    it('masks verification code input appropriately', () => {
      const input = wrapper.find('input[type="text"]')
      expect(input.attributes('inputmode')).toBe('numeric')
      expect(input.attributes('pattern')).toBe('[0-9]*')
    })
  })
})
