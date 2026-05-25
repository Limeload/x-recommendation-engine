/**
 * Tuning Dashboard — Ranking weights + named feed preference controls
 */

'use client';

import React, { useState, useEffect } from 'react';
import {
  Clock,
  Fire,
  Star,
  Target,
  Lightbulb,
  Gear,
  LightbulbFilament,
  Users,
  TrendUp,
  Cpu,
  Flag,
  Smiley,
} from 'phosphor-react';

interface TuningDashboardProps {
  weights: Record<string, number>;
  onWeightsChange: (weights: Record<string, number>) => void;
  selectedUserId: string;
}

const CORE_WEIGHTS = ['recency', 'popularity', 'quality', 'topic_relevance', 'diversity'];

const coreConfig = [
  { key: 'recency', label: 'Recency', description: 'Prefer fresh content', icon: Clock },
  { key: 'popularity', label: 'Popularity', description: 'Prefer high engagement', icon: Fire },
  { key: 'quality', label: 'Quality', description: 'Content quality signals', icon: Star },
  { key: 'topic_relevance', label: 'Topic Relevance', description: 'Match your interests', icon: Target },
  { key: 'diversity', label: 'Diversity', description: 'Avoid topic clustering', icon: Lightbulb },
];

const presets: Record<string, Record<string, number>> = {
  Latest: { recency: 0.35, popularity: 0.15, quality: 0.2, topic_relevance: 0.2, diversity: 0.1 },
  Trending: { recency: 0.1, popularity: 0.45, quality: 0.15, topic_relevance: 0.2, diversity: 0.1 },
  Personal: { recency: 0.1, popularity: 0.1, quality: 0.3, topic_relevance: 0.4, diversity: 0.1 },
  Balanced: { recency: 0.2, popularity: 0.2, quality: 0.2, topic_relevance: 0.2, diversity: 0.2 },
};

