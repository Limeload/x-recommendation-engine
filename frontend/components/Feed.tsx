/**
 * Tweet Feed Component
 * Displays ranked tweets with explanations and real-time indicators
 */

'use client';

import React, { useEffect, useState } from 'react';
import { RankedTweet } from '@/types';
import TweetCard from './TweetCard';

interface FeedComponentProps {
  tweets: RankedTweet[];
  loading: boolean;
  selectedUserId: string;
}

export default function FeedComponent({
  tweets,
  loading,
  selectedUserId,
}: FeedComponentProps) {
  const [newTweetIds, setNewTweetIds] = useState<Set<string>>(new Set());

  // Track which tweets are newly added
  useEffect(() => {
    const newIds = new Set<string>();
    tweets.slice(0, 5).forEach(t => {
      newIds.add(t.tweet.tweet_id);
    });
    setNewTweetIds(newIds);

    // Remove highlighting after 3 seconds
    const timeout = setTimeout(() => {
      setNewTweetIds(new Set());
    }, 3000);

    return () => clearTimeout(timeout);
  }, [tweets]);

  if (loading) {
    return (
      <div className="space-y-4">
        {[...Array(5)].map((_, i) => (
          <div
            key={i}
            className="border border-gray-200 rounded-lg p-4 animate-pulse bg-gray-50"
          >
            <div className="h-20 bg-gray-200 rounded" />
          </div>
        ))}
      </div>
    );
  }

  if (tweets.length === 0) {
    return (
      <div className="border border-gray-200 rounded-lg p-12 text-center text-gray-500">
        <p className="text-sm">No tweets to display. Try adjusting your filters or weights.</p>
      </div>
    );
  }

  return (
    <div className="border border-gray-200 rounded-lg overflow-hidden bg-white">
      {tweets.map((rankedTweet, index) => (
        <div key={rankedTweet.tweet.tweet_id} className="border-b border-gray-100 last:border-b-0">
          <TweetCard
            rankedTweet={rankedTweet}
            rank={index + 1}
            isNew={newTweetIds.has(rankedTweet.tweet.tweet_id)}
          />
        </div>
      ))}
    </div>
  );
}
