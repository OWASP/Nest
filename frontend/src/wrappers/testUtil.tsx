import { HeroUIProvider } from '@heroui/system'
import { render as rtlRender, screen, fireEvent, waitFor, cleanup } from '@testing-library/react'
import { within } from '@testing-library/dom'
import React from 'react'

function render(ui: React.ReactElement, options = {}) {
  return rtlRender(ui, {
    wrapper: ({ children }) => <HeroUIProvider>{children}</HeroUIProvider>,
    ...options,
  })
}

export { render, screen, fireEvent, waitFor, within, cleanup }
export * from '@testing-library/react'
