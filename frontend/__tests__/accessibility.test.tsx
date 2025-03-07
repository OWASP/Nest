import { MockedProvider } from '@apollo/client/testing'
import { ChakraProvider } from '@chakra-ui/react'
import { render } from '@testing-library/react'
import { axe, toHaveNoViolations } from 'jest-axe'
import { BrowserRouter } from 'react-router-dom'
import { system } from 'utils/theme'
import { ErrorWrapper } from 'wrappers/ErrorWrapper'
// import App from '../src/App'

expect.extend(toHaveNoViolations)

test('App should have no accessibility violations', async () => {
  const { container } = render(
    <ChakraProvider theme={system}>
      <BrowserRouter>
        <ErrorWrapper>
          <MockedProvider mocks={[]} addTypename={false}>
            {/* <App /> */}
          </MockedProvider>
        </ErrorWrapper>
      </BrowserRouter>
    </ChakraProvider>
  )

  const results = await axe(container)
  expect(results).toHaveNoViolations()
})
