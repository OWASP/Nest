'use client'

import { ApolloProvider } from '@apollo/client'
import { HeroUIProvider, ToastProvider } from '@heroui/react'
import { useDjangoSession } from 'hooks/useDjangoSession'
import { SessionProvider } from 'next-auth/react'
import { ThemeProvider as NextThemesProvider } from 'next-themes'
import React, { Suspense } from 'react'
import apolloClient from 'utils/helpers/apolloClient'

function AppInitializer() {
  useDjangoSession()
  return null
}

export function Providers({ children }: { children: React.ReactNode }) {
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
