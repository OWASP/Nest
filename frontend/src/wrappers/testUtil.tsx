import { ChakraProvider } from '@chakra-ui/react'
import { render as rtlRender } from '@testing-library/react'
import React from 'react'
import { BrowserRouter } from 'react-router-dom'
import { system } from 'utils/theme'

function render(ui: React.ReactElement, options = {}) {
  return rtlRender(ui, {
    wrapper: ({ children }) => (
      <BrowserRouter>
        {' '}
        <ChakraProvider value={system}>{children}</ChakraProvider>
      </BrowserRouter>
    ),
    ...options,
  })
}

export * from '@testing-library/react'

export { render }
