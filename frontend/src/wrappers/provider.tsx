'use client'
import { ApolloProvider } from '@apollo/client/react'
import { HeroUIProvider, ToastProvider } from '@heroui/react'
import { useDjangoSession } from 'hooks/useDjangoSession'
import { SessionProvider } from 'next-auth/react'
import { ThemeProvider as NextThemesProvider } from 'next-themes'
import posthog from 'posthog-js'
import { PostHogProvider } from 'posthog-js/react'
import React, { Suspense, useEffect, useState } from 'react'
import { ENVIRONMENT } from 'utils/env.client'
import apolloClient from 'utils/helpers/apolloClient'

// <AppInitializer> is a component that initializes the Django session.
// It ensures the session is synced with Django when the app starts.
// AppInitializer is mounted once. Its job is to call useDjangoSession(),
// which syncs the GitHub access token (stored in the NextAuth session) with the Django session.

function AppInitializer() {
  useDjangoSession()
  return null
}

export function Providers({ children }: { children: React.ReactNode }) {
  const [posthogInitialized, setPosthogInitialized] = useState(false)

  useEffect(() => {
    const isProduction = ENVIRONMENT === 'production'
    const isStaging = ENVIRONMENT === 'staging'
    const posthogKey = process.env.NEXT_PUBLIC_POSTHOG_KEY
    const posthogHost = process.env.NEXT_PUBLIC_POSTHOG_HOST

    if ((isProduction || isStaging) && posthogKey && posthogHost) {
      posthog.init(posthogKey, {
        // eslint-disable-next-line @typescript-eslint/naming-convention
        api_host: posthogHost,
      })
    }

    setPosthogInitialized(true)
  }, [])

  return (
    <Suspense>
      <SessionProvider>
        <HeroUIProvider>
          <NextThemesProvider attribute="class" defaultTheme="dark">
            <ToastProvider />
            {posthogInitialized ? (
              <PostHogProvider client={posthog}>
                <ApolloProvider client={apolloClient}>
                  <AppInitializer />
                  {children}
                </ApolloProvider>
              </PostHogProvider>
            ) : (
              <ApolloProvider client={apolloClient}>
                <AppInitializer />
                {children}
              </ApolloProvider>
            )}
          </NextThemesProvider>
        </HeroUIProvider>
      </SessionProvider>
    </Suspense>
  )
}
