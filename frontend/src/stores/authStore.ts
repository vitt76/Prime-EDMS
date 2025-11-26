import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authService } from '@/services/authService'
import type { User, TwoFactorStatus, TwoFactorSetup } from '@/types'

export const useAuthStore = defineStore(
  'auth',
  () => {
    // State
    const user = ref<User | null>(null)
    const token = ref<string | null>(null)
    const isAuthenticated = ref(false)
    const permissions = ref<string[]>([])
    const lastActivity = ref<Date | null>(null)

    // 2FA State
    const twoFactorStatus = ref<TwoFactorStatus | null>(null)
    const twoFactorPending = ref(false)
    const twoFactorSetup = ref<TwoFactorSetup | null>(null)

    // Getters
    const hasPermission = computed(() => {
      return (permission: string) => {
        return permissions.value.includes(permission) || user.value?.permissions?.includes(permission) || false
      }
    })

    const hasRole = computed(() => {
      return (role: string) => {
        return user.value?.role === role
      }
    })

    const requiresTwoFactor = computed(() => {
      return twoFactorStatus.value?.enabled === true
    })

    const isTwoFactorVerified = computed(() => {
      return !twoFactorPending.value && isAuthenticated.value
    })

    // Actions
    async function login(email: string, password: string) {
      try {
        const response = await authService.login(email, password)
        token.value = response.token
        user.value = response.user
        isAuthenticated.value = true
        permissions.value = response.permissions || []
        lastActivity.value = new Date()

        // Store token in localStorage
        if (token.value) {
          localStorage.setItem('auth_token', token.value)
        }

        // Check 2FA status and set pending if enabled
        try {
          const twoFactorStatusResponse = await authService.getTwoFactorStatus()
          twoFactorStatus.value = twoFactorStatusResponse
          if (twoFactorStatusResponse.enabled) {
            twoFactorPending.value = true
          }
        } catch (error) {
          console.warn('Failed to check 2FA status during login:', error)
          // Don't fail login if 2FA check fails
        }

        return { success: true }
      } catch (error) {
        isAuthenticated.value = false
        throw error
      }
    }

    async function logout() {
      try {
        await authService.logout()
      } catch (error) {
        // Continue with logout even if API call fails
        console.error('Logout error:', error)
      } finally {
        token.value = null
        user.value = null
        isAuthenticated.value = false
        permissions.value = []
        lastActivity.value = null
        // Reset 2FA state
        twoFactorStatus.value = null
        twoFactorPending.value = false
        twoFactorSetup.value = null
        localStorage.removeItem('auth_token')
      }
    }

    async function refreshToken() {
      try {
        const response = await authService.refreshToken()
        token.value = response.token
        if (token.value) {
          localStorage.setItem('auth_token', token.value)
        }
        return { success: true }
      } catch (error) {
        // Token refresh failed, logout user
        await logout()
        throw error
      }
    }

    async function checkAuth() {
      const storedToken = localStorage.getItem('auth_token')
      if (!storedToken) {
        isAuthenticated.value = false
        return false
      }

      try {
        const response = await authService.getCurrentUser()
        token.value = storedToken
        user.value = response.user
        isAuthenticated.value = true
        permissions.value = response.permissions || []
        lastActivity.value = new Date()

        // Check 2FA status
        try {
          const twoFactorStatusResponse = await authService.getTwoFactorStatus()
          twoFactorStatus.value = twoFactorStatusResponse
          if (twoFactorStatusResponse.enabled) {
            twoFactorPending.value = true
          }
        } catch (error) {
          console.warn('Failed to check 2FA status during auth check:', error)
          // Don't fail auth check if 2FA check fails
        }

        return true
      } catch (error) {
        // Token invalid, clear auth
        await logout()
        return false
      }
    }

    function updateActivity() {
      lastActivity.value = new Date()
    }

    // 2FA Actions
    async function checkTwoFactorStatus() {
      try {
        const status = await authService.getTwoFactorStatus()
        twoFactorStatus.value = status
        return status
      } catch (error) {
        console.error('Failed to check 2FA status:', error)
        twoFactorStatus.value = null
        throw error
      }
    }

    async function enableTwoFactor() {
      try {
        const setup = await authService.enableTwoFactor()
        twoFactorSetup.value = setup
        return setup
      } catch (error) {
        console.error('Failed to enable 2FA:', error)
        throw error
      }
    }

    async function verifyTwoFactor(token: string, method: 'totp' | 'backup_code' = 'totp') {
      try {
        const response = await authService.verifyTwoFactor(token, method)
        if (response.success && response.user) {
          user.value = response.user
          twoFactorPending.value = false
          twoFactorStatus.value = { enabled: true, method }
        }
        return response
      } catch (error) {
        console.error('Failed to verify 2FA:', error)
        throw error
      }
    }

    async function disableTwoFactor() {
      try {
        const response = await authService.disableTwoFactor()
        if (response.success) {
          twoFactorStatus.value = { enabled: false }
          twoFactorSetup.value = null
        }
        return response
      } catch (error) {
        console.error('Failed to disable 2FA:', error)
        throw error
      }
    }

    async function regenerateBackupCodes() {
      try {
        const response = await authService.regenerateBackupCodes()
        if (twoFactorSetup.value) {
          twoFactorSetup.value.backup_codes = response.backup_codes
        }
        return response
      } catch (error) {
        console.error('Failed to regenerate backup codes:', error)
        throw error
      }
    }

    function setTwoFactorPending(pending: boolean) {
      twoFactorPending.value = pending
    }

    function clearTwoFactorSetup() {
      twoFactorSetup.value = null
    }

    return {
      // State
      user,
      token,
      isAuthenticated,
      permissions,
      lastActivity,
      twoFactorStatus,
      twoFactorPending,
      twoFactorSetup,
      // Getters
      hasPermission,
      hasRole,
      requiresTwoFactor,
      isTwoFactorVerified,
      // Actions
      login,
      logout,
      refreshToken,
      checkAuth,
      updateActivity,
      // 2FA Actions
      checkTwoFactorStatus,
      enableTwoFactor,
      verifyTwoFactor,
      disableTwoFactor,
      regenerateBackupCodes,
      setTwoFactorPending,
      clearTwoFactorSetup
    }
  },
  {
    persist: {
      paths: ['user', 'isAuthenticated', 'permissions', 'twoFactorStatus'] // Don't persist token or temp 2FA data
    }
  }
)

