import { screen } from '@testing-library/react'
import { render } from 'wrappers/testUtil'
import NotFound from 'app/not-found'

describe('NotFound Page', () => {
  test('renders ErrorDisplay component with correct 404 configuration', () => {
    render(<NotFound />)

    expect(screen.getByText('404')).toBeInTheDocument()
    expect(screen.getByText('Page Not Found')).toBeInTheDocument()
    expect(
      screen.getByText("Sorry, the page you're looking for doesn't exist.")
    ).toBeInTheDocument()
  })
})
