import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'New site',
  description: 'Configure metadata when implementing pages.',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ja">
      <body className="antialiased">{children}</body>
    </html>
  )
}
