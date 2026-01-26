# WebSocket Real-Time Updates Documentation

## Overview

The recommendation engine now supports real-time bidirectional communication via WebSockets. This enables:

- **Live Notifications**: Users receive notifications instantly when others engage with their tweets
- **Trending Updates**: Real-time changes to trending topics and discourse metrics
- **Feed Updates**: New tweets appear in the feed without polling
- **Engagement Updates**: Live engagement metrics (likes, replies, retweets) for tweets
- **Typing Indicators**: Show when users are composing tweets

## Architecture

### Backend Components

**WebSocket Manager** (`backend/routes/websocket_manager.py`):
- Manages active WebSocket connections
- Maintains connection pools per user and for global broadcasts
- Handles connection lifecycle (connect, disconnect)
- Broadcasts messages to single users or all connected clients

**WebSocket Routes** (`backend/routes/websocket_routes.py`):
- 4 WebSocket endpoints for different event types
- 1 REST endpoint for connection statistics
- Auto-reconnection support (handled client-side)
- Heartbeat mechanism (ping/pong)

**Broadcasting Utilities** (`backend/routes/websocket_broadcast.py`):
- Async helper functions to emit events
- Wrapper around WebSocketManager for easy integration
- Error handling and logging

### Frontend Components

**WebSocket Client** (`frontend/lib/websocket-client.ts`):
- TypeScript client for connecting to WebSocket endpoints
- Automatic reconnection with exponential backoff
- Heartbeat to keep connections alive
- Message routing and handler management

**React Hooks** (`frontend/lib/use-websocket.ts`):
- `useNotifications()` - Subscribe to engagement notifications
- `useTrending()` - Subscribe to trending topics updates
- `useFeedUpdates()` - Subscribe to new feed items
- `useEngagementUpdates()` - Subscribe to engagement changes

## WebSocket Endpoints

### 1. User Notifications Endpoint
```
ws://localhost:8000/ws/notifications/{user_id}
```

**Purpose**: Receive real-time notifications when other users engage with your tweets

**Message Format**:
```json
{
  "type": "notification",
  "timestamp": "2026-01-25T10:30:00",
  "data": {
    "notification_id": "n1",
    "type": "LIKE|REPLY|RETWEET|FOLLOW|MENTION",
    "actor_id": "user_2",
    "actor_name": "Jane Investor",
    "tweet_id": "t1",
    "created_at": "2026-01-25T10:30:00"
  }
}
```

**Notification Types**:
- `LIKE`: Another user liked your tweet
- `REPLY`: Another user replied to your tweet
- `RETWEET`: Another user retweeted your tweet
- `FOLLOW`: Another user started following you
- `MENTION`: Another user mentioned you in a tweet

**Backend Integration**:
```python
# In notification_routes.py or wherever notifications are created
from routes.websocket_broadcast import broadcast_notification

# When a notification is created
notification = notification_manager.add_notification(
    user_id="user_1",
    actor_id="user_2",
    actor_name="Jane",
    notification_type=NotificationType.LIKE,
    tweet_id="t1"
)

# Broadcast it via WebSocket
await broadcast_notification(user_id="user_1", notification_data={
    "notification_id": notification.notification_id,
    "type": notification.type.value,
    "actor_id": notification.actor_id,
    "actor_name": notification.actor_name,
    "tweet_id": notification.tweet_id
})
```

### 2. Trending Topics Endpoint
```
ws://localhost:8000/ws/trending
```

**Purpose**: Receive real-time updates about trending topics and discourse patterns

**Message Format**:
```json
{
  "type": "trending",
  "timestamp": "2026-01-25T10:30:00",
  "data": {
    "topics": [
      {
        "topic": "AI",
        "tweet_count": 250,
        "engagement_score": 8.7,
        "growth_rate": 0.15
      },
      {
        "topic": "Startups",
        "tweet_count": 180,
        "engagement_score": 7.2,
        "growth_rate": 0.08
      }
    ],
    "count": 10
  }
}
```

**Backend Integration**:
```python
# Periodically update trending topics (e.g., in a background task)
from routes.websocket_broadcast import broadcast_trending_update

# Get trending topics
trending_topics = get_trending_topics()

# Broadcast to all connected clients
await broadcast_trending_update(trending_topics)
```

