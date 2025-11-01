import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import type { Icon } from 'types/icon'
import DisplayIcon from 'components/DisplayIcon'

interface TooltipProps {
  children: React.ReactNode
  content: string
  delay: number
  closeDelay: number
  showArrow: boolean
  placement: string
}

interface IconWrapperProps {
  className?: string
  icon: string
}

jest.mock('@heroui/tooltip', () => ({
  Tooltip: ({ children, content, delay, closeDelay, showArrow, placement }: TooltipProps) => (
    <div
      data-testid="tooltip"
      data-tooltip-content={content}
      data-delay={delay}
      data-close-delay={closeDelay}
      data-show-arrow={showArrow}
      data-placement={placement}
    >
      {children}
    </div>
  ),
}))

jest.mock('millify', () => ({
  millify: jest.fn((value: number, options?: { precision: number }) => {
    if (value >= 1000000000) return `${(value / 1000000000).toFixed(options?.precision || 1)}B`
    if (value >= 1000000) return `${(value / 1000000).toFixed(options?.precision || 1)}M`
    if (value >= 1000) return `${(value / 1000).toFixed(options?.precision || 1)}k`
    return value.toString()
  }),
}))

jest.mock('wrappers/FontAwesomeIconWrapper', () => {
  return function MockFontAwesomeIconWrapper({ className, icon }: IconWrapperProps) {
    return <span data-testid="font-awesome-icon" data-icon={icon} className={className} />
  }
})

jest.mock('utils/data', () => ({
  ICONS: {
    starsCount: { label: 'Stars', icon: 'fa-star' },
    forksCount: { label: 'Forks', icon: 'fa-code-fork' },
    contributorsCount: { label: 'Contributors', icon: 'fa-users' },
    contributionCount: { label: 'Contributors', icon: 'fa-users' },
    issuesCount: { label: 'Issues', icon: 'fa-exclamation-circle' },
    license: { label: 'License', icon: 'fa-balance-scale' },
    unknownItem: { label: 'Unknown', icon: 'fa-question' },
  },
}))

