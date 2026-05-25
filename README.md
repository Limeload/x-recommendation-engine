# Recommendation Engine

An open-source personalized feed ranking system inspired by X's architecture. Multi-stage pipeline with explainable scores, per-user weight tuning, and autonomous agent simulation.

## Stack

- **Backend** — Python, FastAPI
- **Frontend** — Next.js 14, TypeScript, Tailwind CSS
- **Realtime** — WebSocket feed updates

## Quick Start

```bash
# Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python main.py          # http://localhost:8000

# Frontend (separate terminal)
cd frontend
npm install
npm run dev             # http://localhost:3000
```

## How It Works

Each tweet is scored across four factors and ranked in real time:

| Factor | Description |
|---|---|
| Recency | Decay function based on post age |
| Popularity | Normalized likes, retweets, replies |
| Quality | Content quality signals |
| Topic Relevance | Alignment with user interests |

Weights are tunable per user via the Settings panel or the API.

Exploration uses **Thompson Sampling** — each author has a Beta-distribution posterior over engagement probability, preventing the feed from over-exploiting already-popular accounts.

## API

```
POST /rank                          # Ranked feed for a user
GET  /users                         # List users
GET  /users/{id}/weights            # Get ranking weights
POST /users/{id}/weights            # Update ranking weights
GET  /api/trending/topics           # Trending topics
GET  /api/trending/discourse-metrics
```

Full docs: [`docs/API_REFERENCE.md`](docs/API_REFERENCE.md)

## License

MIT — see [LICENSE](LICENSE).
