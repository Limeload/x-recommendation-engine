/**
 * Next.js Frontend for X Recommendation Engine
 * Main page with feed and tuning dashboard
 */

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

  // Fetch users on mount
  useEffect(() => {
    const fetchUsers = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/users`);
        const data = await response.json();
        setUsers(data);
      } catch (error) {
        console.error('Failed to fetch users:', error);
      }
    };

    fetchUsers();
  }, []);

  // Fetch ranking feed when user changes
  useEffect(() => {
    fetchRanking();
    fetchWeights();
  }, [selectedUserId]);

  const fetchRanking = async (limit: number = 20) => {
    setLoading(true);
    const startTime = Date.now();
    const minimumLoadingTime = 1500; // 1.5 second minimum loading time

    try {
      const response = await fetch(`${API_BASE_URL}/rank`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: selectedUserId,
          limit: limit,
        }),
      });

      if (!response.ok) throw new Error('Failed to fetch ranking');

      const data = await response.json();

      // Ensure minimum loading time for better UX
      const elapsedTime = Date.now() - startTime;
      const remainingTime = Math.max(0, minimumLoadingTime - elapsedTime);

      if (remainingTime > 0) {
        await new Promise(resolve => setTimeout(resolve, remainingTime));
      }

      setRankedTweets(data);
      setLastUpdateTime(new Date().toLocaleTimeString());
    } catch (error) {
      console.error('Ranking error:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchWeights = async () => {
    try {
      const response = await fetch(
        `${API_BASE_URL}/users/${selectedUserId}/weights`
      );
      const data = await response.json();
      setUserWeights(data.weights);
    } catch (error) {
      console.error('Failed to fetch weights:', error);
    }
  };

  const handleWeightsUpdate = async (newWeights: Record<string, number>) => {
    try {
      const response = await fetch(
        `${API_BASE_URL}/users/${selectedUserId}/weights`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            user_id: selectedUserId,
            weights: newWeights,
          }),
        }
      );

      if (!response.ok) throw new Error('Failed to update weights');

      setUserWeights(newWeights);
      setSettingsSaved(true);

      // Show saved indicator for 2 seconds
      setTimeout(() => setSettingsSaved(false), 2000);

      // Refresh feed with new weights
      await fetchRanking();
    } catch (error) {
      console.error('Failed to update weights:', error);
    }
  };

  return (
    <div className="min-h-screen bg-white text-gray-900">
      {/* Header */}
      <header className="border-b border-gray-200 sticky top-0 bg-white z-40">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-6">
            <h1 className="text-xl font-bold tracking-tight">
              Recommendation Engine
            </h1>
            <span className="text-gray-500 text-sm">
              Intelligent Ranking • Full Transparency • Complete Control
            </span>
          </div>

          <div className="flex items-center space-x-3">
            {/* Settings saved indicator */}
            {settingsSaved && (
              <div className="flex items-center space-x-2 px-3 py-2 bg-green-100 text-green-700 rounded-lg animate-in fade-in">
                <CheckCircle size={16} weight="fill" />
                <span className="text-xs font-semibold">Settings Applied</span>
              </div>
            )}

            {/* Last update time */}
            {lastUpdateTime && (
              <div className="text-xs text-gray-500">
                Updated: {lastUpdateTime}
              </div>
            )}

            <UserSelector
              users={users}
              selectedUserId={selectedUserId}
              onSelect={setSelectedUserId}
            />

            <button
              onClick={() => setShowTuning(!showTuning)}
              className={`px-4 py-2 rounded-lg font-medium transition text-white text-sm ${
                showTuning
                  ? 'bg-gray-800 hover:bg-gray-900'
                  : 'bg-gray-900 hover:bg-gray-800'
              }`}
            >
              {showTuning ? 'Close' : 'Settings'}
            </button>

            <button
              onClick={() => fetchRanking()}
              className="px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition text-gray-900 text-sm font-medium"
            >
              Refresh
            </button>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto flex gap-8 py-8 px-6">
        {/* Main Feed */}
        <div className="flex-1">
          <FeedComponent
            tweets={rankedTweets}
            loading={loading}
            selectedUserId={selectedUserId}
          />
        </div>

        {/* Sidebar - Tuning Dashboard */}
        {showTuning && (
          <div className="w-80 sticky top-20 h-max">
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