### 3. Feed Updates Endpoint
```
ws://localhost:8000/ws/feed/{user_id}
```

**Purpose**: Receive new tweets in real-time for the user's feed

**Message Format**:
```json
{
  "type": "feed_update",
  "timestamp": "2026-01-25T10:30:00",
  "data": {
    "tweets": [
      {
        "tweet_id": "t1",
        "author_id": "a1",
        "content": "Just closed a Series A round...",
        "topics": ["Fundraising", "Startups"],
        "engagement": {
          "likes": 45,
          "replies": 3,
          "retweets": 8
        },
        "created_at": "2026-01-25T10:30:00"
      }
    ],
    "count": 1
  }
}
```

**Backend Integration**:
```python
# When a new tweet is created
from routes.websocket_broadcast import broadcast_feed_update

new_tweet = create_tweet(...)

# Broadcast to all followers
followers = get_user_followers(author_id)
for follower_id in followers:
    await broadcast_feed_update(follower_id, [new_tweet])
```

### 4. Engagement Updates Endpoint
```
ws://localhost:8000/ws/engagement/{tweet_id}
```

**Purpose**: Track real-time engagement metrics for a specific tweet

**Message Format**:
```json
{
  "type": "engagement_update",
  "timestamp": "2026-01-25T10:30:00",
  "data": {
    "tweet_id": "t1",
    "engagement": {
      "likes": 152,
      "replies": 13,
      "retweets": 45,
      "bookmarks": 8
    }
  }
}
```

**Backend Integration**:
```python
# When engagement happens (like, reply, etc.)
from routes.websocket_broadcast import broadcast_engagement_update

# Record engagement
record_engagement(user_id, tweet_id, "like")

# Get updated engagement
engagement = get_tweet_engagement(tweet_id)

# Broadcast update
await broadcast_engagement_update(tweet_id, engagement)
```

## Frontend Usage

### TypeScript Client Example

```typescript
import { RecommendationEngineWebSocket } from '@/lib/websocket-client';

const ws = new RecommendationEngineWebSocket('http://localhost:8000');

// Subscribe to notifications
ws.subscribeToNotifications('user_1', (message) => {
  console.log('New notification:', message);
  // Update UI
});

// Subscribe to trending
ws.subscribeToTrending((message) => {
  console.log('Trending updated:', message.data.topics);
  // Update trending list
});

// Subscribe to feed
ws.subscribeToFeed('user_1', (message) => {
  console.log('New tweets:', message.data.tweets);
  // Add to feed
});

// Subscribe to engagement
ws.subscribeToEngagement('tweet_1', (message) => {
  console.log('Engagement updated:', message.data.engagement);
  // Update engagement counts
});

// Get stats
const stats = await ws.getStats();
console.log('Connected users:', stats.active_users);

// Unsubscribe
ws.unsubscribe('notifications-user_1');
ws.unsubscribeAll(); // Close all connections
```

### React Hook Example

```tsx
import { useNotifications, useTrending, useFeedUpdates, useEngagementUpdates } from '@/lib/use-websocket';

export function NotificationCenter({ userId }: { userId: string }) {
  const { notifications, unreadCount } = useNotifications(userId);

  return (
    <div>
      <h2>Notifications ({unreadCount})</h2>
      <ul>
        {notifications.map((notif) => (
          <li key={notif.notification_id}>
            <strong>{notif.actor_name}</strong> {notif.type}d your tweet
          </li>
        ))}
      </ul>
    </div>
  );
}

export function TrendingWidget() {
  const { trending } = useTrending();

  return (
    <div className="trending-widget">
      <h3>Trending Now</h3>
      {trending.map((topic) => (
        <div key={topic.topic}>
          <strong>{topic.topic}</strong>
          <span>{topic.tweet_count} tweets</span>
        </div>
      ))}
    </div>
  );
}

export function FeedComponent({ userId }: { userId: string }) {
  const { newTweets } = useFeedUpdates(userId);

  return (
    <div>
      {newTweets.length > 0 && (
        <button>Load {newTweets.length} new tweets</button>
      )}
    </div>
  );
}
```

