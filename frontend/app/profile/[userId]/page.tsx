'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { Heart, Repeat, ChatCircle, BookmarkSimple, UserPlus, UserMinus } from 'phosphor-react';
import { User, Tweet } from '@/types';
import { PERSONA_COLOR } from '@/lib/persona';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

function getTimeAgo(dateStr: string): string {
  const diff = (Date.now() - new Date(dateStr).getTime()) / 1000;
  if (diff < 60) return 'now';
  if (diff < 3600) return `${Math.floor(diff / 60)}m`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h`;
  return `${Math.floor(diff / 86400)}d`;
}

interface FollowGraph {
  following: string[];
}

export default function ProfilePage() {
  const params = useParams();
  const userId = params.userId as string;

  const [user, setUser] = useState<User | null>(null);
  const [tweets, setTweets] = useState<Tweet[]>([]);
  const [followGraph, setFollowGraph] = useState<FollowGraph>({ following: [] });
  const [viewerFollowing, setViewerFollowing] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);

  // For demo, "viewer" is user_0
  const VIEWER_ID = 'user_0';

  useEffect(() => {
    if (!userId) return;
    setLoading(true);
    Promise.all([
      fetch(`${API_BASE_URL}/users/${userId}`).then(r => r.json()),
      fetch(`${API_BASE_URL}/api/profiles/${userId}/tweets`).then(r => r.json()).catch(() => []),
      fetch(`${API_BASE_URL}/users/${userId}/following`).then(r => r.json()).catch(() => ({ following: [] })),
      fetch(`${API_BASE_URL}/users/${VIEWER_ID}/following`).then(r => r.json()).catch(() => ({ following: [] })),
    ]).then(([u, tw, fg, vf]) => {
      setUser(u);
      setTweets(Array.isArray(tw) ? tw : []);
      setFollowGraph(fg);
      setViewerFollowing(vf.following ?? []);
    }).catch(console.error)
      .finally(() => setLoading(false));
  }, [userId]);

  const isFollowing = viewerFollowing.includes(userId);

  const toggleFollow = async () => {
    if (isFollowing) return; // unfollow not implemented — just prevent double-follow
    try {
      await fetch(`${API_BASE_URL}/users/${VIEWER_ID}/follow/${userId}`, { method: 'POST' });
      setViewerFollowing(prev => [...prev, userId]);
    } catch (e) {
      console.error(e);
    }
  };

  if (loading) {
    return (
      <div className="p-6 space-y-4">
        <div className="h-24 bg-gray-100 rounded-xl animate-pulse" />
        <div className="h-40 bg-gray-100 rounded-xl animate-pulse" />
      </div>
    );
  }

  if (!user) {
    return (
      <div className="p-6">
        <p className="text-gray-500">User not found.</p>
        <Link href="/" className="text-blue-600 text-sm mt-2 inline-block">← Back to feed</Link>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <header className="border-b border-gray-200 sticky top-0 bg-white z-40 px-6 py-3 flex items-center gap-3">
        <Link href="/" className="text-gray-400 hover:text-gray-700 text-sm">←</Link>
        <div>
          <h1 className="text-base font-semibold text-gray-900">{user.username}</h1>
          <p className="text-xs text-gray-400">{tweets.length} posts</p>
        </div>
      </header>

      <div className="overflow-y-auto">
        {/* Profile card */}
        <div className="px-6 pt-6 pb-4 border-b border-gray-200">
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-4">
              <div className={`w-16 h-16 rounded-full flex items-center justify-center text-2xl font-bold ${PERSONA_COLOR[user.persona] ?? 'bg-gray-100 text-gray-700'}`}>
                {user.username.charAt(0).toUpperCase()}
              </div>
              <div>
                <h2 className="text-xl font-bold text-gray-900">{user.username}</h2>
                <span className={`inline-block text-xs font-medium px-2.5 py-1 rounded-full mt-1 ${
                  PERSONA_COLOR[user.persona] ?? 'bg-gray-100 text-gray-700'
                }`}>
                  {user.persona.replace('_', ' ')}
                </span>
              </div>
            </div>

            {userId !== VIEWER_ID && (
              <button
                onClick={toggleFollow}
                className={`flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium transition ${
                  isFollowing
                    ? 'border border-gray-300 text-gray-700 hover:border-red-300 hover:text-red-600'
                    : 'bg-gray-900 text-white hover:bg-gray-700'
                }`}
              >
                {isFollowing ? <UserMinus size={16} /> : <UserPlus size={16} />}
                {isFollowing ? 'Following' : 'Follow'}
              </button>
            )}
          </div>

          {user.bio && (
            <p className="mt-3 text-sm text-gray-700 leading-relaxed">{user.bio}</p>
          )}

          <div className="flex gap-6 mt-4 text-sm">
            <div>
              <span className="font-bold text-gray-900">{followGraph.following.length}</span>
              <span className="text-gray-500 ml-1">Following</span>
            </div>
            <div>
              <span className="font-bold text-gray-900">
                {user.follower_count.toLocaleString()}
              </span>
              <span className="text-gray-500 ml-1">Followers</span>
            </div>
          </div>

          {user.interests.length > 0 && (
            <div className="mt-3 flex flex-wrap gap-2">
              {user.interests.map(i => (
                <span key={i} className="text-xs bg-blue-50 text-blue-700 px-2.5 py-1 rounded-full">
                  {i}
                </span>
              ))}
            </div>
          )}
        </div>

        {/* Tweets */}
        <div>
          {tweets.length === 0 ? (
            <p className="text-sm text-gray-400 px-6 py-8 text-center">No posts yet.</p>
          ) : (
            tweets.map(tweet => (
              <div key={tweet.tweet_id} className="px-6 py-4 border-b border-gray-100 hover:bg-gray-50 transition">
                <div className="flex items-center gap-2 mb-2">
                  <span className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${PERSONA_COLOR[user.persona] ?? 'bg-gray-100 text-gray-700'}`}>
                    {user.username.charAt(0).toUpperCase()}
                  </span>
                  <span className="font-semibold text-sm text-gray-900">{user.username}</span>
                  <span className="text-gray-300">·</span>
                  <span className="text-xs text-gray-400">{getTimeAgo(tweet.created_at)}</span>
                </div>

                <p className="text-sm text-gray-900 leading-relaxed whitespace-pre-wrap">
                  {tweet.content}
                </p>

                {tweet.topics.length > 0 && (
                  <div className="mt-2 flex flex-wrap gap-1.5">
                    {tweet.topics.map(t => (
                      <span key={t} className="text-xs text-blue-600 bg-blue-50 px-2 py-0.5 rounded">
                        #{t}
                      </span>
                    ))}
                  </div>
                )}

                <div className="mt-3 flex items-center gap-6 text-gray-400 text-xs">
                  <span className="flex items-center gap-1.5 hover:text-gray-700 cursor-pointer">
                    <ChatCircle size={15} /> {tweet.replies}
                  </span>
                  <span className="flex items-center gap-1.5 hover:text-gray-700 cursor-pointer">
                    <Repeat size={15} /> {tweet.retweets}
                  </span>
                  <span className="flex items-center gap-1.5 hover:text-gray-700 cursor-pointer">
                    <Heart size={15} /> {tweet.likes}
                  </span>
                  <span className="flex items-center gap-1.5 hover:text-gray-700 cursor-pointer">
                    <BookmarkSimple size={15} /> {tweet.bookmarks}
                  </span>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
