/**
 * Authentication Service
 * ======================
 * 
 * Phase A1.2: Auth Logic Implementation
 * 
 * Handles authentication with Mayan EDMS backend.
 * Supports Token-based authentication (DRF Token).
 * 
 * API Endpoints (verified against backend):
 * - POST /api/v4/auth/token/obtain/ - Get auth token
 * - GET /api/v4/users/current/ - Get current user info
 */

import axios from 'axios'
import type { User, TwoFactorStatus, TwoFactorSetup } from '@/types'

// ============================================================================
// CONFIGURATION
// ============================================================================

/**
 * Use real API authentication.
 * Default: true (always try real API first)
 * Set VITE_USE_MOCK_AUTH=true in .env to force mock mode
 */
const USE_REAL_API = import.meta.env.VITE_USE_MOCK_AUTH !== 'true'

/**
 * LocalStorage keys
 */
const TOKEN_KEY = 'auth_token'
const USER_KEY = 'auth_user'

// ============================================================================
// TYPES
// ============================================================================

interface LoginResponse {
  user: User
  permissions?: string[]
}

interface TokenObtainResponse {
  token: string
}

interface MayanUserResponse {
  id: number
  username: string
  email?: string
  first_name?: string
  last_name?: string
  is_active?: boolean
  date_joined?: string
  last_login?: string
  groups?: Array<{ id: number; name: string }>
}

interface GetCurrentUserResponse {
  user: User
  permissions?: string[]
}

// ============================================================================
// TOKEN MANAGEMENT
// ============================================================================

/**
 * Get stored auth token
 */
export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY)
}

/**
 * Store auth token
 */
export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token)
}

/**
 * Remove auth token
 */
export function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(USER_KEY)
}

/**
 * Check if token exists
 */
export function hasToken(): boolean {
  return !!getToken()
}

// ============================================================================
// AXIOS INSTANCE WITH TOKEN
// ============================================================================

/**
 * Create axios instance with auth token header
 */
function createAuthAxios() {
  const instance = axios.create({
    timeout: 30000,
    headers: {
      'Content-Type': 'application/json'
    }
  })

  // Add token to all requests
  instance.interceptors.request.use((config) => {
    const token = getToken()
    if (token) {
      config.headers.Authorization = `Token ${token}`
    }
    return config
  })

  return instance
}

const authAxios = createAuthAxios()

// ============================================================================
// AUTH SERVICE CLASS
// ============================================================================

class AuthService {
  /**
   * Login with username/email and password using Token authentication
   */
  async login(username: string, password: string): Promise<void> {
    // DEV MODE: Use mock login for UI testing
    if (!USE_REAL_API) {
      console.log('[Auth] Using mock login (DEV mode)')
      return this.mockLogin(username, password)
    }

    // PRODUCTION: Real Django Token authentication
    console.log('[Auth] Attempting real login for:', username)

    try {
      // Step 1: Obtain token
      const tokenResponse = await axios.post<TokenObtainResponse>(
        '/api/v4/auth/token/obtain/',
        { username, password },
        {
          headers: { 'Content-Type': 'application/json' }
        }
      )

      const token = tokenResponse.data.token
      if (!token) {
        throw new Error('Token not received from server')
      }

      // Store token
      setToken(token)
      console.log('[Auth] Token obtained successfully')

      // Step 2: Get current user info
      const userResponse = await authAxios.get<MayanUserResponse>(
        '/api/v4/users/current/'
      )

      // Store user data
      const userData = this.mapMayanUser(userResponse.data)
      localStorage.setItem(USER_KEY, JSON.stringify(userData))

      console.log('[Auth] Login successful for:', userData.username)
    } catch (error: any) {
      clearToken()
      
      // Handle specific error cases
      if (error.response?.status === 400) {
        throw new Error('Неверное имя пользователя или пароль')
      }
      if (error.response?.status === 401) {
        throw new Error('Неверные учетные данные')
      }
      if (error.code === 'ECONNREFUSED' || error.code === 'ERR_NETWORK') {
        throw new Error('Не удалось подключиться к серверу')
      }
      
      console.error('[Auth] Login error:', error)
      throw new Error(error.message || 'Ошибка входа')
    }
  }

  /**
   * Mock login for development
   */
  private async mockLogin(email: string, password: string): Promise<void> {
    if (!email || !password) {
      throw new Error('Email and password are required')
    }

    // Simulate network delay
    await new Promise(resolve => setTimeout(resolve, 500))

    // Store mock data
    localStorage.setItem('dev_authenticated', 'true')
    localStorage.setItem(USER_KEY, JSON.stringify({
      id: 1,
      username: email.split('@')[0] || 'user',
      email: email,
      first_name: 'Test',
      last_name: 'User',
      is_active: true,
      permissions: ['admin.access', 'documents.view', 'documents.edit'],
      role: 'admin'
    }))

    console.log('[Auth] Mock login successful for:', email)
  }

