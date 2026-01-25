/**
 * Tuning Dashboard Component
 * Allows users to adjust ranking weights
 */

'use client';

import React, { useState } from 'react';

interface TuningDashboardProps {
  weights: Record<string, number>;
  onWeightsChange: (weights: Record<string, number>) => void;
  selectedUserId: string;
}

export default function TuningDashboard({
  weights,
  onWeightsChange,
  selectedUserId,
}: TuningDashboardProps) {
  const [tempWeights, setTempWeights] = useState(weights);
  const [saving, setSaving] = useState(false);

  const handleWeightChange = (key: string, value: number) => {
    setTempWeights((prev) => ({
      ...prev,
      [key]: Math.max(0, Math.min(1, value)),
    }));
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      await onWeightsChange(tempWeights);
    } finally {
      setSaving(false);
    }
  };

  const handleReset = () => {
    setTempWeights(weights);
  };

  const total = Object.values(tempWeights).reduce((a, b) => a + b, 0);
  const isValid = Math.abs(total - 1.0) < 0.01;

  const weightConfig = [
    {
      key: 'recency',
      label: 'Recency',
      description: 'How fresh the content should be',
      icon: '⏰',
    },
    {
      key: 'popularity',
      label: 'Popularity',
      description: 'How much engagement matters',
      icon: '🔥',
    },
    {
      key: 'quality',
      label: 'Quality',
      description: 'Content quality signals',
      icon: '⭐',
    },
    {
      key: 'topic_relevance',
      label: 'Topic Relevance',
      description: 'Match to your interests',
      icon: '🎯',
    },
    {
      key: 'diversity',
      label: 'Diversity',
      description: 'Avoid cluster/redundancy',
      icon: '🌈',
    },
  ];

  return (
    <div className="border border-gray-700 rounded-lg bg-gray-900 p-4">
      <h2 className="text-xl font-bold mb-4 flex items-center">
        <span className="mr-2">⚙️</span>
        Ranking Tuner
      </h2>

      <div className="text-xs text-gray-500 mb-4 p-2 bg-gray-800 rounded">
        User: <span className="font-mono text-blue-400">{selectedUserId}</span>
      </div>

      <div className="space-y-4">
        {weightConfig.map(({ key, label, description, icon }) => (
          <div key={key}>
            <div className="flex items-center justify-between mb-1">
              <label className="flex items-center text-sm font-semibold">
                <span className="mr-2">{icon}</span>
                {label}
              </label>
              <span className="text-sm font-mono font-bold text-blue-500">
                {(tempWeights[key] || 0).toFixed(2)}
              </span>
            </div>

            <p className="text-xs text-gray-500 mb-2">{description}</p>

            <div className="flex items-center space-x-2">
              <input
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={tempWeights[key] || 0}
                onChange={(e) => handleWeightChange(key, parseFloat(e.target.value))}
                className="flex-1 h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-blue-600"
              />
              <button
                onClick={() => handleWeightChange(key, 0)}
                className="text-xs text-gray-500 hover:text-gray-300 px-2 py-1 hover:bg-gray-700 rounded"
              >
                0
              </button>
            </div>

            <div className="mt-2 h-1 bg-gray-700 rounded-full overflow-hidden">
              <div
                className="h-full bg-blue-600 transition-all"
                style={{ width: `${(tempWeights[key] || 0) * 100}%` }}
              />
            </div>
          </div>
        ))}
      </div>

      {/* Weight Sum Indicator */}
      <div className="mt-4 p-3 bg-gray-800 rounded">
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-400">Sum of Weights:</span>
          <span
            className={`font-bold ${
              isValid ? 'text-green-500' : 'text-red-500'
            }`}
          >
            {total.toFixed(2)}
          </span>
        </div>
        {!isValid && (
          <p className="text-xs text-red-500 mt-1">
            Weights should sum to 1.0 (auto-normalized on save)
          </p>
        )}
      </div>

      {/* Presets */}
      <div className="mt-4 space-y-2">
        <p className="text-xs font-semibold text-gray-400">Quick Presets:</p>

        <div className="grid grid-cols-2 gap-2">
          <button
            onClick={() =>
              setTempWeights({
                recency: 0.3,
                popularity: 0.2,
                quality: 0.2,
                topic_relevance: 0.2,
                diversity: 0.1,
              })
            }
            className="text-xs px-2 py-2 bg-gray-800 hover:bg-gray-700 rounded border border-gray-700 transition"
          >
            📰 Latest First
          </button>

          <button
            onClick={() =>
              setTempWeights({
                recency: 0.1,
                popularity: 0.4,
                quality: 0.2,
                topic_relevance: 0.2,
                diversity: 0.1,
              })
            }
            className="text-xs px-2 py-2 bg-gray-800 hover:bg-gray-700 rounded border border-gray-700 transition"
          >
            🔥 Trending
          </button>

          <button
            onClick={() =>
              setTempWeights({
                recency: 0.1,
                popularity: 0.1,
                quality: 0.3,
                topic_relevance: 0.4,
                diversity: 0.1,
              })
            }
            className="text-xs px-2 py-2 bg-gray-800 hover:bg-gray-700 rounded border border-gray-700 transition"
          >
            🎯 Personalized
          </button>

          <button
            onClick={() =>
              setTempWeights({
                recency: 0.2,
                popularity: 0.2,
                quality: 0.2,
                topic_relevance: 0.2,
                diversity: 0.2,
              })
            }
            className="text-xs px-2 py-2 bg-gray-800 hover:bg-gray-700 rounded border border-gray-700 transition"
          >
            ⚖️ Balanced
          </button>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="mt-4 flex gap-2">
        <button
          onClick={handleSave}
          disabled={saving || !isValid}
          className="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 disabled:cursor-not-allowed text-white font-bold rounded transition"
        >
          {saving ? 'Saving...' : 'Save Weights'}
        </button>

        <button
          onClick={handleReset}
          className="flex-1 px-4 py-2 bg-gray-800 hover:bg-gray-700 text-white font-bold rounded transition"
        >
          Reset
        </button>
      </div>

      {/* Info */}
      <div className="mt-4 text-xs text-gray-500 p-2 bg-gray-800 rounded">
        <p>💡 Adjust weights to personalize your feed. Changes are saved to the server immediately.</p>
      </div>
    </div>
  );
}
