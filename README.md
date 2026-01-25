# Recommendation Engine

A production-ready personalized recommendation engine with multi-stage ranking, autonomous agent simulation, and exploration-exploitation strategies. Built to match X's ranking architecture with explainable scoring and interactive tuning.

## Overview

This system demonstrates:
- Multi-stage ranking pipeline with explainability
- Thompson Sampling and UCB exploration strategies
- Autonomous agent simulation with engagement tracking
- Interactive dashboard for weight tuning
- Real-time feed with detailed ranking explanations

## Getting Started

New to the project? Start with:
1. [GETTING_STARTED.md](docs/GETTING_STARTED.md) - Installation and quick start
2. [ARCHITECTURE.md](docs/ARCHITECTURE.md) - System design and components
3. [API_REFERENCE.md](docs/API_REFERENCE.md) - Endpoint documentation
4. [DEVELOPMENT.md](docs/DEVELOPMENT.md) - Contributing guidelines

## Key Features

### Ranking Pipeline
Four-stage ranking system:
- Stage 1: Filtering - Remove low-quality content
- Stage 2: Scoring - Multi-factor relevance calculation
- Stage 3: Diversity - Reduce duplicate topic clustering
- Stage 4: Exploration - Thompson Sampling for learning

### Scoring Factors
- Recency (20%): Recent content preferred
- Popularity (25%): Engagement metrics
- Quality (20%): Content quality assessment
- Topic Relevance (35%): User interest alignment

### Exploration Strategies
Configurable strategies for discovering new content:
- Thompson Sampling: Bayesian approach with posterior estimation
- UCB: Upper Confidence Bound with exploration bonus
- Epsilon-Greedy: Simple random exploration baseline

### Autonomous Agents
Multi-persona agent system simulating different user types:
- Venture capitalists
- Tech enthusiasts
- Product managers
- Data scientists
- Marketing professionals

## Technology Stack

### Backend
- Python 3.8+
- FastAPI for API endpoints
- Pydantic for data validation
- NumPy and SciPy for computation
- In-memory database (PostgreSQL in production)

### Frontend
- Next.js 14+
- React with TypeScript
- Tailwind CSS for styling
- Real-time feed component

## Project Structure

```
recommendation_engine/
├── backend/
│   ├── models/
│   │   ├── ranking_engine.py        # Core ranking pipeline
│   │   ├── exploration_ranker.py    # Exploration strategies
│   │   ├── agents.py                # Agent system
│   │   └── schemas.py               # Data models
│   ├── database/
│   │   ├── inmemory_db.py           # Database implementation
│   │   └── connection.py            # Database setup
│   ├── simulation/
│   │   ├── langchain_tweet_generator.py
│   │   └── agentic_loop.py
│   ├── routes/
│   │   ├── ranking.py               # Ranking endpoints
│   │   ├── agents.py                # Agent endpoints
│   │   └── users.py                 # User endpoints
│   ├── main.py                      # FastAPI application
│   ├── config.py                    # Configuration
│   └── requirements.txt              # Dependencies
├── frontend/
│   ├── app/
│   │   ├── page.tsx                 # Main application
│   │   ├── layout.tsx               # Root layout
│   │   └── globals.css              # Styles
│   ├── components/
│   │   ├── Feed.tsx                 # Tweet feed
│   │   ├── TuningDashboard.tsx      # Weight adjustment
│   │   └── UserSelector.tsx         # User selection
│   ├── types/
│   │   └── index.ts                 # Type definitions
│   ├── package.json
│   └── tsconfig.json
├── docs/
│   ├── GETTING_STARTED.md           # Setup guide
│   ├── ARCHITECTURE.md              # System design
│   ├── API_REFERENCE.md             # API documentation
│   └── DEVELOPMENT.md               # Contributing guide
├── test_exploration_layer.py        # Exploration tests
├── exploration_examples.py          # Working examples
└── README.md                        # This file
```

## Quick Start

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

Server runs on `http://localhost:8000`

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Application runs on `http://localhost:3000`

## API Endpoints

