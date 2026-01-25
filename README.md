# 𝕏 Recommendation Engine - Complete Implementation

A production-ready, explainable personalized recommendation engine that mimics X's ranking system with tunable weights, synthetic user simulation, and an intuitive React-based interface.

## 📋 Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                  Frontend (Next.js + React)             │
│  - Real-time Feed with Ranking Explanations             │
│  - Tuning Dashboard (Weight Adjustment)                 │
│  - User Selector & Analytics                            │
└──────────────────────────┬──────────────────────────────┘
                           │ API Calls
┌──────────────────────────▼──────────────────────────────┐
│               FastAPI Backend (Python)                  │
├──────────────────────────────────────────────────────────┤
│ • Ranking Pipeline (4 stages)                           │
│ • Multi-factor Scoring System                           │
│ • Explainability Engine                                 │
│ • Weight Tuning API                                     │
└──────────────────────────┬──────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────┐
│           Data Layer (In-Memory DB + Vector DB)         │
├──────────────────────────────────────────────────────────┤
│ • User Profiles & Engagement Graphs                     │
│ • Tweet Storage & Embeddings                            │
│ • Synthetic Data Generation                             │
└──────────────────────────────────────────────────────────┘
```

## 🏗️ Project Structure

```
recommendation_engine/
├── backend/
│   ├── models/
│   │   ├── schemas.py              # Data models (User, Tweet, etc.)
│   │   ├── ranking_engine.py       # Multi-stage ranking pipeline
│   │   └── __init__.py
│   ├── database/
│   │   ├── inmemory_db.py          # In-memory database (MVP)
│   │   └── __init__.py
│   ├── simulation/
│   │   ├── synthetic_data.py       # Synthetic user/tweet generation
│   │   └── __init__.py
│   ├── main.py                     # FastAPI application & endpoints
│   ├── config.py                   # Configuration management
│   ├── requirements.txt            # Python dependencies
│   ├── .env.example                # Environment variables template
│   └── .gitignore
│
├── frontend/
│   ├── app/
│   │   ├── layout.tsx              # Root layout
│   │   ├── page.tsx                # Main page (feed + tuning)
│   │   ├── globals.css             # Global styles
│   │   └── favicon.ico
│   ├── components/
│   │   ├── Feed.tsx                # Tweet feed component
│   │   ├── TweetCard.tsx           # Individual tweet with score
│   │   ├── ExplanationPanel.tsx    # Ranking explanation breakdown
│   │   ├── TuningDashboard.tsx     # Weight adjustment UI
│   │   └── UserSelector.tsx        # User selection dropdown
│   ├── types/
│   │   └── index.ts                # TypeScript type definitions
│   ├── package.json
│   ├── tsconfig.json
│   ├── next.config.js
│   ├── tailwind.config.ts
│   ├── postcss.config.js
│   ├── .env.local
│   └── .gitignore
│
└── README.md                        # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+ (backend)
- Node.js 18+ (frontend)
- npm or yarn

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env

# Run the server
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **Base URL**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs (Swagger UI)
- **Alternative Docs**: http://localhost:8000/redoc

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

The frontend will be available at http://localhost:3000

## 🎯 Key Features

### 1. **Multi-Stage Ranking Pipeline**

```python
Stage 1: Candidate Generation
  ├─ In-network (tweets from followed users)
  └─ Out-of-network (recent popular tweets)

Stage 2: Scoring (Heavy Ranker)
  ├─ Recency Score (exponential decay)
  ├─ Popularity Score (likes, retweets, replies, bookmarks)
  ├─ Quality Score (author credibility)
  └─ Topic Relevance (user interests match)

Stage 3: Re-Ranking
  ├─ Diversity filtering (max 3 per author)
  └─ Topic clustering (max 5 per topic)

Stage 4: Explanation Generation
  └─ Human-readable factors & scoring breakdown
```

### 2. **Explainable Ranking**

