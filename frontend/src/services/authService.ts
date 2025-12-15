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

import { apiService } from './apiService'
import { cacheService } from './cacheService'
import type { User, TwoFactorStatus, TwoFactorSetup } from '@/types'

// ============================================================================
// CONFIGURATION
// ============================================================================

/**
 * Feature flags.
 * BFF enabled by default unless explicitly disabled.
 */
const USE_REAL_API = true
const BFF_ENABLED = true

/**
 * LocalStorage keys
 */
const TOKEN_KEY = 'auth_token'
const USER_KEY = 'auth_user'

interface TokenObtainResponse {
  token: string
}

type MayanUserResponse = any

export interface GetCurrentUserResponse {
  user: User
  permissions: string[]
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
// AUTH SERVICE CLASS
// ============================================================================

class AuthService {
  /**
   * Obtain auth token from backend or return mock token
   */
  async obtainToken(username: string, password: string): Promise<{ token: string }> {
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
      } as any
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
   * Update current user profile (headless).
   */
  async updateProfile(payload: { firstName: string; lastName: string; email: string }): Promise<User> {
    const response = await apiService.patch<{
      id: number
      username: string
      first_name: string
      last_name: string
      email: string
    }>(
      '/api/v4/headless/profile/',
      {
        first_name: payload.firstName,
        last_name: payload.lastName,
        email: payload.email
      }
    )

    const user: User = {
      id: response.id,
      username: response.username,
      first_name: response.first_name,
      last_name: response.last_name,
      email: response.email,
      is_active: true,
      permissions: [],
      role: undefined
    }

    // Persist locally for session continuity
    localStorage.setItem(USER_KEY, JSON.stringify(user))
    return user
  }

  /**
   * Get current authenticated user
   */
  async getCurrentUser(): Promise<GetCurrentUserResponse> {
    // PRODUCTION: Fetch from API
    const token = getToken()
    if (!token) {
      throw new Error('Not authenticated')
    }

    // Prefer headless "me" endpoint which includes is_staff/is_superuser and groups.
    try {
      const me = await apiService.get<any>('/api/v4/headless/auth/me/', undefined, false)
      const user = (me && me.user) ? me.user : this.mapMayanUser(me)
      localStorage.setItem(USER_KEY, JSON.stringify(user))
      return { user, permissions: user.permissions || [] }
    } catch (_e) {
      // Fallback to core endpoint
      const response = await apiService.get<MayanUserResponse>(
        '/api/v4/users/current/',
        undefined,
        false // do not cache current user; ensures fresh user after switch
      )
      const user = this.mapMayanUser(response)
      localStorage.setItem(USER_KEY, JSON.stringify(user))
      return { user, permissions: user.permissions || [] }
    }
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
      is_staff: data.is_staff ?? false,
      is_superuser: data.is_superuser ?? false,
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
    cacheService.clear()
    localStorage.removeItem('dev_authenticated')
    // Backend logout not required for token auth; endpoint may be absent (404)
  }

  // --------------------------------------------------------------------------
  // 2FA (not implemented in backend yet)
  // These methods exist to satisfy the frontend store typing.
  // --------------------------------------------------------------------------

  async getTwoFactorStatus(): Promise<TwoFactorStatus> {
    return { enabled: false }
  }

  async enableTwoFactor(): Promise<TwoFactorSetup> {
    throw new Error('2FA is not implemented on the backend yet')
  }

  async verifyTwoFactor(_token: string, _method: 'totp' | 'backup_code' = 'totp'): Promise<any> {
    throw new Error('2FA is not implemented on the backend yet')
  }

  async disableTwoFactor(): Promise<any> {
    throw new Error('2FA is not implemented on the backend yet')
  }

  async regenerateBackupCodes(): Promise<{ backup_codes: string[] }> {
    throw new Error('2FA is not implemented on the backend yet')
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
        return value ? decodeURIComponent(value) : ''
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
