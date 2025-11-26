import { apiService } from './apiService'
import type { User, TwoFactorStatus, TwoFactorSetup, TwoFactorVerify } from '@/types'

interface LoginResponse {
  token: string
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
   * Login with email and password
   */
  async login(email: string, password: string): Promise<LoginResponse> {
    return apiService.post<LoginResponse>('/v4/auth/login/', {
      email,
      password
    })
  }

  /**
   * Logout current user
   */
  async logout(): Promise<void> {
    return apiService.post<void>('/v4/auth/logout/')
  }

  /**
   * Refresh authentication token
   */
  async refreshToken(): Promise<RefreshTokenResponse> {
    return apiService.post<RefreshTokenResponse>('/v4/auth/refresh/')
  }

  /**
   * Get current authenticated user
   */
  async getCurrentUser(): Promise<GetCurrentUserResponse> {
    return apiService.get<GetCurrentUserResponse>('/v4/auth/me/')
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

