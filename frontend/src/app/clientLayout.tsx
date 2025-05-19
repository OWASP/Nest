'use client'

import { Geist, Geist_Mono } from 'next/font/google'
import React, { useEffect } from 'react'
import TagManager from 'react-gtm-module'
import { GTM_ID } from 'utils/credentials'
import { Providers } from 'wrappers/provider'
import BreadCrumbs from 'components/BreadCrumbs'
import Footer from 'components/Footer'
import Header from 'components/Header'
import ScrollToTop from 'components/ScrollToTop'
import './globals.css'

const geistSans = Geist({
  variable: '--font-geist-sans',
  subsets: ['latin'],
})

const geistMono = Geist_Mono({
  variable: '--font-geist-mono',
  subsets: ['latin'],
})

export default function ClientLayout({ children }: { children: React.ReactNode }) {
  useEffect(() => {
    TagManager.initialize({ gtmId: GTM_ID })
  }, [])

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
