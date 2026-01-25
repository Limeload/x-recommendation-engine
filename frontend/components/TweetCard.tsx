/**
 * Individual Tweet Card Component
 * Shows tweet content + ranking explanation
 */

'use client';

import React, { useState } from 'react';
import { ChatCircle, Repeat, Heart, BookmarkSimple } from 'phosphor-react';
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
    <div className="p-4 hover:bg-gray-50 transition cursor-pointer border-l-4 border-transparent hover:border-gray-400">
      {/* Rank Badge + Author Info */}
      <div className="flex items-start space-x-3">
        <div className="flex-shrink-0">
          <div className="w-8 h-8 bg-gray-900 rounded-full flex items-center justify-center font-semibold text-xs text-white">
            {rank}
          </div>
        </div>

        <div className="flex-1 min-w-0">
          {/* Author Header */}
          <div className="flex items-center space-x-2">
            <span className="font-semibold text-sm">{tweet.author_id}</span>
            <span className="text-gray-500 text-xs">@{tweet.author_id}</span>
            <span className="text-gray-400">·</span>
            <span className="text-gray-500 text-xs">
              {new Date(tweet.created_at).toLocaleDateString()}
            </span>
          </div>

          {/* Tweet Content */}
          <div className="mt-2 text-sm whitespace-pre-wrap break-words leading-relaxed">
            {tweet.content}
          </div>

          {/* Topics & Hashtags */}
          <div className="mt-3 flex flex-wrap gap-2">
            {tweet.topics.map((topic) => (
              <span
                key={topic}
                className="text-gray-600 hover:text-gray-900 text-xs"
              >
                #{topic}
              </span>
            ))}
          </div>

          {/* Engagement Metrics */}
          <div className="mt-3 flex items-center space-x-6 text-gray-500 text-xs">
            <div className="flex items-center space-x-1 hover:text-gray-900">
              <ChatCircle size={16} weight="light" />
              <span>{tweet.replies}</span>
            </div>
            <div className="flex items-center space-x-2 hover:text-gray-900">
              <Repeat size={16} weight="light" />
              <span>{tweet.retweets}</span>
            </div>
            <div className="flex items-center space-x-2 hover:text-gray-900">
              <Heart size={16} weight="light" />
              <span>{tweet.likes}</span>
            </div>
            <div className="flex items-center space-x-2 hover:text-gray-900">
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
