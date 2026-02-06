import { render, screen } from '@testing-library/react'
import ContributionStats from 'components/ContributionStats'

describe('ContributionStats', () => {
  const mockStats = {
    commits: 150,
    pullRequests: 25,
    issues: 42,
    total: 217,
  }

  const defaultProps = {
    title: 'Test Contribution Activity',
    stats: mockStats,
  }

  beforeEach(() => {
    jest.clearAllMocks()
  })

  describe('Rendering', () => {
    it('renders the component with title and stats', () => {
      render(<ContributionStats {...defaultProps} />)

      expect(screen.getByText('Test Contribution Activity')).toBeInTheDocument()
      expect(screen.getByText('Commits')).toBeInTheDocument()
      expect(screen.getByText('PRs')).toBeInTheDocument()
      expect(screen.getByText('Issues')).toBeInTheDocument()
      expect(screen.getByText('Total')).toBeInTheDocument()
    })

    it('displays formatted numbers correctly', () => {
      render(<ContributionStats {...defaultProps} />)

      expect(screen.getByText('150')).toBeInTheDocument()
      expect(screen.getByText('25')).toBeInTheDocument()
      expect(screen.getByText('42')).toBeInTheDocument()
      expect(screen.getByText('217')).toBeInTheDocument()
    })

    it('displays large numbers with locale formatting', () => {
      const largeStats = {
        commits: 1500,
        pullRequests: 2500,
        issues: 4200,
        total: 8200,
      }

      render(<ContributionStats title="Large Numbers" stats={largeStats} />)

      expect(screen.getByText('1,500')).toBeInTheDocument()
      expect(screen.getByText('2,500')).toBeInTheDocument()
      expect(screen.getByText('4,200')).toBeInTheDocument()
      expect(screen.getByText('8,200')).toBeInTheDocument()
    })

    it('renders all react-icons correctly', () => {
      render(<ContributionStats {...defaultProps} />)

      const container = screen.getByRole('region')
      const icons = container.querySelectorAll('svg')
      expect(icons).toHaveLength(5) // Title icon + 4 stat icons

      // Verify specific icon data attributes
      expect(screen.getByRole('region')).toBeInTheDocument()
      expect(screen.getByText('Test Contribution Activity')).toBeInTheDocument()
    })

    it('formats extremely large numbers correctly', () => {
      const extremeStats = {
        commits: 1234567,
        pullRequests: 987654,
        issues: 456789,
        total: 2679010,
      }

      render(<ContributionStats title="Extreme Numbers" stats={extremeStats} />)

      expect(screen.getByText('1,234,567')).toBeInTheDocument()
      expect(screen.getByText('987,654')).toBeInTheDocument()
      expect(screen.getByText('456,789')).toBeInTheDocument()
      expect(screen.getByText('2,679,010')).toBeInTheDocument()
    })
  })

  describe('Edge Cases - No Data', () => {
    it('handles undefined stats gracefully', () => {
      render(<ContributionStats title="No Stats" stats={undefined} />)

      expect(screen.getByText('No Stats')).toBeInTheDocument()
      expect(screen.getAllByText('0')).toHaveLength(4) // All stats should show 0
    })

    it('handles null stats gracefully', () => {
      render(<ContributionStats title="Null Stats" stats={null as unknown as typeof mockStats} />)

      expect(screen.getByText('Null Stats')).toBeInTheDocument()
      expect(screen.getAllByText('0')).toHaveLength(4) // All stats should show 0
    })

    it('handles empty object stats', () => {
      render(<ContributionStats title="Empty Stats" stats={{} as typeof mockStats} />)

      expect(screen.getByText('Empty Stats')).toBeInTheDocument()
      expect(screen.getAllByText('0')).toHaveLength(4) // All stats should show 0
    })
  })

  describe('Edge Cases - Partial Data', () => {
    it('handles partial stats data - only commits', () => {
      const partialStats = {
        commits: 100,
      }

      render(<ContributionStats title="Partial Stats" stats={partialStats as typeof mockStats} />)

      // Verify commits value
      expect(screen.getByText('100')).toBeInTheDocument()

      // Verify PRs, issues, and total are 0
      expect(screen.getAllByText('0')).toHaveLength(3) // pullRequests, issues, total should be 0
    })

    it('handles partial stats data - mixed values', () => {
      const partialStats = {
        commits: 50,
        issues: 25,
        total: 75,
      }

      render(<ContributionStats title="Mixed Stats" stats={partialStats as typeof mockStats} />)

      expect(screen.getByText('50')).toBeInTheDocument() // commits
      expect(screen.getByText('25')).toBeInTheDocument() // issues
      expect(screen.getByText('75')).toBeInTheDocument() // total
      expect(screen.getByText('0')).toBeInTheDocument() // pullRequests should be 0
    })

    it('handles zero values correctly', () => {
      const zeroStats = {
        commits: 0,
        pullRequests: 0,
        issues: 0,
        total: 0,
      }

      render(<ContributionStats title="Zero Stats" stats={zeroStats} />)

      expect(screen.getAllByText('0')).toHaveLength(4)
    })
  })

  describe('Edge Cases - Invalid Values', () => {
    it('handles negative values gracefully', () => {
      const negativeStats = {
        commits: -5,
        pullRequests: -3,
        issues: -2,
        total: -10,
      }

      render(<ContributionStats title="Negative Stats" stats={negativeStats} />)

      // Component should still render, showing the negative values or handling them gracefully
      expect(screen.getByText('Negative Stats')).toBeInTheDocument()
    })

    it('handles non-numeric values', () => {
      const invalidStats = {
        commits: 'invalid' as unknown as number,
        pullRequests: null as unknown as number,
        issues: undefined as unknown as number,
        total: 42,
      }

      render(<ContributionStats title="Invalid Stats" stats={invalidStats} />)

      expect(screen.getByText('Invalid Stats')).toBeInTheDocument()
      expect(screen.getByText('42')).toBeInTheDocument() // total should still work
    })

    it('handles very large numbers without breaking', () => {
      const largeStats = {
        commits: Number.MAX_SAFE_INTEGER,
        pullRequests: 999999999,
        issues: 888888888,
        total: Number.MAX_SAFE_INTEGER,
      }

      render(<ContributionStats title="Large Stats" stats={largeStats} />)

      expect(screen.getByText('Large Stats')).toBeInTheDocument()
      // Should not crash, even with very large numbers
    })
  })

  describe('Loading States', () => {
    it('renders with loading-like undefined stats', () => {
      render(<ContributionStats title="Loading..." stats={undefined} />)

      expect(screen.getByText('Loading...')).toBeInTheDocument()
      expect(screen.getAllByText('0')).toHaveLength(4) // Should show zeros while loading
    })

    it('handles transitioning from undefined to actual data', () => {
      const { rerender } = render(<ContributionStats title="Transition Test" stats={undefined} />)

      expect(screen.getAllByText('0')).toHaveLength(4)

      // Simulate data loading
      rerender(<ContributionStats title="Transition Test" stats={mockStats} />)

      expect(screen.getByText('150')).toBeInTheDocument()
      expect(screen.getByText('25')).toBeInTheDocument()
      expect(screen.getByText('42')).toBeInTheDocument()
      expect(screen.getByText('217')).toBeInTheDocument()
    })
  })

  describe('Accessibility', () => {
    it('has proper heading structure', () => {
      render(<ContributionStats {...defaultProps} />)

      const heading = screen.getByRole('heading', { level: 2 })
      expect(heading).toHaveTextContent('Test Contribution Activity')
    })

    it('has proper semantic structure', () => {
      render(<ContributionStats {...defaultProps} />)

      // Check that the container exists and the grid has proper classes
      const container = screen.getByRole('region')
      expect(container).toBeInTheDocument()

      // The mb-6 class is on the grid div, not the container
      const grid = container.querySelector('.grid')
      expect(grid).toHaveClass('mb-6', 'grid', 'grid-cols-2', 'gap-4', 'sm:grid-cols-4')
    })

    it('provides meaningful labels for screen readers', () => {
      render(<ContributionStats {...defaultProps} />)

      expect(screen.getByText('Commits')).toBeInTheDocument()
      expect(screen.getByText('PRs')).toBeInTheDocument()
      expect(screen.getByText('Issues')).toBeInTheDocument()
      expect(screen.getByText('Total')).toBeInTheDocument()
    })
  })

  describe('Different Use Cases', () => {
    it('renders project-specific title correctly', () => {
      render(<ContributionStats title="Project Contribution Activity" stats={mockStats} />)

      expect(screen.getByText('Project Contribution Activity')).toBeInTheDocument()
    })

    it('renders chapter-specific title correctly', () => {
      render(<ContributionStats title="Chapter Contribution Activity" stats={mockStats} />)

      expect(screen.getByText('Chapter Contribution Activity')).toBeInTheDocument()
    })

    it('renders board candidate context correctly', () => {
      render(<ContributionStats title="Board Candidate Contributions" stats={mockStats} />)

      expect(screen.getByText('Board Candidate Contributions')).toBeInTheDocument()
    })
  })

  describe('Type Safety and Props', () => {
    it('accepts readonly props without issues', () => {
      const readonlyProps = {
        title: 'Readonly Test' as const,
        stats: mockStats,
      }

      expect(() => render(<ContributionStats {...readonlyProps} />)).not.toThrow()
    })

    it('handles dynamic title changes', () => {
      const { rerender } = render(<ContributionStats title="Initial Title" stats={mockStats} />)

      expect(screen.getByText('Initial Title')).toBeInTheDocument()

      rerender(<ContributionStats title="Updated Title" stats={mockStats} />)

      expect(screen.getByText('Updated Title')).toBeInTheDocument()
      expect(screen.queryByText('Initial Title')).not.toBeInTheDocument()
    })
  })

  describe('Visual Elements', () => {
    it('renders with proper CSS classes for styling', () => {
      render(<ContributionStats {...defaultProps} />)

      const container = screen.getByRole('region')
      expect(container).toBeInTheDocument()

      const heading = container.querySelector('h2')
      expect(heading).toHaveClass('mb-4', 'flex', 'items-center', 'gap-2')

      // The mb-6 class is on the grid div
      const grid = container.querySelector('.grid')
      expect(grid).toHaveClass('mb-6', 'grid', 'grid-cols-2', 'gap-4', 'sm:grid-cols-4')
    })

    it('renders all required icons with proper attributes', () => {
      render(<ContributionStats {...defaultProps} />)

      const container = screen.getByRole('region')
      const icons = container.querySelectorAll('svg')
      expect(icons).toHaveLength(5)

      // Verify icons have proper styling classes
      icons.forEach((icon) => {
        expect(icon).toHaveClass('text-gray-800', 'dark:text-gray-200')
      })

      // Verify specific viewBox attributes for different react-icons
      const viewBoxes = Array.from(icons).map((icon) => icon.getAttribute('viewBox'))
      expect(viewBoxes).toContain('0 0 512 512') // chart-line and exclamation-circle
      expect(viewBoxes).toContain('0 0 640 512') // code
      expect(viewBoxes).toContain('0 0 384 512') // code-branch
    })
  })
})