describe('DisplayIcon', () => {
  const mockIcons: Icon = {
    starsCount: 1250,
    forksCount: 350,
    contributorsCount: 25,
    contributionCount: 25,
    issuesCount: 42,
    license: 'MIT',
  }

  describe('Basic Rendering', () => {
    it('renders successfully with minimal required props', () => {
      render(<DisplayIcon item="starsCount" icons={mockIcons} />)
      expect(screen.getByTestId('tooltip')).toBeInTheDocument()
    })

    it('renders nothing when item is not in icons object', () => {
      const { container } = render(<DisplayIcon item="nonexistentItem" icons={mockIcons} />)
      expect(container.firstChild).toBeNull()
    })

    it('renders nothing when icons object is empty', () => {
      const { container } = render(<DisplayIcon item="starsCount" icons={{}} />)
      expect(container.firstChild).toBeNull()
    })
  })

  describe('Conditional Rendering Logic', () => {
    it('renders when item exists in icons object', () => {
      render(<DisplayIcon item="starsCount" icons={mockIcons} />)
      expect(screen.getByTestId('tooltip')).toBeInTheDocument()
    })

    it('does not render when item does not exist in icons object', () => {
      const { container } = render(<DisplayIcon item="nonexistent" icons={mockIcons} />)
      expect(container.firstChild).toBeNull()
    })

    it('does not render when icons[item] is falsy', () => {
      const iconsWithFalsy: Icon = { ...mockIcons, starsCount: 0 }
      const { container } = render(<DisplayIcon item="starsCount" icons={iconsWithFalsy} />)
      expect(container.firstChild).toBeNull()
    })
  })

  describe('Prop-based Behavior', () => {
    it('displays correct icon based on item prop', () => {
      render(<DisplayIcon item="starsCount" icons={mockIcons} />)
      const icon = screen.getByTestId('font-awesome-icon')
      expect(icon).toHaveAttribute('data-icon', 'fa-star')
    })

    it('displays different icons for different items', () => {
      const { rerender } = render(<DisplayIcon item="forksCount" icons={mockIcons} />)
      expect(screen.getByTestId('font-awesome-icon')).toHaveAttribute('data-icon', 'fa-code-fork')

      rerender(<DisplayIcon item="contributorsCount" icons={mockIcons} />)
      expect(screen.getByTestId('font-awesome-icon')).toHaveAttribute('data-icon', 'fa-users')
    })

    it('applies different container classes based on item type', () => {
      const { rerender, container } = render(<DisplayIcon item="starsCount" icons={mockIcons} />)
      let containerDiv = container.querySelector('div[class*="rotate-container"]')
      expect(containerDiv).toBeInTheDocument()

      rerender(<DisplayIcon item="forksCount" icons={mockIcons} />)
      containerDiv = container.querySelector('div[class*="flip-container"]')
      expect(containerDiv).toBeInTheDocument()
    })

    it('applies different icon classes based on item type', () => {
      const { rerender } = render(<DisplayIcon item="starsCount" icons={mockIcons} />)
      let icon = screen.getByTestId('font-awesome-icon')
      expect(icon).toHaveClass('icon-rotate')

      rerender(<DisplayIcon item="forksCount" icons={mockIcons} />)
      icon = screen.getByTestId('font-awesome-icon')
      expect(icon).toHaveClass('icon-flip')
    })
  })

  describe('Text and Content Rendering', () => {
    it('displays formatted numbers using millify for numeric values', () => {
      render(<DisplayIcon item="starsCount" icons={mockIcons} />)
      expect(screen.getByText('1.3k')).toBeInTheDocument()
    })

    it('displays string values as-is', () => {
      render(<DisplayIcon item="license" icons={mockIcons} />)
      expect(screen.getByText('MIT')).toBeInTheDocument()
    })

    it('displays tooltip with correct label', () => {
      render(<DisplayIcon item="starsCount" icons={mockIcons} />)
      const tooltip = screen.getByTestId('tooltip')
      expect(tooltip).toHaveAttribute('data-tooltip-content', 'Stars')
    })

    it('formats large numbers correctly', () => {
      const largeNumberIcons: Icon = { starsCount: 1500000 }
      render(<DisplayIcon item="starsCount" icons={largeNumberIcons} />)
      expect(screen.getByText('1.5M')).toBeInTheDocument()
    })
  })

  describe('Default Values and Fallbacks', () => {
    it('handles items not in ICONS constant gracefully', () => {
      const testIcons: Icon = { unknownItem: 'test' }

      render(<DisplayIcon item="unknownItem" icons={testIcons} />)

      const tooltip = screen.getByTestId('tooltip')
      expect(tooltip).toHaveAttribute('data-tooltip-content', 'Unknown')
    })

    it('applies base classes even without special item types', () => {
      render(<DisplayIcon item="license" icons={mockIcons} />)
      const tooltipContainer = screen.getByTestId('tooltip').querySelector('div')
      expect(tooltipContainer).toHaveClass(
        'flex',
        'flex-row-reverse',
        'items-center',
        'justify-center'
      )
    })
  })

  describe('Edge Cases and Invalid Inputs', () => {
    it('throws error when icons object is null', () => {
      expect(() => {
        render(<DisplayIcon item="starsCount" icons={null as never} />)
      }).toThrow('Cannot read properties of null')
    })

    it('throws error when icons object is undefined', () => {
      expect(() => {
        render(<DisplayIcon item="starsCount" icons={undefined as never} />)
      }).toThrow('Cannot read properties of undefined')
    })

    it('handles empty string item', () => {
      const { container } = render(<DisplayIcon item="" icons={mockIcons} />)
      expect(container.firstChild).toBeNull()
    })

    it('handles zero values correctly', () => {
      const zeroIcons: Icon = { starsCount: 0 }
      const { container } = render(<DisplayIcon item="starsCount" icons={zeroIcons} />)
      expect(container.firstChild).toBeNull()
    })

    it('handles negative numbers', () => {
      const negativeIcons: Icon = { starsCount: -5 }
      render(<DisplayIcon item="starsCount" icons={negativeIcons} />)
      expect(screen.getByText('-5')).toBeInTheDocument()
    })

    it('handles very large numbers', () => {
      const largeIcons: Icon = { starsCount: 1500000000 }
      render(<DisplayIcon item="starsCount" icons={largeIcons} />)
      expect(screen.getByText('1.5B')).toBeInTheDocument()
    })
  })

  describe('DOM Structure and Classes', () => {
    it('has correct base container structure', () => {
      render(<DisplayIcon item="license" icons={mockIcons} />)
      const tooltip = screen.getByTestId('tooltip')
      const containerDiv = tooltip.querySelector('div')

      expect(containerDiv).toHaveClass(
        'flex',
        'flex-row-reverse',
        'items-center',
        'justify-center',
        'gap-1',
        'px-4',
        'pb-1',
        '-ml-2'
      )
    })

    it('applies rotate-container class for stars items', () => {
      const { rerender } = render(<DisplayIcon item="starsCount" icons={mockIcons} />)
      let tooltipContainer = screen.getByTestId('tooltip').querySelector('div')
      expect(tooltipContainer).toHaveClass('rotate-container')

      rerender(<DisplayIcon item="starsCount" icons={mockIcons} />)
      tooltipContainer = screen.getByTestId('tooltip').querySelector('div')
      expect(tooltipContainer).toHaveClass('rotate-container')
    })

    it('applies flip-container class for forks and contributors items', () => {
      const testCases = [
        { item: 'forksCount', value: 100 },
        { item: 'contributors_count', value: 50 },
        { item: 'contributionCount', value: 30 },
      ]

      for (const testCase of testCases) {
        const iconsWithItem: Icon = { [testCase.item]: testCase.value }
        const { container } = render(<DisplayIcon item={testCase.item} icons={iconsWithItem} />)
        const containerDiv = container.querySelector('div[class*="flip-container"]')
        expect(containerDiv).toBeInTheDocument()
      }
    })

    it('applies correct icon classes', () => {
      render(<DisplayIcon item="starsCount" icons={mockIcons} />)
      const icon = screen.getByTestId('font-awesome-icon')
      expect(icon).toHaveClass('text-gray-600', 'dark:text-gray-300', 'icon-rotate')
    })

    it('applies correct text span classes', () => {
      render(<DisplayIcon item="license" icons={mockIcons} />)
      const textSpan = screen.getByText('MIT')
      expect(textSpan).toHaveClass('text-gray-600', 'dark:text-gray-300')
    })
  })

  describe('Accessibility', () => {
    it('provides tooltip with descriptive content', () => {
      render(<DisplayIcon item="starsCount" icons={mockIcons} />)
      const tooltip = screen.getByTestId('tooltip')
      expect(tooltip).toHaveAttribute('data-tooltip-content', 'Stars')
    })

    it('has proper tooltip configuration', () => {
      render(<DisplayIcon item="forksCount" icons={mockIcons} />)
      const tooltip = screen.getByTestId('tooltip')
      expect(tooltip).toHaveAttribute('data-delay', '150')
      expect(tooltip).toHaveAttribute('data-close-delay', '100')
      expect(tooltip).toHaveAttribute('data-show-arrow', 'true')
      expect(tooltip).toHaveAttribute('data-placement', 'top')
    })
  })

  describe('Internal Logic', () => {
    it('correctly determines numeric vs string values', () => {
      const mixedIcons: Icon = {
        starsCount: 1000,
        license: 'Apache-2.0',
      }

      const { rerender } = render(<DisplayIcon item="starsCount" icons={mixedIcons} />)
      expect(screen.getByText('1.0k')).toBeInTheDocument()

      rerender(<DisplayIcon item="license" icons={mixedIcons} />)
      expect(screen.getByText('Apache-2.0')).toBeInTheDocument()
    })

    it('filters and joins className arrays correctly', () => {
      render(<DisplayIcon item="license" icons={mockIcons} />)
      const tooltipContainer = screen.getByTestId('tooltip').querySelector('div')
      const classes = tooltipContainer?.className.split(' ') || []

      expect(classes.filter((cls) => cls === '')).toHaveLength(0)
    })
  })

  describe('Event Handling', () => {
    it('renders interactive tooltip that responds to user events', async () => {
      const user = userEvent.setup()
      render(<DisplayIcon item="starsCount" icons={mockIcons} />)

      const tooltip = screen.getByTestId('tooltip')
      expect(tooltip).toBeInTheDocument()

      await user.tab()
      expect(tooltip).toBeInTheDocument()

      await user.hover(tooltip)
      expect(tooltip).toBeInTheDocument()

      await user.unhover(tooltip)
      expect(tooltip).toBeInTheDocument()

      expect(tooltip).toHaveAttribute('data-tooltip-content', 'Stars')
      expect(tooltip).toHaveAttribute('data-show-arrow', 'true')
    })

    it('maintains tooltip accessibility during interactions', async () => {
      const user = userEvent.setup()
      render(<DisplayIcon item="forksCount" icons={mockIcons} />)

      const tooltip = screen.getByTestId('tooltip')

      await user.tab()
      expect(tooltip).toBeInTheDocument()

      expect(tooltip).toHaveAttribute('data-placement', 'top')
      expect(tooltip).toHaveAttribute('data-delay', '150')

      const iconElement = screen.getByTestId('font-awesome-icon')
      const textContent = screen.getByText('350')

      expect(iconElement).toBeInTheDocument()
      expect(textContent).toBeInTheDocument()
    })
  })
})
