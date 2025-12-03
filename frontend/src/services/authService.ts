/**
 * Authentication Service
 * ======================
 * 
 * Handles authentication with Mayan EDMS backend.
 * Supports Token-based authentication (DRF Token).
 * 
 * API Endpoints:
 * - POST /api/v4/auth/token/obtain/ - Get auth token
 * - GET /api/v4/user_management/users/current/ - Get current user
 */

import { apiService } from './apiService'
import type { User } from '@/types'

// ============================================================================
// CONFIGURATION
// ============================================================================

/**
 * Use real API authentication instead of mocks.
 * Set to `true` to connect to real Django backend.
 */
const USE_REAL_API = import.meta.env.VITE_USE_REAL_API === 'true'

/**
 * Token storage key
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
      // Mock mode - simulate async operation and return fake token
      console.log('[Auth] Using mock token for:', username)

      // Simulate network delay
      await new Promise(resolve => setTimeout(resolve, 500))

      // Create mock user data
      const mockUser: User = {
        id: 1,
        username: username || 'admin',
        email: `${username || 'admin'}@example.com`,
        first_name: 'Test',
        last_name: 'User',
        is_active: true,
        permissions: ['admin.access', 'documents.view', 'documents.edit'],
        role: 'admin'
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
   * Get current user info or return mock user
   */
  async getCurrentUser(): Promise<User> {
    if (!USE_REAL_API) {
      // Mock mode - return mock user
      const storedUser = localStorage.getItem(USER_KEY)
      if (storedUser) {
        return JSON.parse(storedUser)
      }

      // Default mock user
      return {
        id: 1,
        username: 'admin',
        email: 'admin@example.com',
        first_name: 'Admin',
        last_name: 'User',
        is_active: true,
        permissions: ['admin.access', 'documents.view', 'documents.edit'],
        role: 'admin'
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
      // Mock mode - just clear local storage
      console.log('[Auth] Mock logout')
      return
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
