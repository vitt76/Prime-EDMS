/**
 * WebSocket service stub for real-time updates
 * This is a placeholder implementation that can be extended with actual WebSocket connection
 */

import { WS_URL } from '@/utils/constants'

type WebSocketEventType =
  | 'comment_added'
  | 'comment_updated'
  | 'comment_deleted'
  | 'asset_updated'
  | 'version_added'
  | 'notification'

type WebSocketEventHandler = (data: unknown) => void

class WebSocketService {
  private ws: WebSocket | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectDelay = 1000
  private eventHandlers: Map<WebSocketEventType, Set<WebSocketEventHandler>> = new Map()
  private isConnecting = false

  /**
   * Connect to WebSocket server
   */
  connect(): void {
    if (this.ws?.readyState === WebSocket.OPEN || this.isConnecting) {
      return
    }

    this.isConnecting = true

    try {
      const wsUrl = WS_URL
      this.ws = new WebSocket(wsUrl)

      this.ws.onopen = () => {
        console.log('WebSocket connected')
        this.isConnecting = false
        this.reconnectAttempts = 0
        this.emit('connected', {})
      }

      this.ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data)
          this.handleMessage(message)
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error)
        }
      }

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error)
        this.isConnecting = false
      }

      this.ws.onclose = () => {
        console.log('WebSocket disconnected')
        this.isConnecting = false
        this.ws = null
        this.emit('disconnected', {})

        // Attempt to reconnect
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
          this.reconnectAttempts++
          setTimeout(() => {
            this.connect()
          }, this.reconnectDelay * this.reconnectAttempts)
        }
      }
    } catch (error) {
      console.error('Failed to connect WebSocket:', error)
      this.isConnecting = false
    }
  }

  /**
   * Disconnect from WebSocket server
   */
  disconnect(): void {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
    this.reconnectAttempts = this.maxReconnectAttempts // Prevent reconnection
  }

  /**
   * Subscribe to an event type
   */
  on(eventType: WebSocketEventType, handler: WebSocketEventHandler): () => void {
    if (!this.eventHandlers.has(eventType)) {
      this.eventHandlers.set(eventType, new Set())
    }
    this.eventHandlers.get(eventType)!.add(handler)

    // Return unsubscribe function
    return () => {
      this.off(eventType, handler)
    }
  }

  /**
   * Unsubscribe from an event type
   */
  off(eventType: WebSocketEventType, handler: WebSocketEventHandler): void {
    const handlers = this.eventHandlers.get(eventType)
    if (handlers) {
      handlers.delete(handler)
    }
  }

  /**
   * Subscribe to asset-specific events (e.g., comments for a specific asset)
   */
  subscribeToAsset(assetId: number): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(
        JSON.stringify({
          type: 'subscribe',
          channel: `asset:${assetId}`
        })
      )
    }
  }

  /**
   * Unsubscribe from asset-specific events
   */
  unsubscribeFromAsset(assetId: number): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(
        JSON.stringify({
          type: 'unsubscribe',
          channel: `asset:${assetId}`
        })
      )
    }
  }

  /**
   * Handle incoming WebSocket message
   */
  private handleMessage(message: { type: WebSocketEventType; data: unknown }): void {
    const { type, data } = message
    const handlers = this.eventHandlers.get(type)
    if (handlers) {
      handlers.forEach((handler) => {
        try {
          handler(data)
        } catch (error) {
          console.error(`Error in WebSocket event handler for ${type}:`, error)
        }
      })
    }
  }

  /**
   * Emit a local event (for testing/stubbing)
   */
  private emit(type: WebSocketEventType | 'connected' | 'disconnected', data: unknown): void {
    if (type === 'connected' || type === 'disconnected') {
      // These are internal events, not forwarded
      return
    }
    this.handleMessage({ type, data })
  }

  /**
   * Check if WebSocket is connected
   */
  get isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN || false
  }

  /**
   * Simulate a WebSocket event (for testing/stubbing when WebSocket is not available)
   */
  simulateEvent(type: WebSocketEventType, data: unknown): void {
    this.handleMessage({ type, data })
  }
}

export const websocketService = new WebSocketService()

// Auto-connect on import (optional - can be controlled manually)
// websocketService.connect()