## Connection Management

### Connection Statistics

Get real-time statistics about active WebSocket connections:

```bash
curl http://localhost:8000/ws/stats
```

Response:
```json
{
  "active_users": 5,
  "total_user_connections": 8,
  "global_connections": 3,
  "total_connections": 11
}
```

### Heartbeat Mechanism

The client automatically sends ping messages every 30 seconds to keep the connection alive. The server responds with pong messages.

### Automatic Reconnection

If a connection drops, the client automatically reconnects with exponential backoff:
- 1st attempt: 3 seconds
- 2nd attempt: 6 seconds
- 3rd attempt: 12 seconds
- 4th attempt: 24 seconds
- 5th attempt: 48 seconds
- After 5 attempts, stops reconnecting (can be configured)

## Integration Checklist

### Backend Integration

- [ ] Import WebSocket utilities in relevant modules
- [ ] Call `broadcast_notification()` when notifications are created
- [ ] Call `broadcast_trending_update()` when trending topics change
- [ ] Call `broadcast_feed_update()` when new tweets are published
- [ ] Call `broadcast_engagement_update()` when engagement happens
- [ ] Use `get_websocket_manager()` for custom broadcasts
- [ ] Add error handling and logging

### Frontend Integration

- [ ] Import WebSocket client or hooks
- [ ] Set up subscriptions in components
- [ ] Handle message updates and UI rendering
- [ ] Clean up subscriptions in useEffect cleanup
- [ ] Add loading/error states
- [ ] Test with dev server running

## Performance Considerations

### Scalability

Current implementation:
- In-memory connection tracking (suitable for development/small scale)
- Per-user connection pools
- Global broadcast connections

For production (1000+ concurrent users):
- Consider moving to Redis for distributed broadcast
- Implement room/channel pattern for targeted broadcasts
- Add connection rate limiting
- Monitor memory usage of connection pools

### Message Volume

- Limit trending updates to once per minute
- Batch engagement updates (e.g., every 5 seconds)
- Filter notifications by user subscriptions
- Compress message payloads

## Error Handling

All broadcasting functions include try-catch blocks and logging:

```python
try:
    await broadcast_notification(user_id, notification_data)
except Exception as e:
    logger.error(f"Failed to broadcast: {e}")
    # Don't crash the main request - logging is sufficient
```

Frontend client auto-reconnects on disconnect with exponential backoff.

## Testing

### Test WebSocket Connection

```bash
# Start server
cd backend && python -m uvicorn main:app --reload

# Test with websocat
websocat ws://localhost:8000/ws/trending

# Or Python:
python -c "
import asyncio
import websockets
import json

async def test():
    async with websockets.connect('ws://localhost:8000/ws/trending') as ws:
        await ws.send('ping')
        msg = await ws.recv()
        print(f'Received: {msg}')

asyncio.run(test())
"
```

## Next Steps

1. **Integrate broadcasting into existing endpoints**
   - Modify notification creation to broadcast
   - Add periodic trending updates task
   - Hook into tweet creation/engagement endpoints

2. **Frontend component implementation**
   - Create real-time notification panel
   - Add trending topics widget
   - Implement live feed updates
   - Show engagement counters

3. **Production hardening**
   - Add Redis for distributed broadcasts
   - Implement room/channel pattern
   - Add connection pooling and limits
   - Monitor and alert on connection issues

4. **Testing**
   - Unit tests for WebSocket manager
   - Integration tests for broadcasting
   - Load testing with multiple connections
   - End-to-end tests with frontend

## Files Changed

**New Files**:
- `backend/routes/websocket_manager.py` - Connection management
- `backend/routes/websocket_routes.py` - WebSocket endpoints
- `backend/routes/websocket_broadcast.py` - Broadcasting utilities
- `frontend/lib/websocket-client.ts` - TypeScript client
- `frontend/lib/use-websocket.ts` - React hooks

**Modified Files**:
- `backend/main.py` - Integrated WebSocket router
- `docs/API_REFERENCE.md` - Added WebSocket documentation

## Status

✅ **WebSocket infrastructure complete and ready for integration**

Next: Hook into existing features to actually emit events
