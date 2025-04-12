import { HeroUIProvider } from '@heroui/system'
import { render as rtlRender } from '@testing-library/react'
import React from 'react'

function render(ui: React.ReactElement, options = {}) {
  return rtlRender(ui, {
    wrapper: ({ children }) => <HeroUIProvider>{children}</HeroUIProvider>,
    ...options,
  })
}

export * from '@testing-library/react'

export { render }
