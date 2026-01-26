"""
WebSocket Broadcasting Utilities
Helper functions to emit real-time events to connected clients
"""

import asyncio
from typing import Dict, List, Any, Optional
from routes.websocket_manager import get_websocket_manager
import logging

logger = logging.getLogger(__name__)


async def broadcast_notification(user_id: str, notification_data: Dict[str, Any]):
    """
    Broadcast a notification to a user via WebSocket

    Args:
        user_id: Target user ID
        notification_data: Notification data to send
    """
    try:
        manager = get_websocket_manager()
        await manager.broadcast_notification(user_id, notification_data)
    except Exception as e:
        logger.error(f"Failed to broadcast notification to {user_id}: {e}")


async def broadcast_trending_update(trending_topics: List[Dict[str, Any]]):
    """
    Broadcast trending topics update to all connected clients

    Args:
        trending_topics: List of trending topics
    """
    try:
        manager = get_websocket_manager()
        await manager.broadcast_trending(trending_topics)
    except Exception as e:
        logger.error(f"Failed to broadcast trending update: {e}")


async def broadcast_feed_update(user_id: str, new_tweets: List[Dict[str, Any]]):
    """
    Broadcast new tweets in feed to a user

    Args:
        user_id: Target user ID
        new_tweets: List of new tweets
    """
    try:
        manager = get_websocket_manager()
        await manager.broadcast_feed_update(user_id, new_tweets)
    except Exception as e:
        logger.error(f"Failed to broadcast feed update to {user_id}: {e}")


async def broadcast_engagement_update(tweet_id: str, engagement_metrics: Dict[str, int]):
    """
    Broadcast engagement update for a tweet

    Args:
        tweet_id: Tweet ID
        engagement_metrics: Updated engagement counts
    """
    try:
        manager = get_websocket_manager()
        await manager.broadcast_engagement_update(tweet_id, engagement_metrics)
    except Exception as e:
        logger.error(f"Failed to broadcast engagement update for tweet {tweet_id}: {e}")


async def broadcast_typing_indicator(user_id: str, is_typing: bool):
    """
    Broadcast typing indicator to all users

    Args:
        user_id: User who is typing
        is_typing: Whether user is typing
    """
    try:
        manager = get_websocket_manager()
        await manager.broadcast_typing_indicator(user_id, is_typing)
    except Exception as e:
        logger.error(f"Failed to broadcast typing indicator for {user_id}: {e}")
