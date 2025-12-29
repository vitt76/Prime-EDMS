import { apiService } from './apiService'

export type NotificationPriority = 'LOW' | 'NORMAL' | 'HIGH' | 'URGENT'
export type NotificationState = 'CREATED' | 'SENT' | 'READ' | 'ARCHIVED' | 'DELETED'

export interface NotificationAction {
  id: string
  label: string
  url: string
  type: 'link' | 'button'
  icon?: string
  style?: string
}

export interface NotificationItem {
  id: number
  uuid: string
  title: string
  message: string
  event_type: string
  priority: NotificationPriority
  state: NotificationState
  icon_type: string
  icon_url?: string
  actions?: NotificationAction[]
  created_at: string
  read_at?: string | null
}

export interface NotificationListResponse {
  count: number
  next: string | null
  previous: string | null
  unread_count: number
  has_urgent: boolean
  results: NotificationItem[]
}

export interface UnreadCountResponse {
  unread_count: number
  has_urgent: boolean
  urgent_count: number
}

export interface NotificationPreferences {
  notifications_enabled: boolean
  email_notifications_enabled: boolean
  push_notifications_enabled: boolean
  email_digest_enabled: boolean
  email_digest_frequency: string
  quiet_hours_enabled: boolean
  quiet_hours_start: string | null
  quiet_hours_end: string | null
  notification_language: string
}

export const notificationService = {
  getNotifications(params?: {
    state?: string
    page?: number
    page_size?: number
    event_type?: string
    filter_event?: string
    category?: string
    scope?: string
  }) {
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/e2a91df7-36f3-4ec3-8d36-7745f17b1cac', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        sessionId: 'debug-session',
        runId: 'run1',
        hypothesisId: 'D',
        location: 'services/notificationService.ts:65',
        message: 'Frontend: API request to getNotifications',
        data: { params },
        timestamp: Date.now()
      })
    }).catch(() => {})
    // #endregion
    // IMPORTANT:
    // apiService.get() expects Axios config as the 2nd arg, so query params must be passed via { params: ... }.
    // Otherwise query params won't be sent and cacheKey collapses to just the URL.
    return apiService
      .get<NotificationListResponse>('/api/v4/headless/notifications/', { params } as any, false)
      .then(response => {
      // #region agent log
      fetch('http://127.0.0.1:7242/ingest/e2a91df7-36f3-4ec3-8d36-7745f17b1cac', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          sessionId: 'debug-session',
          runId: 'run1',
          hypothesisId: 'D',
          location: 'services/notificationService.ts:75',
          message: 'Frontend: API response from getNotifications',
          data: {
            results_count: response.results?.length || 0,
            unread_count: response.unread_count || 0,
            has_urgent: response.has_urgent || false,
            count: response.count || 0,
            first_result: response.results?.[0] || null
          },
          timestamp: Date.now()
        })
      }).catch(() => {})
      // #endregion
      return response
    }).catch(error => {
      // #region agent log
      fetch('http://127.0.0.1:7242/ingest/e2a91df7-36f3-4ec3-8d36-7745f17b1cac', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          sessionId: 'debug-session',
          runId: 'run1',
          hypothesisId: 'D',
          location: 'services/notificationService.ts:95',
          message: 'Frontend: API error in getNotifications',
          data: { error: String(error), error_message: error?.message, error_status: error?.response?.status },
          timestamp: Date.now()
        })
      }).catch(() => {})
      // #endregion
      throw error
    })
  },

  getNotification(id: number) {
    return apiService.get<NotificationItem>(`/api/v4/headless/notifications/${id}/`)
  },

  markAsRead(id: number) {
    return apiService.patch<NotificationItem>(`/api/v4/headless/notifications/${id}/read/`, {})
  },

  markAllAsRead(filterEventType?: string) {
    return apiService.post<{ marked_count: number; unread_count: number }>(
      '/api/v4/headless/notifications/read-all/',
      filterEventType ? { filter_event_type: filterEventType } : {}
    )
  },

  deleteNotification(id: number) {
    return apiService.delete<void>(`/api/v4/headless/notifications/${id}/`)
  },

  getUnreadCount() {
    // Unread count must be fresh; avoid cache.
    return apiService.get<UnreadCountResponse>('/api/v4/headless/notifications/unread-count/', undefined, false)
  },

  getPreferences() {
    return apiService.get<NotificationPreferences>('/api/v4/headless/notifications/preferences/')
  },

  updatePreferences(patch: Partial<NotificationPreferences>) {
    return apiService.patch<NotificationPreferences>('/api/v4/headless/notifications/preferences/', patch)
  }
}


