"""
WebSocket Routes for Real-Time Updates
Handles connections for notifications, trending topics, and feed updates
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from routes.websocket_manager import get_websocket_manager
import logging

logger = logging.getLogger(__name__)


class WebSocketStats(BaseModel):
    """WebSocket connection statistics"""
    active_users: int
    total_user_connections: int
    global_connections: int
    total_connections: int

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/notifications/{user_id}")
async def websocket_notifications(websocket: WebSocket, user_id: str):
    """
    WebSocket endpoint for user notifications

    Subscribes to real-time notifications for a specific user:
    - Engagement notifications (likes, replies, retweets)
    - Follow notifications
    - Mention notifications

    Example message received:
    ```json
    {
      "type": "notification",
      "timestamp": "2026-01-25T10:30:00",
      "data": {
        "notification_id": "n1",
        "type": "LIKE",
        "actor_id": "user_2",
        "actor_name": "Jane Investor",
        "tweet_id": "t1"
      }
    }
    ```

    Args:
        websocket: WebSocket connection
        user_id: Target user ID
    """
    manager = get_websocket_manager()
    await manager.connect(websocket, user_id)
    logger.info(f"User {user_id} subscribed to notifications")

    try:
        while True:
            # Keep connection alive and receive any client messages
            data = await websocket.receive_text()
            # Client can send ping/heartbeat messages to keep connection alive
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        await manager.disconnect(websocket, user_id)
        logger.info(f"User {user_id} unsubscribed from notifications")


@router.websocket("/ws/trending")
async def websocket_trending(websocket: WebSocket):
    """
    WebSocket endpoint for real-time trending topics

    Subscribes to live updates about trending topics:
    - New trending topics emerge
    - Topic engagement metrics update
    - Topic rankings change

    Example message received:
    ```json
    {
      "type": "trending",
      "timestamp": "2026-01-25T10:30:00",
      "data": {
        "topics": [
          {
            "topic": "AI",
            "tweet_count": 250,
            "engagement_score": 8.7,
            "growth_rate": 0.15
          }
        ],
        "count": 10
      }
    }
    ```

    Args:
        websocket: WebSocket connection
    """
    manager = get_websocket_manager()
    await manager.connect_global(websocket)
    logger.info("Client subscribed to trending topics")

    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
        logger.info("Client unsubscribed from trending topics")


@router.websocket("/ws/feed/{user_id}")
async def websocket_feed(websocket: WebSocket, user_id: str):
    """
    WebSocket endpoint for real-time feed updates

    Subscribes to new tweets in the user's feed:
    - New tweets from followed users
    - Recommended tweets based on interests
    - Trending content

    Example message received:
    ```json
    {
      "type": "feed_update",
      "timestamp": "2026-01-25T10:30:00",
      "data": {
        "tweets": [
          {
            "tweet_id": "t1",
            "author_id": "a1",
            "content": "Just closed a Series A round...",
            "topics": ["Fundraising", "Startups"]
          }
        ],
        "count": 1
      }
    }
    ```

    Args:
        websocket: WebSocket connection
        user_id: Target user ID
    """
    manager = get_websocket_manager()
    await manager.connect(websocket, user_id)
    logger.info(f"User {user_id} subscribed to feed updates")

    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        await manager.disconnect(websocket, user_id)
        logger.info(f"User {user_id} unsubscribed from feed updates")


@router.websocket("/ws/engagement/{tweet_id}")
async def websocket_engagement(websocket: WebSocket, tweet_id: str):
    """
    WebSocket endpoint for real-time engagement updates

    Subscribes to engagement metrics for a specific tweet:
    - Like count changes
    - Reply count changes
    - Retweet count changes

    Example message received:
    ```json
    {
      "type": "engagement_update",
      "timestamp": "2026-01-25T10:30:00",
      "data": {
        "tweet_id": "t1",
        "engagement": {
          "likes": 152,
          "replies": 13,
          "retweets": 45
        }
      }
    }
    ```

    Args:
        websocket: WebSocket connection
        tweet_id: Target tweet ID
    """
    manager = get_websocket_manager()
    await manager.connect_global(websocket)
    logger.info(f"Client subscribed to engagement updates for tweet {tweet_id}")

    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
        logger.info(f"Client unsubscribed from engagement updates for tweet {tweet_id}")


@router.get("/ws/stats", response_model=WebSocketStats)
async def get_websocket_stats() -> WebSocketStats:
    """
    Get real-time WebSocket connection statistics

    Returns:
        WebSocketStats with connection stats:
        - active_users: Number of users with open connections
        - total_user_connections: Total user-specific connections
        - global_connections: Total global broadcast connections
        - total_connections: Sum of all connections
    """
    manager = get_websocket_manager()
    stats = manager.get_connection_stats()
    return WebSocketStats(**stats)
