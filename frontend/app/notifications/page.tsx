'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import Link from 'next/link';
import { Heart, Repeat, ChatCircle, UserPlus, Bell } from 'phosphor-react';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const WS_BASE_URL = API_BASE_URL.replace(/^http/, 'ws');

interface Notification {
  id: string;
  type: 'like' | 'reply' | 'retweet' | 'follow' | 'mention';
  actor: string;
  content?: string;
  tweet_id?: string;
  created_at: string;
}

const TYPE_META: Record<string, { icon: React.ElementType; color: string; label: string }> = {
  like: { icon: Heart, color: 'text-red-500', label: 'liked your post' },
  reply: { icon: ChatCircle, color: 'text-blue-500', label: 'replied to your post' },
  retweet: { icon: Repeat, color: 'text-green-500', label: 'reposted your post' },
  follow: { icon: UserPlus, color: 'text-purple-500', label: 'followed you' },
  mention: { icon: ChatCircle, color: 'text-orange-500', label: 'mentioned you' },
};

function getTimeAgo(dateStr: string): string {
  const diff = (Date.now() - new Date(dateStr).getTime()) / 1000;
  if (diff < 60) return 'just now';
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
  return `${Math.floor(diff / 86400)}d ago`;
}

// Simulated notification types for when the WS delivers raw engagement events
function eventToNotification(event: Record<string, unknown>, idx: number): Notification {
  return {
    id: `notif_${idx}_${Date.now()}`,
    type: (event.type as Notification['type']) ?? 'like',
    actor: (event.actor as string) ?? (event.user_id as string) ?? 'someone',
    content: event.content as string | undefined,
    tweet_id: event.tweet_id as string | undefined,
    created_at: (event.created_at as string) ?? new Date().toISOString(),
  };
}

export default function NotificationsPage() {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [wsStatus, setWsStatus] = useState<'connecting' | 'connected' | 'disconnected'>('connecting');
  const wsRef = useRef<WebSocket | null>(null);

  // Seed some notifications from HTTP on load
  useEffect(() => {
    fetch(`${API_BASE_URL}/api/notifications?user_id=user_0&limit=20`)
      .then(r => r.json())
      .then(data => {
        if (Array.isArray(data)) {
          setNotifications(data.map((n, i) => eventToNotification(n as Record<string, unknown>, i)));
        }
      })
      .catch(() => {
        // Backend may not have this endpoint yet — seed demo notifications
        const demo: Notification[] = [
          { id: 'demo_1', type: 'like', actor: 'trader_alpha', created_at: new Date(Date.now() - 120000).toISOString() },
          { id: 'demo_2', type: 'follow', actor: 'politician_Rep', created_at: new Date(Date.now() - 300000).toISOString() },
          { id: 'demo_3', type: 'retweet', actor: 'meme_account_dank', content: 'POV: you just discovered AI', created_at: new Date(Date.now() - 600000).toISOString() },
          { id: 'demo_4', type: 'reply', actor: 'engineer_pro', content: 'Great take on the infrastructure gap!', created_at: new Date(Date.now() - 900000).toISOString() },
          { id: 'demo_5', type: 'like', actor: 'founder_x', created_at: new Date(Date.now() - 1200000).toISOString() },
        ];
        setNotifications(demo);
      });
  }, []);

  // WebSocket for real-time notifications
  const connect = useCallback(() => {
    const ws = new WebSocket(`${WS_BASE_URL}/ws/notifications/user_0`);
    wsRef.current = ws;

    ws.onopen = () => setWsStatus('connected');
    ws.onclose = () => {
      setWsStatus('disconnected');
      setTimeout(connect, 5000); // auto-reconnect
    };
    ws.onerror = () => setWsStatus('disconnected');
    ws.onmessage = event => {
      try {
        const data = JSON.parse(event.data) as Record<string, unknown>;
        if (data.type === 'notification' || data.type === 'engagement') {
          setNotifications(prev => [
            eventToNotification(data, prev.length),
            ...prev.slice(0, 49), // keep latest 50
          ]);
        }
      } catch {
        // ignore malformed frames
      }
    };
  }, []);

  useEffect(() => {
    connect();
    return () => wsRef.current?.close();
  }, [connect]);

  return (
    <div className="flex flex-col h-full">
      <header className="border-b border-gray-200 sticky top-0 bg-white z-40 px-6 py-3 flex items-center justify-between">
        <div>
          <h1 className="text-base font-semibold text-gray-900">Notifications</h1>
          <p className="text-xs text-gray-400">Showing for user_0</p>
        </div>
        <div className={`flex items-center gap-1.5 text-xs px-2 py-1 rounded-full ${
          wsStatus === 'connected'
            ? 'bg-green-100 text-green-700'
            : wsStatus === 'connecting'
            ? 'bg-yellow-100 text-yellow-700'
            : 'bg-red-100 text-red-700'
        }`}>
          <span className="w-1.5 h-1.5 rounded-full bg-current" />
          {wsStatus === 'connected' ? 'Live' : wsStatus === 'connecting' ? 'Connecting…' : 'Reconnecting…'}
        </div>
      </header>

      <div className="overflow-y-auto">
        {notifications.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-20 text-gray-400">
            <Bell size={48} weight="light" />
            <p className="mt-4 text-sm">No notifications yet.</p>
            <p className="text-xs mt-1">They'll appear here as agents engage.</p>
          </div>
        ) : (
          <div>
            {notifications.map(n => {
              const meta = TYPE_META[n.type] ?? TYPE_META.like;
              const Icon = meta.icon;
              return (
                <div
                  key={n.id}
                  className="flex items-start gap-4 px-6 py-4 border-b border-gray-100 hover:bg-gray-50 transition"
                >
                  <div className={`mt-0.5 ${meta.color}`}>
                    <Icon size={20} weight="fill" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-gray-900">
                      <span className="font-semibold">{n.actor}</span>
                      {' '}
                      <span className="text-gray-600">{meta.label}</span>
                    </p>
                    {n.content && (
                      <p className="mt-1 text-sm text-gray-500 line-clamp-2 italic">
                        "{n.content}"
                      </p>
                    )}
                    <p className="mt-1 text-xs text-gray-400">{getTimeAgo(n.created_at)}</p>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        <div className="px-6 py-4 text-xs text-gray-400 border-t border-gray-100">
          Notifications stream live via WebSocket as agents interact with your posts.
        </div>
      </div>
    </div>
  );
}