Every ranked tweet includes:
- **Total Score**: Overall ranking score (0-1)
- **Component Scores**: Individual factor contributions
- **Weight Breakdown**: How each factor contributed
- **Key Factors**: Human-readable explanation
- **Persona Match**: Which user persona benefits most

Example explanation:
```json
{
  "total_score": 0.82,
  "recency_score": 0.9,
  "popularity_score": 0.75,
  "quality_score": 0.85,
  "topic_relevance_score": 0.88,
  "key_factors": [
    "High affinity to 'AI' persona",
    "Recent high-engagement content",
    "Strong quality signals",
    "Authored by followed user"
  ]
}
```

### 3. **Tunable Weights Dashboard**

Users can adjust the importance of ranking factors:
- **Recency** (⏰): How fresh should content be?
- **Popularity** (🔥): How much does engagement matter?
- **Quality** (⭐): Content quality signals
- **Topic Relevance** (🎯): Match to user interests
- **Diversity** (🌈): Avoid redundancy

Quick presets:
- 📰 Latest First
- 🔥 Trending
- 🎯 Personalized
- ⚖️ Balanced

### 4. **Synthetic User Simulation**

Generates realistic synthetic personas:
- **Founders**: Focused on startups, innovation, fundraising
- **Journalists**: Interested in news, investigation, business
- **Engineers**: Passionate about systems, open source, ML
- **Investors**: Focus on fintech, markets, opportunities
- **Content Creators**: Community, design, marketing
- **Researchers**: Academic, papers, theory
- **Analysts**: Data, business intelligence, trends

Each persona has:
- Unique interests and expertise areas
- Characteristic tweet templates
- Realistic engagement patterns
- Follow relationships

## 📡 API Endpoints

### Ranking (Core)
```bash
POST /rank
  - Get personalized ranked feed for a user
  - Request: { user_id, limit, filters }
  - Response: List[RankedTweet] with explanations

GET /rank/explain/{tweet_id}
  - Detailed explanation for why a tweet was ranked
  - Response: Full ranking breakdown
```

### User Management
```bash
GET /users
  - List all users

GET /users/{user_id}
  - Get specific user

POST /users
  - Create new user

GET /users/{user_id}/weights
  - Get current ranking weights

POST /users/{user_id}/weights
  - Update ranking weights (from tuning dashboard)
```

### Tweets
```bash
GET /tweets
  - Get recent tweets

GET /tweets/{tweet_id}
  - Get specific tweet

POST /tweets
  - Create new tweet

GET /tweets/search?q=...
  - Search tweets by keyword
```

### Engagement
```bash
GET /users/{user_id}/following
  - Get user's following list

POST /users/{user_id}/follow/{target_user_id}
  - Add follow relationship
```

### Analytics
```bash
GET /topics/trending
  - Get trending topics

GET /analytics/stats
  - System statistics (users, tweets, personas)

GET /health
  - Health check
```

## 🧮 Ranking Algorithm Details

### Recency Score
```
score = e^(-k * age_hours)
where k = ln(2) / 24 (half-life of 24 hours)
```
- Tweet from 1 hour ago: ~0.97
- Tweet from 6 hours ago: ~0.83
- Tweet from 24 hours ago: ~0.50
- Tweet from 7 days ago: ~0.004

### Popularity Score
```
score = 0.4 * norm(likes)
      + 0.35 * norm(retweets)
      + 0.15 * norm(replies)
      + 0.1 * norm(bookmarks)
```

Normalization maximums:
- Likes: 10,000
- Retweets: 2,000
- Replies: 500
- Bookmarks: 1,000

### Topic Relevance Score
```
score = 0.6 * jaccard(user_interests, tweet_topics)
      + 0.4 * expertise_match
```

### Final Score
```
total = recency_weight * recency_score
      + popularity_weight * popularity_score
      + quality_weight * quality_score
      + topic_relevance_weight * topic_relevance_score
      - diversity_weight * diversity_penalty
```

## 🔌 Integration Points

### Vector Database (Pinecone/Weaviate)

