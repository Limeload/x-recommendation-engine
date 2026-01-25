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

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function Home() {
  const [selectedUserId, setSelectedUserId] = useState<string>('user_0');
  const [users, setUsers] = useState<User[]>([]);
  const [rankedTweets, setRankedTweets] = useState<RankedTweet[]>([]);
  const [userWeights, setUserWeights] = useState<Record<string, number>>({});
  const [loading, setLoading] = useState(false);
  const [showTuning, setShowTuning] = useState(false);

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
      setRankedTweets(data);
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
      fetchRanking(); // Refresh feed with new weights
    } catch (error) {
      console.error('Failed to update weights:', error);
    }
  };

  return (
    <div className="min-h-screen bg-black text-white">
      {/* Header */}
      <header className="border-b border-gray-700 sticky top-0 bg-black bg-opacity-80 backdrop-blur z-40">
        <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <h1 className="text-2xl font-bold">
              𝕏 Recommendation Engine
            </h1>
            <span className="text-gray-500 text-sm">
              Explainable • Personalized • Tunable
            </span>
          </div>

          <div className="flex items-center space-x-4">
            <UserSelector
              users={users}
              selectedUserId={selectedUserId}
              onSelect={setSelectedUserId}
            />

            <button
              onClick={() => setShowTuning(!showTuning)}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-full font-bold transition"
            >
              {showTuning ? 'Hide' : 'Tuning Dashboard'}
            </button>

            <button
              onClick={() => fetchRanking()}
              className="px-4 py-2 bg-gray-900 hover:bg-gray-800 border border-gray-700 rounded-full transition"
            >
              Refresh
            </button>
          </div>
        </div>
      </header>

      <div className="max-w-6xl mx-auto flex gap-6 py-6 px-4">
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
