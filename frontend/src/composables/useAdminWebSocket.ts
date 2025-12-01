/**
 * Mock WebSocket composable for Admin real-time updates
 * Simulates WebSocket behavior with mock data
 */
import { ref, onMounted, onUnmounted, reactive } from 'vue'

export interface AdminNotification {
  id: string
  type: 'info' | 'success' | 'warning' | 'error'
  title: string
  message: string
  timestamp: string
  read: boolean
}

export interface SystemEvent {
  id: string
  type: 'user_login' | 'document_upload' | 'ai_completed' | 'storage_warning' | 'system_update'
  actor?: string
  description: string
  timestamp: string
  metadata?: Record<string, any>
}

export interface SystemStats {
  activeUsers: number
  uploadsInProgress: number
  aiQueueSize: number
  storageUsedPercent: number
  cpuUsage: number
  memoryUsage: number
}

export function useAdminWebSocket() {
  const isConnected = ref(false)
  const connectionStatus = ref<'connecting' | 'connected' | 'disconnected' | 'error'>('disconnected')
  const notifications = ref<AdminNotification[]>([])
  const recentEvents = ref<SystemEvent[]>([])
  const systemStats = reactive<SystemStats>({
    activeUsers: 8,
    uploadsInProgress: 3,
    aiQueueSize: 15,
    storageUsedPercent: 25.6,
    cpuUsage: 45,
    memoryUsage: 62
  })

  let mockInterval: ReturnType<typeof setInterval> | null = null
  let statsInterval: ReturnType<typeof setInterval> | null = null

  const mockEvents: Omit<SystemEvent, 'id' | 'timestamp'>[] = [
    { type: 'user_login', actor: 'maria@company.ru', description: 'Пользователь вошёл в систему' },
    { type: 'document_upload', actor: 'admin', description: 'Загружено 12 файлов в "Маркетинг"' },
    { type: 'ai_completed', description: 'AI-анализ завершён для 5 документов' },
    { type: 'document_upload', actor: 'editor', description: 'Загружен видеофайл "presentation.mp4"' },
    { type: 'storage_warning', description: 'Хранилище заполнено на 80%' },
    { type: 'user_login', actor: 'guest@external.com', description: 'Новый пользователь авторизовался' },
    { type: 'ai_completed', description: 'OCR обработка завершена для 3 документов' },
    { type: 'system_update', description: 'Доступно обновление системы v2.5.0' }
  ]

  const mockNotifications: Omit<AdminNotification, 'id' | 'timestamp' | 'read'>[] = [
    { type: 'success', title: 'Импорт завершён', message: '234 файла успешно импортированы из Яндекс.Диска' },
    { type: 'info', title: 'Новый пользователь', message: 'Приглашение принято: sergey@company.ru' },
    { type: 'warning', title: 'Высокая нагрузка', message: 'AI-очередь превысила 100 задач' },
    { type: 'error', title: 'Ошибка синхронизации', message: 'Не удалось подключиться к S3 бакету' },
    { type: 'success', title: 'Бэкап создан', message: 'Автоматический бэкап успешно сохранён' }
  ]

  function connect() {
    connectionStatus.value = 'connecting'
    
    // Simulate connection delay
    setTimeout(() => {
      isConnected.value = true
      connectionStatus.value = 'connected'
      
      // Start mock data generation
      startMockUpdates()
    }, 500)
  }

  function disconnect() {
    isConnected.value = false
    connectionStatus.value = 'disconnected'
    stopMockUpdates()
  }

  function startMockUpdates() {
    // Generate random events every 5-15 seconds
    mockInterval = setInterval(() => {
      if (Math.random() > 0.5) {
        const eventTemplate = mockEvents[Math.floor(Math.random() * mockEvents.length)]
        const newEvent: SystemEvent = {
          ...eventTemplate,
          id: `evt-${Date.now()}`,
          timestamp: new Date().toISOString()
        }
        recentEvents.value.unshift(newEvent)
        if (recentEvents.value.length > 20) {
          recentEvents.value.pop()
        }
      }

      // Occasionally add notification
      if (Math.random() > 0.8) {
        const notifTemplate = mockNotifications[Math.floor(Math.random() * mockNotifications.length)]
        const newNotification: AdminNotification = {
          ...notifTemplate,
          id: `notif-${Date.now()}`,
          timestamp: new Date().toISOString(),
          read: false
        }
        notifications.value.unshift(newNotification)
        if (notifications.value.length > 10) {
          notifications.value.pop()
        }
      }
    }, 8000)

    // Update stats every 3 seconds
    statsInterval = setInterval(() => {
      systemStats.activeUsers = Math.max(1, systemStats.activeUsers + Math.floor(Math.random() * 3 - 1))
      systemStats.uploadsInProgress = Math.max(0, Math.min(10, systemStats.uploadsInProgress + Math.floor(Math.random() * 3 - 1)))
      systemStats.aiQueueSize = Math.max(0, systemStats.aiQueueSize + Math.floor(Math.random() * 5 - 2))
      systemStats.cpuUsage = Math.max(10, Math.min(95, systemStats.cpuUsage + (Math.random() * 10 - 5)))
      systemStats.memoryUsage = Math.max(30, Math.min(90, systemStats.memoryUsage + (Math.random() * 5 - 2.5)))
    }, 3000)
  }

  function stopMockUpdates() {
    if (mockInterval) {
      clearInterval(mockInterval)
      mockInterval = null
    }
    if (statsInterval) {
      clearInterval(statsInterval)
      statsInterval = null
    }
  }

  function markNotificationRead(id: string) {
    const notification = notifications.value.find(n => n.id === id)
    if (notification) {
      notification.read = true
    }
  }

  function markAllNotificationsRead() {
    notifications.value.forEach(n => n.read = true)
  }

  function clearNotifications() {
    notifications.value = []
  }

  const unreadCount = ref(0)
  
  // Watch for unread notifications
  function updateUnreadCount() {
    unreadCount.value = notifications.value.filter(n => !n.read).length
  }

  onMounted(() => {
    connect()
  })

  onUnmounted(() => {
    disconnect()
  })

  return {
    isConnected,
    connectionStatus,
    notifications,
    recentEvents,
    systemStats,
    unreadCount,
    connect,
    disconnect,
    markNotificationRead,
    markAllNotificationsRead,
    clearNotifications,
    updateUnreadCount
  }
}


