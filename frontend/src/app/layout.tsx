import type { Metadata } from 'next'
import { Geist, Geist_Mono } from 'next/font/google'
import React from 'react'
import { Providers } from 'wrappers/provider'
import Footer from 'components/Footer'

import Header from 'components/Header'
import './globals.css'
const geistSans = Geist({
  variable: '--font-geist-sans',
  subsets: ['latin'],
})

const geistMono = Geist_Mono({
  variable: '--font-geist-mono',
  subsets: ['latin'],
})

export const metadata: Metadata = {
  title: 'OWASP Nest',
  description: 'OWASP Nest',
  icons: {
    icon: 'https://owasp.org/www--site-theme/favicon.ico',
    shortcut: 'https://owasp.org/www--site-theme/favicon.ico',
    apple: 'https://owasp.org/www--site-theme/favicon.ico',
  },
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
        style={{ minHeight: '100vh' }}
      >
        <Providers>
          <Header />
          {children}
          <Footer />
        </Providers>
      </body>
    </html>
  )
}
