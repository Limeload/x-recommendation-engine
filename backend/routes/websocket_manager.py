"""
WebSocket Manager for Real-Time Updates
Handles connections and broadcasts for notifications, trending topics, and feed updates
"""

import json
import asyncio
from typing import Set, Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class WebSocketManager:
    """Manages WebSocket connections and broadcasts real-time updates"""

    def __init__(self):
        # Active connections: {user_id: set of WebSocket connections}
        self.active_connections: Dict[str, Set] = {}
        # Global broadcast connections (for trending topics, etc.)
        self.global_connections: Set = set()

    async def connect(self, websocket, user_id: str):
        """
        Register a new WebSocket connection for a user

        Args:
            websocket: WebSocket connection
            user_id: User ID
        """
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)
        logger.info(f"WebSocket connected: user_id={user_id}, total={len(self.active_connections[user_id])}")

    async def connect_global(self, websocket):
        """
        Register a connection for global broadcasts (trending, etc.)

        Args:
            websocket: WebSocket connection
        """
        await websocket.accept()
        self.global_connections.add(websocket)
        logger.info(f"Global WebSocket connected, total={len(self.global_connections)}")

    async def disconnect(self, websocket, user_id: Optional[str] = None):
        """
        Remove a WebSocket connection

        Args:
            websocket: WebSocket connection
            user_id: User ID (if user-specific connection)
        """
        if user_id and user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
            logger.info(f"WebSocket disconnected: user_id={user_id}")

        self.global_connections.discard(websocket)

    async def broadcast_notification(self, user_id: str, notification: Dict[str, Any]):
        """
        Broadcast a notification to a specific user

        Args:
            user_id: Target user ID
            notification: Notification data
        """
        if user_id not in self.active_connections:
            return

        message = {
            "type": "notification",
            "timestamp": datetime.utcnow().isoformat(),
            "data": notification
        }

        disconnected = set()
        for connection in self.active_connections[user_id]:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.warning(f"Error sending notification to {user_id}: {e}")
                disconnected.add(connection)

        # Clean up disconnected connections
        for conn in disconnected:
            await self.disconnect(conn, user_id)

    async def broadcast_trending(self, trending_topics: list):
        """
        Broadcast trending topics update to all global connections

        Args:
            trending_topics: List of trending topics
        """
        message = {
            "type": "trending",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "topics": trending_topics,
                "count": len(trending_topics)
            }
        }

        disconnected = set()
        for connection in self.global_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.warning(f"Error sending trending update: {e}")
                disconnected.add(connection)

        # Clean up disconnected connections
        for conn in disconnected:
            await self.disconnect(conn)

    async def broadcast_feed_update(self, user_id: str, new_tweets: list):
        """
        Broadcast new tweets in user's feed

        Args:
            user_id: Target user ID
            new_tweets: List of new tweets
        """
        if user_id not in self.active_connections:
            return

        message = {
            "type": "feed_update",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "tweets": new_tweets,
                "count": len(new_tweets)
            }
        }

        disconnected = set()
        for connection in self.active_connections[user_id]:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.warning(f"Error sending feed update to {user_id}: {e}")
                disconnected.add(connection)

        # Clean up disconnected connections
        for conn in disconnected:
            await self.disconnect(conn, user_id)

    async def broadcast_engagement_update(self, tweet_id: str, engagement_update: Dict[str, Any]):
        """
        Broadcast engagement update for a tweet

        Args:
            tweet_id: Tweet ID
            engagement_update: Updated engagement metrics
        """
        message = {
            "type": "engagement_update",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "tweet_id": tweet_id,
                "engagement": engagement_update
            }
        }

        disconnected = set()
        for user_connections in self.active_connections.values():
            for connection in user_connections:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.warning(f"Error sending engagement update: {e}")
                    disconnected.add(connection)

        # Clean up disconnected connections
        for conn in disconnected:
            await self.disconnect(conn)

    async def broadcast_typing_indicator(self, user_id: str, is_typing: bool):
        """
        Broadcast typing indicator to user's followers

        Args:
            user_id: User who is typing
            is_typing: Whether user is typing
        """
        message = {
            "type": "typing",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "user_id": user_id,
                "typing": is_typing
            }
        }

        # Broadcast to all connections (simpler for MVP)
        disconnected = set()
        for user_connections in self.active_connections.values():
            for connection in user_connections:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.warning(f"Error sending typing indicator: {e}")
                    disconnected.add(connection)

        # Clean up disconnected connections
        for conn in disconnected:
            await self.disconnect(conn)

    async def send_to_user(self, user_id: str, message: Dict[str, Any]):
        """
        Send a message to a specific user

        Args:
            user_id: Target user ID
            message: Message to send
        """
        if user_id not in self.active_connections:
            return

        disconnected = set()
        for connection in self.active_connections[user_id]:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.warning(f"Error sending message to {user_id}: {e}")
                disconnected.add(connection)

        # Clean up disconnected connections
        for conn in disconnected:
            await self.disconnect(conn, user_id)

    def get_connection_stats(self) -> Dict[str, Any]:
        """
        Get WebSocket connection statistics

        Returns:
            Statistics about active connections
        """
        total_user_connections = sum(len(conns) for conns in self.active_connections.values())
        return {
            "active_users": len(self.active_connections),
            "total_user_connections": total_user_connections,
            "global_connections": len(self.global_connections),
            "total_connections": total_user_connections + len(self.global_connections)
        }


# Global WebSocket manager instance
_websocket_manager: Optional[WebSocketManager] = None


def get_websocket_manager() -> WebSocketManager:
    """Get the global WebSocket manager instance"""
    global _websocket_manager
    if _websocket_manager is None:
        _websocket_manager = WebSocketManager()
    return _websocket_manager
