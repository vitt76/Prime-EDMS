import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authService, hasToken, clearToken } from '@/services/authService'
import { formatApiError } from '@/utils/errors'
import type { User } from '@/types'

export const useAuthStore = defineStore(
  'auth',
  () => {
    // State
    const user = ref<User | null>(null)
    const token = ref<string | null>(localStorage.getItem('auth_token'))
    const permissions = ref<string[]>([])
    const isLoading = ref(false)
    const error = ref<string | null>(null)
    const lastActivity = ref<Date | null>(null)
    const twoFactorStatus = ref<any | null>(null)
    const twoFactorPending = ref(false)
    const twoFactorSetup = ref<any | null>(null)


    // Computed
    const isAuthenticated = computed(() => !!token.value && !!user.value)

    // Computed helpers
    const hasPermission = (permission: string) => permissions.value.includes(permission)
    const hasRole = (role: string) => {
      const userRole = (user.value as any)?.role || (user.value as any)?.groups?.[0]
      return userRole === role
    }
    const requiresTwoFactor = computed(() => {
      const status = twoFactorStatus.value
      return !!status?.enabled
    })
    const isTwoFactorVerified = computed(() => {
      const status = twoFactorStatus.value
      if (!status?.enabled) return true
      return !!status?.verified
    })

    // Actions
    async function login(username: string, password: string) {
      isLoading.value = true
      error.value = null

      try {
        // Step 1: Get token
        const tokenResponse = await authService.obtainToken(username, password)
        token.value = tokenResponse.token
        localStorage.setItem('auth_token', tokenResponse.token)

        // Step 2: Get user info
        const userResponse = await authService.getCurrentUser()
        user.value = userResponse
        permissions.value = userResponse.permissions || []

        return { success: true }
      } catch (err) {
        error.value = formatApiError(err)
        return { success: false, error: error.value }
      } finally {
        isLoading.value = false
      }
    }

    async function logout() {
      try {
        await authService.logout()
      } finally {
        // Always clear local state
        token.value = null
        user.value = null
        permissions.value = []
        localStorage.removeItem('auth_token')
      }
    }

    async function refreshToken() {
      // For session authentication, token refresh is not needed
      // Sessions are managed by Django automatically
      return { success: true }
    }

    /**
     * Initialize auth state on app startup.
     * Checks localStorage for token and restores session if valid.
     * This is the primary entry point for auth initialization.
     */
    async function initialize(): Promise<boolean> {
      console.log('[AuthStore] Initializing auth state...')
      
      // Check if we have a real auth token in localStorage
      const hasRealToken = hasToken()
      // Check mock auth flag (for dev mode without backend)
      const hasMockAuth = localStorage.getItem('dev_authenticated') === 'true'
      
      // If we have persisted auth state but no real token and no mock flag, clear it
      if (isAuthenticated.value && !hasRealToken && !hasMockAuth) {
        console.warn('[AuthStore] Persisted auth but no token/mock flag, clearing state')
        user.value = null
        permissions.value = []
        lastActivity.value = null
        return false
      }
      
      // No token found - user is not authenticated
      if (!hasRealToken && !hasMockAuth) {
        console.log('[AuthStore] No token found, user not authenticated')
        user.value = null
        permissions.value = []
        lastActivity.value = null
        return false
      }

      // Token found - validate it by fetching current user
      try {
        console.log('[AuthStore] Token found, validating...')
        const response = await authService.getCurrentUser()
        user.value = response.user
        permissions.value = response.permissions || []
        lastActivity.value = new Date()
        
        console.log('[AuthStore] ✅ Session restored for:', response.user.username)
        return true
      } catch (error) {
        console.warn('[AuthStore] ❌ Token validation failed:', error)
        // Clear auth state on failure
        user.value = null
        permissions.value = []
        lastActivity.value = null
        clearToken()
        localStorage.removeItem('dev_authenticated')
        return false
      }
    }

    /**
     * @deprecated Use initialize() instead
     */
    async function checkAuth(): Promise<boolean> {
      return initialize()
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
      user,
      token,
      permissions,
      isLoading,
      error,
      isAuthenticated,
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
      initialize,  // Primary auth initialization method
      checkAuth,   // @deprecated - use initialize()
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
      paths: ['token']  // Only persist token, not user data
    }
  }
)

