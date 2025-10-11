import { render, screen } from '@testing-library/react'
import ArchivedBadge from 'components/ArchivedBadge'

jest.mock('@fortawesome/react-fontawesome', () => ({
  FontAwesomeIcon: ({ className }: { className: string }) => (
    <i data-testid="archive-icon" className={className} />
  ),
}))

describe('ArchivedBadge', () => {
  describe('Basic Rendering', () => {
    it('renders successfully with default props', () => {
      render(<ArchivedBadge />)

      expect(screen.getByText('Archived')).toBeInTheDocument()
    })

    it('displays the archived text', () => {
      render(<ArchivedBadge />)

      const badge = screen.getByText('Archived')
      expect(badge).toBeVisible()
    })

    it('has the correct tooltip', () => {
      render(<ArchivedBadge />)

      const badge = screen.getByText('Archived')
      expect(badge).toHaveAttribute('title', 'This repository has been archived and is read-only')
    })
  })

  describe('Size Variants', () => {
    it('renders with small size', () => {
      render(<ArchivedBadge size="sm" />)

      const badge = screen.getByText('Archived')
      expect(badge).toHaveClass('px-2', 'py-1', 'text-xs')
    })

    it('renders with medium size (default)', () => {
      render(<ArchivedBadge size="md" />)

      const badge = screen.getByText('Archived')
      expect(badge).toHaveClass('px-3', 'py-1', 'text-sm')
    })

    it('renders with large size', () => {
      render(<ArchivedBadge size="lg" />)

      const badge = screen.getByText('Archived')
      expect(badge).toHaveClass('px-4', 'py-2', 'text-base')
    })

    it('defaults to medium size when size prop is not provided', () => {
      render(<ArchivedBadge />)

      const badge = screen.getByText('Archived')
      expect(badge).toHaveClass('px-3', 'py-1', 'text-sm')
    })
  })

  describe('Icon Display', () => {
    it('shows icon by default', () => {
      render(<ArchivedBadge />)

      const icon = screen.getByTestId('archive-icon')
      expect(icon).toBeInTheDocument()
    })

    it('shows icon when showIcon is true', () => {
      render(<ArchivedBadge showIcon={true} />)

      const icon = screen.getByTestId('archive-icon')
      expect(icon).toBeInTheDocument()
    })

    it('hides icon when showIcon is false', () => {
      render(<ArchivedBadge showIcon={false} />)

      const icon = screen.queryByTestId('archive-icon')
      expect(icon).not.toBeInTheDocument()
    })

    it('applies correct icon class', () => {
      render(<ArchivedBadge />)

      const icon = screen.getByTestId('archive-icon')
      expect(icon).toHaveClass('h-3', 'w-3')
    })
  })

  describe('Styling', () => {
    it('has correct base styling classes', () => {
      render(<ArchivedBadge />)

      const badge = screen.getByText('Archived')
      expect(badge).toHaveClass('inline-flex', 'items-center', 'gap-1.5', 'rounded-full', 'border')
    })

    it('has correct light mode color classes', () => {
      render(<ArchivedBadge />)

      const badge = screen.getByText('Archived')
      expect(badge).toHaveClass('border-yellow-600', 'bg-yellow-50', 'text-yellow-800')
    })

    it('has correct dark mode color classes', () => {
      render(<ArchivedBadge />)

      const badge = screen.getByText('Archived')
      expect(badge).toHaveClass(
        'dark:border-yellow-500',
        'dark:bg-yellow-900/30',
        'dark:text-yellow-400'
      )
    })

    it('has font-medium class', () => {
      render(<ArchivedBadge />)

      const badge = screen.getByText('Archived')
      expect(badge).toHaveClass('font-medium')
    })
  })

  describe('Custom ClassName', () => {
    it('applies custom className', () => {
      render(<ArchivedBadge className="custom-class" />)

      const badge = screen.getByText('Archived')
      expect(badge).toHaveClass('custom-class')
    })

    it('preserves default classes with custom className', () => {
      render(<ArchivedBadge className="ml-2" />)

      const badge = screen.getByText('Archived')
      expect(badge).toHaveClass('ml-2', 'inline-flex', 'rounded-full')
    })

    it('handles empty custom className', () => {
      render(<ArchivedBadge className="" />)

      const badge = screen.getByText('Archived')
      expect(badge).toBeInTheDocument()
    })
  })

  describe('Accessibility', () => {
    it('renders as a span element', () => {
      render(<ArchivedBadge />)

      const badge = screen.getByText('Archived')
      expect(badge.tagName).toBe('SPAN')
    })

    it('has descriptive tooltip for screen readers', () => {
      render(<ArchivedBadge />)

      const badge = screen.getByText('Archived')
      const title = badge.getAttribute('title')
      expect(title).toBeTruthy()
      expect(title).toContain('archived')
      expect(title).toContain('read-only')
    })

    it('has appropriate semantic structure with icon', () => {
      render(<ArchivedBadge />)

      const badge = screen.getByText('Archived')
      expect(badge).toContainHTML('i')
    })
  })

  describe('Edge Cases', () => {
    it('handles all props together', () => {
      render(<ArchivedBadge size="lg" showIcon={false} className="extra-margin" />)

      const badge = screen.getByText('Archived')
      expect(badge).toBeInTheDocument()
      expect(badge).toHaveClass('px-4', 'py-2', 'text-base', 'extra-margin')
      expect(screen.queryByTestId('archive-icon')).not.toBeInTheDocument()
    })

    it('renders consistently across multiple instances', () => {
      const { rerender } = render(<ArchivedBadge />)

      const firstRender = screen.getByText('Archived').className

      rerender(<ArchivedBadge />)

      const secondRender = screen.getByText('Archived').className
      expect(firstRender).toBe(secondRender)
    })

    it('does not render any interactive elements', () => {
      const { container } = render(<ArchivedBadge />)

      expect(container.querySelector('button')).not.toBeInTheDocument()
      expect(container.querySelector('a')).not.toBeInTheDocument()
      expect(container.querySelector('input')).not.toBeInTheDocument()
    })
  })

  describe('Snapshot Testing', () => {
    it('matches snapshot with default props', () => {
      const { container } = render(<ArchivedBadge />)
      expect(container.firstChild).toMatchSnapshot()
    })

    it('matches snapshot with small size', () => {
      const { container } = render(<ArchivedBadge size="sm" showIcon={false} />)
      expect(container.firstChild).toMatchSnapshot()
    })

    it('matches snapshot with large size and icon', () => {
      const { container } = render(<ArchivedBadge size="lg" showIcon={true} />)
      expect(container.firstChild).toMatchSnapshot()
    })
  })
})
