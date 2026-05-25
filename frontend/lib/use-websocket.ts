'use client';

/**
 * React hooks for WebSocket integration
 * Provides easy integration of real-time WebSocket events with React components
 */

import { useEffect, useCallback, useState } from 'react';
import { RecommendationEngineWebSocket } from './websocket-client';

/**
 * Hook to subscribe to notifications
 */
export function useNotifications(userId: string) {
  const [notifications, setNotifications] = useState<any[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    const ws = new RecommendationEngineWebSocket();

    ws.subscribeToNotifications(userId, (message) => {
      if (message.type === 'notification') {
        setNotifications((prev) => [message.data, ...prev]);
        if (!message.data.read) {
          setUnreadCount((prev) => prev + 1);
        }
      }
    });

    return () => {
      ws.unsubscribe(`notifications-${userId}`);
    };
  }, [userId]);

  return { notifications, unreadCount };
}

/**
 * Hook to subscribe to trending topics
 */
export function useTrending() {
  const [trending, setTrending] = useState<any[]>([]);

  useEffect(() => {
    const ws = new RecommendationEngineWebSocket();

    ws.subscribeToTrending((message) => {
      if (message.type === 'trending') {
        setTrending(message.data.topics || []);
      }
    });

    return () => {
      ws.unsubscribe('trending');
    };
  }, []);

  return { trending };
}

/**
 * Hook to subscribe to feed updates
 */
export function useFeedUpdates(userId: string) {
  const [newTweets, setNewTweets] = useState<any[]>([]);

  useEffect(() => {
    const ws = new RecommendationEngineWebSocket();

    ws.subscribeToFeed(userId, (message) => {
      if (message.type === 'feed_update') {
        setNewTweets(message.data.tweets || []);
      }
    });

    return () => {
      ws.unsubscribe(`feed-${userId}`);
    };
  }, [userId]);

  return { newTweets };
}

/**
 * Hook to subscribe to engagement updates
 */
export function useEngagementUpdates(tweetId: string) {
  const [engagement, setEngagement] = useState<any>(null);

  useEffect(() => {
    const ws = new RecommendationEngineWebSocket();

    ws.subscribeToEngagement(tweetId, (message) => {
      if (message.type === 'engagement_update') {
        setEngagement(message.data.engagement);
      }
    });

    return () => {
      ws.unsubscribe(`engagement-${tweetId}`);
    };
  }, [tweetId]);

  return { engagement };
}

/**
 * Example usage in a component:
 *
 * export function NotificationCenter({ userId }: { userId: string }) {
 *   const { notifications, unreadCount } = useNotifications(userId);
 *
 *   return (
 *     <div className="notification-center">
 *       <h2>Notifications ({unreadCount})</h2>
 *       <ul>
 *         {notifications.map((notif) => (
 *           <li key={notif.notification_id}>
 *             <p>{notif.actor_name} {notif.type}d your tweet</p>
 *             <time>{new Date(notif.created_at).toLocaleString()}</time>
 *           </li>
 *         ))}
 *       </ul>
 *     </div>
 *   );
 * }
 *
 * export function TrendingTopics() {
 *   const { trending } = useTrending();
 *
 *   return (
 *     <div className="trending">
 *       <h3>Trending Now</h3>
 *       <ul>
 *         {trending.map((topic) => (
 *           <li key={topic.topic}>
 *             <strong>{topic.topic}</strong>
 *             <span>{topic.tweet_count} tweets</span>
 *           </li>
 *         ))}
 *       </ul>
 *     </div>
 *   );
 * }
 *
 * export function TweetCard({ tweet }: { tweet: any }) {
 *   const { engagement } = useEngagementUpdates(tweet.tweet_id);
 *
 *   return (
 *     <div className="tweet">
 *       <p>{tweet.content}</p>
 *       <div className="engagement">
 *         <span>👍 {engagement?.likes || tweet.engagement.likes}</span>
 *         <span>💬 {engagement?.replies || tweet.engagement.replies}</span>
 *         <span>🔄 {engagement?.retweets || tweet.engagement.retweets}</span>
 *       </div>
 *     </div>
 *   );
 * }
 */
