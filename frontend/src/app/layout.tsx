import type { Metadata } from 'next'
import React from 'react'
import ClientLayout from './clientLayout'

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

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return <ClientLayout>{children}</ClientLayout>
}
