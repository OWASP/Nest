import { GoogleAnalytics } from '@next/third-parties/google'
import { BreadcrumbRoot } from 'contexts/BreadcrumbContext'
import type { Metadata } from 'next'
import { Geist, Geist_Mono } from 'next/font/google'
import React from 'react'
import { Providers } from 'wrappers/provider'
import { GTM_ID } from 'utils/env.client'
import { IS_GITHUB_AUTH_ENABLED } from 'utils/env.server'
import AutoScrollToTop from 'components/AutoScrollToTop'
import BreadCrumbsWrapper from 'components/BreadCrumbsWrapper'
import Footer from 'components/Footer'
import Header from 'components/Header'
import ScrollToTop from 'components/ScrollToTop'

import 'app/globals.css'

export const dynamic = 'force-dynamic'

const geistSans = Geist({
  subsets: ['latin'],
  variable: '--font-geist-sans',
})

const geistMono = Geist_Mono({
  subsets: ['latin'],
  variable: '--font-geist-mono',
})

export const metadata: Metadata = {
  description: 'Your gateway to OWASP. Discover, engage, and help shape the future!',
  icons: {
    apple: '/img/favicon.ico',
    icon: '/img/favicon.ico',
    shortcut: '/img/favicon.ico',
  },
  openGraph: {
    description: 'Your gateway to OWASP. Discover, engage, and help shape the future!',
    images: [
      {
        alt: 'OWASP logo',
        height: 630,
        url: 'https://nest.owasp.org/img/nest_1200x630_light.png',
        width: 1200,
      },
    ],
    locale: 'en_US',
    siteName: 'OWASP Nest',
    title: 'OWASP Nest',
    type: 'website',
    url: 'https://nest.owasp.org/',
  },
  title: 'OWASP Nest',
  twitter: {
    card: 'summary_large_image',
    creator: '@owasp',
    description: 'Your gateway to OWASP. Discover, engage, and help shape the future!',
    images: ['https://nest.owasp.org/img/nest_1200x630_light.png'],
    site: '@owasp',
    title: 'Home – OWASP Nest',
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
          <BreadcrumbRoot>
            <div className="flex min-h-screen flex-col">
              <AutoScrollToTop />
              <Header isGitHubAuthEnabled={IS_GITHUB_AUTH_ENABLED} />
              <BreadCrumbsWrapper />
              <main className="flex flex-1 flex-col justify-center">{children}</main>
              <Footer />
              <ScrollToTop />
            </div>
          </BreadcrumbRoot>
        </Providers>
        {/* Fixed: Guaranteed string value for GoogleAnalytics to satisfy strict typing */}
        <GoogleAnalytics gaId={GTM_ID || ''} />
      </body>
    </html>
  )
}