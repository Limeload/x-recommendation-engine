/**
 * User Selector Component
 * Dropdown to select which user's feed to view
 */

'use client';

import React, { useState } from 'react';
import { User } from '@/types';

interface UserSelectorProps {
  users: User[];
  selectedUserId: string;
  onSelect: (userId: string) => void;
}

export default function UserSelector({
  users,
  selectedUserId,
  onSelect,
}: UserSelectorProps) {
  const [isOpen, setIsOpen] = useState(false);

  const selectedUser = users.find((u) => u.user_id === selectedUserId);

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="px-4 py-2 bg-gray-900 hover:bg-gray-800 border border-gray-700 rounded-lg text-sm font-semibold flex items-center space-x-2 transition"
      >
        <span>👤</span>
        <span>{selectedUser?.username || 'Select User'}</span>
        <span className="text-xs">▼</span>
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-64 bg-gray-900 border border-gray-700 rounded-lg shadow-xl z-50 max-h-96 overflow-y-auto">
          {users.map((user) => (
            <button
              key={user.user_id}
              onClick={() => {
                onSelect(user.user_id);
                setIsOpen(false);
              }}
              className={`w-full text-left px-4 py-3 border-b border-gray-800 hover:bg-gray-800 transition flex items-start justify-between ${
                user.user_id === selectedUserId ? 'bg-gray-800' : ''
              }`}
            >
              <div className="flex-1 min-w-0">
                <div className="font-semibold text-sm">{user.username}</div>
                <div className="text-xs text-gray-500 flex items-center space-x-1 mt-1">
                  <span className="px-2 py-0.5 bg-gray-700 rounded">
                    {user.persona}
                  </span>
                  <span>·</span>
                  <span>{user.follower_count.toLocaleString()} followers</span>
                </div>
                <div className="text-xs text-gray-600 mt-1 line-clamp-1">
                  Interests: {user.interests.join(', ')}
                </div>
              </div>
              {user.user_id === selectedUserId && (
                <span className="ml-2 text-blue-500 font-bold">✓</span>
              )}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
