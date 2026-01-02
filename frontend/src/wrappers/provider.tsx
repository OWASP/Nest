'use client'

import { ApolloProvider } from '@apollo/client/react'
import { HeroUIProvider, ToastProvider } from '@heroui/react'
import { useDjangoSession } from 'hooks/useDjangoSession'
import { SessionProvider } from 'next-auth/react'
import { ThemeProvider as NextThemesProvider } from 'next-themes'
import React, { Suspense } from 'react'
import apolloClient from 'utils/helpers/apolloClient'

// It ensures the session is synced with Django when the app starts.
// AppInitializer is mounted once. Its job is to call useDjangoSession(),
// which syncs the GitHub access token (stored in the NextAuth session)
// with the Django session.

// -------------------------
// Theme validation helpers
// -------------------------

type ValidTheme = 'dark' | 'light'

const VALID_THEMES: ValidTheme[] = ['dark', 'light']
const THEME_STORAGE_KEY = '__nest_theme__'

/**
 * next-themes applies the persisted theme value directly as a CSS class
 * during initial render.
 *
 * If the stored value contains spaces (e.g. "Default Theme"), the browser
 * throws InvalidCharacterError and the app crashes before rendering.
 *
 * To prevent this, we validate the persisted value and remove it only
 * if it is invalid, allowing next-themes to safely fall back to default.
 */
function getInitialTheme(): ValidTheme {
  if (typeof window === 'undefined') {
    // SSR-safe default
    return 'dark'
  }

  try {
    const stored = localStorage.getItem(THEME_STORAGE_KEY)

    if (stored && VALID_THEMES.includes(stored as ValidTheme)) {
      return stored as ValidTheme
    }

    // Remove invalid persisted value to prevent next-themes crash
    if (stored) {
      localStorage.removeItem(THEME_STORAGE_KEY)
    }
  } catch {
    // Ignore storage access errors and fall back safely
  }

  return 'dark'
}

function AppInitializer() {
  useDjangoSession()
  return null
}

export function Providers({ children }: { children: React.ReactNode }) {
  const [theme] = React.useState<ValidTheme>(getInitialTheme)

  return (
    <Suspense>
      <SessionProvider>
        <HeroUIProvider>
          <NextThemesProvider
            attribute="class"
            defaultTheme={theme}
            themes={VALID_THEMES}
            storageKey={THEME_STORAGE_KEY}
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
