# API Reference

## Base URL
`http://localhost:8000`

## Authentication
None required for MVP

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
