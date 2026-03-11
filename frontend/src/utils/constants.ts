/**
 * Application constants
 */

export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

const normalizeWsBaseUrl = (value: string): string => value.replace(/\/+$/, '')

const computeWsUrl = (): string => {
  const explicit = import.meta.env.VITE_WS_URL
  if (explicit) return normalizeWsBaseUrl(explicit)

  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'

  // Prefer API host if provided, otherwise fallback to current host.
  let host = window.location.host
  const apiUrl = import.meta.env.VITE_API_URL
  if (apiUrl) {
    try {
      host = new URL(apiUrl).host || host
    } catch {
      // ignore invalid URL; keep window host
    }
  }

  return normalizeWsBaseUrl(`${protocol}//${host}/ws`)
}

export const WS_URL = computeWsUrl()

const appendWebSocketQuery = (
  path: string,
  params: Record<string, string | null | undefined>
): string => {
  const query = new URLSearchParams()
  Object.entries(params).forEach(([key, value]) => {
    if (value) {
      query.set(key, value)
    }
  })

  const serialized = query.toString()
  return serialized ? `${path}?${serialized}` : path
}

export const buildNotificationsWebSocketUrl = (
  token: string,
  organizationId?: string | null
): string => {
  return appendWebSocketQuery(
    `${WS_URL}/notifications/`,
    {
      token,
      organization_id: organizationId
    }
  )
}

export const ANALYTICS_WS_URL = `${WS_URL}/analytics/`

export const buildAnalyticsWebSocketUrl = (
  token?: string | null,
  organizationId?: string | null
): string => {
  return appendWebSocketQuery(
    ANALYTICS_WS_URL,
    {
      token,
      organization_id: organizationId
    }
  )
}

export const APP_TITLE = import.meta.env.VITE_APP_TITLE || 'DAM System'
export const APP_VERSION = import.meta.env.VITE_APP_VERSION || '1.0.0'

// Pagination
export const DEFAULT_PAGE_SIZE = 50
export const MAX_PAGE_SIZE = 100

// File upload
export const MAX_FILE_SIZE = 100 * 1024 * 1024 // 100MB
export const ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
export const ALLOWED_VIDEO_TYPES = ['video/mp4', 'video/webm', 'video/ogg']
export const ALLOWED_DOCUMENT_TYPES = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']

// Debounce delays
export const SEARCH_DEBOUNCE_MS = 300
export const INPUT_DEBOUNCE_MS = 500

// Cache TTL
export const CACHE_TTL = 5 * 60 * 1000 // 5 minutes