export default function TuningDashboard({
  weights,
  onWeightsChange,
  selectedUserId,
}: TuningDashboardProps) {
  const [tempWeights, setTempWeights] = useState<Record<string, number>>(weights);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    setTempWeights(weights);
  }, [weights]);

  const set = (key: string, value: number) => {
    setTempWeights(prev => ({ ...prev, [key]: Math.max(0, Math.min(1, value)) }));
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      await onWeightsChange(tempWeights);
    } finally {
      setSaving(false);
    }
  };

  const applyPreset = (preset: Record<string, number>) => {
    setTempWeights(prev => ({ ...prev, ...preset }));
  };

  const coreTotal = CORE_WEIGHTS.reduce((s, k) => s + (tempWeights[k] ?? 0), 0);
  const coreValid = Math.abs(coreTotal - 1.0) < 0.01;

  return (
    <div className="border border-gray-200 rounded-lg bg-white shadow-sm flex flex-col max-h-[85vh]">
      <div className="p-5 overflow-y-auto flex-1 space-y-6">

        {/* Header */}
        <div>
          <h2 className="text-lg font-semibold flex items-center text-gray-900">
            <Gear size={20} weight="bold" className="mr-2" />
            Algorithm Settings
          </h2>
          <p className="mt-1 text-xs text-gray-500">
            Adjusting for <span className="font-semibold text-gray-700">{selectedUserId}</span>
          </p>
        </div>

        {/* ── Section 1: Core Ranking Weights ── */}
        <section>
          <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-3">
            Ranking Weights <span className="text-gray-400 font-normal">(must sum to 1.0)</span>
          </p>
          <div className="space-y-4">
            {coreConfig.map(({ key, label, description, icon: Icon }) => (
              <div key={key}>
                <div className="flex items-center justify-between mb-1">
                  <label className="flex items-center text-sm font-medium text-gray-900">
                    <Icon size={15} weight="bold" className="mr-2 text-gray-600" />
                    {label}
                  </label>
                  <span className="text-sm font-mono font-semibold bg-gray-100 px-2 py-0.5 rounded text-gray-900">
                    {(tempWeights[key] ?? 0).toFixed(2)}
                  </span>
                </div>
                <p className="text-xs text-gray-400 mb-1">{description}</p>
                <input
                  type="range" min="0" max="1" step="0.05"
                  value={tempWeights[key] ?? 0}
                  onChange={e => set(key, parseFloat(e.target.value))}
                  className="w-full h-1.5 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-gray-800"
                />
              </div>
            ))}
          </div>

          {/* Weight sum indicator */}
          <div className={`mt-3 flex items-center justify-between text-xs px-3 py-2 rounded border ${
            coreValid ? 'bg-green-50 border-green-200 text-green-700' : 'bg-red-50 border-red-200 text-red-700'
          }`}>
            <span>Total weight</span>
            <span className="font-bold">{coreTotal.toFixed(2)}</span>
          </div>

          {/* Quick presets */}
          <div className="mt-3">
            <p className="text-xs text-gray-500 mb-2 font-medium">Quick presets:</p>
            <div className="grid grid-cols-4 gap-1.5">
              {Object.entries(presets).map(([name, preset]) => (
                <button
                  key={name}
                  onClick={() => applyPreset(preset)}
                  className="text-xs px-2 py-1.5 bg-gray-100 hover:bg-gray-200 rounded border border-gray-200 transition text-gray-800 font-medium"
                >
                  {name}
                </button>
              ))}
            </div>
          </div>
        </section>

        {/* ── Section 2: Feed Preferences ── */}
        <section>
          <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-3">
            Feed Preferences
          </p>
          <div className="space-y-5">

            {/* Friends vs Global */}
            <div>
              <div className="flex items-center justify-between mb-1">
                <label className="flex items-center text-sm font-medium text-gray-900">
                  <Users size={15} weight="bold" className="mr-2 text-blue-500" />
                  Network Preference
                </label>
                <span className="text-xs font-mono bg-blue-50 text-blue-800 px-2 py-0.5 rounded">
                  {(tempWeights['in_network_boost'] ?? 0.3).toFixed(2)}
                </span>
              </div>
              <div className="flex justify-between text-xs text-gray-400 mb-1">
                <span>Global</span>
                <span>Friends First</span>
              </div>
              <input
                type="range" min="0" max="1" step="0.05"
                value={tempWeights['in_network_boost'] ?? 0.3}
                onChange={e => set('in_network_boost', parseFloat(e.target.value))}
                className="w-full h-1.5 bg-gradient-to-r from-gray-200 to-blue-300 rounded-lg appearance-none cursor-pointer accent-blue-600"
              />
              <p className="text-xs text-gray-400 mt-1">
                {(tempWeights['in_network_boost'] ?? 0.3) > 0.6
                  ? 'Heavily favoring accounts you follow'
                  : (tempWeights['in_network_boost'] ?? 0.3) < 0.3
                  ? 'Mostly global / discovery mode'
                  : 'Balanced mix of network and global'}
              </p>
            </div>

            {/* Niche vs Viral */}
            <div>
              <div className="flex items-center justify-between mb-1">
                <label className="flex items-center text-sm font-medium text-gray-900">
                  <TrendUp size={15} weight="bold" className="mr-2 text-orange-500" />
                  Content Style
                </label>
                <span className="text-xs font-mono bg-orange-50 text-orange-800 px-2 py-0.5 rounded">
                  {(tempWeights['virality_boost'] ?? 0.5).toFixed(2)}
                </span>
              </div>
              <div className="flex justify-between text-xs text-gray-400 mb-1">
                <span>Niche / Specialist</span>
                <span>Viral / Trending</span>
              </div>
              <input
                type="range" min="0" max="1" step="0.05"
                value={tempWeights['virality_boost'] ?? 0.5}
                onChange={e => set('virality_boost', parseFloat(e.target.value))}
                className="w-full h-1.5 bg-gradient-to-r from-purple-200 to-orange-300 rounded-lg appearance-none cursor-pointer accent-orange-500"
              />
              <p className="text-xs text-gray-400 mt-1">
                {(tempWeights['virality_boost'] ?? 0.5) > 0.65
                  ? 'Showing fast-moving viral content'
                  : (tempWeights['virality_boost'] ?? 0.5) < 0.35
                  ? 'Preferring niche, specialist content'
                  : 'Mix of niche depth and viral breadth'}
              </p>
            </div>
          </div>
        </section>

        {/* ── Section 3: Topic Category Affinities ── */}
        <section>
          <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-3">
            Topic Interests
          </p>
          <div className="space-y-4">

            <div>
              <div className="flex items-center justify-between mb-1">
                <label className="flex items-center text-sm font-medium text-gray-900">
                  <Cpu size={15} weight="bold" className="mr-2 text-sky-500" />
                  Tech / AI / Engineering
                </label>
                <span className="text-xs font-mono bg-sky-50 text-sky-800 px-2 py-0.5 rounded">
                  {(tempWeights['tech_affinity'] ?? 0.7).toFixed(2)}
                </span>
              </div>
              <input
                type="range" min="0" max="1" step="0.05"
                value={tempWeights['tech_affinity'] ?? 0.7}
                onChange={e => set('tech_affinity', parseFloat(e.target.value))}
                className="w-full h-1.5 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-sky-500"
              />
            </div>

            <div>
              <div className="flex items-center justify-between mb-1">
                <label className="flex items-center text-sm font-medium text-gray-900">
                  <Flag size={15} weight="bold" className="mr-2 text-red-500" />
                  Politics / Policy
                </label>
                <span className="text-xs font-mono bg-red-50 text-red-800 px-2 py-0.5 rounded">
                  {(tempWeights['politics_affinity'] ?? 0.3).toFixed(2)}
                </span>
              </div>
              <input
                type="range" min="0" max="1" step="0.05"
                value={tempWeights['politics_affinity'] ?? 0.3}
                onChange={e => set('politics_affinity', parseFloat(e.target.value))}
                className="w-full h-1.5 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-red-500"
              />
            </div>

            <div>
              <div className="flex items-center justify-between mb-1">
                <label className="flex items-center text-sm font-medium text-gray-900">
                  <Smiley size={15} weight="bold" className="mr-2 text-yellow-500" />
                  Culture / Memes / Entertainment
                </label>
                <span className="text-xs font-mono bg-yellow-50 text-yellow-800 px-2 py-0.5 rounded">
                  {(tempWeights['culture_affinity'] ?? 0.5).toFixed(2)}
                </span>
              </div>
              <input
                type="range" min="0" max="1" step="0.05"
                value={tempWeights['culture_affinity'] ?? 0.5}
                onChange={e => set('culture_affinity', parseFloat(e.target.value))}
                className="w-full h-1.5 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-yellow-500"
              />
            </div>
          </div>

          <p className="text-xs text-gray-400 mt-3">
            0 = suppress this category · 0.5 = neutral · 1 = strongly prefer
          </p>
        </section>

        {/* ── Save / Reset ── */}
        <div className="flex gap-2 pt-2 border-t border-gray-100">
          <button
            onClick={handleSave}
            disabled={saving || !coreValid}
            className="flex-1 px-4 py-2 bg-gray-900 hover:bg-gray-800 disabled:bg-gray-200 disabled:cursor-not-allowed text-white font-medium rounded transition text-sm"
          >
            {saving ? 'Saving…' : 'Apply Changes'}
          </button>
          <button
            onClick={() => setTempWeights(weights)}
            className="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-800 font-medium rounded transition border border-gray-200 text-sm"
          >
            Reset
          </button>
        </div>

        <div className="flex items-start gap-2 text-xs text-gray-500 p-3 bg-gray-50 rounded border border-gray-100">
          <LightbulbFilament size={14} className="flex-shrink-0 mt-0.5" />
          <p>Changes re-rank your feed in real time. Section 1 weights must sum to 1.0 to save.</p>
        </div>

      </div>
    </div>
  );
}
