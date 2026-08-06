'use client'
import { ApolloProvider } from '@apollo/client/react'
import { HeroUIProvider, ToastProvider } from '@heroui/react'
import { useDjangoSession } from 'hooks/useDjangoSession'
import { SessionProvider } from 'next-auth/react'
import { ThemeProvider as NextThemesProvider } from 'next-themes'
import React, { Suspense } from 'react'
import apolloClient from 'utils/helpers/apolloClient'

// <AppInitializer> is a component that initializes the Django session.
// It ensures the session is synced with Django when the app starts.
// AppInitializer is mounted once. Its job is to call useDjangoSession(),
// which syncs the GitHub access token (stored in the NextAuth session) with the Django session.

function AppInitializer() {
  useDjangoSession()
  return null
}

export function Providers({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  if (!apolloClient) {
    return (
      <div className="flex min-h-screen items-center justify-center px-4 text-red-500">
        <div className="max-w-2xl text-center">
          <h1 className="text-xl font-semibold">GraphQL client is not configured</h1>
          <p className="mt-2 text-sm text-foreground-700">
            The frontend could not initialize Apollo because the GraphQL endpoint is unavailable.
          </p>
          <p className="mt-2 text-sm text-foreground-700">
            <strong>Set NEXT_PUBLIC_GRAPHQL_URL in frontend/.env</strong> and ensure the backend GraphQL service
            is running.
          </p>
        </div>
      </div>
    )
  }

  return (
    <Suspense>
      <SessionProvider>
        <HeroUIProvider>
          <NextThemesProvider attribute="class" defaultTheme="dark">
            <ToastProvider />
            <ApolloProvider client={apolloClient}>
              <AppInitializer />
              {children}
            </ApolloProvider>
          </NextThemesProvider>
        </HeroUIProvider>
      </SessionProvider>
    </Suspense>
  )
}
