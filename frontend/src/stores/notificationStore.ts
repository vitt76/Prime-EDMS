import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export interface Notification {
  id: string
  type: 'success' | 'error' | 'warning' | 'info'
  title: string
  message: string
  timestamp: Date
  read: boolean
  action?: {
    label: string
    handler: () => void
  }
}

export interface NotificationCenterAction {
  id: string
  label: string
  url: string
  type: 'link' | 'button'
  icon?: string
  style?: string
}

export interface NotificationCenterItem {
  id: number
  uuid: string
  title: string
  message: string
  event_type: string
  priority: 'LOW' | 'NORMAL' | 'HIGH' | 'URGENT'
  state: 'CREATED' | 'SENT' | 'READ' | 'ARCHIVED' | 'DELETED'
  icon_type: string
  icon_url?: string
  actions?: NotificationCenterAction[]
  created_at: string
  read_at?: string | null
}

export const useNotificationStore = defineStore(
  'notification',
  () => {
    // State
    const notifications = ref<Notification[]>([])
    const wsConnected = ref(false)

    // Notification Center (server-side notifications)
    const centerNotifications = ref<NotificationCenterItem[]>([])
    const centerUnreadCount = ref(0)
    const centerHasUrgent = ref(false)
    const centerIsLoading = ref(false)
    const centerFilter = ref<'all' | 'unread' | 'important'>('unread')
    const centerCategory = ref<
      'all' | 'uploads' | 'processing' | 'views' | 'downloads' | 'lifecycle'
    >('all')
    const centerScope = ref<'dam' | 'all'>('dam')
    const centerLastState = ref<'SENT' | 'ALL' | 'READ'>('SENT')
    const preferences = ref<any | null>(null)

    // Getters
    const unreadCount = computed(() => {
      return notifications.value.filter((n) => !n.read).length
    })

    const unreadNotifications = computed(() => {
      return notifications.value.filter((n) => !n.read)
    })

    const centerFilteredNotifications = computed(() => {
      const byCategory = (items: NotificationCenterItem[]) => {
        if (centerCategory.value === 'all') {
          return items
        }

        // Client-side fallback category filter.
        // We *also* send `category` to the backend, but depending on deployment/version
        // the API may ignore it. This makes the UI filtering deterministic.
        const categoryForEventType = (eventType: string): typeof centerCategory.value | 'unknown' => {
          const value = (eventType || '').toLowerCase()

          // Upload / ingest
          if (value.includes('document_create') || value.includes('document_file_created')) return 'uploads'

          // Processing / versioning
          if (value.includes('document_version_') || value.includes('document_version_page_')) return 'processing'

          // Views
          if (value.includes('document_view')) return 'views'

          // Downloads
          if (value.includes('document_file_downloaded')) return 'downloads'

          // Lifecycle / trash
          if (value.includes('trashed') || value.includes('trash')) return 'lifecycle'

          return 'unknown'
        }

        return items.filter((n) => categoryForEventType(n.event_type) === centerCategory.value)
      }

      const base = byCategory(centerNotifications.value)

      switch (centerFilter.value) {
        case 'unread':
          // Include both CREATED and SENT as unread (CREATED can be pending Celery task).
          return base.filter((n) => n.state === 'SENT' || n.state === 'CREATED')
        case 'important':
          return base.filter((n) => n.priority === 'HIGH' || n.priority === 'URGENT')
        default:
          return base
      }
    })

    // Actions
    function addNotification(notification: Omit<Notification, 'id' | 'timestamp' | 'read'>) {
      const newNotification: Notification = {
        ...notification,
        id: `notif-${Date.now()}-${Math.random()}`,
        timestamp: new Date(),
        read: false
      }
      notifications.value.unshift(newNotification)

      // Auto-dismiss after 5 seconds for success/info
      if (notification.type === 'success' || notification.type === 'info') {
        setTimeout(() => {
          removeNotification(newNotification.id)
        }, 5000)
      }

      return newNotification.id
    }

    function removeNotification(id: string) {
      const index = notifications.value.findIndex((n) => n.id === id)
      if (index !== -1) {
        notifications.value.splice(index, 1)
      }
    }

    function markAsRead(id: string) {
      const notification = notifications.value.find((n) => n.id === id)
      if (notification) {
        notification.read = true
      }
    }

    function markAllAsRead() {
      notifications.value.forEach((n) => {
        n.read = true
      })
    }

    function clearAll() {
      notifications.value = []
    }

    function connectWebSocket() {
      // TODO: Implement WebSocket connection
      wsConnected.value = true
    }

    function disconnectWebSocket() {
      // TODO: Implement WebSocket disconnection
      wsConnected.value = false
    }

    function setWsConnected(value: boolean) {
      wsConnected.value = value
    }

    async function fetchCenterNotifications(state: 'SENT' | 'ALL' | 'READ' = 'SENT', page = 1) {
      centerIsLoading.value = true
      centerLastState.value = state
      try {
        const { notificationService } = await import('@/services/notificationService')
        const response = await notificationService.getNotifications({
          state,
          page,
          page_size: 20,
          scope: centerScope.value,
          category: centerCategory.value === 'all' ? undefined : centerCategory.value
        })
        // #region agent log
        fetch('http://127.0.0.1:7242/ingest/e2a91df7-36f3-4ec3-8d36-7745f17b1cac', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            sessionId: 'debug-session',
            runId: 'run1',
            hypothesisId: 'D',
            location: 'stores/notificationStore.ts:144',
            message: 'Frontend: API response received',
            data: {
              results_count: response.results?.length || 0,
              unread_count: response.unread_count || 0,
              has_urgent: response.has_urgent || false,
              first_result_id: response.results?.[0]?.id,
              first_result_state: response.results?.[0]?.state,
              first_result_title: response.results?.[0]?.title
            },
            timestamp: Date.now()
          })
        }).catch(() => {})
        // #endregion
        centerNotifications.value = response.results || []
        centerUnreadCount.value = response.unread_count || 0
        centerHasUrgent.value = !!response.has_urgent
      } catch (error) {
        // Keep UX stable; toast errors are handled elsewhere
        // eslint-disable-next-line no-console
        console.error('Failed to fetch Notification Center notifications', error)
        // #region agent log
        fetch('http://127.0.0.1:7242/ingest/e2a91df7-36f3-4ec3-8d36-7745f17b1cac', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            sessionId: 'debug-session',
            runId: 'run1',
            hypothesisId: 'D',
            location: 'stores/notificationStore.ts:150',
            message: 'Frontend: API error',
            data: { error: String(error) },
            timestamp: Date.now()
          })
        }).catch(() => {})
        // #endregion
      } finally {
        centerIsLoading.value = false
      }
    }

    async function getCenterUnreadCount() {
      try {
        const { notificationService } = await import('@/services/notificationService')
        const response = await notificationService.getUnreadCount()
        centerUnreadCount.value = response.unread_count || 0
        centerHasUrgent.value = !!response.has_urgent
      } catch (error) {
        // eslint-disable-next-line no-console
        console.error('Failed to fetch Notification Center unread count', error)
      }
    }

    async function markCenterAsRead(id: number) {
      try {
        const { notificationService } = await import('@/services/notificationService')
        await notificationService.markAsRead(id)
        const item = centerNotifications.value.find((n) => n.id === id)
        if (item) {
          item.state = 'READ'
          item.read_at = new Date().toISOString()
        }
        centerUnreadCount.value = Math.max(0, centerUnreadCount.value - 1)
      } catch (error) {
        // eslint-disable-next-line no-console
        console.error('Failed to mark Notification Center notification as read', error)
      }
    }

    async function markAllCenterAsRead(filterEventType?: string) {
      try {
        const { notificationService } = await import('@/services/notificationService')
        await notificationService.markAllAsRead(filterEventType)
        centerNotifications.value.forEach((n) => {
          if (n.state === 'SENT') {
            n.state = 'READ'
            n.read_at = new Date().toISOString()
          }
        })
        centerUnreadCount.value = 0
      } catch (error) {
        // eslint-disable-next-line no-console
        console.error('Failed to mark all Notification Center notifications as read', error)
      }
    }

    async function deleteCenterNotification(id: number) {
      try {
        const { notificationService } = await import('@/services/notificationService')
        await notificationService.deleteNotification(id)
        centerNotifications.value = centerNotifications.value.filter((n) => n.id !== id)
      } catch (error) {
        // eslint-disable-next-line no-console
        console.error('Failed to delete Notification Center notification', error)
      }
    }

    async function fetchPreferences() {
      try {
        const { notificationService } = await import('@/services/notificationService')
        preferences.value = await notificationService.getPreferences()
      } catch (error) {
        // eslint-disable-next-line no-console
        console.error('Failed to fetch Notification Center preferences', error)
      }
    }

    async function updatePreferences(patch: any) {
      try {
        const { notificationService } = await import('@/services/notificationService')
        preferences.value = await notificationService.updatePreferences(patch)
      } catch (error) {
        // eslint-disable-next-line no-console
        console.error('Failed to update Notification Center preferences', error)
      }
    }

    function handleNewCenterNotification(payload: any) {
      // Minimal schema normalization
      const notification: NotificationCenterItem = {
        id: payload.id,
        uuid: payload.uuid || String(payload.id),
        title: payload.title || '',
        message: payload.message || '',
        event_type: payload.event_type || '',
        priority: payload.priority || 'NORMAL',
        state: payload.state || 'SENT',
        icon_type: payload.icon_type || 'info',
        icon_url: payload.icon_url,
        actions: payload.actions || [],
        created_at: payload.created_at || new Date().toISOString(),
        read_at: payload.read_at || null
      }
      centerNotifications.value.unshift(notification)
      centerUnreadCount.value += 1
      if (notification.priority === 'URGENT') centerHasUrgent.value = true
    }

    function setCenterFilter(filter: 'all' | 'unread' | 'important') {
      centerFilter.value = filter
    }

    function setCenterCategory(category: 'all' | 'uploads' | 'processing' | 'views' | 'downloads' | 'lifecycle') {
      centerCategory.value = category
      // Refresh the list using the last requested state (popover uses SENT, archive uses ALL).
      fetchCenterNotifications(centerLastState.value, 1)
    }

    function setCenterScope(scope: 'dam' | 'all') {
      centerScope.value = scope
      fetchCenterNotifications(centerLastState.value, 1)
    }

    return {
      // State
      notifications,
      wsConnected,
      centerNotifications,
      centerUnreadCount,
      centerHasUrgent,
      centerIsLoading,
      centerFilter,
      centerCategory,
      centerScope,
      preferences,
      // Getters
      unreadCount,
      unreadNotifications,
      centerFilteredNotifications,
      // Actions
      addNotification,
      removeNotification,
      markAsRead,
      markAllAsRead,
      clearAll,
      connectWebSocket,
      disconnectWebSocket,
      setWsConnected,
      fetchCenterNotifications,
      getCenterUnreadCount,
      markCenterAsRead,
      markAllCenterAsRead,
      deleteCenterNotification,
      fetchPreferences,
      updatePreferences,
      handleNewCenterNotification,
      setCenterFilter,
      setCenterCategory,
      setCenterScope
    }
  },
  {
    persist: {
      paths: ['notifications'] // Persist toast notifications only
    }
  }
)

