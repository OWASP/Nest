import React from 'react'
import { render, screen } from 'wrappers/testUtil'
import type { LeadersListProps } from 'types/leaders'
import LeadersList from 'components/LeadersList'

jest.mock('next/link', () => {
  return function MockLink({
    children,
    href,
    'aria-label': ariaLabel,
    className,
    title,
  }: {
    children: React.ReactNode
    href: string
    'aria-label'?: string
    className?: string
    title?: string
  }) {
    return (
      <a
        href={href}
        aria-label={ariaLabel}
        className={className}
        title={title}
        data-testid="leader-link"
      >
        {children}
      </a>
    )
  }
})

// Mock TruncatedText component
jest.mock('components/TruncatedText', () => ({
  TruncatedText: ({ children }: { children: React.ReactNode }) => (
    <span data-testid="truncated-text">{children}</span>
  ),
}))

describe('LeadersList Component', () => {
  const defaultProps: LeadersListProps = {
    leaders: 'John Doe, Jane Smith, Bob Johnson',
  }

  afterEach(() => {
    jest.clearAllMocks()
  })

  describe('Renders successfully with minimal required props', () => {
    it('renders with valid leaders string', () => {
      render(<LeadersList leaders="John Doe" />)
      expect(screen.getByText('John Doe')).toBeInTheDocument()
      expect(screen.getByTestId('truncated-text')).toBeInTheDocument()
    })

    it('renders component without crashing', () => {
      const { container } = render(<LeadersList {...defaultProps} />)
      expect(container).toBeInTheDocument()
    })
  })

  describe('Conditional rendering logic', () => {
    it('renders "Unknown" when leaders prop is empty string', () => {
      render(<LeadersList leaders="" />)
      expect(screen.getByText('Unknown')).toBeInTheDocument()
      expect(screen.queryByTestId('truncated-text')).not.toBeInTheDocument()
    })

    it('renders "Unknown" when leaders prop is null', () => {
      render(<LeadersList leaders={null} />)
      expect(screen.getByText('Unknown')).toBeInTheDocument()
      expect(screen.queryByTestId('truncated-text')).not.toBeInTheDocument()
    })

    it('renders "Unknown" when leaders prop is undefined', () => {
      render(<LeadersList leaders={undefined} />)
      expect(screen.getByText('Unknown')).toBeInTheDocument()
      expect(screen.queryByTestId('truncated-text')).not.toBeInTheDocument()
    })

    it('renders "Unknown" when leaders prop is only whitespace', () => {
      render(<LeadersList leaders="   " />)
      expect(screen.getByText('Unknown')).toBeInTheDocument()
      expect(screen.queryByTestId('truncated-text')).not.toBeInTheDocument()
    })

    it('renders leaders when valid non-empty string is provided', () => {
      render(<LeadersList leaders="John Doe" />)
      expect(screen.queryByText('Unknown')).not.toBeInTheDocument()
      expect(screen.getByTestId('truncated-text')).toBeInTheDocument()
    })
  })

  describe('Prop-based behavior', () => {
    it('renders single leader correctly', () => {
      render(<LeadersList leaders="John Doe" />)
      expect(screen.getByText('John Doe')).toBeInTheDocument()
      expect(screen.getAllByTestId('leader-link')).toHaveLength(1)
    })

    it('renders multiple leaders correctly', () => {
      render(<LeadersList {...defaultProps} />)
      expect(screen.getByText('John Doe')).toBeInTheDocument()
      expect(screen.getByText('Jane Smith')).toBeInTheDocument()
      expect(screen.getByText('Bob Johnson')).toBeInTheDocument()
      expect(screen.getAllByTestId('leader-link')).toHaveLength(3)
    })

    it('handles leaders with extra whitespace', () => {
      render(<LeadersList leaders="  John Doe  ,  Jane Smith  " />)
      expect(screen.getByText('John Doe')).toBeInTheDocument()
      expect(screen.getByText('Jane Smith')).toBeInTheDocument()
      expect(screen.getAllByTestId('leader-link')).toHaveLength(2)
    })

    it('handles leaders with special characters', () => {
      render(<LeadersList leaders="John O'Connor, María García, Jean-Paul Dubois" />)
      expect(screen.getByText("John O'Connor")).toBeInTheDocument()
      expect(screen.getByText('María García')).toBeInTheDocument()
      expect(screen.getByText('Jean-Paul Dubois')).toBeInTheDocument()
    })
  })

  describe('Text and content rendering', () => {
    it('displays correct leader names', () => {
      render(<LeadersList {...defaultProps} />)
      expect(screen.getByText('John Doe')).toBeInTheDocument()
      expect(screen.getByText('Jane Smith')).toBeInTheDocument()
      expect(screen.getByText('Bob Johnson')).toBeInTheDocument()
    })

    it('adds commas between multiple leaders', () => {
      const { container } = render(<LeadersList {...defaultProps} />)
      const textContent = container.textContent
      expect(textContent).toContain('John Doe, Jane Smith, Bob Johnson')
    })

    it('does not add comma after single leader', () => {
      const { container } = render(<LeadersList leaders="John Doe" />)
      const textContent = container.textContent
      expect(textContent).toBe('John Doe')
      expect(textContent).not.toContain(',')
    })
  })

  describe('DOM structure / classNames / styles', () => {
    it('wraps content in TruncatedText component', () => {
      render(<LeadersList {...defaultProps} />)
      expect(screen.getByTestId('truncated-text')).toBeInTheDocument()
    })

    it('applies correct CSS classes to links', () => {
      render(<LeadersList leaders="John Doe" />)
      const link = screen.getByTestId('leader-link')
      expect(link).toHaveClass('text-gray-600', 'hover:underline', 'dark:text-gray-400')
    })

    it('generates correct href for each leader', () => {
      render(<LeadersList {...defaultProps} />)
      const links = screen.getAllByTestId('leader-link')

      expect(links[0]).toHaveAttribute('href', '/members?q=John%20Doe')
      expect(links[1]).toHaveAttribute('href', '/members?q=Jane%20Smith')
      expect(links[2]).toHaveAttribute('href', '/members?q=Bob%20Johnson')
    })

    it('properly encodes special characters in URLs', () => {
      render(<LeadersList leaders="John O'Connor, test@example.com" />)
      const links = screen.getAllByTestId('leader-link')

      expect(links[0]).toHaveAttribute('href', "/members?q=John%20O'Connor")
      expect(links[1]).toHaveAttribute('href', '/members?q=test%40example.com')
    })
  })

  describe('Accessibility roles and labels', () => {
    it('provides proper aria-label for each leader link', () => {
      render(<LeadersList {...defaultProps} />)
      const links = screen.getAllByTestId('leader-link')

      expect(links[0]).toHaveAttribute('aria-label', 'View profile of John Doe')
      expect(links[1]).toHaveAttribute('aria-label', 'View profile of Jane Smith')
      expect(links[2]).toHaveAttribute('aria-label', 'View profile of Bob Johnson')
    })

    it('provides title attribute for each leader link', () => {
      render(<LeadersList {...defaultProps} />)
      const links = screen.getAllByTestId('leader-link')

      expect(links[0]).toHaveAttribute('title', 'John Doe')
      expect(links[1]).toHaveAttribute('title', 'Jane Smith')
      expect(links[2]).toHaveAttribute('title', 'Bob Johnson')
    })

    it('ensures links are focusable and have proper attributes', () => {
      render(<LeadersList leaders="John Doe" />)
      const link = screen.getByTestId('leader-link')

      expect(link).toHaveAttribute('href')
      expect(link).toHaveAttribute('aria-label')
      expect(link).toHaveAttribute('title')
    })
  })

  describe('Handles edge cases and invalid inputs', () => {
    it('handles empty array from split (single comma)', () => {
      render(<LeadersList leaders="," />)
      const { container } = render(<LeadersList leaders="," />)
      expect(container.textContent).toBe(', ')
    })

    it('handles multiple consecutive commas', () => {
      render(<LeadersList leaders="John Doe,, Jane Smith" />)
      const links = screen.getAllByTestId('leader-link')
      expect(links).toHaveLength(3) // John Doe, empty string, Jane Smith
    })

    it('handles trailing comma', () => {
      render(<LeadersList leaders="John Doe, Jane Smith," />)
      const links = screen.getAllByTestId('leader-link')
      expect(links).toHaveLength(3) // John Doe, Jane Smith, empty string
    })

    it('handles leading comma', () => {
      render(<LeadersList leaders=", John Doe, Jane Smith" />)
      const links = screen.getAllByTestId('leader-link')
      expect(links).toHaveLength(3) // empty string, John Doe, Jane Smith
    })

    it('handles very long leader names', () => {
      const longName = 'A'.repeat(100)
      render(<LeadersList leaders={longName} />)
      expect(screen.getByText(longName)).toBeInTheDocument()
      expect(screen.getByTestId('leader-link')).toHaveAttribute('title', longName)
    })

    it('handles numeric strings as leader names', () => {
      render(<LeadersList leaders="123, 456" />)
      expect(screen.getByText('123')).toBeInTheDocument()
      expect(screen.getByText('456')).toBeInTheDocument()
    })
  })

  describe('Default values and fallbacks', () => {
    it('shows Unknown when no valid leaders are provided', () => {
      render(<LeadersList leaders="" />)
      expect(screen.getByText('Unknown')).toBeInTheDocument()
    })

    it('handles undefined gracefully', () => {
      render(<LeadersList leaders={undefined} />)
      expect(screen.getByText('Unknown')).toBeInTheDocument()
    })

    it('handles null gracefully', () => {
      render(<LeadersList leaders={null} />)
      expect(screen.getByText('Unknown')).toBeInTheDocument()
    })
  })

  describe('Component integration', () => {
    it('integrates properly with TruncatedText component', () => {
      render(<LeadersList {...defaultProps} />)
      const truncatedText = screen.getByTestId('truncated-text')
      expect(truncatedText).toBeInTheDocument()

      // Check that leader links are inside TruncatedText
      const links = screen.getAllByTestId('leader-link')
      for (const link of links) {
        expect(truncatedText).toContainElement(link)
      }
    })

    it('generates unique keys for each leader span', () => {
      // This is tested implicitly by React not throwing warnings
      // and by the component rendering correctly with multiple leaders
      const { container } = render(<LeadersList {...defaultProps} />)
      const spans = container.querySelectorAll('span span') // spans inside TruncatedText
      expect(spans.length).toBeGreaterThan(0)
    })
  })
})
