"""
User Profile Routes
Get user profile information and tweet history
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

router = APIRouter(prefix="/api/profiles", tags=["profiles"])

# Will be set by main.py
_db = None

def set_db(db):
    """Set the database instance"""
    global _db
    _db = db


class UserProfile(BaseModel):
    """Complete user profile information"""
    user_id: str
    username: str
    persona: str
    bio: str
    follower_count: int
    following_count: int
    tweet_count: int
    created_at: datetime
    interests: List[str]
    expertise_areas: List[str]
    average_engagement_per_tweet: float
    total_engagement: int


class UserStats(BaseModel):
    """User engagement statistics"""
    user_id: str
    total_tweets: int
    total_likes: int
    total_retweets: int
    total_replies: int
    total_bookmarks: int
    average_engagement_per_tweet: float
    most_engaged_topics: List[str]
    follower_count: int
    following_count: int


@router.get("/{user_id}")
async def get_user_profile(user_id: str) -> UserProfile:
    """
    Get complete user profile.

    Args:
        user_id: User ID to fetch

    Returns:
        User profile with stats

    Example:
        ```
        GET /api/profiles/user_1
        ```
    """
    db = _db
    if not db:
        raise HTTPException(status_code=503, detail="Database not available")

    user = db.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get user's tweets
    all_tweets = db.get_all_tweets()
    user_tweets = [t for t in all_tweets if t.author_id == user_id]

    # Calculate stats
    total_engagement = sum(
        t.likes + t.retweets + t.replies for t in user_tweets
    )
    avg_engagement = (total_engagement / len(user_tweets)) if user_tweets else 0

    # Get follower/following counts
    all_users = db.get_all_users()
    following_count = len([u for u in all_users if db.is_following(user_id, u.user_id)])
    follower_count = len([u for u in all_users if db.is_following(u.user_id, user_id)])

    return UserProfile(
        user_id=user.user_id,
        username=user.username,
        persona=user.persona.value,
        bio=user.bio,
        follower_count=follower_count,
        following_count=following_count,
        tweet_count=len(user_tweets),
        created_at=user.created_at,
        interests=user.interests,
        expertise_areas=user.expertise_areas,
        average_engagement_per_tweet=avg_engagement,
        total_engagement=total_engagement
    )


@router.get("/{user_id}/stats")
async def get_user_stats(db, user_id: str) -> UserStats:
    """
    Get detailed user engagement statistics.

    Args:
        user_id: User ID

    Returns:
        User statistics

    Example:
        ```
        GET /api/profiles/user_1/stats
        ```
    """
    user = db.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    all_tweets = db.get_all_tweets()
    user_tweets = [t for t in all_tweets if t.author_id == user_id]

    total_likes = sum(t.likes for t in user_tweets)
    total_retweets = sum(t.retweets for t in user_tweets)
    total_replies = sum(t.replies for t in user_tweets)
    total_bookmarks = sum(t.bookmarks for t in user_tweets)

    total_engagement = total_likes + total_retweets + total_replies + total_bookmarks
    avg_engagement = (total_engagement / len(user_tweets)) if user_tweets else 0

    # Most engaged topics
    topic_engagement = {}
    for tweet in user_tweets:
        for topic in tweet.topics:
            if topic not in topic_engagement:
                topic_engagement[topic] = 0
            topic_engagement[topic] += (
                tweet.likes + tweet.retweets + tweet.replies
            )

    most_engaged = sorted(
        topic_engagement.items(),
        key=lambda x: x[1],
        reverse=True
    )
    most_engaged_topics = [t[0] for t in most_engaged[:5]]

    # Follower/following counts
    all_users = db.get_all_users()
    following_count = len([u for u in all_users if db.is_following(user_id, u.user_id)])
    follower_count = len([u for u in all_users if db.is_following(u.user_id, user_id)])

    return UserStats(
        user_id=user_id,
        total_tweets=len(user_tweets),
        total_likes=total_likes,
        total_retweets=total_retweets,
        total_replies=total_replies,
        total_bookmarks=total_bookmarks,
        average_engagement_per_tweet=avg_engagement,
        most_engaged_topics=most_engaged_topics,
        follower_count=follower_count,
        following_count=following_count
    )


@router.get("/{user_id}/tweets")
async def get_user_tweets(
    db,
    user_id: str,
    limit: int = 50,
    sort_by: str = "recent"  # "recent", "engagement"
) -> List[dict]:
    """
    Get tweets from a user.

    Args:
        user_id: User ID
        limit: Max tweets (default 50)
        sort_by: Sort order - "recent" or "engagement"

    Returns:
        List of tweets

    Example:
        ```
        GET /api/profiles/user_1/tweets?limit=20&sort_by=engagement
        ```
    """
    user = db.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    all_tweets = db.get_all_tweets()
    user_tweets = [t for t in all_tweets if t.author_id == user_id]

    # Sort
    if sort_by == "engagement":
        user_tweets.sort(
            key=lambda t: t.likes + t.retweets + t.replies,
            reverse=True
        )
    else:  # recent
        user_tweets.sort(key=lambda t: t.created_at, reverse=True)

    # Format
    result = []
    for tweet in user_tweets[:limit]:
        result.append({
            "tweet_id": tweet.tweet_id,
            "content": tweet.content,
            "created_at": tweet.created_at,
            "topics": tweet.topics,
            "engagement": {
                "likes": tweet.likes,
                "retweets": tweet.retweets,
                "replies": tweet.replies,
                "bookmarks": tweet.bookmarks
            }
        })

    return result


@router.get("/{user_id}/following")
async def get_user_following(db, user_id: str, limit: int = 100) -> List[dict]:
    """
    Get users that this user follows.

    Args:
        user_id: User ID
        limit: Max users (default 100)

    Returns:
        List of followed users

    Example:
        ```
        GET /api/profiles/user_1/following?limit=50
        ```
    """
    all_users = db.get_all_users()
    following = [
        u for u in all_users
        if db.is_following(user_id, u.user_id)
    ]

    result = []
    for user in following[:limit]:
        result.append({
            "user_id": user.user_id,
            "username": user.username,
            "persona": user.persona.value,
            "interests": user.interests,
        })

    return result


@router.get("/{user_id}/followers")
async def get_user_followers(db, user_id: str, limit: int = 100) -> List[dict]:
    """
    Get followers of this user.

    Args:
        user_id: User ID
        limit: Max followers (default 100)

    Returns:
        List of followers

    Example:
        ```
        GET /api/profiles/user_1/followers?limit=50
        ```
    """
    all_users = db.get_all_users()
    followers = [
        u for u in all_users
        if db.is_following(u.user_id, user_id)
    ]

    result = []
    for user in followers[:limit]:
        result.append({
            "user_id": user.user_id,
            "username": user.username,
            "persona": user.persona.value,
            "interests": user.interests,
        })

    return result
