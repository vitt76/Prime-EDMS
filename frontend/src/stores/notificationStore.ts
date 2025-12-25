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
    const preferences = ref<any | null>(null)

    // Getters
    const unreadCount = computed(() => {
      return notifications.value.filter((n) => !n.read).length
    })

    const unreadNotifications = computed(() => {
      return notifications.value.filter((n) => !n.read)
    })

    const centerFilteredNotifications = computed(() => {
      switch (centerFilter.value) {
        case 'unread':
          return centerNotifications.value.filter((n) => n.state === 'SENT')
        case 'important':
          return centerNotifications.value.filter((n) => n.priority === 'HIGH' || n.priority === 'URGENT')
        default:
          return centerNotifications.value
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

    async function fetchCenterNotifications(state = 'SENT', page = 1) {
      centerIsLoading.value = true
      try {
        const { notificationService } = await import('@/services/notificationService')
        const response = await notificationService.getNotifications({
          state,
          page,
          page_size: 20
        })
        centerNotifications.value = response.results || []
        centerUnreadCount.value = response.unread_count || 0
        centerHasUrgent.value = !!response.has_urgent
      } catch (error) {
        // Keep UX stable; toast errors are handled elsewhere
        // eslint-disable-next-line no-console
        console.error('Failed to fetch Notification Center notifications', error)
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

    return {
      // State
      notifications,
      wsConnected,
      centerNotifications,
      centerUnreadCount,
      centerHasUrgent,
      centerIsLoading,
      centerFilter,
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
      setCenterFilter
    }
  },
  {
    persist: {
      paths: ['notifications'] // Persist toast notifications only
    }
  }
)

