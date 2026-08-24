import { render, screen } from '@testing-library/react'
import AccessDeniedDisplay from 'components/AccessDeniedDisplay'

describe('AccessDeniedDisplay', () => {
  it('renders default title and message when props are omitted', () => {
    render(<AccessDeniedDisplay />)
    expect(screen.getByRole('heading', { name: 'Access Denied' })).toBeInTheDocument()
    expect(screen.getByText('You do not have permission to access this page.')).toBeInTheDocument()
  })

  it('renders custom title and message when provided', () => {
    render(<AccessDeniedDisplay title="Custom Title" message="Custom explanation for the user." />)
    expect(screen.getByRole('heading', { name: 'Custom Title' })).toBeInTheDocument()
    expect(screen.getByText('Custom explanation for the user.')).toBeInTheDocument()
  })
})
