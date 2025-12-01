import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useAuthStore } from '@/stores/authStore'
import { authService } from '@/services/authService'
import type { User } from '@/types'

// Mock authService
vi.mock('@/services/authService', () => ({
  authService: {
    login: vi.fn(),
    logout: vi.fn(),
    refreshToken: vi.fn(),
    getCurrentUser: vi.fn()
  }
}))

const mockUser: User = {
  id: 1,
  username: 'testuser',
  email: 'test@example.com',
  first_name: 'Test',
  last_name: 'User',
  is_active: true,
  permissions: ['documents.view_document']
}

describe('authStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    localStorage.clear()
  })

  it('initializes with default state', () => {
    const store = useAuthStore()
    
    expect(store.user).toBeNull()
    expect(store.token).toBeNull()
    expect(store.isAuthenticated).toBe(false)
    expect(store.permissions).toEqual([])
    expect(store.lastActivity).toBeNull()
  })

  it('logs in successfully', async () => {
    const mockResponse = {
      user: mockUser,
      token: 'mock-token',
      permissions: ['documents.view_document']
    }
    vi.mocked(authService.login).mockResolvedValue(mockResponse)
    
    const store = useAuthStore()
    const result = await store.login('test@example.com', 'password')
    
    expect(result.success).toBe(true)
    expect(store.user).toEqual(mockUser)
    expect(store.token).toBe('mock-token')
    expect(store.isAuthenticated).toBe(true)
    expect(store.permissions).toEqual(['documents.view_document'])
    expect(localStorage.getItem('auth_token')).toBe('mock-token')
  })

  it('handles login error', async () => {
    const error = new Error('Invalid credentials')
    vi.mocked(authService.login).mockRejectedValue(error)
    
    const store = useAuthStore()
    
    await expect(store.login('test@example.com', 'wrong')).rejects.toThrow()
    expect(store.isAuthenticated).toBe(false)
    expect(store.user).toBeNull()
  })

  it('logs out successfully', async () => {
    vi.mocked(authService.logout).mockResolvedValue(undefined)
    
    const store = useAuthStore()
    store.user = mockUser
    store.token = 'mock-token'
    store.isAuthenticated = true
    localStorage.setItem('auth_token', 'mock-token')
    
    await store.logout()
    
    expect(store.user).toBeNull()
    expect(store.token).toBeNull()
    expect(store.isAuthenticated).toBe(false)
    expect(store.permissions).toEqual([])
    expect(localStorage.getItem('auth_token')).toBeNull()
  })

  it('handles logout error gracefully', async () => {
    const error = new Error('Network error')
    vi.mocked(authService.logout).mockRejectedValue(error)
    
    const store = useAuthStore()
    store.user = mockUser
    store.token = 'mock-token'
    store.isAuthenticated = true
    
    await store.logout()
    
    // Should still clear local state even if API call fails
    expect(store.user).toBeNull()
    expect(store.isAuthenticated).toBe(false)
  })

  it('refreshes token successfully', async () => {
    const mockResponse = { token: 'new-token' }
    vi.mocked(authService.refreshToken).mockResolvedValue(mockResponse)
    
    const store = useAuthStore()
    store.token = 'old-token'
    
    const result = await store.refreshToken()
    
    expect(result.success).toBe(true)
    expect(store.token).toBe('new-token')
    expect(localStorage.getItem('auth_token')).toBe('new-token')
  })

  it('logs out on token refresh failure', async () => {
    const error = new Error('Token expired')
    vi.mocked(authService.refreshToken).mockRejectedValue(error)
    vi.mocked(authService.logout).mockResolvedValue(undefined)
    
    const store = useAuthStore()
    store.user = mockUser
    store.token = 'old-token'
    store.isAuthenticated = true
    
    await expect(store.refreshToken()).rejects.toThrow()
    
    expect(store.isAuthenticated).toBe(false)
    expect(store.user).toBeNull()
  })

  it('checks auth with valid token', async () => {
    const mockResponse = {
      user: mockUser,
      permissions: ['documents.view_document']
    }
    vi.mocked(authService.getCurrentUser).mockResolvedValue(mockResponse)
    localStorage.setItem('auth_token', 'valid-token')
    
    const store = useAuthStore()
    const result = await store.checkAuth()
    
    expect(result).toBe(true)
    expect(store.user).toEqual(mockUser)
    expect(store.isAuthenticated).toBe(true)
    expect(store.token).toBe('valid-token')
  })

  it('checks auth with no token', async () => {
    const store = useAuthStore()
    const result = await store.checkAuth()
    
    expect(result).toBe(false)
    expect(store.isAuthenticated).toBe(false)
  })

  it('checks auth with invalid token', async () => {
    const error = new Error('Invalid token')
    vi.mocked(authService.getCurrentUser).mockRejectedValue(error)
    vi.mocked(authService.logout).mockResolvedValue(undefined)
    localStorage.setItem('auth_token', 'invalid-token')
    
    const store = useAuthStore()
    const result = await store.checkAuth()
    
    expect(result).toBe(false)
    expect(store.isAuthenticated).toBe(false)
    expect(localStorage.getItem('auth_token')).toBeNull()
  })

  it('checks permission correctly', async () => {
    const mockResponse = {
      user: mockUser,
      token: 'mock-token',
      permissions: ['documents.view_document', 'documents.add_document']
    }
    vi.mocked(authService.login).mockResolvedValue(mockResponse)
    
    const store = useAuthStore()
    await store.login('test@example.com', 'password')
    
    expect(store.hasPermission('documents.view_document')).toBe(true)
    expect(store.hasPermission('documents.add_document')).toBe(true)
    expect(store.hasPermission('documents.delete_document')).toBe(false)
  })

  it('updates last activity', () => {
    const store = useAuthStore()
    const before = store.lastActivity
    
    store.updateActivity()
    
    expect(store.lastActivity).not.toBe(before)
    expect(store.lastActivity).toBeInstanceOf(Date)
  })
})
