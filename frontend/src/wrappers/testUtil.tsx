import { HeroUIProvider } from '@heroui/system'
import { screen, fireEvent, waitFor, within } from '@testing-library/dom'
import { render as rtlRender, cleanup } from '@testing-library/react'
import React from 'react'

function render(ui: React.ReactElement, options = {}) {
  return rtlRender(ui, {
    wrapper: ({ children }) => <HeroUIProvider>{children}</HeroUIProvider>,
    ...options,
  })
}

export { render, screen, fireEvent, waitFor, within, cleanup }
export * from '@testing-library/react'
