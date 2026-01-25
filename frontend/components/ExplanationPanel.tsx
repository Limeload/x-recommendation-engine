/**
 * Explanation Panel Component
 * Shows detailed breakdown of why a tweet was ranked
 */

'use client';

import React from 'react';
import { CheckCircle } from 'phosphor-react';
import { RankingExplanation } from '@/types';

interface ExplanationPanelProps {
  explanation: RankingExplanation;
}

export default function ExplanationPanel({
  explanation,
}: ExplanationPanelProps) {
  const renderScoreBar = (score: number, label: string, weight: number) => {
    const percentage = score * 100;
    const weightPercentage = weight * 100;

    return (
      <div key={label} className="mb-3">
        <div className="flex items-center justify-between text-xs mb-1">
          <span className="font-semibold text-gray-900">{label}</span>
          <div className="text-right">
            <div className="font-semibold text-gray-900">
              {(score * 100).toFixed(0)}%
            </div>
            <div className="text-gray-500 text-xs">
              Weight: {(weightPercentage).toFixed(0)}%
            </div>
          </div>
        </div>

        <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
          <div
            className="h-full bg-gray-800 transition-all"
            style={{ width: `${percentage}%` }}
          />
        </div>
      </div>
    );
  };

  return (
    <div className="mt-4 p-3 bg-gray-50 border border-gray-200 rounded text-sm space-y-3">
      {/* Main Score */}
      <div className="border-b border-gray-200 pb-3">
        <div className="flex items-center justify-between">
          <span className="font-semibold text-gray-900">Overall Score</span>
          <span className="text-lg font-semibold text-gray-900">
            {(explanation.total_score * 100).toFixed(1)}%
          </span>
        </div>
      </div>

      {/* Component Scores */}
      <div>
        <div className="font-semibold text-gray-900 mb-2">Score Breakdown:</div>

        {renderScoreBar(
          explanation.recency_score,
          'Recency',
          explanation.recency_weight
        )}
        {renderScoreBar(
          explanation.popularity_score,
          'Popularity',
          explanation.popularity_weight
        )}
        {renderScoreBar(
          explanation.quality_score,
          'Quality',
          explanation.quality_weight
        )}
        {renderScoreBar(
          explanation.topic_relevance_score,
          'Topic Relevance',
          explanation.topic_relevance_weight
        )}

        {explanation.diversity_penalty > 0 && (
          <div className="mt-2 text-xs text-red-600">
            Diversity Penalty: -{(explanation.diversity_penalty * 100).toFixed(1)}%
          </div>
        )}
      </div>

      {/* Key Factors */}
      <div className="border-t border-gray-200 pt-3">
        <div className="font-semibold text-gray-900 mb-2">Why This Ranked:</div>
        <ul className="space-y-1">
          {explanation.key_factors.map((factor, idx) => (
            <li key={idx} className="text-xs text-gray-700 flex items-start">
              <CheckCircle size={14} weight="bold" className="text-gray-600 mr-2 flex-shrink-0 mt-0.5" />
              <span>{factor}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Persona Match */}
      {explanation.persona_match && (
        <div className="border-t border-gray-200 pt-3">
          <div className="inline-block px-2 py-1 bg-gray-200 text-gray-900 rounded text-xs font-semibold">
            Matches {explanation.persona_match} persona
          </div>
        </div>
      )}
    </div>
  );
}
