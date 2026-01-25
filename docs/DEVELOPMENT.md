# Development Guide

## Project Structure

```
recommendation_engine/
├── backend/
│   ├── models/
│   │   ├── ranking_engine.py          # Core ranking pipeline
│   │   ├── exploration_ranker.py      # Thompson Sampling, UCB, Epsilon-Greedy
│   │   └── agents.py                  # Autonomous agent system
│   ├── database/
│   │   ├── connection.py              # Database setup
│   │   ├── models.py                  # Pydantic data models
│   │   └── queries.py                 # Database operations
│   ├── simulation/
│   │   └── simulator.py               # Batch tweet generation
│   ├── routes/
│   │   ├── ranking.py                 # Ranking endpoints
│   │   ├── agents.py                  # Agent endpoints
│   │   └── users.py                   # User management endpoints
│   ├── main.py                        # FastAPI application
│   └── requirements.txt                # Python dependencies
├── frontend/
│   ├── app/
│   │   ├── page.tsx                   # Main application UI
│   │   ├── layout.tsx                 # Layout wrapper
│   │   └── globals.css                # Global styles
│   ├── public/                        # Static assets
│   ├── package.json                   # Node dependencies
│   └── tsconfig.json                  # TypeScript configuration
├── docs/
│   ├── GETTING_STARTED.md             # Setup and quick start
│   ├── ARCHITECTURE.md                # System design
│   ├── API_REFERENCE.md               # API documentation
│   └── DEVELOPMENT.md                 # This file
├── test_exploration_layer.py          # Exploration tests
├── exploration_examples.py            # Working examples
└── README.md                          # Project overview
```

## Development Setup

### Backend Setup

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate
```

2. Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

3. Start development server:
```bash
python main.py
```

Server runs on `http://localhost:8000`

### Frontend Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Start development server:
```bash
npm run dev
```

Application runs on `http://localhost:3000`

## Code Standards

### Python

- Use type hints for all functions
- Follow PEP 8 style guide
- Maximum line length: 100 characters
- Use docstrings for classes and public methods
- Keep functions focused and under 50 lines when possible

Example:
```python
def calculate_score(
    engagement: int,
    quality: float,
    recency_hours: int
) -> float:
    """Calculate composite ranking score.

    Args:
        engagement: Total engagement count
        quality: Quality score (0-1)
        recency_hours: Hours since creation

    Returns:
        Composite score (0-1)
    """
    popularity_factor = min(1.0, engagement / 1000)
    recency_factor = 1.0 / (1.0 + recency_hours / 24)

    return (popularity_factor * 0.4 +
            quality * 0.4 +
            recency_factor * 0.2)
```

### TypeScript/React

- Use functional components with hooks
- Add types for all props and state
- Keep components under 300 lines
- One component per file when possible
- Use descriptive variable names

Example:
```typescript
interface RankedTweet {
  tweet: Tweet;
  score: number;
  explanation: string[];
}

export const FeedItem: React.FC<{ item: RankedTweet }> = ({ item }) => {
  return (
    <div className="feed-item">
      <h3>{item.tweet.content}</h3>
      <p>Score: {item.score.toFixed(2)}</p>
    </div>
  );
};
```

## Testing

### Running Tests

```bash
pytest test_exploration_layer.py -v
```

### Running Examples

```bash
python exploration_examples.py
```

### Test Coverage

Run with coverage:
```bash
pytest test_exploration_layer.py --cov=backend
```

### Writing Tests

Tests should be:
- Independent and isolated
- Fast (< 100ms per test)
- Clear in intent
- Use descriptive names

Example:
```python
def test_thompson_sampling_learns_from_engagement():
    ranker = ThompsonSamplingRanker(exploration_rate=0.1)

    ranker.record_engagement("a1", "like")
    ranker.record_engagement("a1", "like")
    ranker.record_engagement("a2", "none")

    stats = ranker.get_stats()
    assert stats.engagement_rate["a1"] > stats.engagement_rate["a2"]
```

## Git Workflow

### Branch Naming

- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation
- `refactor/description` - Code improvements

### Commit Messages

Keep commits focused and descriptive:
```
feat: add Thompson Sampling exploration strategy

- Implements Beta-Bernoulli conjugate prior
- Updates engagement statistics on feedback
- Adds posterior probability calculation

Closes #123
```

