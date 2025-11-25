import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authService } from '@/services/authService'
import type { User } from '@/types'

export const useAuthStore = defineStore(
  'auth',
  () => {
    // State
    const user = ref<User | null>(null)
    const token = ref<string | null>(null)
    const isAuthenticated = ref(false)
    const permissions = ref<string[]>([])
    const lastActivity = ref<Date | null>(null)

    // Getters
    const hasPermission = computed(() => {
      return (permission: string) => {
        return permissions.value.includes(permission) || user.value?.permissions?.includes(permission) || false
      }
    })

    const hasRole = computed(() => {
      return (role: string) => {
        // TODO: Implement role checking when roles are added to User type
        return false
      }
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

    return {
      // State
      user,
      token,
      isAuthenticated,
      permissions,
      lastActivity,
      // Getters
      hasPermission,
      hasRole,
      // Actions
      login,
      logout,
      refreshToken,
      checkAuth,
      updateActivity
    }
  },
  {
    persist: {
      paths: ['user', 'isAuthenticated', 'permissions'] // Don't persist token
    }
  }
)

