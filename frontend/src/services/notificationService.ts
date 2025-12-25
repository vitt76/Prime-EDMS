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
  }) {
    return apiService.get<NotificationListResponse>('/api/v4/headless/notifications/', params)
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
    return apiService.get<UnreadCountResponse>('/api/v4/headless/notifications/unread-count/')
  },

  getPreferences() {
    return apiService.get<NotificationPreferences>('/api/v4/headless/notifications/preferences/')
  },

  updatePreferences(patch: Partial<NotificationPreferences>) {
    return apiService.patch<NotificationPreferences>('/api/v4/headless/notifications/preferences/', patch)
  }
}


