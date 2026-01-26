#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')

from models.ranking_engine import RankingEngine
from database.inmemory_db import InMemoryDB
from simulation.synthetic_data import SyntheticDataGenerator
from models.schemas import UserPersona
import traceback

# Init DB
db = InMemoryDB()

# Create test user
user = SyntheticDataGenerator.generate_user('user_0', 'test_user', UserPersona.FOUNDER)
db.add_user(user)

# Create test tweets
for i in range(5):
    tweet = SyntheticDataGenerator.generate_tweet(f'tweet_{i}', 'user_0', UserPersona.FOUNDER)
    db.add_tweet(tweet)

# Test ranking
try:
    ranking_engine = RankingEngine(user)
    candidates = db.get_all_tweets()
    engagement_graph = {}
    result = ranking_engine.rank_tweets(candidates, engagement_graph, None)
    print(f'✅ Ranking successful: {len(result)} tweets')
    for i, r in enumerate(result[:3]):
        print(f"  {i+1}. {r.tweet_id}: score={r.score:.4f}")
except Exception as e:
    print(f'❌ Error: {e}')
    traceback.print_exc()
