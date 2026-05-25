/**
 * WebSocket Client Utilities
 * Frontend client for connecting to real-time WebSocket endpoints
 */

export class RecommendationEngineWebSocket {
  private baseUrl: string;
  private userWebSockets: Map<string, WebSocket> = new Map();
  private globalWebSockets: Map<string, WebSocket> = new Map();
  private messageHandlers: Map<string, (data: any) => void> = new Map();
  private reconnectAttempts: Map<string, number> = new Map();
  private maxReconnectAttempts = 5;
  private reconnectDelay = 3000;

  constructor(baseUrl: string = 'http://localhost:8000') {
    this.baseUrl = baseUrl.replace('http', 'ws');
  }

  /**
   * Subscribe to user notifications
   * @param userId - User ID
   * @param onMessage - Callback for notification messages
   */
  subscribeToNotifications(
    userId: string,
    onMessage: (notification: any) => void
  ): void {
    const url = `${this.baseUrl}/ws/notifications/${userId}`;
    this.connectWebSocket(
      `notifications-${userId}`,
      url,
      onMessage,
      'user',
      userId
    );
  }

  /**
   * Subscribe to trending topics updates
   * @param onMessage - Callback for trending messages
   */
  subscribeToTrending(onMessage: (trending: any) => void): void {
    const url = `${this.baseUrl}/ws/trending`;
    this.connectWebSocket('trending', url, onMessage, 'global');
  }

  /**
   * Subscribe to feed updates
   * @param userId - User ID
   * @param onMessage - Callback for feed messages
   */
  subscribeToFeed(
    userId: string,
    onMessage: (feed: any) => void
  ): void {
    const url = `${this.baseUrl}/ws/feed/${userId}`;
    this.connectWebSocket(
      `feed-${userId}`,
      url,
      onMessage,
      'user',
      userId
    );
  }

  /**
   * Subscribe to engagement updates for a tweet
   * @param tweetId - Tweet ID
   * @param onMessage - Callback for engagement messages
   */
  subscribeToEngagement(
    tweetId: string,
    onMessage: (engagement: any) => void
  ): void {
    const url = `${this.baseUrl}/ws/engagement/${tweetId}`;
    this.connectWebSocket(
      `engagement-${tweetId}`,
      url,
      onMessage,
      'global'
    );
  }

  /**
   * Connect to WebSocket endpoint with auto-reconnect
   */
  private connectWebSocket(
    key: string,
    url: string,
    onMessage: (data: any) => void,
    type: 'user' | 'global',
    userId?: string
  ): void {
    try {
      const ws = new WebSocket(url);

      ws.onopen = () => {
        console.log(`[WebSocket] Connected to ${key}`);
        this.reconnectAttempts.set(key, 0);

        // Send initial ping to keep connection alive
        this.startHeartbeat(ws, key);
      };

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log(`[WebSocket] Message from ${key}:`, data);
        onMessage(data);
      };

      ws.onerror = (error) => {
        console.error(`[WebSocket] Error in ${key}:`, error);
      };

      ws.onclose = () => {
        console.log(`[WebSocket] Disconnected from ${key}`);
        this.attemptReconnect(key, url, onMessage, type, userId);
      };

      // Store WebSocket reference
      if (type === 'user' && userId) {
        this.userWebSockets.set(key, ws);
      } else {
        this.globalWebSockets.set(key, ws);
      }

      this.messageHandlers.set(key, onMessage);
    } catch (error) {
      console.error(`[WebSocket] Failed to connect to ${key}:`, error);
    }
  }

  /**
   * Attempt to reconnect with exponential backoff
   */
  private attemptReconnect(
    key: string,
    url: string,
    onMessage: (data: any) => void,
    type: 'user' | 'global',
    userId?: string
  ): void {
    const attempts = this.reconnectAttempts.get(key) || 0;

    if (attempts < this.maxReconnectAttempts) {
      const delay = this.reconnectDelay * Math.pow(2, attempts);
      console.log(
        `[WebSocket] Reconnecting to ${key} in ${delay}ms (attempt ${attempts + 1})`
      );

      setTimeout(() => {
        this.reconnectAttempts.set(key, attempts + 1);
        this.connectWebSocket(key, url, onMessage, type, userId);
      }, delay);
    } else {
      console.error(
        `[WebSocket] Max reconnection attempts reached for ${key}`
      );
    }
  }

  /**
   * Start heartbeat to keep connection alive
   */
  private startHeartbeat(ws: WebSocket, key: string): void {
    const interval = setInterval(() => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send('ping');
      } else {
        clearInterval(interval);
      }
    }, 30000); // Send ping every 30 seconds
  }

  /**
   * Unsubscribe from a WebSocket connection
   */
  unsubscribe(key: string): void {
    const userWs = this.userWebSockets.get(key);
    const globalWs = this.globalWebSockets.get(key);

    if (userWs) {
      userWs.close();
      this.userWebSockets.delete(key);
    }

    if (globalWs) {
      globalWs.close();
      this.globalWebSockets.delete(key);
    }

    this.messageHandlers.delete(key);
    this.reconnectAttempts.delete(key);
    console.log(`[WebSocket] Unsubscribed from ${key}`);
  }

  /**
   * Unsubscribe from all connections
   */
  unsubscribeAll(): void {
    this.userWebSockets.forEach((ws) => ws.close());
    this.globalWebSockets.forEach((ws) => ws.close());
    this.userWebSockets.clear();
    this.globalWebSockets.clear();
    this.messageHandlers.clear();
    this.reconnectAttempts.clear();
    console.log('[WebSocket] Unsubscribed from all connections');
  }

  /**
   * Get connection statistics from server
   */
  async getStats(): Promise<any> {
    const response = await fetch(`${this.baseUrl.replace('ws', 'http')}/ws/stats`);
    return response.json();
  }
}

/**
 * Example usage:
 *
 * const ws = new RecommendationEngineWebSocket();
 *
 * // Subscribe to notifications
 * ws.subscribeToNotifications('user_1', (notification) => {
 *   console.log('New notification:', notification);
 *   // Update UI with notification
 * });
 *
 * // Subscribe to trending topics
 * ws.subscribeToTrending((trending) => {
 *   console.log('Trending updated:', trending);
 *   // Update trending topics in UI
 * });
 *
 * // Subscribe to feed updates
 * ws.subscribeToFeed('user_1', (feed) => {
 *   console.log('New feed items:', feed);
 *   // Add new tweets to feed
 * });
 *
 * // Subscribe to engagement updates
 * ws.subscribeToEngagement('tweet_1', (engagement) => {
 *   console.log('Engagement updated:', engagement);
 *   // Update engagement counts in UI
 * });
 *
 * // Get connection stats
 * const stats = await ws.getStats();
 * console.log('WebSocket stats:', stats);
 *
 * // Unsubscribe
 * ws.unsubscribe('notifications-user_1');
 * ws.unsubscribeAll();
 */
