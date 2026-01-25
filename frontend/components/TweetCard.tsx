/**
 * Individual Tweet Card Component
 * Shows tweet content + ranking explanation
 */

'use client';

import React, { useState } from 'react';
import { RankedTweet } from '@/types';
import ExplanationPanel from './ExplanationPanel';

interface TweetCardProps {
  rankedTweet: RankedTweet;
  rank: number;
}

export default function TweetCard({ rankedTweet, rank }: TweetCardProps) {
  const [showExplanation, setShowExplanation] = useState(false);
  const { tweet, explanation } = rankedTweet;

  return (
    <div className="p-4 hover:bg-gray-800 transition cursor-pointer">
      {/* Rank Badge + Author Info */}
      <div className="flex items-start space-x-3">
        <div className="flex-shrink-0">
          <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center font-bold text-sm">
            #{rank}
          </div>
        </div>

        <div className="flex-1 min-w-0">
          {/* Author Header */}
          <div className="flex items-center space-x-2">
            <span className="font-bold hover:underline">{tweet.author_id}</span>
            <span className="text-gray-500">@{tweet.author_id}</span>
            <span className="text-gray-500">·</span>
            <span className="text-gray-500 text-sm">
              {new Date(tweet.created_at).toLocaleDateString()}
            </span>
          </div>

          {/* Tweet Content */}
          <div className="mt-2 text-base whitespace-pre-wrap break-words">
            {tweet.content}
          </div>

          {/* Topics & Hashtags */}
          <div className="mt-2 flex flex-wrap gap-2">
            {tweet.topics.map((topic) => (
              <span
                key={topic}
                className="text-blue-500 hover:underline text-sm"
              >
                #{topic}
              </span>
            ))}
          </div>

          {/* Engagement Metrics */}
          <div className="mt-3 flex items-center space-x-6 text-gray-500 text-sm">
            <div className="flex items-center space-x-2 hover:text-blue-500">
              <span>💬</span>
              <span>{tweet.replies}</span>
            </div>
            <div className="flex items-center space-x-2 hover:text-green-500">
              <span>🔄</span>
              <span>{tweet.retweets}</span>
            </div>
            <div className="flex items-center space-x-2 hover:text-red-500">
              <span>❤️</span>
              <span>{tweet.likes}</span>
            </div>
            <div className="flex items-center space-x-2 hover:text-blue-500">
              <span>📌</span>
              <span>{tweet.bookmarks}</span>
            </div>
          </div>

          {/* Ranking Score & Explanation Toggle */}
          <div className="mt-3 flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <div className="text-xs font-semibold text-gray-400">
                Ranking Score:
              </div>
              <div className="text-sm font-bold text-blue-500">
                {(explanation.total_score * 100).toFixed(1)}%
              </div>

              {/* Score Breakdown Visualization */}
              <div className="flex items-center space-x-1 ml-2">
                <div
                  className="h-2 bg-blue-600 rounded-full"
                  style={{ width: `${explanation.total_score * 50}px` }}
                />
              </div>
            </div>

            <button
              onClick={() => setShowExplanation(!showExplanation)}
              className="text-xs text-blue-500 hover:underline"
            >
              {showExplanation ? 'Hide' : 'Show'} Explanation
            </button>
          </div>

          {/* Explanation Panel */}
          {showExplanation && <ExplanationPanel explanation={explanation} />}
        </div>
      </div>
    </div>
  );
}
