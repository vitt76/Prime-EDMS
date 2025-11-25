import { apiService } from './apiService'
import type { User } from '@/types'

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
   * Request password reset
   */
  async requestPasswordReset(email: string): Promise<void> {
    return apiService.post<void>('/v4/auth/password-reset/', { email })
  }

  /**
   * Reset password with token
   */
  async resetPassword(token: string, newPassword: string): Promise<void> {
    return apiService.post<void>('/v4/auth/password-reset/confirm/', {
      token,
      new_password: newPassword
    })
  }
}

export const authService = new AuthService()

