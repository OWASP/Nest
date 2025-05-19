import type { Metadata } from 'next'
import { Geist, Geist_Mono } from 'next/font/google'
import React from 'react'
import { Providers } from 'wrappers/provider'
import BreadCrumbs from 'components/BreadCrumbs'
import Footer from 'components/Footer'

import Header from 'components/Header'
import ScrollToTop from 'components/ScrollToTop'

import 'app/globals.css'

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
  description: 'Your gateway to OWASP. Discover, engage, and help shape the future!',
  openGraph: {
    title: 'OWASP Nest',
    description: 'Your gateway to OWASP. Discover, engage, and help shape the future!',
    url: 'https://nest.owasp.org/',
    siteName: 'OWASP Nest',
    images: [
      {
        url: 'https://nest.owasp.org/img/owasp_icon_white_background.png',
        width: 1200,
        height: 630,
        alt: 'OWASP logo',
      },
    ],
    locale: 'en_US',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Home – OWASP Nest',
    description: 'Your gateway to OWASP. Discover, engage, and help shape the future!',
    images: ['https://nest.owasp.org/img/owasp_icon_white_background.png'],
    creator: '@owasp',
    site: '@owasp',
  },
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
          <BreadCrumbs />
          {children}
          <Footer />
          <ScrollToTop />
        </Providers>
      </body>
    </html>
  )
}