### Pull Request Process

1. Create feature branch from main
2. Make changes with clear commits
3. Write/update tests for changes
4. Update documentation if needed
5. Submit PR with description
6. Address review feedback

## Debugging

### Backend Debugging

Add logging for debugging:
```python
import logging

logger = logging.getLogger(__name__)

def rank_tweets(user_id: str):
    logger.info(f"Ranking tweets for user {user_id}")

    try:
        results = engine.rank(user_id)
        logger.debug(f"Got {len(results)} tweets")
        return results
    except Exception as e:
        logger.error(f"Ranking failed: {e}")
        raise
```

### Frontend Debugging

Use React DevTools extension for Chrome/Firefox to inspect component state and props.

## Performance Optimization

### Backend

- Cache expensive computations (ranking scores, user preferences)
- Use vectorized operations with NumPy
- Batch process tweets when generating data
- Monitor API response times

### Frontend

- Use React.memo for expensive components
- Lazy load feed items
- Minimize re-renders with proper dependency arrays
- Use CDN for static assets

## Deployment

### Development Deployment

Both services start locally:
```bash
cd backend && python main.py
cd frontend && npm run dev
```

### Production Deployment

Use Docker for both services:
```bash
docker-compose -f docker-compose.prod.yml up
```

## Adding New Features

1. Create feature branch
2. Add tests first (TDD)
3. Implement feature in backend
4. Create/update API endpoints
5. Update frontend to consume endpoints
6. Update documentation
7. Submit for review

Example: Adding new ranking factor

**Step 1: Test** (test_exploration_layer.py)
```python
def test_new_factor_affects_score():
    engine = RankingEngine()

    tweet1 = create_tweet(new_factor=0.9)
    tweet2 = create_tweet(new_factor=0.3)

    ranked = engine.rank("user_0")
    assert ranked[0].tweet.id == tweet1.id
```

**Step 2: Implement** (ranking_engine.py)
```python
def calculate_new_factor(tweet: Tweet) -> float:
    return tweet.new_metric / 100.0

score = (calculate_new_factor(tweet) * 0.15 +
         existing_factors)
```

**Step 3: Update API** (routes/ranking.py)
```python
@app.post("/rank")
async def rank_tweets(request: RankRequest) -> List[RankedTweet]:
    return engine.rank_with_new_factor(request.user_id)
```

**Step 4: Update Frontend** (page.tsx)
```typescript
const FeedItem: React.FC<{ item: RankedTweet }> = ({ item }) => {
  return (
    <div>
      <p>New Factor: {item.explanation.new_factor}</p>
    </div>
  );
};
```

**Step 5: Update Docs** (ARCHITECTURE.md)
- Add new factor to ranking pipeline
- Document calculation formula
- Explain impact on results

## Common Tasks

### Adding a new endpoint

1. Create route function in `backend/routes/`
2. Add Pydantic models in `backend/database/models.py`
3. Implement logic in appropriate model
4. Document in API_REFERENCE.md
5. Add frontend integration

### Modifying ranking weights

Edit user weights via API:
```bash
curl -X POST http://localhost:8000/users/user_0/weights \
  -H "Content-Type: application/json" \
  -d '{
    "recency": 0.3,
    "popularity": 0.2,
    "quality": 0.2,
    "topic_relevance": 0.3
  }'
```

### Generating new tweets

```bash
python backend/simulation/simulator.py --count 100 --persona venture_capitalist
```

## Troubleshooting

### Backend won't start
- Check port 8000 is available
- Verify virtual environment activated
- Reinstall requirements: `pip install -r backend/requirements.txt`

### Frontend build fails
- Clear node_modules: `rm -rf node_modules && npm install`
- Check Node.js version (16+ required)
- Check TypeScript errors: `npm run build`

### API connection fails
- Verify backend is running on 8000
- Check CORS settings in main.py
- Check frontend environment variables

## Resources

- FastAPI documentation: https://fastapi.tiangolo.com
- React documentation: https://react.dev
- Thompson Sampling: https://en.wikipedia.org/wiki/Thompson_sampling
- Python type hints: https://docs.python.org/3/library/typing.html

## Contact & Support

For questions or issues:
1. Check GETTING_STARTED.md troubleshooting section
2. Review ARCHITECTURE.md for system design
3. Check test files for usage examples
