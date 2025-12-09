'use client'
import { ApolloProvider } from '@apollo/client/react'
import { HeroUIProvider, ToastProvider } from '@heroui/react'
import { useDjangoSession } from 'hooks/useDjangoSession'
import { SessionProvider } from 'next-auth/react'
import { ThemeProvider as NextThemesProvider } from 'next-themes'
import posthog from 'posthog-js'
import { PostHogProvider } from 'posthog-js/react'
import React, { Suspense, useEffect } from 'react'
import apolloClient from 'utils/helpers/apolloClient'

// <AppInitializer> is a component that initializes the Django session.
// It ensures the session is synced with Django when the app starts.
// AppInitializer is mounted once. Its job is to call useDjangoSession(),
// which syncs the GitHub access token (stored in the NextAuth session) with the Django session.

function AppInitializer() {
  useDjangoSession()

  // Initialize PostHog
  useEffect(() => {
    const isProduction = process.env.NEXT_PUBLIC_ENVIRONMENT === 'production'
    const isStaging = process.env.NEXT_PUBLIC_ENVIRONMENT === 'staging'

    if (isProduction || isStaging) {
      posthog.init(process.env.NEXT_PUBLIC_POSTHOG_KEY, {
        // eslint-disable-next-line @typescript-eslint/naming-convention
        api_host: process.env.NEXT_PUBLIC_POSTHOG_HOST,
      })
    }
  }, [])

  return null
}

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <Suspense>
      <SessionProvider>
        <HeroUIProvider>
          <NextThemesProvider attribute="class" defaultTheme="dark">
            <ToastProvider />
            <PostHogProvider client={posthog}>
              <ApolloProvider client={apolloClient}>
                <AppInitializer />
                {children}
              </ApolloProvider>
            </PostHogProvider>
          </NextThemesProvider>
        </HeroUIProvider>
      </SessionProvider>
    </Suspense>
  )
}
