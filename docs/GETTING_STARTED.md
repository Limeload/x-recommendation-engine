# Getting Started

## Prerequisites

- Python 3.8+
- Node.js 16+
- pip and npm

## Installation

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
```

### Frontend Setup

```bash
cd frontend
npm install
```

## Running the Application

### Start Backend Server

```bash
cd backend
python main.py
```

Server runs at `http://localhost:8000`

### Start Frontend Development Server

```bash
cd frontend
npm run dev
```

Frontend runs at `http://localhost:3000`

## Quick Test

### Test Ranking Engine

```bash
pytest test_exploration_layer.py -v
pytest test_agentic_loop.py -v
```

### Run Examples

```bash
python exploration_examples.py
python run_agentic_loop.py
```

## Using the Frontend

1. Open `http://localhost:3000`
2. Select a user from the dropdown
3. View the ranked feed with explanations
4. Click "Tuning Dashboard" to adjust weights
5. See feed update in real-time

## Environment Variables

Create `.env.local` in frontend directory:

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Architecture Overview

The system has three main components:

### Phase 1: Content Generation
LangChain-based tweet generator creates synthetic content using persona templates (Venture Capitalist, Engineer, Founder).

### Phase 2: Autonomous Engagement
Agentic loop runs autonomous agents that monitor feeds and autonomously like, reply, or engage with tweets based on their interest vectors.

### Phase 3: Intelligent Ranking
Multi-stage ranking engine with exploration-exploitation layer that:
- Filters candidates
- Scores by relevance, recency, popularity, quality
- Applies diversity constraints
- Injects 10% exploratory content

## Key Concepts

### Ranking Stages

1. Candidate Generation: Filter tweets by quality, topics, users
2. Scoring: Multi-factor scoring (recency, popularity, quality, relevance)
3. Diversity Filter: Ensure topic and author diversity
4. Exploration: Inject exploratory items using selected strategy

### Exploration Strategies

- Epsilon-Greedy: Random selection from exploration pool
- Thompson Sampling: Bayesian learning from engagement
- UCB: Optimistic exploration with uncertainty bonus

### Engagement Feedback

Record engagement to improve Thompson Sampling and UCB strategies:

```python
engine.record_engagement_for_exploration(
    tweet_id="t1",
    author_id="a1",
    engagement_type="like"
)
```

## Configuration

### Ranking Weights

User preference weights control ranking:
- recency: 0.2 (how recent)
- popularity: 0.25 (likes, retweets)
- quality: 0.2 (content quality)
- topic_relevance: 0.25 (match to interests)

Adjust via tuning dashboard or API.

### Exploration Rate

Default: 10% of feed for exploration

Change at runtime:
```python
engine.set_exploration_rate(0.15)
```

### Exploration Strategy

Choose strategy:
```python
from backend.models.exploration_ranker import ExplorationStrategy

engine.set_exploration_strategy(ExplorationStrategy.THOMPSON_SAMPLING)
```

## Database

Currently uses in-memory storage for development. For production:

1. Replace inmemory_db.py with PostgreSQL/MongoDB driver
2. Update database layer in main.py
3. Adjust schema definitions

## Troubleshooting

### Port Already in Use

If port 8000 is in use:
```bash
lsof -i :8000
kill -9 <PID>
```

### Missing Dependencies

Ensure all requirements are installed:
```bash
pip install -r backend/requirements.txt
```

### API Connection Failed

Check .env.local has correct API_URL and backend is running.

## Next Steps

1. Read ARCHITECTURE.md for system design details
2. Review API_REFERENCE.md for endpoint documentation
3. Check DEVELOPMENT.md for contribution guidelines
4. Run examples to understand functionality
