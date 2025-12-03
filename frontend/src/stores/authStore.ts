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


    // Computed
    const isAuthenticated = computed(() => !!token.value && !!user.value)

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

    async function checkAuth() {
      if (!token.value) return false

      try {
        const userResponse = await authService.getCurrentUser()
        user.value = userResponse
        permissions.value = userResponse.permissions || []
        return true
      } catch {
        await logout()
        return false
      }
    }

    return {
      user, token, permissions, isLoading, error,
      isAuthenticated,
      login, logout, checkAuth
    }
  },
  {
    persist: {
      paths: ['token']  // Only persist token, not user data
    }
  }
)

