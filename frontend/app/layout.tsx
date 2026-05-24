import type { Metadata } from 'next';
import Link from 'next/link';
import './globals.css';

export const metadata: Metadata = {
  title: 'X Recommendation Engine',
  description: 'Personalized, explainable, and tunable recommendation system',
};

function NavLink({ href, label, emoji }: { href: string; label: string; emoji: string }) {
  return (
    <Link
      href={href}
      className="flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-gray-100 transition text-gray-700 hover:text-gray-900 font-medium text-sm group"
    >
      <span className="text-lg group-hover:scale-110 transition-transform">{emoji}</span>
      <span>{label}</span>
    </Link>
  );
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-white text-gray-900">
        <div className="min-h-screen flex max-w-7xl mx-auto">

          {/* ── Left Nav Sidebar ── */}
          <aside className="w-56 flex-shrink-0 sticky top-0 h-screen border-r border-gray-200 flex flex-col py-6 px-3">
            <div className="mb-6 px-4">
              <span className="text-xl font-bold tracking-tight">AlgoFeed</span>
              <p className="text-xs text-gray-400 mt-0.5">Transparent ranking</p>
            </div>

            <nav className="space-y-1 flex-1">
              <NavLink href="/" label="Home" emoji="🏠" />
              <NavLink href="/explore" label="Explore" emoji="🔍" />
              <NavLink href="/notifications" label="Notifications" emoji="🔔" />
            </nav>

            <div className="mt-auto px-4 text-xs text-gray-400">
              <p>Ranking is fully auditable.</p>
              <p className="mt-0.5">Click "Show Explanation" on any tweet.</p>
            </div>
          </aside>

          {/* ── Page Content ── */}
          <main className="flex-1 min-w-0">
            {children}
          </main>

        </div>
      </body>
    </html>
  );
}