To use vector embeddings for semantic search:

```python
# In database/vector_db.py
from pinecone import Pinecone

pc = Pinecone(api_key=settings.PINECONE_API_KEY)
index = pc.Index(settings.PINECONE_INDEX_NAME)

# Store tweet embeddings
index.upsert(vectors=[
    (tweet_id, embedding, {"content": tweet.content})
])

# Search similar tweets
results = index.query(vector=user_embedding, top_k=10)
```

### LLM Integration (OpenAI/Anthropic)

For generating synthetic tweets and explanations:

```python
# In simulation/synthetic_data.py
from langchain.llms import OpenAI

llm = OpenAI(api_key=settings.OPENAI_API_KEY)

# Generate realistic tweet content
prompt = f"Generate a tweet about {topic} by a {persona}:"
tweet_content = llm(prompt)
```

## 📊 Database Schema

### User
- `user_id`: Unique identifier
- `username`: Display name
- `persona`: UserPersona enum
- `interests`: List of topics
- `expertise_areas`: Areas of expertise
- `preference_weights`: Tunable ranking weights

### Tweet
- `tweet_id`: Unique identifier
- `author_id`: Creator user ID
- `content`: Tweet text
- `created_at`: Timestamp
- `engagement`: likes, retweets, replies, bookmarks
- `topics`: Classification tags
- `quality_score`: 0-1 quality signal

### EngagementGraph
- `following`: List of followed user IDs
- `followers`: List of follower user IDs
- `engagement_events`: List of interaction events
- `topic_affinities`: Topic interest scores

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest -v
```

### Frontend Tests
```bash
cd frontend
npm run test
```

## 🚢 Production Deployment

### Backend (FastAPI)
```bash
# Using Gunicorn
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app

# Or Docker
docker build -t recommendation-engine-backend .
docker run -p 8000:8000 recommendation-engine-backend
```

### Frontend (Next.js)
```bash
# Production build
npm run build
npm run start

# Or Docker
docker build -t recommendation-engine-frontend .
docker run -p 3000:3000 recommendation-engine-frontend
```

### Environment Variables
```env
# Backend
OPENAI_API_KEY=...
PINECONE_API_KEY=...
USE_VECTOR_DB=true

# Frontend
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
```

## 📈 Future Enhancements

### Phase 2: LLM Integration
- [ ] LLM-powered synthetic user generation
- [ ] Natural language explanations
- [ ] Automatic persona detection
- [ ] Dynamic weight recommendations

### Phase 3: Vector Search
- [ ] Pinecone/Weaviate integration
- [ ] Semantic similarity ranking
- [ ] Topic embeddings
- [ ] User interest embeddings

### Phase 4: Advanced Features
- [ ] Real-time feed updates (WebSockets)
- [ ] User interaction tracking
- [ ] A/B testing framework
- [ ] Feedback loops for ranking optimization
- [ ] Multi-user social graph simulation
- [ ] Trending topic detection

## 🛠️ Technical Stack

### Backend
- **Framework**: FastAPI (async)
- **Language**: Python 3.9+
- **ORM**: Pydantic (models)
- **Database**: In-memory (MVP) → PostgreSQL (prod)
- **Vector DB**: Pinecone/Weaviate (optional)
- **LLM**: OpenAI/Anthropic (optional)

### Frontend
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Components**: React 18
- **State**: React Hooks
- **HTTP Client**: Fetch API

## 📝 License

MIT License - see LICENSE file

## 👨‍💼 Author

Built as a comprehensive recommendation engine for X (Twitter) with explainability and tunability as first-class features.

---

## 🎓 Learning Resources

- [X Recommendation Algorithm](https://github.com/X-corp/the-algorithm)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [Pydantic Validation](https://docs.pydantic.dev/)
- [Tailwind CSS](https://tailwindcss.com/docs)

## 💬 Support

For issues, questions, or suggestions, please open an issue or reach out to the development team.

---

**Happy Ranking! 🚀**
# x-recommendation-engine
