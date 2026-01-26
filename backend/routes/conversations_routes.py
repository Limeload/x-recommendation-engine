"""
Conversation Threading Support
Manages tweet threads and conversation branches
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

router = APIRouter(prefix="/api/conversations", tags=["conversations"])

# Will be set by main.py
_db = None

def set_db(db):
    """Set the database instance"""
    global _db
    _db = db


class ConversationThread(BaseModel):
    """A conversation thread with nested replies"""
    tweet_id: str
    author_id: str
    author_name: str
    content: str
    created_at: datetime
    likes: int
    retweets: int
    replies: int
    reply_to: Optional[str] = None  # Parent tweet ID
    replies_list: List['ConversationThread'] = []


# Update model forward refs
ConversationThread.model_rebuild()


class ThreadBuilder:
    """Builds conversation threads from flat tweet structure"""

    @staticmethod
    def get_thread(tweet_id: str, max_depth: int = 10) -> Optional[ConversationThread]:
        """Reconstruct conversation thread starting from a tweet."""
        db = _db
        if not db:
            return None

        tweet = db.get_tweet(tweet_id)
        if not tweet:
            return None

        author = db.get_user(tweet.author_id)

        thread = ConversationThread(
            tweet_id=tweet.tweet_id,
            author_id=tweet.author_id,
            author_name=author.username if author else "Unknown",
            content=tweet.content,
            created_at=tweet.created_at,
            likes=tweet.likes,
            retweets=tweet.retweets,
            replies=tweet.replies,
            reply_to=tweet.reply_to,
            replies_list=[]
        )

        # Add nested replies (if max_depth not exceeded)
        if max_depth > 0:
            replies = ThreadBuilder._get_replies(tweet_id)
            thread.replies_list = [
                ThreadBuilder.get_thread(reply_id, max_depth - 1)
                for reply_id in replies
                if ThreadBuilder.get_thread(reply_id, max_depth - 1)
            ]

        return thread

    @staticmethod
    def _get_replies(tweet_id: str) -> List[str]:
        """Get all direct replies to a tweet"""
        db = _db
        if not db:
            return []

        tweets = db.get_all_tweets()
        return [t.tweet_id for t in tweets if t.reply_to == tweet_id]

    @staticmethod
    def get_conversation_chain(tweet_id: str) -> List[str]:
        """Get full conversation chain (ancestors and descendants)."""
        db = _db
        if not db:
            return [tweet_id]

        chain = [tweet_id]
        tweet = db.get_tweet(tweet_id)

        # Walk up to root
        while tweet and tweet.reply_to:
            chain.insert(0, tweet.reply_to)
            tweet = db.get_tweet(tweet.reply_to)

        return chain


@router.get("/{tweet_id}/thread")
async def get_conversation_thread(
    tweet_id: str,
    max_depth: int = 10
) -> Optional[ConversationThread]:
    """
    Get conversation thread for a tweet.

    Args:
        tweet_id: Root tweet ID
        max_depth: Maximum nesting depth (1-20, default 10)

    Returns:
        Conversation thread with nested replies

    Example:
        ```
        GET /api/conversations/tweet_1/thread?max_depth=5
        ```
    """
    if max_depth < 1 or max_depth > 20:
        raise HTTPException(status_code=400, detail="max_depth must be 1-20")

    thread = ThreadBuilder.get_thread(tweet_id, max_depth)

    if not thread:
        raise HTTPException(status_code=404, detail="Tweet not found")

    return thread


@router.get("/{tweet_id}/chain")
async def get_conversation_chain_endpoint(tweet_id: str) -> dict:
    """
    Get conversation chain (full thread from root to leaf).

    Args:
        tweet_id: Tweet to get chain for

    Returns:
        Object with chain of tweet IDs and count

    Example:
        ```
        GET /api/conversations/tweet_1/chain
        ```
    """
    chain = ThreadBuilder.get_conversation_chain(tweet_id)

    return {
        "root_tweet_id": chain[0] if chain else None,
        "current_tweet_id": tweet_id,
        "chain": chain,
        "depth": len(chain) - 1
    }


@router.get("/{tweet_id}/replies")
async def get_tweet_replies(
    tweet_id: str,
    limit: int = 50,
    sort_by: str = "recent"  # "recent", "engagement"
) -> List[dict]:
    """
    Get all direct replies to a tweet.

    Args:
        tweet_id: Parent tweet ID
        limit: Max replies (default 50)
        sort_by: Sort order - "recent" or "engagement" (default recent)

    Returns:
        List of reply tweets

    Example:
        ```
        GET /api/conversations/tweet_1/replies?limit=20&sort_by=engagement
        ```
    """
    db = _db
    if not db:
        return []

    tweets = db.get_all_tweets()
    replies = [t for t in tweets if t.reply_to == tweet_id]

    # Sort
    if sort_by == "engagement":
        replies.sort(
            key=lambda t: t.likes + t.retweets + t.replies,
            reverse=True
        )
    else:  # recent
        replies.sort(key=lambda t: t.created_at, reverse=True)

    # Format response
    result = []
    for reply in replies[:limit]:
        author = db.get_user(reply.author_id)
        result.append({
            "tweet_id": reply.tweet_id,
            "author_id": reply.author_id,
            "author_name": author.username if author else "Unknown",
            "content": reply.content,
            "created_at": reply.created_at,
            "engagement": {
                "likes": reply.likes,
                "retweets": reply.retweets,
                "replies": reply.replies
            }
        })

    return result


class RootTweet(BaseModel):
    """Root tweet of a conversation"""
    tweet_id: str
    author_id: str
    author_name: str
    content: str
    created_at: datetime
    reply_count: int


@router.get("/{tweet_id}/root")
async def get_conversation_root(tweet_id: str) -> 'RootTweet':
    """
    Get the root tweet of a conversation thread.

    Args:
        tweet_id: Any tweet in the thread

    Returns:
        Root tweet info

    Example:
        ```
        GET /api/conversations/tweet_1/root
        ```
    """
    db = _db
    if not db:
        raise HTTPException(status_code=503, detail="Database not available")

    if not tweet:
        raise HTTPException(status_code=404, detail="Tweet not found")

    # Walk up to root
    while tweet.reply_to:
        parent = db.get_tweet(tweet.reply_to)
        if not parent:
            break
        tweet = parent

    author = db.get_user(tweet.author_id)

    # Count replies
    all_tweets = db.get_all_tweets()
    reply_count = sum(1 for t in all_tweets if t.reply_to == tweet.tweet_id)

    return RootTweet(
        tweet_id=tweet.tweet_id,
        author_id=tweet.author_id,
        author_name=author.username if author else "Unknown",
        content=tweet.content,
        created_at=tweet.created_at,
        reply_count=reply_count
    )
