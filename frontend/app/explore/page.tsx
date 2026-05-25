'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { PERSONA_COLOR } from '@/lib/persona';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface TrendingTopic {
  topic: string;
  tweet_count: number;
  engagement_score: number;
  growth_rate: number;
}

interface DiscourseMetrics {
  total_tweets: number;
  average_engagement: number;
  top_topics: string[];
  topic_distribution: Record<string, number>;
  diversity_index: number;
}

interface UserResult {
  user_id: string;
  username: string;
  persona: string;
  interests: string[];
}

function TopicBar({ topic, count, max }: { topic: string; count: number; max: number }) {
  const pct = max > 0 ? (count / max) * 100 : 0;
  return (
    <div className="flex items-center gap-3 py-1.5">
      <span className="w-32 text-sm text-gray-700 font-medium truncate">{topic}</span>
      <div className="flex-1 bg-gray-100 rounded-full h-2 overflow-hidden">
        <div
          className="h-full bg-gray-800 rounded-full transition-all duration-500"
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className="text-xs text-gray-500 w-8 text-right">{count}</span>
    </div>
  );
}

export default function ExplorePage() {
  const [trending, setTrending] = useState<TrendingTopic[]>([]);
  const [discourse, setDiscourse] = useState<DiscourseMetrics | null>(null);
  const [users, setUsers] = useState<UserResult[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<UserResult[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const [trendRes, discourseRes, usersRes] = await Promise.all([
          fetch(`${API_BASE_URL}/api/trending/topics?limit=15`),
          fetch(`${API_BASE_URL}/api/trending/discourse-metrics`),
          fetch(`${API_BASE_URL}/users`),
        ]);
        setTrending(await trendRes.json());
        setDiscourse(await discourseRes.json());
        const allUsers = await usersRes.json();
        setUsers(allUsers.slice(0, 12));
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    };
    load();
    const interval = setInterval(load, 30000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (!searchQuery.trim()) {
      setSearchResults([]);
      return;
    }
    const timer = setTimeout(async () => {
      try {
        const res = await fetch(
          `${API_BASE_URL}/api/search/users?q=${encodeURIComponent(searchQuery)}&limit=8`
        );
        setSearchResults(await res.json());
      } catch (e) {
        console.error(e);
      }
    }, 300);
    return () => clearTimeout(timer);
  }, [searchQuery]);

  const maxCount = discourse?.topic_distribution
    ? Math.max(...Object.values(discourse.topic_distribution))
    : 1;

  return (
    <div className="flex flex-col h-full">
      <header className="border-b border-gray-200 sticky top-0 bg-white z-40 px-6 py-3">
        <h1 className="text-base font-semibold text-gray-900">Explore</h1>
        <p className="text-xs text-gray-400">Trending topics & discourse metrics</p>
      </header>

      <div className="p-6 space-y-8 overflow-y-auto">

        {/* Search */}
        <section>
          <input
            type="text"
            placeholder="Search users or topics…"
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
            className="w-full px-4 py-2.5 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-gray-300"
          />
          {searchResults.length > 0 && (
            <div className="mt-2 border border-gray-200 rounded-xl divide-y divide-gray-100 bg-white shadow-sm">
              {searchResults.map(u => (
                <Link
                  key={u.user_id}
                  href={`/profile/${u.user_id}`}
                  className="flex items-center gap-3 px-4 py-3 hover:bg-gray-50 transition"
                >
                  <span className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold flex-shrink-0 ${PERSONA_COLOR[u.persona] ?? 'bg-gray-100 text-gray-700'}`}>
                    {u.username.charAt(0).toUpperCase()}
                  </span>
                  <div>
                    <p className="text-sm font-medium text-gray-900">{u.username}</p>
                    <p className="text-xs text-gray-400">{u.persona.replace('_', ' ')}</p>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </section>

        {/* Trending Topics */}
        <section>
          <h2 className="text-sm font-semibold text-gray-900 mb-4">Trending Topics</h2>
          {loading ? (
            <div className="space-y-2">
              {[...Array(8)].map((_, i) => (
                <div key={i} className="h-8 bg-gray-100 rounded animate-pulse" />
              ))}
            </div>
          ) : trending.length === 0 ? (
            <p className="text-sm text-gray-400">No trending topics yet. Run the simulation.</p>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {trending.map((t, i) => (
                <div
                  key={t.topic}
                  className="border border-gray-200 rounded-xl p-4 hover:bg-gray-50 transition"
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="text-xs text-gray-400">#{i + 1} Trending</p>
                      <p className="text-base font-bold text-gray-900 mt-0.5">{t.topic}</p>
                      <p className="text-xs text-gray-500 mt-1">
                        {t.tweet_count} posts · {t.engagement_score.toFixed(0)} engagements
                      </p>
                    </div>
                    <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded-full font-medium">
                      {t.growth_rate.toFixed(1)}/hr
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>

        {/* Discourse Health */}
        {discourse && (
          <section>
            <h2 className="text-sm font-semibold text-gray-900 mb-4">Discourse Health</h2>
            <div className="grid grid-cols-3 gap-4 mb-6">
              <div className="border border-gray-200 rounded-xl p-4 text-center">
                <p className="text-2xl font-bold text-gray-900">{discourse.total_tweets}</p>
                <p className="text-xs text-gray-500 mt-1">Total Posts</p>
              </div>
              <div className="border border-gray-200 rounded-xl p-4 text-center">
                <p className="text-2xl font-bold text-gray-900">
                  {discourse.average_engagement.toFixed(1)}
                </p>
                <p className="text-xs text-gray-500 mt-1">Avg. Engagement</p>
              </div>
              <div className="border border-gray-200 rounded-xl p-4 text-center">
                <p className="text-2xl font-bold text-gray-900">
                  {(discourse.diversity_index * 100).toFixed(0)}%
                </p>
                <p className="text-xs text-gray-500 mt-1">Topic Diversity</p>
              </div>
            </div>

            <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-3">
              Topic Distribution
            </h3>
            <div className="border border-gray-200 rounded-xl p-4 space-y-1">
              {Object.entries(discourse.topic_distribution)
                .sort(([, a], [, b]) => b - a)
                .map(([topic, count]) => (
                  <TopicBar key={topic} topic={topic} count={count} max={maxCount} />
                ))}
            </div>

            {/* Filter bubble indicator */}
            <div className={`mt-4 p-4 rounded-xl border ${
              discourse.diversity_index > 0.6
                ? 'bg-green-50 border-green-200'
                : discourse.diversity_index > 0.35
                ? 'bg-yellow-50 border-yellow-200'
                : 'bg-red-50 border-red-200'
            }`}>
              <p className="text-xs font-semibold mb-1 flex items-center gap-1.5">
                Filter Bubble Risk:
                <span className={`inline-block w-2 h-2 rounded-full ${
                  discourse.diversity_index > 0.6 ? 'bg-green-500' : discourse.diversity_index > 0.35 ? 'bg-yellow-500' : 'bg-red-500'
                }`} />
                <span className={
                  discourse.diversity_index > 0.6 ? 'text-green-700' : discourse.diversity_index > 0.35 ? 'text-yellow-700' : 'text-red-700'
                }>
                  {discourse.diversity_index > 0.6 ? 'Low' : discourse.diversity_index > 0.35 ? 'Moderate' : 'High'}
                </span>
              </p>
              <p className="text-xs text-gray-600">
                {discourse.diversity_index > 0.6
                  ? 'Discourse spans many topics. Healthy diversity.'
                  : discourse.diversity_index > 0.35
                  ? 'A few topics dominate. Consider boosting Diversity weight.'
                  : 'Discourse is highly concentrated. Increase Diversity slider to break out.'}
              </p>
            </div>
          </section>
        )}

        {/* Suggested Personas */}
        <section>
          <h2 className="text-sm font-semibold text-gray-900 mb-4">Who to Follow</h2>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {users.map(u => (
              <Link
                key={u.user_id}
                href={`/profile/${u.user_id}`}
                className="border border-gray-200 rounded-xl p-4 hover:bg-gray-50 transition flex flex-col gap-2"
              >
                <div className="flex items-center gap-2">
                  <span className={`w-9 h-9 rounded-full flex items-center justify-center text-sm font-bold flex-shrink-0 ${PERSONA_COLOR[u.persona] ?? 'bg-gray-100 text-gray-700'}`}>
                    {u.username.charAt(0).toUpperCase()}
                  </span>
                  <div className="min-w-0">
                    <p className="text-sm font-semibold text-gray-900 truncate">{u.username}</p>
                    <p className="text-xs text-gray-400 truncate">{u.persona.replace('_', ' ')}</p>
                  </div>
                </div>
                {u.interests?.length > 0 && (
                  <div className="flex flex-wrap gap-1">
                    {u.interests.slice(0, 2).map(i => (
                      <span key={i} className="text-xs bg-blue-50 text-blue-700 px-1.5 py-0.5 rounded">
                        {i}
                      </span>
                    ))}
                  </div>
                )}
              </Link>
            ))}
          </div>
        </section>

      </div>
    </div>
  );
}
