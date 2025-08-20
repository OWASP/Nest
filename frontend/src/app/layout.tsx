import { GoogleAnalytics } from '@next/third-parties/google';
import type { Metadata } from 'next';
import { Geist, Geist_Mono } from 'next/font/google';
import React from 'react';
import { Providers } from 'wrappers/provider';
import { GTM_ID, IS_GITHUB_AUTH_ENABLED } from 'utils/credentials';
import AutoScrollToTop from 'components/AutoScrollToTop';
import BreadCrumbs from 'components/BreadCrumbs';
import Footer from 'components/Footer';
import Header from 'components/Header';
import ScrollToTop from 'components/ScrollToTop';

import 'app/globals.css';

const geistSans = Geist({
  subsets: ['latin'],
  variable: '--font-geist-sans',
});

const geistMono = Geist_Mono({
  subsets: ['latin'],
  variable: '--font-geist-mono',
});

export const metadata: Metadata = {
  description: 'Your gateway to OWASP. Discover, engage, and help shape the future!',
  icons: {
    apple: 'https://owasp.org/www--site-theme/favicon.ico',
    icon: 'https://owasp.org/www--site-theme/favicon.ico',
    shortcut: 'https://owasp.org/www--site-theme/favicon.ico',
  },
  openGraph: {
    description: 'Your gateway to OWASP. Discover, engage, and help shape the future!',
    images: [
      {
        alt: 'OWASP logo',
        height: 630,
        url: 'https://nest.owasp.org/img/owasp_icon_white_background.png',
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
    images: ['https://nest.owasp.org/img/owasp_icon_white_background.png'],
    site: '@owasp',
    title: 'Home – OWASP Nest',
  },
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={`
          ${geistSans.variable} ${geistMono.variable} antialiased 
          flex flex-col min-h-screen 
          supports-[min-height:100dvh]:min-h-[100dvh] 
          overflow-x-hidden
        `}
      >
        {/* Visually hidden but keyboard-focusable skip link for accessibility */}
        <a
          href="#main-content"
          className="sr-only focus:not-sr-only focus:absolute focus:top-2 focus:left-2 bg-white p-2 z-50"
        >
          Skip to content
        </a>
        <Providers>
          <AutoScrollToTop />
          <Header isGitHubAuthEnabled={IS_GITHUB_AUTH_ENABLED} />
          <BreadCrumbs />
          {/* Single document-wide main landmark for a11y; no nested mains */}
          <main
            id="main-content"
            className="flex-1 flex flex-col min-w-0"
          >
            {children}
          </main>
          <Footer className="mt-auto" />
          <ScrollToTop />
        </Providers>
      </body>
      <GoogleAnalytics gaId={GTM_ID} />
    </html>
  );
}