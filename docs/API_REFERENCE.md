# API Reference

## Base URL
`http://localhost:8000`

## Authentication
None required for MVP

## Quick Overview

**Total Endpoints: 70+** across 9 feature categories
- Original Features: 30+ endpoints (ranking, users, tweets, agents, exploration)
- New Features: 30+ endpoints (trending, search, notifications, conversations, profiles, experiments)
- Real-Time Updates: 5+ WebSocket endpoints and 1 stats endpoint

---

## Endpoints

### Ranking

#### Get Ranked Feed
```
POST /rank
```

Request:
```json
{
  "user_id": "user_0",
  "limit": 20
}
```

Response:
```json
[
  {
    "tweet": {
      "tweet_id": "t1",
      "author_id": "a1",
      "content": "...",
      "topics": ["AI", "Startup"],
      "engagement": {
        "likes": 100,
        "retweets": 20,
        "replies": 5
      },
      "quality_score": 0.85,
      "created_at": "2026-01-25T00:00:00"
    },
    "explanation": {
      "total_score": 0.89,
      "recency_score": 0.9,
      "popularity_score": 0.85,
      "quality_score": 0.85,
      "topic_relevance_score": 0.92,
      "key_factors": [
        "Recent content",
        "Strong match to interests"
      ]
    },
    "rank": 1
  }
]
```

### Users

#### List Users
```
GET /users
```

Response:
```json
[
  {
    "id": "user_0",
    "username": "venture_capitalist_1",
    "name": "Venture Capitalist",
    "interests": ["AI", "Startups", "Fundraising"],
    "expertise_areas": ["Due Diligence", "Valuation"]
  }
]
```

#### Get User Weights
```
GET /users/{user_id}/weights
```

Response:
```json
{
  "weights": {
    "recency": 0.2,
    "popularity": 0.25,
    "quality": 0.2,
    "topic_relevance": 0.25
  }
}
```

#### Update User Weights
```
POST /users/{user_id}/weights
```

Request:
```json
{
  "user_id": "user_0",
  "weights": {
    "recency": 0.3,
    "popularity": 0.2,
    "quality": 0.2,
    "topic_relevance": 0.3
  }
}
```

Response:
```json
{
  "success": true,
  "weights": {
    "recency": 0.3,
    "popularity": 0.2,
    "quality": 0.2,
    "topic_relevance": 0.3
  }
}
```

### Tweet Generation

#### Generate Tweets
```
POST /api/generate-tweets
```

Request:
```json
{
  "persona_type": "venture_capitalist",
  "num_tweets": 10,
  "batch_size": 5
}
```

Response:
```json
{
  "tweets": [
    {
      "content": "Just invested in an AI startup...",
      "topics": ["AI", "Startups"]
    }
  ],
  "count": 10,
  "persona_type": "venture_capitalist"
}
```

### Agents

#### Register Agent
```
POST /api/agents/register
```

Request:
```json
{
  "user_id": "agent_1",
  "name": "Agent Name",
  "persona_type": "venture_capitalist",
  "interests": ["AI", "Startups"],
  "expertise": ["Due Diligence"]
}
```

Response:
```json
{
  "success": true,
  "agent_id": "agent_1"
}
```

#### List Agents
```
GET /api/agents/list
```

Response:
```json
[
  {
    "user_id": "agent_1",
    "name": "Agent Name",
    "persona_type": "venture_capitalist",
    "total_engagements": 45
  }
]
```

#### Get Agent Stats
```
GET /api/agents/{user_id}/stats
```

Response:
```json
{
  "user_id": "agent_1",
  "user_name": "Agent Name",
  "total_engagements": 45,
  "engagement_counts": {
    "like": 30,
    "reply": 10,
    "retweet": 5,
    "bookmark": 0
  },
  "average_confidence": 0.78,
  "interests": ["AI", "Startups"]
}
```

#### Run Agentic Loop
```
POST /api/agents/run-loop
```

Request:
```json
{
  "num_cycles": 2,
  "max_engagements_per_check": 5
}
```

Response:
```json
{
  "success": true,
  "cycles_run": 2,
  "total_decisions": 48
}
```

### Exploration Statistics

#### Get Exploration Stats
```
GET /api/exploration/stats
```

Response:
```json
{
  "total_authors_tracked": 42,
  "average_engagement_rate": 0.68,
  "engagement_rate_std": 0.15,
  "exploration_rate": 0.10,
  "strategy_used": "thompson_sampling"
}
```