  /**
   * Map Mayan user response to frontend User type
   */
  private mapMayanUser(mayanUser: MayanUserResponse): User {
    // Extract permissions from groups
    const permissions: string[] = []
    if (mayanUser.groups) {
      mayanUser.groups.forEach(group => {
        // Map group names to permission strings
        if (group.name.toLowerCase().includes('admin')) {
          permissions.push('admin.access', 'documents.view', 'documents.edit', 'documents.delete')
        } else {
          permissions.push('documents.view')
        }
      })
    }

    return {
      id: mayanUser.id,
      username: mayanUser.username,
      email: mayanUser.email || `${mayanUser.username}@localhost`,
      first_name: mayanUser.first_name || '',
      last_name: mayanUser.last_name || '',
      is_active: mayanUser.is_active !== false,
      permissions,
      role: permissions.includes('admin.access') ? 'admin' : 'user'
    }
  }

  /**
   * Logout current user.
   * Clears token from localStorage and removes Authorization header.
   */
  async logout(): Promise<void> {
    console.log('[Auth] Logging out...')
    
    // Clear all auth data from localStorage
    clearToken()
    localStorage.removeItem('dev_authenticated')
    
    // Reset axios default headers
    delete axios.defaults.headers.common['Authorization']
    
    console.log('[Auth] ✅ Logged out successfully')
  }

  /**
   * Get current authenticated user
   */
  async getCurrentUser(): Promise<GetCurrentUserResponse> {
    // DEV MODE: Return stored mock user
    if (!USE_REAL_API) {
      const userData = localStorage.getItem(USER_KEY)
      if (userData) {
        const user = JSON.parse(userData)
        return { user, permissions: user.permissions || [] }
      }

      // Default mock user
      return {
        user: {
          id: 1,
          email: 'admin@example.com',
          first_name: 'Admin',
          last_name: 'User',
          username: 'admin',
          is_active: true,
          permissions: ['admin.access', 'documents.view'],
          role: 'admin'
        },
        permissions: ['admin.access', 'documents.view']
      }
    }

    // PRODUCTION: Fetch from API
    const token = getToken()
    if (!token) {
      throw new Error('Not authenticated')
    }

    try {
      const response = await authAxios.get<MayanUserResponse>(
        '/api/v4/users/current/'
      )
      const user = this.mapMayanUser(response.data)
      
      // Update stored user data
      localStorage.setItem(USER_KEY, JSON.stringify(user))

      return { user, permissions: user.permissions || [] }
    } catch (error: any) {
      if (error.response?.status === 401) {
        clearToken()
        throw new Error('Session expired')
      }
      throw error
    }
  }

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    if (!USE_REAL_API) {
      return localStorage.getItem('dev_authenticated') === 'true'
    }

    return hasToken()
  }

  /**
   * Validate token by making an API call
   */
  async validateToken(): Promise<boolean> {
    if (!USE_REAL_API) {
      return this.isAuthenticated()
    }

    if (!hasToken()) {
      return false
    }

    try {
      await authAxios.get('/api/v4/users/current/')
      return true
    } catch {
      clearToken()
      return false
    }
  }

  /**
   * Get CSRF token from cookies or meta tag
   */
  private getCsrfToken(): string {
    // Try to get from cookies
    const cookies = document.cookie.split(';')
    for (const cookie of cookies) {
      const [name, value] = cookie.trim().split('=')
      if (name === 'csrftoken') {
        return decodeURIComponent(value)
      }
    }

    // Try to get from meta tag
    const metaToken = document.querySelector('meta[name="csrf-token"]') as HTMLMetaElement
    if (metaToken) {
      return metaToken.content
    }

    return ''
  }

  // ============================================================================
  // PASSWORD MANAGEMENT (placeholder - needs backend support)
  // ============================================================================

  async requestPasswordReset(email: string): Promise<void> {
    console.warn('[Auth] Password reset not implemented')
    throw new Error('Password reset is not available')
  }

  async changePassword(payload: { oldPassword: string; newPassword: string }): Promise<void> {
    console.warn('[Auth] Password change not implemented')
    throw new Error('Password change is not available')
  }

  async resetPassword(payload: { token: string; newPassword: string; confirmPassword: string }): Promise<void> {
    console.warn('[Auth] Password reset not implemented')
    throw new Error('Password reset is not available')
  }

  // ============================================================================
  // 2FA (placeholder - needs backend support)
  // ============================================================================

  async getTwoFactorStatus(): Promise<TwoFactorStatus> {
    // 2FA not implemented in Mayan EDMS by default
    return { enabled: false }
  }

  async enableTwoFactor(): Promise<TwoFactorSetup> {
    throw new Error('2FA is not available')
  }

  async verifyTwoFactor(token: string, method: 'totp' | 'backup_code' = 'totp'): Promise<{ success: boolean; user?: User }> {
    throw new Error('2FA is not available')
  }

  async disableTwoFactor(): Promise<{ success: boolean }> {
    throw new Error('2FA is not available')
  }

  async regenerateBackupCodes(): Promise<{ backup_codes: string[] }> {
    throw new Error('2FA is not available')
  }
}

// ============================================================================
// EXPORTS
// ============================================================================

export const authService = new AuthService()

// Export token utilities for use in other services
export { authAxios, USE_REAL_API }
