import { apiService } from './apiService'
import type { User, TwoFactorStatus, TwoFactorSetup, TwoFactorVerify } from '@/types'

interface LoginResponse {
  user: User
  permissions?: string[]
}

interface RefreshTokenResponse {
  token: string
}

interface GetCurrentUserResponse {
  user: User
  permissions?: string[]
}

const AUTH_PASSWORD_BASE = '/api/auth/password/'

class AuthService {
  /**
   * Login with email and password using session authentication
   */
  async login(email: string, password: string): Promise<void> {
    // In dev mode, use mock login for UI testing
    if (import.meta.env.DEV) {
      if (!email || !password) {
        throw new Error('Email and password are required')
      }
      // Simulate network delay
      await new Promise(resolve => setTimeout(resolve, 500))
      
      // Store mock user data
      localStorage.setItem('dev_authenticated', 'true')
      localStorage.setItem('dev_user', JSON.stringify({
        id: 1,
        username: email.split('@')[0] || 'user',
        email: email,
        first_name: 'Test',
        last_name: 'User',
        is_active: true,
        permissions: ['admin.access', 'documents.view', 'documents.edit'],
        role: 'admin'
      }))
      console.log('[Dev] Mock login successful for:', email)
      return
    }

    // Production: real Django session authentication
    try {
      const formData = new FormData()
      formData.append('username', email)
      formData.append('password', password)

      const csrfToken = this.getCsrfToken()
      if (csrfToken) {
        formData.append('csrfmiddlewaretoken', csrfToken)
      }

      const response = await fetch('/authentication/login/', {
        method: 'POST',
        body: formData,
        headers: {
          'X-CSRFToken': csrfToken,
          'X-Requested-With': 'XMLHttpRequest'
        },
        credentials: 'same-origin',
        redirect: 'manual'
      })

      if (response.status === 302 || response.status === 200 || response.type === 'opaqueredirect') {
        console.log('Login successful')
        return
      } else {
        throw new Error(`Login failed: ${response.status}`)
      }
    } catch (error) {
      console.error('Login error:', error)
      throw error
    }
  }

  /**
   * Logout current user
   */
  async logout(): Promise<void> {
    // In development mode, clear localStorage
    if (import.meta.env.DEV) {
      localStorage.removeItem('dev_authenticated')
      localStorage.removeItem('dev_user')
      console.log('[Dev] Mock logout successful')
      return
    }

    // In production, use real Django logout
    const response = await fetch('/authentication/logout/', {
      method: 'POST',
      headers: {
        'X-CSRFToken': this.getCsrfToken(),
        'X-Requested-With': 'XMLHttpRequest'
      },
      credentials: 'same-origin'
    })

    if (!response.ok) {
      throw new Error(`Logout failed: ${response.status}`)
    }
  }

  /**
   * Get current authenticated user from Django context
   */
  async getCurrentUser(): Promise<GetCurrentUserResponse> {
    // In development mode, return stored mock user data
    if (import.meta.env.DEV) {
      const userData = localStorage.getItem('dev_user')
      if (userData) {
        const user = JSON.parse(userData)
        return {
          user: user,
          permissions: user.permissions || ['admin.access', 'documents.view']
        }
      }
      // Default mock user if none stored
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

    // In production, use Django context
    if (typeof window !== 'undefined' && (window as any).DJANGO_CONTEXT) {
      const djangoContext = (window as any).DJANGO_CONTEXT
      return {
        user: djangoContext.user,
        permissions: djangoContext.user.permissions || []
      }
    }

    throw new Error('Unable to get current user')
  }

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    // In development mode (Vite dev server), Django context is not available
    // We'll use a different approach for auth checking
    if (import.meta.env.DEV) {
      // In dev mode, check if we have a session cookie or localStorage flag
      return localStorage.getItem('dev_authenticated') === 'true'
    }

    // In production (Django served), use Django context
    if (typeof window !== 'undefined' && (window as any).DJANGO_CONTEXT) {
      return (window as any).DJANGO_CONTEXT.user.is_authenticated
    }
    return false
  }

  /**
   * Get CSRF token from cookies or meta tag
   */
  private getCsrfToken(): string {
    // Try to get from Django context first
    if (typeof window !== 'undefined' && (window as any).DJANGO_CONTEXT) {
      return (window as any).DJANGO_CONTEXT.csrf_token
    }

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

    // Fallback - this will likely fail, but better than undefined
    return ''
  }

  /**
   * Register new user (if allowed)
   */
  async register(data: {
    email: string
    password: string
    first_name?: string
    last_name?: string
  }): Promise<LoginResponse> {
    return apiService.post<LoginResponse>('/v4/auth/register/', data)
  }

  /**
   * Request password reset (forgot password)
   */
  async requestPasswordReset(email: string): Promise<void> {
    return apiService.post<void>(`${AUTH_PASSWORD_BASE}forgot/`, { email })
  }

  /**
   * Change password for authenticated user
   */
  async changePassword(payload: {
    oldPassword: string
    newPassword: string
  }): Promise<void> {
    return apiService.post<void>(`${AUTH_PASSWORD_BASE}change/`, {
      old_password: payload.oldPassword,
      new_password: payload.newPassword
    })
  }

  /**
   * Reset password with token
   */
  async resetPassword(payload: {
    token: string
    newPassword: string
    confirmPassword: string
  }): Promise<void> {
    return apiService.post<void>(`${AUTH_PASSWORD_BASE}reset/`, {
      token: payload.token,
      new_password: payload.newPassword,
      confirm_password: payload.confirmPassword
    })
  }

  /**
   * Get 2FA status for current user
   */
  async getTwoFactorStatus(): Promise<TwoFactorStatus> {
    return apiService.get<TwoFactorStatus>('/v4/auth/me/2fa/')
  }

  /**
   * Enable 2FA for current user
   */
  async enableTwoFactor(): Promise<TwoFactorSetup> {
    return apiService.post<TwoFactorSetup>('/v4/auth/me/2fa/enable/')
  }

  /**
   * Verify 2FA token during setup or login
   */
  async verifyTwoFactor(token: string, method: 'totp' | 'backup_code' = 'totp'): Promise<{ success: boolean; user?: User }> {
    const payload: TwoFactorVerify = { token, method }
    return apiService.post<{ success: boolean; user?: User }>('/v4/auth/me/2fa/verify/', payload)
  }

  /**
   * Disable 2FA for current user
   */
  async disableTwoFactor(): Promise<{ success: boolean }> {
    return apiService.post<{ success: boolean }>('/v4/auth/me/2fa/disable/')
  }

  /**
   * Regenerate backup codes
   */
  async regenerateBackupCodes(): Promise<{ backup_codes: string[] }> {
    return apiService.post<{ backup_codes: string[] }>('/v4/auth/me/2fa/regenerate-backup/')
  }
}

export const authService = new AuthService()