#### Record Engagement
```
POST /api/exploration/engagement
```

Request:
```json
{
  "tweet_id": "t1",
  "author_id": "a1",
  "engagement_type": "like"
}
```
---

## NEW FEATURES (30+ Endpoints)

### Trending Topics & Analytics (`/api/trending`)

#### Get Trending Topics
```
GET /api/trending/topics
```

Query Parameters:
- `hours` (1-720): Time window for trending calculation (default: 24)
- `limit` (1-50): Max topics to return (default: 10)
- `min_tweets` (optional): Min tweets threshold for a topic

Response:
```json
[
  {
    "topic": "AI",
    "tweet_count": 245,
    "engagement_score": 8.5,
    "growth_rate": 0.15,
    "top_authors": ["author_1", "author_2"]
  }
]
```

#### Get Discourse Metrics
```
GET /api/trending/discourse-metrics
```

Returns current state of discourse with distribution analysis:

Response:
```json
{
  "total_tweets": 1000,
  "average_engagement": 4.2,
  "top_topics": ["AI", "Startups", "Funding"],
  "topic_distribution": {
    "AI": 0.35,
    "Startups": 0.28,
    "Funding": 0.15
  },
  "diversity_index": 0.78
}
```

#### Compare Discourse Scenarios
```
GET /api/trending/discourse-compare
```

Query Parameters:
- `scenario1` (optional): Weight config 1 (recency, popularity, quality, relevance)
- `scenario2` (optional): Weight config 2

Compares how different ranking weights affect discourse patterns.

---

### Search Functionality (`/api/search`)

#### Search Tweets
```
GET /api/search/tweets
```

Query Parameters:
- `q` (required): Search query
- `limit` (1-100): Results to return (default: 20)
- `sort`: "relevance" or "recent" (default: relevance)

Response:
```json
[
  {
    "tweet_id": "t1",
    "content": "AI is transforming...",
    "author_id": "a1",
    "relevance_score": 0.92,
    "engagement": {
      "likes": 150,
      "retweets": 45,
      "replies": 12
    }
  }
]
```

#### Search Users
```
GET /api/search/users
```

Query Parameters:
- `q` (required): Search query (username, interests, expertise)
- `limit` (1-50): Results to return (default: 10)

Response:
```json
[
  {
    "user_id": "user_1",
    "username": "investor_john",
    "name": "John Investor",
    "interests": ["AI", "Startups"],
    "expertise_areas": ["Fundraising", "Due Diligence"],
    "relevance_score": 0.85
  }
]
```

#### Trending Search Terms
```
GET /api/search/trending-search
```

Query Parameters:
- `hours` (optional): Time window (default: 24)
- `limit` (optional): Top N terms (default: 20)

Response:
```json
{
  "trending_terms": ["AI startup", "fundraising", "due diligence", "series A"],
  "search_volume": [120, 95, 78, 65]
}
```

---

### Notifications System (`/api/notifications`)

#### Get User Notifications
```
GET /api/notifications/{user_id}
```

Query Parameters:
- `unread_only` (boolean): Filter unread only (default: false)
- `limit` (1-100): Results per page (default: 20)
- `offset` (integer): Pagination offset (default: 0)

Response:
```json
[
  {
    "notification_id": "n1",
    "type": "LIKE",
    "actor_id": "user_2",
    "actor_name": "Jane Investor",
    "tweet_id": "t1",
    "created_at": "2026-01-25T10:30:00",
    "read": false
  }
]
```

#### Mark Notification as Read
```
POST /api/notifications/{notification_id}/read
```

Response:
```json
{
  "success": true,
  "notification_id": "n1"
}
```

#### Mark All Notifications as Read
```
POST /api/notifications/{user_id}/read-all
```

Response:
```json
{
  "success": true,
  "marked_read": 5
}
```

#### Get Notification Statistics
```
GET /api/notifications/{user_id}/stats
```

Response:
```json
{
  "total_unread": 12,
  "breakdown": {
    "LIKE": 8,
    "REPLY": 3,
    "RETWEET": 1,
    "FOLLOW": 0,
    "MENTION": 0
  }
}
```

---

### Conversation Threading (`/api/conversations`)

#### Get Thread (Nested)
```
GET /api/conversations/{tweet_id}/thread
```

Query Parameters:
- `max_depth` (1-20): Maximum thread depth (default: 5)

Returns nested conversation tree:

