"""
Notifications System
Tracks user engagements (likes, replies, retweets) on their tweets
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


class NotificationType(str, Enum):
    """Types of notifications"""
    LIKE = "like"
    RETWEET = "retweet"
    REPLY = "reply"
    FOLLOW = "follow"
    MENTION = "mention"


class Notification(BaseModel):
    """A notification for a user"""
    notification_id: str
    user_id: str  # Notification recipient
    actor_id: str  # User who triggered notification
    actor_name: str
    type: NotificationType
    tweet_id: Optional[str]
    content: Optional[str]  # For replies
    created_at: datetime
    read: bool = False


class NotificationManager:
    """Manages user notifications"""

    def __init__(self):
        self.notifications: List[Notification] = []
        self._notification_counter = 0

    def add_notification(
        self,
        user_id: str,
        actor_id: str,
        actor_name: str,
        notification_type: NotificationType,
        tweet_id: Optional[str] = None,
        content: Optional[str] = None
    ) -> Notification:
        """Create and store a notification"""
        notification = Notification(
            notification_id=f"notif_{self._notification_counter}",
            user_id=user_id,
            actor_id=actor_id,
            actor_name=actor_name,
            type=notification_type,
            tweet_id=tweet_id,
            content=content,
            created_at=datetime.utcnow(),
            read=False
        )
        self.notifications.append(notification)
        self._notification_counter += 1
        return notification

    def get_user_notifications(
        self,
        user_id: str,
        unread_only: bool = False,
        limit: int = 50
    ) -> List[Notification]:
        """Get notifications for a user"""
        notifications = [
            n for n in self.notifications
            if n.user_id == user_id
        ]

        if unread_only:
            notifications = [n for n in notifications if not n.read]

        # Sort by recent first
        notifications.sort(key=lambda n: n.created_at, reverse=True)
        return notifications[:limit]

    def mark_as_read(self, notification_id: str) -> bool:
        """Mark a notification as read"""
        for notif in self.notifications:
            if notif.notification_id == notification_id:
                notif.read = True
                return True
        return False

    def mark_all_read(self, user_id: str) -> int:
        """Mark all notifications as read for a user"""
        count = 0
        for notif in self.notifications:
            if notif.user_id == user_id and not notif.read:
                notif.read = True
                count += 1
        return count

    def get_unread_count(self, user_id: str) -> int:
        """Get count of unread notifications"""
        return sum(
            1 for n in self.notifications
            if n.user_id == user_id and not n.read
        )


# Global notification manager
notification_manager = NotificationManager()


def init_notification_manager(manager: NotificationManager):
    """Initialize the global notification manager"""
    global notification_manager
    notification_manager = manager


@router.get("/{user_id}")
async def get_notifications(
    user_id: str,
    unread_only: bool = False,
    limit: int = 50
) -> List[Notification]:
    """
    Get notifications for a user.

    Args:
        user_id: User to get notifications for
        unread_only: Only unread notifications (default False)
        limit: Max notifications (default 50)

    Returns:
        List of notifications sorted by recency

    Example:
        ```
        GET /api/notifications/user_1?unread_only=false&limit=20
        ```
    """
    return notification_manager.get_user_notifications(user_id, unread_only, limit)


@router.get("/{user_id}/unread-count")
async def get_unread_count(user_id: str) -> dict:
    """
    Get unread notification count for a user.

    Args:
        user_id: User to count notifications for

    Returns:
        Dictionary with unread_count

    Example:
        ```
        GET /api/notifications/user_1/unread-count
        ```
    """
    count = notification_manager.get_unread_count(user_id)
    return {"unread_count": count}


@router.post("/{notification_id}/read")
async def mark_notification_read(notification_id: str) -> dict:
    """
    Mark a notification as read.

    Args:
        notification_id: Notification to mark read

    Returns:
        Success status

    Example:
        ```
        POST /api/notifications/notif_0/read
        ```
    """
    success = notification_manager.mark_as_read(notification_id)
    if not success:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"success": True}


@router.post("/{user_id}/read-all")
async def mark_all_notifications_read(user_id: str) -> dict:
    """
    Mark all notifications as read for a user.

    Args:
        user_id: User to mark notifications read

    Returns:
        Count of marked notifications

    Example:
        ```
        POST /api/notifications/user_1/read-all
        ```
    """
    count = notification_manager.mark_all_read(user_id)
    return {"marked_read": count}


class NotificationStats(BaseModel):
    """Notification statistics"""
    user_id: str
    total_notifications: int
    unread_count: int
    likes_count: int
    replies_count: int
    retweets_count: int
    follows_count: int


@router.get("/{user_id}/stats")
async def get_notification_stats(user_id: str) -> NotificationStats:
    """
    Get notification statistics for a user.

    Args:
        user_id: User to get stats for

    Returns:
        Notification statistics

    Example:
        ```
        GET /api/notifications/user_1/stats
        ```
    """
    notifications = notification_manager.get_user_notifications(user_id, limit=1000)

    stats = {
        "user_id": user_id,
        "total_notifications": len(notifications),
        "unread_count": sum(1 for n in notifications if not n.read),
        "likes_count": sum(1 for n in notifications if n.type == NotificationType.LIKE),
        "replies_count": sum(1 for n in notifications if n.type == NotificationType.REPLY),
        "retweets_count": sum(1 for n in notifications if n.type == NotificationType.RETWEET),
        "follows_count": sum(1 for n in notifications if n.type == NotificationType.FOLLOW),
    }

    return NotificationStats(**stats)
