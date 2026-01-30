/**
 * Individual Tweet Card Component
 * Shows tweet content + ranking explanation + real-time indicators
 */

'use client';

import React, { useState } from 'react';
import { ChatCircle, Repeat, Heart, BookmarkSimple } from 'phosphor-react';
import { RankedTweet } from '@/types';
import ExplanationPanel from './ExplanationPanel';

interface TweetCardProps {
  rankedTweet: RankedTweet;
  rank: number;
  isNew?: boolean;  // For real-time highlighting
}

const getTimeAgo = (dateStr: string): string => {
  const now = new Date();
  const tweetDate = new Date(dateStr);
  const diffMs = now.getTime() - tweetDate.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMins / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (diffMins < 1) return 'now';
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;
  return tweetDate.toLocaleDateString();
};

const isRecentlyCreated = (dateStr: string): boolean => {
  const now = new Date();
  const tweetDate = new Date(dateStr);
  const diffMins = (now.getTime() - tweetDate.getTime()) / 60000;
  return diffMins < 60;  // Highlight tweets less than 1 hour old
};

export default function TweetCard({ rankedTweet, rank, isNew = false }: TweetCardProps) {
  const [showExplanation, setShowExplanation] = useState(false);
  const { tweet, explanation } = rankedTweet;
  const isJustNow = isRecentlyCreated(tweet.created_at);
  const authorName = tweet.author_name || tweet.author_id;
  const timeAgo = getTimeAgo(tweet.created_at);

  return (
    <div className={`p-4 border-l-4 transition cursor-pointer ${
      isNew ? 'bg-blue-50 border-blue-400' : 'hover:bg-gray-50 border-transparent hover:border-gray-400'
    }`}>
      {/* New indicator */}
      {isNew && (
        <div className="mb-2 inline-block px-2 py-1 bg-blue-200 text-blue-900 text-xs font-semibold rounded">
          Added to Feed
        </div>
      )}

      {/* Author Info */}
      <div className="flex items-start space-x-3">
        <div className="flex-1 min-w-0">
          {/* Author Header */}
          <div className="flex items-center space-x-2 flex-wrap">
            <span className="font-semibold text-sm text-gray-900">{authorName}</span>
            <span className="text-gray-400">·</span>
            <span className={`text-xs font-medium ${
              isJustNow ? 'text-blue-600 font-semibold' : 'text-gray-500'
            }`}>
              {timeAgo}
            </span>
          </div>

          {/* Tweet Content */}
          <div className="mt-2 text-sm whitespace-pre-wrap break-words leading-relaxed text-gray-900">
            {tweet.content}
          </div>

          {/* Topics & Hashtags */}
          <div className="mt-3 flex flex-wrap gap-2">
            {tweet.topics.map((topic) => (
              <span
                key={topic}
                className="text-blue-600 hover:text-blue-800 text-xs bg-blue-50 px-2 py-1 rounded"
              >
                #{topic}
              </span>
            ))}
          </div>

          {/* Engagement Metrics */}
          <div className="mt-3 flex items-center space-x-6 text-gray-500 text-xs">
            <div className="flex items-center space-x-1 hover:text-gray-900 cursor-pointer">
              <ChatCircle size={16} weight="light" />
              <span>{tweet.replies}</span>
            </div>
            <div className="flex items-center space-x-2 hover:text-gray-900 cursor-pointer">
              <Repeat size={16} weight="light" />
              <span>{tweet.retweets}</span>
            </div>
            <div className="flex items-center space-x-2 hover:text-gray-900 cursor-pointer">
              <Heart size={16} weight="light" />
              <span>{tweet.likes}</span>
            </div>
            <div className="flex items-center space-x-2 hover:text-gray-900 cursor-pointer">
              <BookmarkSimple size={16} weight="light" />
              <span>{tweet.bookmarks}</span>
            </div>
          </div>

          {/* Ranking Score & Explanation Toggle */}
          <div className="mt-3 flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <span className="text-xs text-gray-600">
                Score:
              </span>
              <span className="text-sm font-semibold text-gray-900">
                {(explanation.total_score * 100).toFixed(1)}%
              </span>
              <div className="w-24 h-2 bg-gray-200 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gray-800 transition-all"
                  style={{ width: `${explanation.total_score * 100}%` }}
                />
              </div>
            </div>

            <button
              onClick={() => setShowExplanation(!showExplanation)}
              className="text-xs text-gray-600 hover:text-gray-900 underline"
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