Response:
```json
{
  "tweet_id": "t1",
  "content": "Original tweet...",
  "author_id": "a1",
  "replies": [
    {
      "tweet_id": "t2",
      "content": "Reply to t1...",
      "author_id": "a2",
      "replies": [
        {
          "tweet_id": "t3",
          "content": "Reply to t2...",
          "author_id": "a3",
          "replies": []
        }
      ]
    }
  ]
}
```

#### Get Conversation Chain (Linear)
```
GET /api/conversations/{tweet_id}/chain
```

Returns linear path from root to current tweet:

Response:
```json
{
  "chain": [
    {"tweet_id": "t1", "author_id": "a1", "content": "Original..."},
    {"tweet_id": "t2", "author_id": "a2", "content": "Reply 1..."},
    {"tweet_id": "t3", "author_id": "a3", "content": "Reply 2..."}
  ]
}
```

#### Get Direct Replies
```
GET /api/conversations/{tweet_id}/replies
```

Query Parameters:
- `sort`: "recent" or "engagement" (default: recent)
- `limit` (1-100): Results (default: 20)

Response:
```json
[
  {
    "tweet_id": "t2",
    "author_id": "a2",
    "content": "Direct reply...",
    "engagement": {"likes": 10, "replies": 2}
  }
]
```

#### Get Root Tweet
```
GET /api/conversations/{tweet_id}/root
```

Returns the original tweet in the conversation:

Response:
```json
{
  "tweet_id": "t1",
  "author_id": "a1",
  "content": "Original tweet...",
  "depth_to_root": 3
}
```

---

### Profile Pages (`/api/profiles`)

#### Get User Profile
```
GET /api/profiles/{user_id}
```

Response:
```json
{
  "user_id": "user_1",
  "username": "investor_john",
  "name": "John Investor",
  "bio": "VC investor focused on AI/ML startups",
  "interests": ["AI", "Startups", "Fundraising"],
  "expertise_areas": ["Due Diligence", "Valuation"],
  "followers_count": 1250,
  "following_count": 340,
  "total_tweets": 450,
  "engagement_stats": {
    "likes_received": 5600,
    "replies_received": 340,
    "retweets_received": 890
  }
}
```

#### Get User Statistics
```
GET /api/profiles/{user_id}/stats
```

Response:
```json
{
  "user_id": "user_1",
  "total_tweets": 450,
  "average_engagement": 3.2,
  "most_engaged_topics": ["AI", "Startups"],
  "engagement_breakdown": {
    "likes": 5600,
    "replies": 340,
    "retweets": 890,
    "bookmarks": 120
  }
}
```

#### Get User's Tweets
```
GET /api/profiles/{user_id}/tweets
```

Query Parameters:
- `sort`: "recent" or "engagement" (default: recent)
- `limit` (1-100): Results (default: 20)
- `offset` (integer): Pagination (default: 0)

Response:
```json
[
  {
    "tweet_id": "t1",
    "content": "Tweet content...",
    "created_at": "2026-01-25T10:30:00",
    "engagement": {"likes": 45, "replies": 3, "retweets": 8}
  }
]
```

#### Get Following List
```
GET /api/profiles/{user_id}/following
```

Query Parameters:
- `limit` (1-100): Results (default: 20)
- `offset` (integer): Pagination (default: 0)

Response:
```json
[
  {
    "user_id": "user_2",
    "username": "investor_jane",
    "name": "Jane Investor",
    "interests": ["AI", "Blockchain"]
  }
]
```

#### Get Followers List
```
GET /api/profiles/{user_id}/followers
```

Query Parameters: Same as following list

Response: Same as following list

---

### A/B Testing Framework (`/api/experiments`)

#### Create Experiment
```
POST /api/experiments/create
```

Request:
```json
{
  "name": "Recency Boost Test",
  "description": "Test increasing recency weight",
  "control_weights": {
    "recency": 0.2,
    "popularity": 0.25,
    "quality": 0.2,
    "topic_relevance": 0.35
  },
  "treatment_weights": {
    "recency": 0.5,
    "popularity": 0.15,
    "quality": 0.15,
    "topic_relevance": 0.2
  },
  "split_ratio": 0.5
}
```

Response:
```json
{
  "experiment_id": "exp_1",
  "name": "Recency Boost Test",
  "status": "created"
}
```

#### Start Experiment
```
POST /api/experiments/{exp_id}/start
```

Response:
```json
{
  "success": true,
  "experiment_id": "exp_1",
  "status": "running"
}
```

#### End Experiment
```
POST /api/experiments/{exp_id}/end
```

