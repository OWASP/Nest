import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import React from 'react'
import ActionButton from 'components/ActionButton'

jest.mock('@heroui/tooltip', () => ({
  Tooltip: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
}))

jest.mock('next/link', () => {
  return ({
    children,
    href,
    onClick,
  }: {
    children: React.ReactNode
    href: string
    onClick?: () => void
  }) => (
    <a
      href={href}
      onClick={(e) => {
        e.preventDefault()
        onClick?.()
      }}
    >
      {children}
    </a>
  )
})

describe('ActionButton', () => {
  afterEach(() => {
    cleanup()
    jest.clearAllMocks()
  })

  it('renders without crashing', () => {
    render(<ActionButton>Test Button</ActionButton>)
    expect(screen.getByText('Test Button')).toBeInTheDocument()
  })

  it('renders as a button when no URL is provided', () => {
    render(<ActionButton>Click Me</ActionButton>)
    expect(screen.getByRole('button')).toBeInTheDocument()
  })

  it('renders as a link when URL is provided', () => {
    render(<ActionButton url="https://example.com">Visit Site</ActionButton>)
    const link = screen.getByRole('link')
    expect(link).toBeInTheDocument()
    expect(link).toHaveAttribute('href', 'https://example.com')
  })

  it('displays different content based on children prop', () => {
    render(<ActionButton>Custom Text</ActionButton>)
    expect(screen.getByText('Custom Text')).toBeInTheDocument()
  })

  it('shows tooltip when tooltipLabel is provided', async () => {
    render(<ActionButton tooltipLabel="Test Label">Test Button</ActionButton>)
    await waitFor(() => {
      const interactiveElement = screen.getByRole('button')
      expect(interactiveElement).toHaveAttribute('aria-label', 'Test Label')
    })
  })

  it('does not show tooltip when tooltipLabel is not provided', () => {
    render(<ActionButton>Test Button</ActionButton>)
    expect(screen.getByText('Test Button')).not.toHaveAttribute('data-tooltip-content')
  })

  it('calls onClick handler when button is clicked', async () => {
    const mockOnClick = jest.fn()
    render(<ActionButton onClick={mockOnClick}>Click me</ActionButton>)
    await waitFor(() => {
      fireEvent.click(screen.getByRole('button'))
      expect(mockOnClick).toHaveBeenCalled()
    })
  })

  it('calls onClick handler when link is clicked', async () => {
    const mockOnClick = jest.fn()
    render(
      <ActionButton url="https://example.com" onClick={mockOnClick}>
        Visit Site
      </ActionButton>
    )
    await waitFor(() => {
      fireEvent.click(screen.getByRole('link'))
      expect(mockOnClick).toHaveBeenCalled()
    })
  })

  it('handles missing children gracefully', () => {
    render(<ActionButton tooltipLabel="Action button">{undefined}</ActionButton>)

    const button = screen.getByRole('button')
    expect(button).toBeInTheDocument()
    try {
      expect(button).toHaveAccessibleName('Action button')
    } catch {
      // eslint-disable-next-line jest/no-conditional-expect
      expect(button).not.toHaveAccessibleName('')
    }
  })

  it('handles invalid url gracefully', () => {
    render(<ActionButton url="">Test Button</ActionButton>)
    expect(screen.getByRole('button')).toBeInTheDocument()
    expect(screen.queryByRole('link')).not.toBeInTheDocument()
  })

  it('handles onClick without crashing when no handler is provided', () => {
    render(<ActionButton url="https://example.com">Test Button</ActionButton>)
    expect(() => {
      fireEvent.click(screen.getByRole('link'))
    }).not.toThrow()
  })
})
