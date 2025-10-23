import { render, screen } from '@testing-library/react'
import StatusBadge from 'components/StatusBadge'

jest.mock('@fortawesome/react-fontawesome', () => ({
  FontAwesomeIcon: ({ className }: { className: string }) => (
    <svg className={className} aria-hidden="true" />
  ),
}))

describe('StatusBadge', () => {
  describe('Basic Rendering', () => {
    it('renders successfully with archived status', () => {
      render(<StatusBadge status="archived" />)
      expect(screen.getByText('Archived')).toBeInTheDocument()
    })

    it('renders successfully with inactive status', () => {
      render(<StatusBadge status="inactive" />)
      expect(screen.getByText('Inactive')).toBeInTheDocument()
    })

    it('displays the status text', () => {
      render(<StatusBadge status="archived" />)
      const badge = screen.getByText('Archived')
      expect(badge).toBeVisible()
    })
  })

  describe('Status Types - Archived', () => {
    it('has the correct tooltip for archived status', () => {
      render(<StatusBadge status="archived" />)
      const badge = screen.getByText('Archived')
      expect(badge).toHaveAttribute('title', 'This entity has been archived and is read-only')
    })

    it('has correct light mode color classes for archived', () => {
      render(<StatusBadge status="archived" />)
      const badge = screen.getByText('Archived')
      expect(badge).toHaveClass('border-yellow-600', 'bg-yellow-50', 'text-yellow-800')
    })

    it('has correct dark mode color classes for archived', () => {
      render(<StatusBadge status="archived" />)
      const badge = screen.getByText('Archived')
      expect(badge).toHaveClass(
        'dark:border-yellow-500',
        'dark:bg-yellow-900/30',
        'dark:text-yellow-400'
      )
    })
  })

  describe('Status Types - Inactive', () => {
    it('has the correct tooltip for inactive status', () => {
      render(<StatusBadge status="inactive" />)
      const badge = screen.getByText('Inactive')
      expect(badge).toHaveAttribute('title', 'This entity is currently inactive')
    })

    it('has correct light mode color classes for inactive', () => {
      render(<StatusBadge status="inactive" />)
      const badge = screen.getByText('Inactive')
      expect(badge).toHaveClass('border-red-600', 'bg-red-50', 'text-red-800')
    })

    it('has correct dark mode color classes for inactive', () => {
      render(<StatusBadge status="inactive" />)
      const badge = screen.getByText('Inactive')
      expect(badge).toHaveClass('dark:border-red-500', 'dark:bg-red-900/30', 'dark:text-red-400')
    })
  })

  describe('Size Variants', () => {
    it('renders with small size', () => {
      render(<StatusBadge status="archived" size="sm" />)
      const badge = screen.getByText('Archived')
      expect(badge).toHaveClass('px-2', 'py-1', 'text-xs')
    })

    it('renders with medium size (default)', () => {
      render(<StatusBadge status="archived" size="md" />)
      const badge = screen.getByText('Archived')
      expect(badge).toHaveClass('px-3', 'py-1', 'text-sm')
    })

    it('renders with large size', () => {
      render(<StatusBadge status="archived" size="lg" />)
      const badge = screen.getByText('Archived')
      expect(badge).toHaveClass('px-4', 'py-2', 'text-base')
    })

    it('defaults to medium size when size prop is not provided', () => {
      render(<StatusBadge status="archived" />)
      const badge = screen.getByText('Archived')
      expect(badge).toHaveClass('px-3', 'py-1', 'text-sm')
    })
  })

  describe('Icon Display', () => {
    it('shows icon by default', () => {
      const { container } = render(<StatusBadge status="archived" />)
      const icon = container.querySelector('svg')
      expect(icon).toBeInTheDocument()
    })

    it('shows icon when showIcon is true', () => {
      const { container } = render(<StatusBadge status="archived" showIcon={true} />)
      const icon = container.querySelector('svg')
      expect(icon).toBeInTheDocument()
    })

    it('hides icon when showIcon is false', () => {
      const { container } = render(<StatusBadge status="archived" showIcon={false} />)
      const icon = container.querySelector('svg')
      expect(icon).not.toBeInTheDocument()
    })

    it('applies correct icon class', () => {
      const { container } = render(<StatusBadge status="archived" />)
      const icon = container.querySelector('svg')
      expect(icon).toHaveClass('h-3', 'w-3')
    })

    it('hides icon for inactive status when showIcon is false', () => {
      const { container } = render(<StatusBadge status="inactive" showIcon={false} />)
      const icon = container.querySelector('svg')
      expect(icon).not.toBeInTheDocument()
    })
  })

  describe('Custom Overrides', () => {
    it('uses custom text when provided', () => {
      render(<StatusBadge status="archived" customText="Read-Only" />)
      expect(screen.getByText('Read-Only')).toBeInTheDocument()
      expect(screen.queryByText('Archived')).not.toBeInTheDocument()
    })

    it('uses custom tooltip when provided', () => {
      render(<StatusBadge status="archived" customTooltip="Custom tooltip text" />)
      const badge = screen.getByText('Archived')
      expect(badge).toHaveAttribute('title', 'Custom tooltip text')
    })

    it('maintains default text when customText is not provided', () => {
      render(<StatusBadge status="inactive" />)
      expect(screen.getByText('Inactive')).toBeInTheDocument()
    })

    it('applies custom text with correct styling', () => {
      render(<StatusBadge status="inactive" customText="Not Active" />)
      const badge = screen.getByText('Not Active')
      expect(badge).toHaveClass('bg-red-50', 'text-red-800')
    })
  })

  describe('Styling', () => {
    it('has correct base styling classes', () => {
      render(<StatusBadge status="archived" />)
      const badge = screen.getByText('Archived')
      expect(badge).toHaveClass('inline-flex', 'items-center', 'gap-1.5', 'rounded-full', 'border')
    })

    it('has font-medium class', () => {
      render(<StatusBadge status="archived" />)
      const badge = screen.getByText('Archived')
      expect(badge).toHaveClass('font-medium')
    })

    it('maintains consistent styling across status types', () => {
      const { rerender } = render(<StatusBadge status="archived" />)
      const archivedBadge = screen.getByText('Archived')
      const baseClasses = ['inline-flex', 'items-center', 'rounded-full', 'border', 'font-medium']

      for (const cls of baseClasses) {
        expect(archivedBadge).toHaveClass(cls)
      }

      rerender(<StatusBadge status="inactive" />)
      const inactiveBadge = screen.getByText('Inactive')

      for (const cls of baseClasses) {
        expect(inactiveBadge).toHaveClass(cls)
      }
    })
  })

  describe('Custom ClassName', () => {
    it('applies custom className', () => {
      render(<StatusBadge status="archived" className="custom-class" />)
      const badge = screen.getByText('Archived')
      expect(badge).toHaveClass('custom-class')
    })

    it('preserves default classes with custom className', () => {
      render(<StatusBadge status="archived" className="ml-2" />)
      const badge = screen.getByText('Archived')
      expect(badge).toHaveClass('ml-2', 'inline-flex', 'rounded-full')
    })

    it('handles empty custom className', () => {
      render(<StatusBadge status="archived" className="" />)
      const badge = screen.getByText('Archived')
      expect(badge).toBeInTheDocument()
    })

    it('applies custom className to different status types', () => {
      render(<StatusBadge status="inactive" className="my-custom-class" />)
      const badge = screen.getByText('Inactive')
      expect(badge).toHaveClass('my-custom-class')
    })
  })

  describe('Accessibility', () => {
    it('renders as a span element', () => {
      render(<StatusBadge status="archived" />)
      const badge = screen.getByText('Archived')
      expect(badge.tagName).toBe('SPAN')
    })

    it('has descriptive tooltip for screen readers', () => {
      render(<StatusBadge status="archived" />)
      const badge = screen.getByText('Archived')
      const title = badge.getAttribute('title')
      expect(title).toBeTruthy()
      expect(title).toContain('archived')
      expect(title).toContain('read-only')
    })

    it('has appropriate aria-label', () => {
      render(<StatusBadge status="archived" />)
      const badge = screen.getByText('Archived')
      expect(badge).toHaveAttribute('aria-label', 'This entity has been archived and is read-only')
    })

    it('has appropriate aria-label for inactive status', () => {
      render(<StatusBadge status="inactive" />)
      const badge = screen.getByText('Inactive')
      expect(badge).toHaveAttribute('aria-label', 'This entity is currently inactive')
    })

    it('has appropriate semantic structure with icon', () => {
      render(<StatusBadge status="archived" />)
      const badge = screen.getByText('Archived')
      expect(badge).toContainHTML('i')
    })

    it('maintains accessibility without icon', () => {
      render(<StatusBadge status="archived" showIcon={false} />)
      const badge = screen.getByText('Archived')
      expect(badge).toHaveAttribute('title')
      expect(badge).toHaveAttribute('aria-label')
    })
  })

  describe('Edge Cases', () => {
    it('handles all props together', () => {
      const { container } = render(
        <StatusBadge
          status="archived"
          size="lg"
          showIcon={false}
          className="extra-margin"
          customText="Custom"
          customTooltip="Custom tip"
        />
      )
      const badge = screen.getByText('Custom')
      expect(badge).toBeInTheDocument()
      expect(badge).toHaveClass('px-4', 'py-2', 'text-base', 'extra-margin')
      expect(badge).toHaveAttribute('title', 'Custom tip')
      expect(container.querySelector('svg')).not.toBeInTheDocument()
    })

    it('renders consistently across multiple instances', () => {
      const { rerender } = render(<StatusBadge status="archived" />)
      const firstRender = screen.getByText('Archived').className

      rerender(<StatusBadge status="archived" />)
      const secondRender = screen.getByText('Archived').className
      expect(firstRender).toBe(secondRender)
    })

    it('does not render any interactive elements', () => {
      const { container } = render(<StatusBadge status="archived" />)
      expect(container.querySelector('button')).not.toBeInTheDocument()
      expect(container.querySelector('a')).not.toBeInTheDocument()
      expect(container.querySelector('input')).not.toBeInTheDocument()
    })

    it('handles rapid status changes', () => {
      const { rerender } = render(<StatusBadge status="archived" />)
      expect(screen.getByText('Archived')).toBeInTheDocument()

      rerender(<StatusBadge status="inactive" />)
      expect(screen.getByText('Inactive')).toBeInTheDocument()
      expect(screen.queryByText('Archived')).not.toBeInTheDocument()
    })

    it('combines small size with custom text and no icon', () => {
      const { container } = render(
        <StatusBadge status="inactive" size="sm" customText="N/A" showIcon={false} />
      )
      const badge = screen.getByText('N/A')
      expect(badge).toHaveClass('px-2', 'py-1', 'text-xs')
      expect(container.querySelector('svg')).not.toBeInTheDocument()
    })
  })

  describe('Integration Scenarios', () => {
    it('renders multiple badges with different statuses', () => {
      const { container } = render(
        <div>
          <StatusBadge status="archived" />
          <StatusBadge status="inactive" />
        </div>
      )
      expect(screen.getByText('Archived')).toBeInTheDocument()
      expect(screen.getByText('Inactive')).toBeInTheDocument()
      expect(container.querySelectorAll('span').length).toBe(2)
    })

    it('maintains unique styling for each status in a group', () => {
      render(
        <div>
          <StatusBadge status="archived" />
          <StatusBadge status="inactive" />
        </div>
      )
      const archivedBadge = screen.getByText('Archived')
      const inactiveBadge = screen.getByText('Inactive')

      expect(archivedBadge).toHaveClass('bg-yellow-50')
      expect(inactiveBadge).toHaveClass('bg-red-50')
    })
  })
})
