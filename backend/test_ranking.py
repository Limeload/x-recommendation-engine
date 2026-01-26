#!/usr/bin/env python3
"""Quick test of the ranking engine"""
import sys
sys.path.insert(0, '.')

from database.inmemory_db import InMemoryDB
from models.ranking_engine import RankingEngine
from simulation.synthetic_data import SyntheticDataGenerator
from models.schemas import UserPersona
import random

# Initialize database
db = InMemoryDB()

# Generate test data
personas = list(UserPersona)
for i, persona in enumerate(personas):
    user = SyntheticDataGenerator.generate_user(f"user_{i}", f"{persona.value}_{i}", persona)
    db.add_user(user)

for i in range(50):
    user_idx = i % len(personas)
    persona = personas[user_idx]
    tweet = SyntheticDataGenerator.generate_tweet(f"tweet_{i}", f"user_{user_idx}", persona)
    db.add_tweet(tweet)

# Test ranking
user = db.get_user("user_0")
candidates = db.get_recent_tweets(limit=100)
engagement_graph = db.get_engagement_graph("user_0")

ranking_engine = RankingEngine(user)
ranked_tweets = ranking_engine.rank_tweets(candidates, engagement_graph, {})

print("✓ Ranking engine works!")
print(f"  Generated {len(ranked_tweets)} ranked tweets")
if ranked_tweets:
    print(f"  Top tweet: {ranked_tweets[0].tweet.tweet_id} (score: {ranked_tweets[0].explanation.total_score:.3f})")
    print(f"  Rank 1 tweet: {ranked_tweets[0].tweet.content[:50]}...")
