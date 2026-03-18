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
    <div className="flex min-h-screen flex-col items-center justify-center gap-4 text-center">
      <h1 className="text-xl font-semibold text-red-500">
        ⚠️ Backend connection failed
      </h1>

      <p className="text-gray-500 max-w-md">
        Unable to initialize the GraphQL client. This usually means the backend
        server is not running or environment variables are not configured
        correctly.
      </p>

      <div className="text-sm text-gray-400">
        <p>Try the following:</p>
        <ul className="mt-2 list-disc list-inside">
          <li>Start the backend server</li>
          <li>Check your environment variables (e.g. NEXT_PUBLIC_API_URL)</li>
          
        </ul>
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