Response:
```json
{
  "success": true,
  "experiment_id": "exp_1",
  "status": "ended"
}
```

#### Get Experiment Details
```
GET /api/experiments/{exp_id}
```

Response:
```json
{
  "experiment_id": "exp_1",
  "name": "Recency Boost Test",
  "status": "running",
  "created_at": "2026-01-25T10:00:00",
  "started_at": "2026-01-25T10:05:00",
  "control_weights": {...},
  "treatment_weights": {...}
}
```

#### List Experiments
```
GET /api/experiments/
```

Query Parameters:
- `status` (optional): "created", "running", "ended"
- `limit` (1-100): Results (default: 20)

Response:
```json
[
  {
    "experiment_id": "exp_1",
    "name": "Recency Boost Test",
    "status": "running",
    "created_at": "2026-01-25T10:00:00"
  }
]
```

#### Record Experiment Results
```
POST /api/experiments/{exp_id}/results
```

Request:
```json
{
  "control_metrics": {
    "avg_engagement": 4.5,
    "diversity_index": 0.75,
    "total_impressions": 50000
  },
  "treatment_metrics": {
    "avg_engagement": 4.8,
    "diversity_index": 0.72,
    "total_impressions": 50000
  }
}
```

Response:
```json
{
  "success": true,
  "experiment_id": "exp_1",
  "winner": "treatment",
  "significance": 0.85,
  "improvement": "6.7%"
}
```

#### Get Experiment Results
```
GET /api/experiments/{exp_id}/results
```

Response: Same as record results response

#### List Experiment Templates
```
GET /api/experiments/templates/list
```

Response:
```json
[
  {
    "key": "recency_boost",
    "name": "Recency Boost",
    "description": "Test increasing recency weight to surface fresher content"
  },
  {
    "key": "popularity_boost",
    "name": "Popularity Boost",
    "description": "Test increasing popularity weight to favor trending content"
  },
  {
    "key": "quality_focus",
    "name": "Quality Focus",
    "description": "Test increasing quality weight to emphasize well-written tweets"
  },
  {
    "key": "diversity_focus",
    "name": "Diversity Focus",
    "description": "Test algorithms that maximize topic diversity"
  }
]
```

#### Create Experiment from Template
```
POST /api/experiments/templates/{key}/create
```

Request:
```json
{
  "name": "Q1 Recency Test",
  "split_ratio": 0.5
}
```

Response:
```json
{
  "experiment_id": "exp_2",
  "name": "Q1 Recency Test",
  "template": "recency_boost",
  "status": "created"
}
```

---

### Spam Detection & Safety

Integrated into the ranking pipeline. Applied automatically to all ranked content.

**How it works:**
- Analyzes content before ranking
- Classifies as SAFE, WARNING, SPAM, or HARMFUL
- Applies moderation multiplier (0.0-1.0) to reduce ranking of problematic content
- Prevents spam/harmful content from dominating feed

**Detection signals:**
- Spam keywords and patterns
- Excessive capitalization
- Repeated punctuation
- Suspicious link patterns
- Harmful language and threats

**Use in `/rank` endpoint:**
- Spam/harmful content receives lower scores
- Moderation multiplier embedded in explanation

---


Response:
```json
{
  "success": true
}
```

## Error Handling

All errors return appropriate HTTP status codes:

- 200: Success
- 400: Bad request
- 404: Not found
- 500: Server error

Error response format:
```json
{
  "detail": "Error message describing the issue"
}
```

## Rate Limiting

No rate limiting for MVP. Implement in production if needed.

## Data Types

### Engagement
```json
{
  "likes": 100,
  "retweets": 20,
  "replies": 5,
  "bookmarks": 10
}
```

### User
```json
{
  "id": "user_id",
  "username": "username",
  "name": "Full Name",
  "interests": ["topic1", "topic2"],
  "expertise_areas": ["area1", "area2"],
  "preference_weights": {
    "recency": 0.2,
    "popularity": 0.25,
    "quality": 0.2,
    "topic_relevance": 0.25
  }
}
```

### Tweet
```json
{
  "tweet_id": "t1",
  "author_id": "a1",
  "content": "Tweet content",
  "topics": ["topic1"],
  "engagement": {
    "likes": 100,
    "retweets": 20,
    "replies": 5,
    "bookmarks": 10
  },
  "quality_score": 0.85,
  "created_at": "2026-01-25T00:00:00"
}
```

---

## REAL-TIME UPDATES (WebSocket)

### Overview

