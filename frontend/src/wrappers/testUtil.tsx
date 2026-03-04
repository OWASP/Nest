import { HeroUIProvider } from '@heroui/system'
import { render as rtlRender } from '@testing-library/react'
import { BreadcrumbRoot } from 'contexts/BreadcrumbContext'
import React from 'react'
import { createMockApolloClient } from 'utils/helpers/mockApolloClient'

const mockApolloClient = createMockApolloClient()

let ApolloProvider: React.ComponentType<Record<string, unknown>> | null = null

;(async () => {
  try {
    const apolloModule = (await import('@apollo/client/react')) as Record<string, unknown>
    ApolloProvider = apolloModule.ApolloProvider as React.ComponentType<
      Record<string, unknown>
    > | null
  } catch {
    // Module may be mocked in tests, will handle gracefully below
  }
})()

function render(ui: React.ReactElement, options = {}) {
  const wrapper = ({ children }: { children: React.ReactNode }) => {
    const content = (
      <HeroUIProvider>
        <BreadcrumbRoot>{children}</BreadcrumbRoot>
      </HeroUIProvider>
    )

    if (ApolloProvider) {
      return React.createElement(ApolloProvider, { client: mockApolloClient }, content)
    }

    return content
  }

  return rtlRender(ui, {
    wrapper,
    ...options,
  })
}

export * from '@testing-library/react'

export { render }
