'use client'

import { ApolloProvider } from '@apollo/client'
import { HeroUIProvider, ToastProvider } from '@heroui/react'
import { ThemeProvider as NextThemesProvider } from 'next-themes'
import React, { Suspense } from 'react'
import apolloClient from 'utils/helpers/apolloClient'

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <Suspense>
      <HeroUIProvider>
        <NextThemesProvider attribute="class" defaultTheme="dark">
          <ToastProvider />
          <ApolloProvider client={apolloClient}>{children}</ApolloProvider>
        </NextThemesProvider>
      </HeroUIProvider>
    </Suspense>
  )
}
