/**
 * User Selector Component
 * Dropdown to select which user's feed to view
 */

'use client';

import React, { useState } from 'react';
import { User, CaretDown, Check } from 'phosphor-react';
import { User as UserType } from '@/types';

interface UserSelectorProps {
  users: UserType[];
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
        className="px-3 py-2 bg-gray-100 hover:bg-gray-200 border border-gray-300 rounded-lg text-sm font-medium flex items-center space-x-2 transition text-gray-900"
      >
        <User size={16} weight="bold" />
        <span>{selectedUser?.username || 'Select User'}</span>
        <CaretDown size={12} weight="bold" />
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-64 bg-white border border-gray-200 rounded-lg shadow-lg z-50 max-h-96 overflow-y-auto">
          {users.map((user) => (
            <button
              key={user.user_id}
              onClick={() => {
                onSelect(user.user_id);
                setIsOpen(false);
              }}
              className={`w-full text-left px-4 py-3 border-b border-gray-100 hover:bg-gray-50 transition flex items-start justify-between ${
                user.user_id === selectedUserId ? 'bg-gray-50' : ''
              }`}
            >
              <div className="flex-1 min-w-0">
                <div className="font-medium text-sm text-gray-900">{user.username}</div>
                <div className="text-xs text-gray-600 flex items-center space-x-1 mt-1">
                  <span className="px-2 py-0.5 bg-gray-100 rounded text-gray-700">
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
                <Check size={16} weight="bold" className="ml-2 text-gray-900" />
              )}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