WebSocket endpoints enable real-time bidirectional communication for:
- **Notifications**: Receive engagement notifications instantly
- **Trending Topics**: Get live updates on trending content
- **Feed Updates**: New tweets appear without polling
- **Engagement Metrics**: Live engagement counters
- **Typing Indicators**: See when users are composing

### Connection Protocol

All WebSocket connections:
- Accept heartbeat `ping` messages (client sends, server responds with `pong`)
- Auto-reconnect with exponential backoff (client-side)
- Send JSON-formatted messages with `type`, `timestamp`, and `data`
- Maintain connection for push notifications

### WebSocket Endpoints

#### 1. User Notifications
```
WS /ws/notifications/{user_id}
```

Receive real-time notifications when others engage with your tweets.

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
- `LIKE`: User liked your tweet
- `REPLY`: User replied to your tweet
- `RETWEET`: User retweeted your tweet
- `FOLLOW`: User started following you
- `MENTION`: User mentioned you

#### 2. Trending Topics
```
WS /ws/trending
```

Receive live updates about trending topics and discourse patterns.

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

#### 3. Feed Updates
```
WS /ws/feed/{user_id}
```

Receive new tweets in real-time for your feed.

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
        "content": "Just closed a Series A...",
        "topics": ["Fundraising"],
        "engagement": {
          "likes": 45,
          "replies": 3,
          "retweets": 8
        }
      }
    ],
    "count": 1
  }
}
```

#### 4. Engagement Updates
```
WS /ws/engagement/{tweet_id}
```

Track real-time engagement metrics for a specific tweet.

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

#### 5. Typing Indicators
```
WS /ws/typing/{user_id}
```

Broadcast typing status to all connected users.

**Message Format**:
```json
{
  "type": "typing",
  "timestamp": "2026-01-25T10:30:00",
  "data": {
    "user_id": "user_1",
    "typing": true
  }
}
```

### WebSocket Statistics

#### Get Connection Stats
```
GET /ws/stats
```

Returns current WebSocket connection statistics.

Response:
```json
{
  "active_users": 5,
  "total_user_connections": 8,
  "global_connections": 3,
  "total_connections": 11
}
```

**Fields**:
- `active_users`: Number of users with open connections
- `total_user_connections`: Total user-specific (notifications, feed) connections
- `global_connections`: Total global broadcast (trending, engagement) connections
- `total_connections`: Sum of all active connections

### Client Implementation

#### JavaScript Example
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/notifications/user_1');

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  if (message.type === 'notification') {
    console.log('New notification:', message.data);
    // Update UI with notification
  }
};

ws.onclose = () => {
  console.log('Connection closed - auto-reconnect will retry');
};

// Keep connection alive
setInterval(() => {
  if (ws.readyState === WebSocket.OPEN) {
    ws.send('ping');
  }
}, 30000);
```

#### React Hook Example
```tsx
import { useNotifications, useTrending } from '@/lib/use-websocket';

export function Dashboard({ userId }: { userId: string }) {
  const { notifications, unreadCount } = useNotifications(userId);
  const { trending } = useTrending();

  return (
    <div>
      <NotificationPanel notifications={notifications} count={unreadCount} />
      <TrendingWidget topics={trending} />
    </div>
  );
}
```

### Connection Management

**Heartbeat**: Client sends `ping` every 30 seconds; server responds with `pong`

**Reconnection**: Automatic with exponential backoff (3s → 6s → 12s → 24s → 48s)

**Max Retries**: 5 attempts (configurable in client)

**Timeout**: No explicit timeout; relies on TCP keepalive and heartbeat

### Error Handling

- Connection errors are logged but don't crash the app
- Failed broadcasts are logged; client auto-reconnects
- All async operations wrapped in try-catch

### Performance Notes

- In-memory connection tracking (suitable for development)
- Per-user connection pools for efficient broadcasting
- Messages sent as JSON (consider compression for production)
- Heartbeat every 30 seconds to detect stale connections

### Production Considerations

For scaling beyond 1000 concurrent users:
- Migrate to Redis pub/sub for distributed broadcasts
- Implement connection pooling and rate limiting
- Add message compression and batching
- Monitor memory usage of connection pools
- Set up alerting for connection anomalies

### See Also

- **WebSocket Documentation**: See [WEBSOCKET.md](WEBSOCKET.md) for detailed implementation guide
- **Frontend Integration**: See `frontend/lib/websocket-client.ts` for TypeScript client
- **React Hooks**: See `frontend/lib/use-websocket.ts` for ready-to-use hooks
````
