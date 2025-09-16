import { render, screen, cleanup } from '@testing-library/react'
import React from 'react'
import Badges from 'components/Badges'

// Mock FontAwesome components
jest.mock('@fortawesome/react-fontawesome', () => ({
  FontAwesomeIcon: ({
    icon,
    className,
    ...props
  }: {
    icon: string[] | { iconName: string }
    className?: string
    [key: string]: unknown
  }) => {
    const iconName = Array.isArray(icon) ? icon[1] : icon.iconName
    return <span data-testid={`icon-${iconName}`} className={className} {...props} />
  },
}))

// Mock FontAwesome library
jest.mock('@fortawesome/fontawesome-svg-core', () => ({
  library: { add: jest.fn() },
  // Simulate FA lookup; throw if not found
  findIconDefinition: jest.fn(({ iconName }: { iconName: string }) => {
    const valid = new Set([
      'medal',
      'shield-alt',
      'code',
      'user-graduate',
      'crown',
      'star',
      'trophy',
      'user-tie',
    ])
    if (valid.has(iconName)) return { iconName }
    throw new Error('not found')
  }),
}))

// Mock FontAwesome icons
jest.mock('@fortawesome/free-solid-svg-icons', () => ({
  fas: {
    medal: { iconName: 'medal' },
    'shield-alt': { iconName: 'shield-alt' },
    code: { iconName: 'code' },
    'user-graduate': { iconName: 'user-graduate' },
    crown: { iconName: 'crown' },
    star: { iconName: 'star' },
    trophy: { iconName: 'trophy' },
    'user-tie': { iconName: 'user-tie' },
  },
}))

jest.mock('@heroui/tooltip', () => ({
  Tooltip: ({
    children,
    content,
    ...props
  }: {
    children: React.ReactNode
    content: string
    [key: string]: unknown
  }) => (
    <div data-testid="tooltip" data-content={content} {...props}>
      {children}
    </div>
  ),
}))

