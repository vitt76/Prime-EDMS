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


// ============================================================================
// AUTH SERVICE CLASS
// ============================================================================

class AuthService {
  /**
   * Obtain auth token from backend or return mock token
   */
  async obtainToken(username: string, password: string): Promise<{ token: string }> {
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

      // Save user data
      localStorage.setItem(USER_KEY, JSON.stringify(mockUser))

      return { token: `mock_token_${Date.now()}` }
    }

    // Real API mode
    const response = await apiService.post<{ token: string }>(
      '/api/v4/auth/token/obtain/',
      { username, password }
    )
    return response
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
    }

    // Real API mode - use correct endpoint
    const response = await apiService.get<any>('/api/v4/users/current/')
    return {
      id: response.id,
      username: response.username,
      email: response.email,
      first_name: response.first_name,
      last_name: response.last_name,
      is_active: response.is_active,
      permissions: ['admin.access', 'documents.view', 'documents.edit'], // Default permissions
      role: 'admin' // Default role
    }
  }

  /**
   * Logout (clear local storage or call API)
   */
  async logout(): Promise<void> {
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

    // Real API mode
    await apiService.post('/api/v4/auth/logout/')
  }
}

// ============================================================================
// EXPORTS
// ============================================================================

export const authService = new AuthService()

// Export token utilities for use in other services
export { USE_REAL_API }