### Core Ranking
- `POST /rank` - Get ranked tweet feed for user

### User Management
- `GET /users` - List all users
- `GET /users/{user_id}/weights` - Get ranking weights
- `POST /users/{user_id}/weights` - Update ranking weights

### Agents
- `POST /api/agents/register` - Register autonomous agent
- `GET /api/agents/list` - List all agents
- `POST /api/agents/run-loop` - Run agent engagement cycle

### Exploration
- `GET /api/exploration/stats` - Get exploration statistics
- `POST /api/exploration/engagement` - Record engagement event

Full API documentation in [API_REFERENCE.md](docs/API_REFERENCE.md)

## Testing

Run the exploration layer tests:
```bash
pytest test_exploration_layer.py -v
```

Run working examples:
```bash
python exploration_examples.py
```

## Development

For contribution guidelines, coding standards, and development setup:
See [DEVELOPMENT.md](docs/DEVELOPMENT.md)

## System Architecture

### Data Flow
1. User request arrives at `/rank` endpoint
2. Fetch user profile and recent tweets
3. Stage 1: Filter low-quality tweets
4. Stage 2: Score remaining tweets
5. Stage 3: Apply diversity constraints
6. Stage 4: Apply exploration strategy
7. Return ranked tweets with explanations

### Ranking Pipeline

Each tweet receives:
- **Recency Score**: Decay function based on age
- **Popularity Score**: Normalized engagement metrics
- **Quality Score**: Content quality assessment
- **Topic Relevance Score**: User interest alignment

Final score combines all factors with configurable weights.

### Exploration Mechanism

Thompson Sampling tracks engagement statistics per author:
- Successes: Engagements (likes, retweets, replies)
- Trials: Total rankings shown
- Beta distribution posterior for each author
- Probabilistic sampling for exploration

## Configuration

Adjust ranking weights per user via API:

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

Change exploration strategy:
```python
ranker = ExplorationRanker(strategy="thompson_sampling")
ranker.set_strategy("ucb")
ranker.set_exploration_rate(0.15)
```

## Performance

- Ranking latency: < 500ms per request
- Memory per author: ~200 bytes
- Scalability: Handles 1000+ authors efficiently
- Concurrency: Thread-safe operations

## Troubleshooting

### Backend won't start
- Verify port 8000 is available
- Check Python virtual environment activated
- Reinstall dependencies: `pip install -r backend/requirements.txt`

### Frontend connection fails
- Ensure backend is running on port 8000
- Check CORS settings in `backend/main.py`
- Verify frontend environment variables in `.env.local`

### Test failures
- Clear cache: `rm -rf __pycache__ .pytest_cache`
- Reinstall dependencies with `--force-reinstall`
- Check Python version (3.8+ required)

Full troubleshooting in [GETTING_STARTED.md](docs/GETTING_STARTED.md#troubleshooting)

## Learning Path

1. Start with [GETTING_STARTED.md](docs/GETTING_STARTED.md) for hands-on experience
2. Read [ARCHITECTURE.md](docs/ARCHITECTURE.md) to understand system design
3. Reference [API_REFERENCE.md](docs/API_REFERENCE.md) for endpoint details
4. Study [DEVELOPMENT.md](docs/DEVELOPMENT.md) for contribution guidelines
5. Explore test files for usage examples

## Key Concepts

### Thompson Sampling
Bayesian approach to exploration using Beta-Bernoulli conjugate priors. Maintains engagement statistics per author and samples from posterior distribution for probabilistic author selection.

### Ranking Explainability
Each ranked item includes detailed breakdown of scoring factors, making the ranking decision transparent to users.

### Autonomous Agents
Simulated users with configurable personas, interests, and engagement patterns. Used to test system behavior and generate realistic engagement data.

### Exploration-Exploitation Tradeoff
Balancing showing known-good content (exploitation) with discovering new content (exploration) to maximize long-term engagement.

## License

This project is part of Headstarter AI's engineering program.

## Support

- Code examples: See `exploration_examples.py`
- Tests: See `test_exploration_layer.py`
- Questions: Check relevant documentation in `/docs/`
