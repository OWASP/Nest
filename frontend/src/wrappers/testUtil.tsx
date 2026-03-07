import { HeroUIProvider } from '@heroui/system'
import { render as rtlRender } from '@testing-library/react'
import { BreadcrumbRoot } from 'contexts/BreadcrumbContext'
import React from 'react'
import { createMockApolloClient } from 'utils/helpers/mockApolloClient'

const mockApolloClient = createMockApolloClient()

// eslint-disable-next-line @typescript-eslint/no-require-imports
const ApolloProvider = (require('@apollo/client/react') as Record<string, unknown>)
  .ApolloProvider as React.ComponentType<Record<string, unknown>> | null

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
