'use client'
import { ApolloProvider } from '@apollo/client/react'
import { HeroUIProvider, ToastProvider } from '@heroui/react'
import { addToast } from '@heroui/toast'
import { useDjangoSession } from 'hooks/useDjangoSession'
import { SessionProvider } from 'next-auth/react'
import { ThemeProvider as NextThemesProvider } from 'next-themes'
import React, { Suspense } from 'react'
import apolloClient from 'utils/helpers/apolloClient'
import { ENVIRONMENT, GRAPHQL_URL } from 'utils/env.client'
import { getCsrfToken } from 'utils/utility'

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
  const isProduction = ENVIRONMENT === 'production'
  const [isGraphQLEndpointUnreachable, setIsGraphQLEndpointUnreachable] = React.useState(false)
  const lastToastMessageRef = React.useRef<string | null>(null)

  React.useEffect(() => {
    if (!apolloClient || !GRAPHQL_URL) {
      return
    }
    const graphqlUrl = GRAPHQL_URL

    const abortController = new AbortController()


    const verifyGraphQLEndpoint = async () => {
      try {
        const csrfToken = await getCsrfToken()
        const response = await fetch(graphqlUrl, {
          body: JSON.stringify({ query: 'query { __typename }' }),
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
          },
          method: 'POST',
          signal: abortController.signal,
        })

        if (!response.ok) {
          setIsGraphQLEndpointUnreachable(true)
          return
        }

        setIsGraphQLEndpointUnreachable(false)
      } catch {
        if (!abortController.signal.aborted) {
          setIsGraphQLEndpointUnreachable(true)
        }
      }
    }

    void verifyGraphQLEndpoint()

    return () => {
      abortController.abort()
    }
  }, [])

  const graphQLErrorMessage = !apolloClient
    ? isProduction
      ? 'Something went wrong'
      : 'GraphQL client setup required. Ensure backend is running and GraphQL environment variables are configured.'
    : isGraphQLEndpointUnreachable
      ? isProduction
        ? 'Something went wrong'
        : 'GraphQL endpoint is unreachable. Ensure the backend service is running and NEXT_PUBLIC_GRAPHQL_URL is correct.'
      : null

  React.useEffect(() => {
    if (!graphQLErrorMessage || lastToastMessageRef.current === graphQLErrorMessage) {
      return
    }

    addToast({
      color: 'danger',
      description: graphQLErrorMessage,
      shouldShowTimeoutProgress: true,
      timeout: 5000,
      title: 'Configuration Error',
      variant: 'solid',
    })

    lastToastMessageRef.current = graphQLErrorMessage
  }, [graphQLErrorMessage])

  return (
    <Suspense>
      <SessionProvider>
        <HeroUIProvider>
          <NextThemesProvider attribute="class" defaultTheme="dark">
            <ToastProvider />
            {apolloClient ? (
              <ApolloProvider client={apolloClient}>
                <AppInitializer />
                {children}
              </ApolloProvider>
            ) : null}
          </NextThemesProvider>
        </HeroUIProvider>
      </SessionProvider>
    </Suspense>
  )
}
