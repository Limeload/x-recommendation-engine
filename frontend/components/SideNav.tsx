'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { House, MagnifyingGlass, Bell } from 'phosphor-react';

const navItems = [
  { href: '/', label: 'Home', icon: House },
  { href: '/explore', label: 'Explore', icon: MagnifyingGlass },
  { href: '/notifications', label: 'Notifications', icon: Bell },
];

export default function SideNav() {
  const pathname = usePathname();

  return (
    <aside className="w-56 flex-shrink-0 sticky top-0 h-screen border-r border-gray-200 flex flex-col py-6 px-3">
      <div className="mb-6 px-4">
        <span className="text-xl font-bold tracking-tight">AlgoFeed</span>
        <p className="text-xs text-gray-400 mt-0.5">Transparent ranking</p>
      </div>

      <nav className="space-y-1 flex-1">
        {navItems.map(({ href, label, icon: Icon }) => {
          const isActive = pathname === href;
          return (
            <Link
              key={href}
              href={href}
              className={`flex items-center gap-3 px-4 py-3 rounded-xl transition font-medium text-sm ${
                isActive
                  ? 'bg-gray-100 text-gray-900'
                  : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
              }`}
            >
              <Icon size={18} weight={isActive ? 'bold' : 'regular'} />
              <span>{label}</span>
            </Link>
          );
        })}
      </nav>

      <div className="mt-auto px-4 text-xs text-gray-400">
        <p>Ranking is fully auditable.</p>
        <p className="mt-0.5">Click "Show Explanation" on any tweet.</p>
      </div>
    </aside>
  );
}
