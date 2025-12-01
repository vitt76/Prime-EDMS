import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useNotificationStore, type Notification } from '@/stores/notificationStore'

describe('notificationStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('initializes with default state', () => {
    const store = useNotificationStore()
    
    expect(store.notifications).toEqual([])
    expect(store.wsConnected).toBe(false)
    expect(store.unreadCount).toBe(0)
    expect(store.unreadNotifications).toEqual([])
  })

  it('adds notification successfully', () => {
    const store = useNotificationStore()
    
    const id = store.addNotification({
      type: 'info',
      title: 'Test',
      message: 'Test message'
    })
    
    expect(store.notifications).toHaveLength(1)
    expect(store.notifications[0].id).toBe(id)
    expect(store.notifications[0].type).toBe('info')
    expect(store.notifications[0].title).toBe('Test')
    expect(store.notifications[0].message).toBe('Test message')
    expect(store.notifications[0].read).toBe(false)
    expect(store.notifications[0].timestamp).toBeInstanceOf(Date)
  })

  it('calculates unread count correctly', () => {
    const store = useNotificationStore()
    
    store.addNotification({ type: 'info', title: 'Test 1', message: 'Message 1' })
    store.addNotification({ type: 'success', title: 'Test 2', message: 'Message 2' })
    
    expect(store.unreadCount).toBe(2)
    
    store.markAsRead(store.notifications[0].id)
    
    expect(store.unreadCount).toBe(1)
  })

  it('marks notification as read', () => {
    const store = useNotificationStore()
    
    const id = store.addNotification({
      type: 'info',
      title: 'Test',
      message: 'Test message'
    })
    
    expect(store.notifications[0].read).toBe(false)
    
    store.markAsRead(id)
    
    expect(store.notifications[0].read).toBe(true)
  })

  it('marks all notifications as read', () => {
    const store = useNotificationStore()
    
    store.addNotification({ type: 'info', title: 'Test 1', message: 'Message 1' })
    store.addNotification({ type: 'success', title: 'Test 2', message: 'Message 2' })
    store.addNotification({ type: 'warning', title: 'Test 3', message: 'Message 3' })
    
    expect(store.unreadCount).toBe(3)
    
    store.markAllAsRead()
    
    expect(store.unreadCount).toBe(0)
    expect(store.notifications.every(n => n.read)).toBe(true)
  })

  it('removes notification', () => {
    const store = useNotificationStore()
    
    const id1 = store.addNotification({ type: 'info', title: 'Test 1', message: 'Message 1' })
    const id2 = store.addNotification({ type: 'success', title: 'Test 2', message: 'Message 2' })
    
    expect(store.notifications).toHaveLength(2)
    
    store.removeNotification(id1)
    
    expect(store.notifications).toHaveLength(1)
    expect(store.notifications[0].id).toBe(id2)
  })

  it('clears all notifications', () => {
    const store = useNotificationStore()
    
    store.addNotification({ type: 'info', title: 'Test 1', message: 'Message 1' })
    store.addNotification({ type: 'success', title: 'Test 2', message: 'Message 2' })
    
    expect(store.notifications).toHaveLength(2)
    
    store.clearAll()
    
    expect(store.notifications).toEqual([])
  })

  it('auto-dismisses success notifications after 5 seconds', () => {
    const store = useNotificationStore()
    
    const id = store.addNotification({
      type: 'success',
      title: 'Test',
      message: 'Test message'
    })
    
    expect(store.notifications).toHaveLength(1)
    
    vi.advanceTimersByTime(5000)
    
    expect(store.notifications).toHaveLength(0)
  })

  it('auto-dismisses info notifications after 5 seconds', () => {
    const store = useNotificationStore()
    
    const id = store.addNotification({
      type: 'info',
      title: 'Test',
      message: 'Test message'
    })
    
    expect(store.notifications).toHaveLength(1)
    
    vi.advanceTimersByTime(5000)
    
    expect(store.notifications).toHaveLength(0)
  })

  it('does not auto-dismiss error notifications', () => {
    const store = useNotificationStore()
    
    const id = store.addNotification({
      type: 'error',
      title: 'Test',
      message: 'Test message'
    })
    
    expect(store.notifications).toHaveLength(1)
    
    vi.advanceTimersByTime(5000)
    
    expect(store.notifications).toHaveLength(1)
  })

  it('does not auto-dismiss warning notifications', () => {
    const store = useNotificationStore()
    
    const id = store.addNotification({
      type: 'warning',
      title: 'Test',
      message: 'Test message'
    })
    
    expect(store.notifications).toHaveLength(1)
    
    vi.advanceTimersByTime(5000)
    
    expect(store.notifications).toHaveLength(1)
  })

  it('filters unread notifications correctly', () => {
    const store = useNotificationStore()
    
    const id1 = store.addNotification({ type: 'info', title: 'Test 1', message: 'Message 1' })
    const id2 = store.addNotification({ type: 'success', title: 'Test 2', message: 'Message 2' })
    
    expect(store.unreadNotifications).toHaveLength(2)
    
    store.markAsRead(id1)
    
    expect(store.unreadNotifications).toHaveLength(1)
    expect(store.unreadNotifications[0].id).toBe(id2)
  })

  it('handles notification with action', () => {
    const store = useNotificationStore()
    const handler = vi.fn()
    
    const id = store.addNotification({
      type: 'info',
      title: 'Test',
      message: 'Test message',
      action: {
        label: 'Click me',
        handler
      }
    })
    
    expect(store.notifications[0].action).toBeDefined()
    expect(store.notifications[0].action?.label).toBe('Click me')
    
    store.notifications[0].action?.handler()
    
    expect(handler).toHaveBeenCalled()
  })

  it('connects WebSocket', () => {
    const store = useNotificationStore()
    
    expect(store.wsConnected).toBe(false)
    
    store.connectWebSocket()
    
    expect(store.wsConnected).toBe(true)
  })

  it('disconnects WebSocket', () => {
    const store = useNotificationStore()
    store.wsConnected = true
    
    store.disconnectWebSocket()
    
    expect(store.wsConnected).toBe(false)
  })
})
