import { beforeEach, describe, expect, it, vi } from 'vitest'

const notificationStore = {
  setWsConnected: vi.fn(),
  handleNewCenterNotification: vi.fn()
}

const buildNotificationsWebSocketUrl = vi.fn(() => 'ws://socket.test/ws/notifications/?token=test')

vi.mock('@/stores/notificationStore', () => ({
  useNotificationStore: () => notificationStore
}))

vi.mock('@/utils/constants', () => ({
  buildNotificationsWebSocketUrl
}))

class MockWebSocket {
  static OPEN = 1
  static instances: MockWebSocket[] = []

  readyState = MockWebSocket.OPEN
  onopen: (() => void) | null = null
  onmessage: ((event: { data: string }) => void) | null = null
  onerror: (() => void) | null = null
  onclose: (() => void) | null = null
  send = vi.fn()
  close = vi.fn(() => {
    this.onclose?.()
  })

  constructor(public url: string) {
    MockWebSocket.instances.push(this)
  }
}

describe('useWebSocket', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    MockWebSocket.instances = []
    vi.stubGlobal('WebSocket', MockWebSocket as unknown as typeof WebSocket)
    localStorage.clear()
    localStorage.setItem('auth_token', 'test-token')
    localStorage.setItem('current_organization_id', 'org-1')
  })

  it('builds notification websocket url with token and organization', async () => {
    const { useWebSocket } = await import('@/hooks/useWebSocket')
    const { connect } = useWebSocket()

    connect()

    expect(buildNotificationsWebSocketUrl).toHaveBeenCalledWith(
      'test-token',
      'org-1'
    )
    expect(MockWebSocket.instances[0]?.url).toBe(
      'ws://socket.test/ws/notifications/?token=test'
    )
  })

  it('handles notification payloads and disconnect state', async () => {
    const { useWebSocket } = await import('@/hooks/useWebSocket')
    const { connect, disconnect } = useWebSocket()

    connect()
    const socket = MockWebSocket.instances[0]

    socket.onopen?.()
    expect(notificationStore.setWsConnected).toHaveBeenCalledWith(true)

    socket.onmessage?.({
      data: JSON.stringify({
        type: 'notification.new',
        data: { id: 7, title: 'Hello' }
      })
    })
    expect(notificationStore.handleNewCenterNotification).toHaveBeenCalledWith({
      id: 7,
      title: 'Hello'
    })

    disconnect()
    expect(notificationStore.setWsConnected).toHaveBeenLastCalledWith(false)
  })
})
