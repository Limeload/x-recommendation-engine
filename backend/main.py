"""
FastAPI Backend for Recommendation Engine
Main application entry point with all endpoints
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import logging

from models.schemas import (
    User,
    Tweet,
    RankingRequest,
    RankedTweet,
    WeightTuningRequest,
    UserPersona,
)
from models.ranking_engine import RankingEngine
from models.spam_detector import SpamDetector, init_spam_detector
from database.inmemory_db import InMemoryDB
from simulation.synthetic_data import SyntheticDataGenerator
from routes.notifications_routes import (
    router as notifications_router,
    notification_manager,
    init_notification_manager,
)
from routes.conversations_routes import router as conversations_router
from routes.profile_routes import router as profile_router
from routes.experiments_routes import (
    router as experiments_router,
    experiment_manager,
    init_experiment_manager,
)
from routes.websocket_routes import router as websocket_router
from routes.websocket_manager import get_websocket_manager

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="X Recommendation Engine API",
    description="Personalized recommendation engine with explainable rankings",
    version="1.0.0",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global database instance
db = InMemoryDB()

# Initialize spam detector and managers
spam_detector = SpamDetector()
init_spam_detector(spam_detector)
init_notification_manager(notification_manager)
init_experiment_manager(experiment_manager)

# Set database for routers
from routes.conversations_routes import set_db as conversations_set_db
from routes.profile_routes import set_db as profile_set_db

conversations_set_db(db)
profile_set_db(db)

# Include routers
app.include_router(notifications_router)
app.include_router(conversations_router)
app.include_router(profile_router)
app.include_router(experiments_router)
app.include_router(websocket_router)


# ==================== Initialization Endpoints ====================


@app.on_event("startup")
async def startup_event():
    """Initialize synthetic data on startup"""
    logger.info("Initializing synthetic data...")
    _initialize_synthetic_data()
    logger.info("Startup complete. Synthetic data loaded.")


def _initialize_synthetic_data():
    """Generate synthetic users, tweets, and engagement patterns"""
    personas = list(UserPersona)

    # Generate 10 synthetic users
    for i, persona in enumerate(personas):
        user = SyntheticDataGenerator.generate_user(
            user_id=f"user_{i}",
            username=f"{persona.value}_user_{i}",
            persona=persona,
        )
        db.add_user(user)
        logger.info(f"Created user: {user.username}")

    # Generate 50 tweets from various users
    tweet_id_counter = 0
    all_users = db.get_all_users()
    for i in range(50):
        user_idx = i % len(personas)
        user_id = f"user_{user_idx}"
        persona = personas[user_idx]
        author_name = all_users[user_idx].username if user_idx < len(all_users) else f"user_{user_idx}"

        tweet = SyntheticDataGenerator.generate_tweet(
            tweet_id=f"tweet_{tweet_id_counter}",
            author_id=user_id,
            persona=persona,
            author_name=author_name,
        )
        db.add_tweet(tweet)
        tweet_id_counter += 1

    # Create some follow relationships
    for i in range(len(personas)):
        # Each user follows 3-5 other random users
        follow_count = min(3, len(personas) - 1)
        follow_targets = [j for j in range(len(personas)) if j != i]
        for target in random.sample(follow_targets, k=follow_count):
            db.add_following(f"user_{i}", f"user_{target}")

    # Generate engagement events
    event_id_counter = 0
    users = db.get_all_users()
    tweets = db.get_all_tweets()

    for user in users:
        # Each user engages with 10-20 random tweets
        engagement_count = min(15, len(tweets))
        for _ in range(engagement_count):
            target_tweet = random.choice(tweets)
            if target_tweet.author_id != user.user_id:  # Don't engage with own tweets
                event = SyntheticDataGenerator.generate_engagement_event(
                    event_id=f"event_{event_id_counter}",
                    user_id=user.user_id,
                    target_tweet_id=target_tweet.tweet_id,
                    target_user_id=target_tweet.author_id,
                )
                db.add_engagement_event(user.user_id, event)
                event_id_counter += 1

    logger.info(f"Created {len(db.get_all_users())} users")
    logger.info(f"Created {len(db.get_all_tweets())} tweets")
    logger.info(f"Created {event_id_counter} engagement events")


import random


# ==================== User Endpoints ====================


@app.get("/users", response_model=List[User])
async def list_users():
    """
    Get all users in the system

    Returns:
        List of all users
    """
    users = db.get_all_users()
    return users


@app.get("/users/{user_id}", response_model=User)
async def get_user(user_id: str):
    """
    Get a specific user by ID

    Args:
        user_id: User ID

    Returns:
        User object
    """
    user = db.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.post("/users", response_model=User)
async def create_user(user: User):
    """
    Create a new user

    Args:
        user: User object

    Returns:
        Created user
    """
    if db.get_user(user.user_id):
        raise HTTPException(status_code=400, detail="User already exists")
    db.add_user(user)
    return user


# ==================== Ranking Endpoints ====================


@app.post("/rank", response_model=List[RankedTweet])
async def rank_tweets(request: RankingRequest):
    """
    Get personalized ranked feed for a user

    Implements the full ranking pipeline:
    1. Candidate Generation (recent tweets)
    2. Scoring (multi-factor ranking)
    3. Re-ranking (diversity filtering)

    Args:
        request: RankingRequest with user_id, limit, and optional filters

    Returns:
        List of RankedTweet objects with explanations
    """
    try:
        user = db.get_user(request.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Stage 1: Candidate Generation
        candidates = db.get_recent_tweets(limit=100)

        engagement_graph = db.get_engagement_graph(request.user_id)

        # Stage 2: Scoring & Stage 3: Re-ranking
        ranking_engine = RankingEngine(user)
        ranked_tweets, exploration_explanations = ranking_engine.rank_tweets(
            candidates=candidates,
            engagement_graph=engagement_graph,
            filter_params=request.filters,
        )

        # Return top-k results
        return ranked_tweets[: request.limit]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in rank_tweets: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/rank/explain/{tweet_id}")
async def explain_ranking(
    tweet_id: str,
    user_id: str = Query(..., description="User ID for context"),
):
    """
    Detailed explanation for why a tweet was ranked for a user

    Args:
        tweet_id: Tweet ID to explain
        user_id: User ID for context

    Returns:
        Detailed explanation object
    """
    tweet = db.get_tweet(tweet_id)
    if not tweet:
        raise HTTPException(status_code=404, detail="Tweet not found")

    user = db.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    ranking_engine = RankingEngine(user)
    engagement_graph = db.get_engagement_graph(user_id)
    explanation = ranking_engine._score_tweet(tweet, engagement_graph)

    return {
        "tweet": tweet,
        "explanation": explanation,
    }


# ==================== Weight Tuning Endpoints ====================


@app.get("/users/{user_id}/weights")
async def get_user_weights(user_id: str):
    """
    Get current ranking weights for a user

    Args:
        user_id: User ID

    Returns:
        Current preference weights
    """
    user = db.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "user_id": user_id,
        "weights": user.preference_weights,
    }


@app.post("/users/{user_id}/weights")
async def update_user_weights(user_id: str, request: WeightTuningRequest):
    """
    Update ranking weights for a user (Tuning Dashboard feature)

    Allows users to adjust the importance of different ranking factors:
    - recency: How fresh the content should be
    - popularity: How much engagement matters
    - quality: Content quality signals
    - topic_relevance: Match to user interests
    - diversity: Avoid cluster effects

    Args:
        user_id: User ID
        request: WeightTuningRequest with new weights

    Returns:
        Updated user object
    """
    user = db.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Validate weights
    for key, value in request.weights.items():
        if not 0 <= value <= 1:
            raise HTTPException(
                status_code=400,
                detail=f"Weight '{key}' must be between 0 and 1",
            )

    # Update user weights
    user.preference_weights.update(request.weights)
    db.update_user(user)

    return {
        "message": "Weights updated successfully",
        "user_id": user_id,
        "new_weights": user.preference_weights,
    }


# ==================== Tweet Endpoints ====================


@app.get("/tweets", response_model=List[Tweet])
async def list_tweets(limit: int = Query(20, le=100)):
    """
    Get recent tweets

    Args:
        limit: Maximum number of tweets to return

    Returns:
        List of recent tweets
    """
    tweets = db.get_recent_tweets(limit=limit)
    return tweets


@app.get("/tweets/{tweet_id}", response_model=Tweet)
async def get_tweet(tweet_id: str):
    """
    Get a specific tweet by ID

    Args:
        tweet_id: Tweet ID

    Returns:
        Tweet object
    """
    tweet = db.get_tweet(tweet_id)
    if not tweet:
        raise HTTPException(status_code=404, detail="Tweet not found")
    return tweet


@app.post("/tweets", response_model=Tweet)
async def create_tweet(tweet: Tweet):
    """
    Create a new tweet

    Args:
        tweet: Tweet object

    Returns:
        Created tweet
    """
    if db.get_tweet(tweet.tweet_id):
        raise HTTPException(status_code=400, detail="Tweet already exists")
    db.add_tweet(tweet)
    return tweet


@app.get("/tweets/search", response_model=List[Tweet])
async def search_tweets(
    q: str = Query(..., description="Search query"),
):
    """
    Search tweets by keyword or topic

    Args:
        q: Search query

    Returns:
        List of matching tweets
    """
    results = db.search_tweets_by_keyword(q)
    return results


@app.get("/topics/trending", response_model=Dict[str, int])
async def get_trending_topics(limit: int = Query(10, le=50)):
    """
    Get trending topics across all tweets

    Args:
        limit: Number of topics to return

    Returns:
        Dictionary of topic -> count
    """
    all_trending = db.get_trending_topics()
    return dict(list(all_trending.items())[:limit])


# ==================== Engagement Endpoints ====================


@app.get("/users/{user_id}/following")
async def get_user_following(user_id: str):
    """
    Get list of users that a user follows

    Args:
        user_id: User ID

    Returns:
        List of followed user IDs
    """
    graph = db.get_engagement_graph(user_id)
    return {"user_id": user_id, "following": graph.following}


@app.post("/users/{user_id}/follow/{target_user_id}")
async def follow_user(user_id: str, target_user_id: str):
    """
    Add a follow relationship

    Args:
        user_id: User ID doing the following
        target_user_id: User ID to follow

    Returns:
        Success message
    """
    if not db.get_user(target_user_id):
        raise HTTPException(status_code=404, detail="Target user not found")

    db.add_following(user_id, target_user_id)
    return {"message": f"User {user_id} now follows {target_user_id}"}


# ==================== Analytics Endpoints ====================


@app.get("/analytics/stats")
async def get_system_stats():
    """
    Get system statistics

    Returns:
        System statistics
    """
    return {
        "total_users": len(db.get_all_users()),
        "total_tweets": len(db.get_all_tweets()),
        "trending_topics": db.get_trending_topics(),
        "personas": list(UserPersona),
    }


# ==================== Trending & Search Endpoints ====================


@app.get("/api/trending/topics")
async def get_trending_topics(
    hours: int = Query(24, ge=1, le=720),
    limit: int = Query(10, ge=1, le=50)
):
    """
    Get trending topics for the specified time window.

    Args:
        hours: Look-back window in hours (1-720, default 24)
        limit: Max topics to return (1-50, default 10)

    Returns:
        List of trending topics sorted by engagement
    """
    from collections import Counter
    from datetime import timedelta

    tweets = db.get_all_tweets()
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
    recent_tweets = [t for t in tweets if t.created_at >= cutoff_time]

    topic_data = {}
    for tweet in recent_tweets:
        for topic in tweet.topics:
            if topic not in topic_data:
                topic_data[topic] = {"count": 0, "engagement": 0}
            topic_data[topic]["count"] += 1
            topic_data[topic]["engagement"] += tweet.likes + tweet.retweets + tweet.replies

    trending = [
        {
            "topic": topic,
            "tweet_count": data["count"],
            "engagement_score": data["engagement"],
            "growth_rate": data["count"] / hours
        }
        for topic, data in topic_data.items()
        if data["count"] >= 2
    ]

    trending.sort(key=lambda x: x["engagement_score"], reverse=True)
    return trending[:limit]


@app.get("/api/trending/discourse-metrics")
async def get_discourse_metrics():
    """
    Get current discourse metrics (topics, engagement, diversity).

    Returns:
        Discourse metrics and patterns
    """
    from collections import Counter

    tweets = db.get_all_tweets()

    if not tweets:
        return {
            "total_tweets": 0,
            "average_engagement": 0,
            "top_topics": [],
            "diversity_index": 0.0
        }

    topic_counts = Counter()
    for tweet in tweets:
        topic_counts.update(tweet.topics)

    total_engagement = sum(t.likes + t.retweets + t.replies for t in tweets)
    avg_engagement = total_engagement / len(tweets)

    return {
        "total_tweets": len(tweets),
        "average_engagement": avg_engagement,
        "top_topics": [t[0] for t in topic_counts.most_common(5)],
        "topic_distribution": dict(topic_counts.most_common(10)),
        "diversity_index": min(len(topic_counts) / 20, 1.0)
    }


@app.get("/api/search/tweets")
async def search_tweets(
    q: str = Query(..., min_length=1, max_length=100),
    limit: int = Query(20, ge=1, le=100)
):
    """
    Full-text search for tweets.

    Args:
        q: Search query
        limit: Max results

    Returns:
        List of matching tweets
    """
    tweets = db.get_all_tweets()
    q_lower = q.lower()

    results = []
    for tweet in tweets:
        relevance = 0
        if q_lower in tweet.content.lower():
            relevance = 1.0
        else:
            # Check topics
            for topic in tweet.topics:
                if q_lower in topic.lower():
                    relevance = max(relevance, 0.7)

        if relevance > 0:
            author = db.get_user(tweet.author_id)
            results.append({
                "tweet_id": tweet.tweet_id,
                "content": tweet.content[:100],
                "author": author.username if author else "Unknown",
                "relevance": relevance,
                "engagement": tweet.likes + tweet.retweets + tweet.replies
            })

    results.sort(key=lambda x: (x["relevance"], x["engagement"]), reverse=True)
    return results[:limit]


@app.get("/api/search/users")
async def search_users(
    q: str = Query(..., min_length=1, max_length=50),
    limit: int = Query(10, ge=1, le=50)
):
    """
    Search for users by username or interests.

    Args:
        q: Search query
        limit: Max results

    Returns:
        List of matching users
    """
    users = db.get_all_users()
    q_lower = q.lower()

    results = []
    for user in users:
        relevance = 0
        if q_lower in user.username.lower():
            relevance = 1.0
        else:
            for interest in user.interests:
                if q_lower in interest.lower():
                    relevance = max(relevance, 0.7)

        if relevance > 0:
            results.append({
                "user_id": user.user_id,
                "username": user.username,
                "persona": user.persona.value,
                "interests": user.interests[:3],
                "relevance": relevance
            })

    results.sort(key=lambda x: x["relevance"], reverse=True)
    return results[:limit]


# ==================== Health Check ====================



@app.get("/health")
async def health_check():
    """
    Health check endpoint

    Returns:
        Status message
    """
    return {
        "status": "healthy",
        "service": "X Recommendation Engine API",
        "version": "1.0.0",
    }


# ==================== Root Endpoint ====================


@app.get("/")
async def root():
    """
    API documentation

    Returns:
        API information
    """
    return {
        "message": "X Recommendation Engine API",
        "docs": "/docs",
        "endpoints": {
            "ranking": "/rank",
            "users": "/users",
            "tweets": "/tweets",
            "trending": "/topics/trending",
            "analytics": "/analytics/stats",
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
