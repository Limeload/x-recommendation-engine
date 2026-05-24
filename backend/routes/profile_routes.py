"""
User Profile Routes
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List
from models.schemas import Tweet

router = APIRouter(prefix="/api/profiles", tags=["profiles"])

_db = None


def set_db(db):
    global _db
    _db = db


def _following_set(user_id: str) -> set:
    graph = _db.get_engagement_graph(user_id)
    return set(graph.following)


@router.get("/{user_id}")
async def get_user_profile(user_id: str):
    if not _db:
        raise HTTPException(status_code=503, detail="Database not available")
    user = _db.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_tweets = [t for t in _db.get_all_tweets() if t.author_id == user_id]
    total_engagement = sum(t.likes + t.retweets + t.replies for t in user_tweets)
    avg_engagement = (total_engagement / len(user_tweets)) if user_tweets else 0.0

    graph = _db.get_engagement_graph(user_id)

    return {
        "user_id": user.user_id,
        "username": user.username,
        "persona": user.persona.value,
        "bio": user.bio,
        "follower_count": len(graph.followers),
        "following_count": len(graph.following),
        "tweet_count": len(user_tweets),
        "created_at": user.created_at,
        "interests": user.interests,
        "expertise_areas": user.expertise_areas,
        "average_engagement_per_tweet": avg_engagement,
        "total_engagement": total_engagement,
    }


@router.get("/{user_id}/tweets", response_model=List[Tweet])
async def get_user_tweets(
    user_id: str,
    limit: int = Query(50, le=100),
    sort_by: str = Query("recent"),
):
    if not _db:
        raise HTTPException(status_code=503, detail="Database not available")
    if not _db.get_user(user_id):
        raise HTTPException(status_code=404, detail="User not found")

    user_tweets = [t for t in _db.get_all_tweets() if t.author_id == user_id]

    if sort_by == "engagement":
        user_tweets.sort(key=lambda t: t.likes + t.retweets + t.replies, reverse=True)
    else:
        user_tweets.sort(key=lambda t: t.created_at, reverse=True)

    return user_tweets[:limit]


@router.get("/{user_id}/stats")
async def get_user_stats(user_id: str):
    if not _db:
        raise HTTPException(status_code=503, detail="Database not available")
    user = _db.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_tweets = [t for t in _db.get_all_tweets() if t.author_id == user_id]
    total_likes = sum(t.likes for t in user_tweets)
    total_retweets = sum(t.retweets for t in user_tweets)
    total_replies = sum(t.replies for t in user_tweets)
    total_bookmarks = sum(t.bookmarks for t in user_tweets)
    total_engagement = total_likes + total_retweets + total_replies + total_bookmarks
    avg_engagement = (total_engagement / len(user_tweets)) if user_tweets else 0.0

    topic_engagement: dict = {}
    for tweet in user_tweets:
        for topic in tweet.topics:
            topic_engagement[topic] = topic_engagement.get(topic, 0) + tweet.likes + tweet.retweets
    most_engaged_topics = sorted(topic_engagement, key=topic_engagement.get, reverse=True)[:5]  # type: ignore

    graph = _db.get_engagement_graph(user_id)

    return {
        "user_id": user_id,
        "total_tweets": len(user_tweets),
        "total_likes": total_likes,
        "total_retweets": total_retweets,
        "total_replies": total_replies,
        "total_bookmarks": total_bookmarks,
        "average_engagement_per_tweet": avg_engagement,
        "most_engaged_topics": most_engaged_topics,
        "follower_count": len(graph.followers),
        "following_count": len(graph.following),
    }
