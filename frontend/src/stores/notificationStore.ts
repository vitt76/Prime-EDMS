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

export const useNotificationStore = defineStore(
  'notification',
  () => {
    // State
    const notifications = ref<Notification[]>([])
    const wsConnected = ref(false)

    // Getters
    const unreadCount = computed(() => {
      return notifications.value.filter((n) => !n.read).length
    })

    const unreadNotifications = computed(() => {
      return notifications.value.filter((n) => !n.read)
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

    return {
      // State
      notifications,
      wsConnected,
      // Getters
      unreadCount,
      unreadNotifications,
      // Actions
      addNotification,
      removeNotification,
      markAsRead,
      markAllAsRead,
      clearAll,
      connectWebSocket,
      disconnectWebSocket
    }
  },
  {
    persist: {
      paths: ['notifications'] // Persist notifications
    }
  }
)

