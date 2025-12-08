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
import { apiService } from './apiService'
import type { User, TwoFactorStatus, TwoFactorSetup } from '@/types'

// ============================================================================
// CONFIGURATION
// ============================================================================

/**
 * Feature flags.
 * BFF enabled by default unless explicitly disabled.
 */
const USE_REAL_API = import.meta.env.VITE_USE_MOCK_AUTH !== 'true'
const BFF_ENABLED = import.meta.env.VITE_BFF_ENABLED !== 'false'

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

    // Step 1: Obtain token (DRF token auth)
    const formData = new URLSearchParams()
    formData.append('username', username)
    formData.append('password', password)

    const tokenResponse = await apiService.post<TokenObtainResponse>(
      '/api/v4/auth/token/obtain/',
      formData,
      {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      }
    )

    const token = tokenResponse.token || (tokenResponse as any).data?.token
    if (!token) {
      clearToken()
      throw new Error('Token not received from server')
    }

    // Store token for interceptors
    setToken(token)
    console.log('[Auth] Token obtained successfully')

    // Step 2: Get current user info
    const userResponse = await apiService.get<MayanUserResponse>('/api/v4/users/current/')
    const userData = this.mapMayanUser(userResponse)
    localStorage.setItem(USER_KEY, JSON.stringify(userData))

    console.log('[Auth] Login successful for:', userData.username)
    return { token }
  }

  /**
   * Change password via headless API.
   */
  async changePassword(payload: { oldPassword: string; newPassword: string }): Promise<void> {
    await apiService.post(
      '/api/v4/headless/password/change/',
      {
        current_password: payload.oldPassword,
        new_password: payload.newPassword,
        new_password_confirm: payload.newPassword
      }
    )
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

    const response = await apiService.get<MayanUserResponse>('/api/v4/users/current/')
    const user = this.mapMayanUser(response)
    
    // Update stored user data
    localStorage.setItem(USER_KEY, JSON.stringify(user))

    return { user, permissions: user.permissions || [] }
  }

  /**
   * Map Mayan user response to frontend User type
   */
  private mapMayanUser(data: any): User {
    if (!data) {
      throw new Error('Empty user response')
    }
    return {
      id: data.id,
      username: data.username,
      email: data.email,
      first_name: data.first_name,
      last_name: data.last_name,
      is_active: data.is_active ?? true,
      permissions: data.permissions || [],
      role: data.role || (data.groups && data.groups[0]) || undefined,
      two_factor_enabled: data.two_factor_enabled ?? false
    }
  }

  /**
   * Logout (clear local storage; optional API call)
   */
  async logout(): Promise<void> {
    clearToken()
    localStorage.removeItem('dev_authenticated')
    // Optionally hit backend logout endpoint if implemented
    try {
      await apiService.post('/api/v4/auth/token/logout/', {})
    } catch (err) {
      console.warn('[Auth] Logout API call failed (ignored):', err)
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

    // Fallback for real API mode: return empty string if not found
    return ''
  }
}

// ============================================================================
// EXPORTS
// ============================================================================

export const authService = new AuthService()

// Export token utilities for use in other services
export { USE_REAL_API, BFF_ENABLED }
