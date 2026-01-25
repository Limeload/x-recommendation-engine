# Architecture

## System Components

### Frontend
- Next.js React application
- Real-time feed display with explanations
- Tuning dashboard for weight adjustment
- User selection interface

### Backend
FastAPI server with four main modules:

1. Models
   - schemas.py: Data structures
   - ranking_engine.py: Multi-stage ranking
   - exploration_ranker.py: Exploration-exploitation strategies

2. Database
   - inmemory_db.py: In-memory data storage

3. Simulation
   - langchain_tweet_generator.py: Synthetic content generation
   - agentic_loop.py: Autonomous agent behavior

4. Routes
   - API endpoints for ranking, tuning, agents

### Data Flow

User Request
  -> Ranking Engine (4 stages)
    -> Filter candidates
    -> Score and rank
    -> Apply diversity
    -> Add exploration
  -> Return ranked feed with explanations

## Ranking Pipeline

### Stage 1: Filtering
Remove tweets that don't meet criteria:
- Quality threshold
- Topic inclusion/exclusion
- User filtering

### Stage 2: Scoring
Multi-factor scoring combines:
- Recency Score: e^(-lambda * age_hours)
- Popularity Score: Weighted engagement (likes, retweets, replies)
- Quality Score: Author credibility signal
- Topic Relevance: Jaccard similarity + expertise match

Formula: weighted_score = sum(weight_i * score_i)

### Stage 3: Diversity
Ensures feed variety:
- Max tweets per author (default 3)
- Max tweets per topic (default 5)
- Diversity penalty for unknown authors

### Stage 4: Exploration-Exploitation
Injects discovery into feed using selected strategy.

## Exploration Strategies

### Epsilon-Greedy
Simplest approach:
- Keep top N items (exploitation)
- Randomly select from remaining (exploration)
- No learning or adaptation

Best for: Prototyping, baselines

### Thompson Sampling
Bayesian approach:
- Model author as Beta distribution
- Posterior: Beta(alpha + successes, beta + failures)
- Sample: theta ~ Beta(posterior)
- Score: 0.6 * theta + 0.4 * original_score

Learns from engagement feedback automatically.

Best for: Production systems, learning user preferences

### UCB (Upper Confidence Bound)
Optimistic approach:
- Score = empirical_rate + c * sqrt(ln(n) / N)
- empirical_rate = successes / (successes + failures)
- Confidence bonus decreases as item is exposed
- Automatic exploration decay

Best for: Theoretical optimality, advanced systems

## Autonomous Agents

Agents simulate user behavior:
- Monitor feed independently
- Score tweets using interest vectors
- Make engagement decisions (like, reply, retweet, bookmark)
- Generate LLM-powered replies (optional)

Interest vector scoring: 0.6 * relevance + 0.2 * quality + 0.2 * recency

## Data Models

### User
- id, username, name
- interests: list of topics
- expertise_areas: specialized knowledge
- preference_weights: ranking tuning parameters

### Tweet
- tweet_id, author_id, content
- topics: list of topics
- engagement: likes, retweets, replies, bookmarks
- quality_score: content quality signal
- created_at: timestamp

### RankedTweet
- tweet: Tweet object
- explanation: RankingExplanation
- rank: position in feed

### RankingExplanation
- total_score: combined ranking score
- Component scores and weights
- key_factors: human-readable reasons

## Integration Points

### Frontend-Backend
REST API over HTTP:
- POST /rank: Get ranked feed
- POST /users/{user_id}/weights: Update weights
- GET /users: List users

### Agent-Ranking
Agents read from ranking engine:
- Query feed
- Record engagement
- Improve ranking over time

### Learning Loop
Engagement recording improves future rankings:
- User engages with exploratory item
- Feedback recorded
- Thompson/UCB updates beliefs
- Next ranking adapted

## Performance Characteristics

### Memory
- Thompson Sampling: ~200 bytes per author
- UCB: ~200 bytes per author
- Epsilon-Greedy: minimal

### Latency
- Ranking: 50-200ms (depends on candidate pool)
- Exploration: +5-7ms overhead
- Total feed request: <500ms

### Scalability
- Supports 100+ concurrent users
- Handles 1000+ tweets per user
- ~50 authors tracked per strategy

## Technology Stack

### Frontend
- Next.js 14+
- React 18+
- TypeScript
- Tailwind CSS

### Backend
- Python 3.8+
- FastAPI
- Pydantic
- NumPy, SciPy (for statistics)
- LangChain (optional, for LLM integration)

### Storage
- In-memory (development)
- PostgreSQL/MongoDB (recommended for production)

## Deployment

### Development
```bash
cd backend && python main.py
cd frontend && npm run dev
```

### Production
1. Use production ASGI server (Gunicorn + Uvicorn)
2. Replace in-memory DB with PostgreSQL
3. Configure environment variables
4. Use CDN for frontend assets
5. Set up monitoring and logging

### Docker
Provided docker-compose.yml for containerization:
```bash
docker-compose up
```
