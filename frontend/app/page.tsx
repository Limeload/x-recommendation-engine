'use client';

import { useState, useEffect } from 'react';
import FeedComponent from '@/components/Feed';
import TuningDashboard from '@/components/TuningDashboard';
import UserSelector from '@/components/UserSelector';
import { RankedTweet, User } from '@/types';
import { CheckCircle } from 'phosphor-react';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function Home() {
  const [selectedUserId, setSelectedUserId] = useState<string>('user_0');
  const [users, setUsers] = useState<User[]>([]);
  const [rankedTweets, setRankedTweets] = useState<RankedTweet[]>([]);
  const [userWeights, setUserWeights] = useState<Record<string, number>>({});
  const [loading, setLoading] = useState(false);
  const [showTuning, setShowTuning] = useState(false);
  const [settingsSaved, setSettingsSaved] = useState(false);
  const [lastUpdateTime, setLastUpdateTime] = useState<string>('');

  useEffect(() => {
    fetch(`${API_BASE_URL}/users`)
      .then(r => r.json())
      .then(setUsers)
      .catch(console.error);
  }, []);

  useEffect(() => {
    fetchRanking();
    fetchWeights();
  }, [selectedUserId]);

  const fetchRanking = async (limit = 20) => {
    setLoading(true);
    const start = Date.now();
    try {
      const res = await fetch(`${API_BASE_URL}/rank`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: selectedUserId, limit }),
      });
      if (!res.ok) throw new Error('Ranking failed');
      const data = await res.json();
      const elapsed = Date.now() - start;
      if (elapsed < 800) await new Promise(r => setTimeout(r, 800 - elapsed));
      setRankedTweets(data);
      setLastUpdateTime(new Date().toLocaleTimeString());
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const fetchWeights = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/users/${selectedUserId}/weights`);
      const data = await res.json();
      setUserWeights(data.weights);
    } catch (e) {
      console.error(e);
    }
  };

  const handleWeightsUpdate = async (newWeights: Record<string, number>) => {
    try {
      await fetch(`${API_BASE_URL}/users/${selectedUserId}/weights`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: selectedUserId, weights: newWeights }),
      });
      setUserWeights(newWeights);
      setSettingsSaved(true);
      setTimeout(() => setSettingsSaved(false), 2000);
      await fetchRanking();
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Page header */}
      <header className="border-b border-gray-200 sticky top-0 bg-white z-40 px-6 py-3 flex items-center justify-between">
        <div>
          <h1 className="text-base font-semibold text-gray-900">Home Feed</h1>
          {lastUpdateTime && (
            <p className="text-xs text-gray-400">Updated {lastUpdateTime}</p>
          )}
        </div>

        <div className="flex items-center gap-3">
          {settingsSaved && (
            <div className="flex items-center gap-1.5 px-3 py-1.5 bg-green-100 text-green-700 rounded-lg text-xs font-semibold">
              <CheckCircle size={14} weight="fill" />
              Applied
            </div>
          )}

          <UserSelector users={users} selectedUserId={selectedUserId} onSelect={setSelectedUserId} />

          <button
            onClick={() => setShowTuning(!showTuning)}
            className={`px-3 py-1.5 rounded-lg font-medium text-sm transition ${
              showTuning ? 'bg-gray-800 text-white' : 'bg-gray-100 hover:bg-gray-200 text-gray-800'
            }`}
          >
            {showTuning ? 'Close Settings' : 'Settings'}
          </button>

          <button
            onClick={() => fetchRanking()}
            className="px-3 py-1.5 bg-gray-100 hover:bg-gray-200 rounded-lg text-gray-800 text-sm font-medium transition"
          >
            Refresh
          </button>
        </div>
      </header>

      {/* Content */}
      <div className="flex gap-6 p-6 flex-1">
        <div className="flex-1 min-w-0">
          <FeedComponent tweets={rankedTweets} loading={loading} selectedUserId={selectedUserId} />
        </div>

        {showTuning && (
          <div className="w-80 flex-shrink-0 sticky top-20 h-max">
            <TuningDashboard
              weights={userWeights}
              onWeightsChange={handleWeightsUpdate}
              selectedUserId={selectedUserId}
            />
          </div>
        )}
      </div>
    </div>
  );
}
