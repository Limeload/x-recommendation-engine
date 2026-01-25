/**
 * Tuning Dashboard Component
 * Allows users to adjust ranking weights
 */

'use client';

import React, { useState } from 'react';
import {
  Clock,
  Fire,
  Star,
  Target,
  Lightbulb,
  Newspaper,
  Gear,
  LightbulbFilament,
  Scales,
} from 'phosphor-react';

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
      icon: Clock,
    },
    {
      key: 'popularity',
      label: 'Popularity',
      description: 'How much engagement matters',
      icon: Fire,
    },
    {
      key: 'quality',
      label: 'Quality',
      description: 'Content quality signals',
      icon: Star,
    },
    {
      key: 'topic_relevance',
      label: 'Topic Relevance',
      description: 'Match to your interests',
      icon: Target,
    },
    {
      key: 'diversity',
      label: 'Diversity',
      description: 'Avoid cluster/redundancy',
      icon: Lightbulb,
    },
  ];

  return (
    <div className="border border-gray-200 rounded-lg bg-white p-5">
      <h2 className="text-lg font-semibold mb-4 flex items-center text-gray-900">
        <Gear size={20} weight="bold" className="mr-2" />
        Settings
      </h2>

      <div className="text-xs text-gray-600 mb-4 p-2 bg-gray-50 rounded border border-gray-200">
        User: <span className="font-mono text-gray-900">{selectedUserId}</span>
      </div>

      <div className="space-y-4">
        {weightConfig.map(({ key, label, description, icon: IconComponent }) => (
          <div key={key}>
            <div className="flex items-center justify-between mb-1">
              <label className="flex items-center text-sm font-medium text-gray-900">
                <IconComponent size={16} weight="bold" className="mr-2" />
                {label}
              </label>
              <span className="text-sm font-mono font-semibold text-gray-900">
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
                className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-gray-800"
              />
              <button
                onClick={() => handleWeightChange(key, 0)}
                className="text-xs text-gray-600 hover:text-gray-900 px-2 py-1 hover:bg-gray-100 rounded"
              >
                0
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Weight Sum Indicator */}
      <div className="mt-4 p-3 bg-gray-50 rounded border border-gray-200">
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-700">Sum of Weights:</span>
          <span
            className={`font-semibold ${
              isValid ? 'text-gray-900' : 'text-red-600'
            }`}
          >
            {total.toFixed(2)}
          </span>
        </div>
        {!isValid && (
          <p className="text-xs text-red-600 mt-1">
            Weights should sum to 1.0 (auto-normalized on save)
          </p>
        )}
      </div>

      {/* Presets */}
      <div className="mt-4 space-y-2">
        <p className="text-xs font-semibold text-gray-800">Quick Presets:</p>

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
            className="text-xs px-2 py-2 bg-gray-50 hover:bg-gray-100 rounded border border-gray-200 transition flex items-center justify-center gap-1 text-gray-900 font-medium"
          >
            <Newspaper size={14} weight="bold" />
            Latest
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
            className="text-xs px-2 py-2 bg-gray-50 hover:bg-gray-100 rounded border border-gray-200 transition flex items-center justify-center gap-1 text-gray-900 font-medium"
          >
            <Fire size={14} weight="bold" />
            Trending
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
            className="text-xs px-2 py-2 bg-gray-50 hover:bg-gray-100 rounded border border-gray-200 transition flex items-center justify-center gap-1 text-gray-900 font-medium"
          >
            <Target size={14} weight="bold" />
            Personal
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
            className="text-xs px-2 py-2 bg-gray-50 hover:bg-gray-100 rounded border border-gray-200 transition flex items-center justify-center gap-1 text-gray-900 font-medium"
          >
            <Scales size={14} weight="bold" />
            Balanced
          </button>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="mt-4 flex gap-2">
        <button
          onClick={handleSave}
          disabled={saving || !isValid}
          className="flex-1 px-4 py-2 bg-gray-900 hover:bg-gray-800 disabled:bg-gray-200 disabled:cursor-not-allowed text-white font-medium rounded transition text-sm"
        >
          {saving ? 'Saving...' : 'Save'}
        </button>

        <button
          onClick={handleReset}
          className="flex-1 px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-900 font-medium rounded transition border border-gray-200 text-sm"
        >
          Reset
        </button>
      </div>

      {/* Info */}
      <div className="mt-4 text-xs text-gray-600 p-3 bg-gray-50 rounded border border-gray-200 flex items-start gap-2">
        <LightbulbFilament size={16} weight="bold" className="flex-shrink-0 mt-0.5 text-gray-700" />
        <p>Adjust weights to personalize your feed. Changes save automatically.</p>
      </div>
    </div>
  );
}
