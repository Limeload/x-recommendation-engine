import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'X Recommendation Engine',
  description: 'Personalized, explainable, and tunable recommendation system',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
