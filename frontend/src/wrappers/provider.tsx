'use client'
import { ApolloProvider } from '@apollo/client/react'
import { ToastProvider } from '@heroui/react'
import { useDjangoSession } from 'hooks/useDjangoSession'
import { SessionProvider } from 'next-auth/react'
import { ThemeProvider as NextThemesProvider } from 'next-themes'
import React, { Suspense } from 'react'
import apolloClient from 'utils/helpers/apolloClient'

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
      <div className="flex min-h-screen items-center justify-center text-red-500">
        Configuration Error: GraphQL Client failed to initialize
      </div>
    )
  }

  return (
    <Suspense>
      <SessionProvider>
        <NextThemesProvider attribute="class" defaultTheme="dark">
          <ToastProvider />
          <ApolloProvider client={apolloClient}>
            <AppInitializer />
            {children}
          </ApolloProvider>
        </NextThemesProvider>
      </SessionProvider>
    </Suspense>
  )
}
