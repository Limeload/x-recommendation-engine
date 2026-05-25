import type { Metadata } from 'next';
import SideNav from '@/components/SideNav';
import './globals.css';

export const metadata: Metadata = {
  title: 'X Recommendation Engine',
  description: 'Personalized, explainable, and tunable recommendation system',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-white text-gray-900">
        <div className="min-h-screen flex max-w-7xl mx-auto">
          <SideNav />
          <main className="flex-1 min-w-0">
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}
