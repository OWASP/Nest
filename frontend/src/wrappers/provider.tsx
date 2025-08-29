'use client'

import { HeroUIProvider, ToastProvider } from '@heroui/react'
import { useDjangoSession } from 'hooks/useDjangoSession'
import { SessionProvider } from 'next-auth/react'
import { ThemeProvider as NextThemesProvider } from 'next-themes'
import React, { Suspense } from 'react'

// 🚫 Apollo temporarily disabled
// import { ApolloProvider } from '@apollo/client'
// import apolloClient from 'utils/helpers/apolloClient'

// AppInitializer still syncs your Django session
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
            {/* ApolloProvider temporarily removed */}
            <AppInitializer />
            {children}
          </NextThemesProvider>
        </HeroUIProvider>
      </SessionProvider>
    </Suspense>
  )
}