describe('Badges', () => {
  const defaultProps = {
    name: 'Test Badge',
    cssClass: 'fa-medal',
  }

  afterEach(() => {
    cleanup()
  })

  describe('Essential Rendering Tests', () => {
    it('renders successfully with valid icon', () => {
      render(<Badges {...defaultProps} />)

      expect(screen.getByTestId('icon-medal')).toBeInTheDocument()
      expect(screen.getByTestId('tooltip')).toHaveAttribute('data-content', 'Test Badge')
    })

    it('renders without tooltip when showTooltip is false', () => {
      render(<Badges {...defaultProps} showTooltip={false} />)

      expect(screen.getByTestId('icon-medal')).toBeInTheDocument()
      expect(screen.queryByTestId('tooltip')).not.toBeInTheDocument()
    })

    it('renders with tooltip by default when showTooltip is not specified', () => {
      render(<Badges {...defaultProps} />)

      expect(screen.getByTestId('icon-medal')).toBeInTheDocument()
      expect(screen.getByTestId('tooltip')).toBeInTheDocument()
    })
  })

  describe('Icon Handling', () => {
    it('renders correct icon for valid cssClass', () => {
      render(<Badges {...defaultProps} cssClass="fa-crown" />)

      expect(screen.getByTestId('icon-crown')).toBeInTheDocument()
    })

    it('renders correct icon for cssClass without fa- prefix', () => {
      render(<Badges {...defaultProps} cssClass="crown" />)

      expect(screen.getByTestId('icon-crown')).toBeInTheDocument()
    })

    it('renders fallback medal icon for cssClass with multiple fa- prefixes', () => {
      render(<Badges {...defaultProps} cssClass="fa-fa-crown" />)

      // Should fall back to medal icon since 'fa-crown' is not a valid FontAwesome icon
      expect(screen.getByTestId('icon-medal')).toBeInTheDocument()
    })

    it('handles different valid icons', () => {
      const icons = ['fa-medal', 'fa-crown', 'fa-star', 'fa-trophy']
      icons.forEach((icon) => {
        const { unmount } = render(<Badges {...defaultProps} cssClass={icon} />)
        expect(screen.getByTestId(`icon-${icon.replace('fa-', '')}`)).toBeInTheDocument()
        unmount()
      })
    })
  })

  describe('Fallback Behavior', () => {
    it('renders fallback medal icon for invalid cssClass', () => {
      render(<Badges {...defaultProps} cssClass="fa-invalid" />)

      expect(screen.getByTestId('icon-medal')).toBeInTheDocument()
      expect(screen.getByTestId('tooltip')).toHaveAttribute(
        'data-content',
        'Test Badge (icon not found)'
      )
    })

    it('renders fallback icon without tooltip when showTooltip is false', () => {
      render(<Badges {...defaultProps} cssClass="fa-invalid" showTooltip={false} />)

      expect(screen.getByTestId('icon-medal')).toBeInTheDocument()
      expect(screen.queryByTestId('tooltip')).not.toBeInTheDocument()
    })

    it('handles empty cssClass gracefully', () => {
      render(<Badges {...defaultProps} cssClass="" />)

      expect(screen.getByTestId('icon-medal')).toBeInTheDocument()
      expect(screen.getByTestId('tooltip')).toHaveAttribute('data-content', 'Test Badge')
    })

    it('handles undefined cssClass gracefully', () => {
      render(<Badges {...defaultProps} cssClass={undefined as unknown as string} />)

      expect(screen.getByTestId('icon-medal')).toBeInTheDocument()
      expect(screen.getByTestId('tooltip')).toHaveAttribute('data-content', 'Test Badge')
    })
  })

  describe('Tooltip Content', () => {
    it('displays badge name in tooltip for valid icon', () => {
      render(<Badges {...defaultProps} name="Special Badge" />)

      expect(screen.getByTestId('tooltip')).toHaveAttribute('data-content', 'Special Badge')
    })

    it('displays badge name for invalid icon with fallback message', () => {
      render(<Badges {...defaultProps} name="Invalid Badge" cssClass="fa-invalid" />)

      expect(screen.getByTestId('tooltip')).toHaveAttribute(
        'data-content',
        'Invalid Badge (icon not found)'
      )
    })

    it('handles special characters in badge name', () => {
      render(<Badges {...defaultProps} name="Badge & More!" />)

      expect(screen.getByTestId('tooltip')).toHaveAttribute('data-content', 'Badge & More!')
    })

    it('handles long badge names', () => {
      const longName = 'Very Long Badge Name That Exceeds Normal Length'
      render(<Badges {...defaultProps} name={longName} cssClass="fa-medal" />)

      expect(screen.getByTestId('tooltip')).toHaveAttribute('data-content', longName)
    })
  })

  describe('CSS Class Processing', () => {
    it('correctly processes cssClass with fa- prefix', () => {
      render(<Badges {...defaultProps} cssClass="fa-crown" />)

      expect(screen.getByTestId('icon-crown')).toBeInTheDocument()
    })

    it('correctly processes cssClass without fa- prefix', () => {
      render(<Badges {...defaultProps} cssClass="crown" />)

      expect(screen.getByTestId('icon-crown')).toBeInTheDocument()
    })

    it('handles cssClass with multiple dashes', () => {
      render(<Badges {...defaultProps} cssClass="fa-user-tie" />)

      expect(screen.getByTestId('icon-user-tie')).toBeInTheDocument()
    })

    it('handles cssClass with underscores (falls back to medal)', () => {
      render(<Badges {...defaultProps} cssClass="fa-user_tie" />)

      // The component should fall back to medal icon since 'user_tie' is not a valid FontAwesome icon
      expect(screen.getByTestId('icon-medal')).toBeInTheDocument()
    })
  })

  describe('Styling and Classes', () => {
    it('applies correct classes to icon', () => {
      render(<Badges {...defaultProps} cssClass="fa-medal" />)

      const icon = screen.getByTestId('icon-medal')
      expect(icon).toHaveClass('h-4', 'w-4')
    })

    it('applies correct classes to fallback icon', () => {
      render(<Badges {...defaultProps} cssClass="fa-invalid" />)

      const icon = screen.getByTestId('icon-medal')
      expect(icon).toHaveClass('h-4', 'w-4', 'text-gray-400')
    })

    it('wraps icon in inline-flex container', () => {
      render(<Badges {...defaultProps} />)

      const container = screen.getByTestId('icon-medal').parentElement?.parentElement
      expect(container).toHaveClass('inline-flex', 'items-center')
    })
  })

  describe('Edge Cases and Error Handling', () => {
    it('handles null cssClass', () => {
      render(<Badges {...defaultProps} cssClass={null as unknown as string} />)

      expect(screen.getByTestId('icon-medal')).toBeInTheDocument()
      expect(screen.getByTestId('tooltip')).toHaveAttribute('data-content', 'Test Badge')
    })

    it('handles numeric cssClass', () => {
      render(<Badges {...defaultProps} cssClass={123 as unknown as string} />)

      expect(screen.getByTestId('icon-medal')).toBeInTheDocument()
      expect(screen.getByTestId('tooltip')).toHaveAttribute(
        'data-content',
        'Test Badge (icon not found)'
      )
    })

    it('handles boolean cssClass', () => {
      render(<Badges {...defaultProps} cssClass={true as unknown as string} />)

      expect(screen.getByTestId('icon-medal')).toBeInTheDocument()
      expect(screen.getByTestId('tooltip')).toHaveAttribute(
        'data-content',
        'Test Badge (icon not found)'
      )
    })

    it('handles whitespace-only cssClass', () => {
      render(<Badges {...defaultProps} cssClass="   " />)

      expect(screen.getByTestId('icon-medal')).toBeInTheDocument()
      expect(screen.getByTestId('tooltip')).toHaveAttribute(
        'data-content',
        'Test Badge (icon not found)'
      )
    })
  })

  describe('Accessibility', () => {
    it('provides tooltip content for screen readers', () => {
      render(<Badges {...defaultProps} name="Accessible Badge" />)

      expect(screen.getByTestId('tooltip')).toHaveAttribute('data-content', 'Accessible Badge')
    })

    it('maintains tooltip accessibility for fallback icons', () => {
      render(<Badges {...defaultProps} name="Fallback Badge" cssClass="fa-invalid" />)

      expect(screen.getByTestId('tooltip')).toHaveAttribute(
        'data-content',
        'Fallback Badge (icon not found)'
      )
    })
  })

  describe('Performance and Optimization', () => {
    it('renders efficiently with multiple badges', () => {
      const badges = [
        { ...defaultProps, name: 'Badge 1', cssClass: 'fa-medal' },
        { ...defaultProps, name: 'Badge 2', cssClass: 'fa-crown' },
        { ...defaultProps, name: 'Badge 3', cssClass: 'fa-star' },
      ]

      badges.forEach((badge, _index) => {
        const { unmount } = render(<Badges {...badge} />)
        expect(screen.getByTestId(`icon-${badge.cssClass.replace('fa-', '')}`)).toBeInTheDocument()
        unmount()
      })
    })

    it('handles rapid re-renders with different props', () => {
      const { rerender } = render(<Badges {...defaultProps} />)

      expect(screen.getByTestId('icon-medal')).toBeInTheDocument()

      rerender(<Badges {...defaultProps} cssClass="fa-crown" />)
      expect(screen.getByTestId('icon-crown')).toBeInTheDocument()

      rerender(<Badges {...defaultProps} cssClass="fa-invalid" />)
      expect(screen.getByTestId('icon-medal')).toBeInTheDocument()
    })
  })
})
