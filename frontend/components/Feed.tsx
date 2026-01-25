/**
 * Tweet Feed Component
 * Displays ranked tweets with explanations
 */

'use client';

import React from 'react';
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
          <TweetCard rankedTweet={rankedTweet} rank={index + 1} />
        </div>
      ))}
    </div>
  );
}
