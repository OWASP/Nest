'use client'

import { ApolloProvider } from '@apollo/client/react'
import { HeroUIProvider, ToastProvider } from '@heroui/react'
import { useDjangoSession } from 'hooks/useDjangoSession'
import { SessionProvider } from 'next-auth/react'
import { ThemeProvider as NextThemesProvider } from 'next-themes'
import React, { Suspense } from 'react'
import apolloClient from 'utils/helpers/apolloClient'

const VALID_THEMES = ['dark', 'light'] as const
type ValidTheme = (typeof VALID_THEMES)[number]

function getValidTheme(): ValidTheme {
  if (typeof window === 'undefined') {
    return 'dark'
  }

  try {
    const stored = localStorage.getItem('__nest_theme__')

    if (stored && VALID_THEMES.includes(stored as ValidTheme)) {
      return stored as ValidTheme
    }

    if (stored) {
      localStorage.removeItem('__nest_theme__')
    }
  } catch {
    // Ignore errors when accessing localStorage
  }

  return 'dark'
}



function AppInitializer() {
  useDjangoSession()
  return null
}

export function Providers({ children }: { children: React.ReactNode }) {
  const [theme] = React.useState<ValidTheme>(getValidTheme)

  return (
    <Suspense>
      <SessionProvider>
        <HeroUIProvider>
          <NextThemesProvider
            attribute="class"
            defaultTheme={theme}
            themes={VALID_THEMES}
            storageKey="__nest_theme__"
          >
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
