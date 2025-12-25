import { WS_URL } from '@/utils/constants'
import { useNotificationStore } from '@/stores/notificationStore'

export function useWebSocket() {
  let websocket: WebSocket | null = null
  let heartbeatTimer: number | null = null
  const notificationStore = useNotificationStore()

  const getToken = (): string | null => {
    try {
      return localStorage.getItem('auth_token')
    } catch {
      return null
    }
  }

  const connect = () => {
    const token = getToken()
    if (!token) return

    // WS_URL already includes "/ws"
    const url = `${WS_URL}/notifications/?token=${encodeURIComponent(token)}`

    websocket = new WebSocket(url)

    websocket.onopen = () => {
      notificationStore.setWsConnected(true)
      // Heartbeat ping
      heartbeatTimer = window.setInterval(() => {
        if (websocket?.readyState === WebSocket.OPEN) {
          websocket.send(
            JSON.stringify({
              type: 'ping',
              timestamp: new Date().toISOString()
            })
          )
        }
      }, 30000)
    }

    websocket.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data)
        if (message?.type === 'notification.new' && message?.data) {
          notificationStore.handleNewCenterNotification(message.data)
        }
      } catch {
        // ignore
      }
    }

    websocket.onerror = () => {
      // ignore, onclose will handle state
    }

    websocket.onclose = () => {
      notificationStore.setWsConnected(false)
      if (heartbeatTimer) {
        window.clearInterval(heartbeatTimer)
        heartbeatTimer = null
      }
      websocket = null
    }
  }

  const disconnect = () => {
    if (heartbeatTimer) {
      window.clearInterval(heartbeatTimer)
      heartbeatTimer = null
    }
    if (websocket) {
      websocket.close()
      websocket = null
    }
    notificationStore.setWsConnected(false)
  }

  return { connect, disconnect }
}


