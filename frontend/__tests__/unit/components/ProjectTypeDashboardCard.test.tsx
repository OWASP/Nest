import { faHeartPulse, faExclamationTriangle, faSkull } from '@fortawesome/free-solid-svg-icons'
import { render, screen, fireEvent } from '@testing-library/react'
import '@testing-library/jest-dom'
import React from 'react'
import ProjectTypeDashboardCard from 'components/ProjectTypeDashboardCard'

jest.mock('next/link', () => {
  return function MockedLink({
    children,
    href,
    className,
    ...props
  }: {
    children: React.ReactNode
    href: string
    className?: string
    [key: string]: unknown
  }) {
    return (
      <a href={href} className={className} {...props}>
        {children}
      </a>
    )
  }
})

jest.mock('components/SecondaryCard', () => {
  return function MockedSecondaryCard({
    title,
    icon,
    className,
    children,
    ...props
  }: {
    title: string
    icon: unknown
    className?: string
    children: React.ReactNode
    [key: string]: unknown
  }) {
    return (
      <div
        data-testid="secondary-card"
        data-title={title}
        data-icon={JSON.stringify(icon)}
        className={className}
        {...props}
      >
        <div data-testid="card-title">{title}</div>
        <div data-testid="card-content">{children}</div>
      </div>
    )
  }
})

describe('ProjectTypeDashboardCard', () => {
  const baseProps = {
    type: 'healthy' as const,
    count: 42,
    icon: faHeartPulse,
  }

  beforeEach(() => {
    jest.clearAllMocks()
  })

  describe('Essential Rendering Tests', () => {
    it('renders successfully with minimal required props', () => {
      render(<ProjectTypeDashboardCard {...baseProps} />)

      expect(screen.getByTestId('secondary-card')).toBeInTheDocument()
      expect(screen.getByTestId('card-title')).toHaveTextContent('Healthy')
      expect(screen.getByText('42')).toBeInTheDocument()
    })

    it('renders all text content correctly', () => {
      render(<ProjectTypeDashboardCard {...baseProps} />)

      const title = screen.getByTestId('card-title')
      const count = screen.getByText('42')

      expect(title).toHaveTextContent('Healthy')
      expect(count).toBeInTheDocument()
      expect(count).toHaveClass('text-2xl', 'font-bold', 'md:text-3xl')
    })

    it('renders with correct link structure', () => {
      render(<ProjectTypeDashboardCard {...baseProps} />)

      const link = screen.getByRole('link')
      expect(link).toHaveAttribute('href', '/projects/dashboard/metrics?health=healthy')
      expect(link).toHaveClass('group')
    })
  })

  describe('Conditional Rendering Logic', () => {
    it('renders correct title for healthy type', () => {
      render(<ProjectTypeDashboardCard type="healthy" count={10} icon={faHeartPulse} />)

      expect(screen.getByTestId('card-title')).toHaveTextContent('Healthy')
    })

    it('renders correct title for needsAttention type', () => {
      render(
        <ProjectTypeDashboardCard type="needsAttention" count={5} icon={faExclamationTriangle} />
      )

      expect(screen.getByTestId('card-title')).toHaveTextContent('Need Attention')
    })

    it('renders correct title for unhealthy type', () => {
      render(<ProjectTypeDashboardCard type="unhealthy" count={2} icon={faSkull} />)

      expect(screen.getByTestId('card-title')).toHaveTextContent('Unhealthy')
    })
  })

  describe('Prop-based Behavior', () => {
    it('displays different count values correctly', () => {
      const { rerender } = render(<ProjectTypeDashboardCard {...baseProps} count={0} />)
      expect(screen.getByText('0')).toBeInTheDocument()

      rerender(<ProjectTypeDashboardCard {...baseProps} count={999} />)
      expect(screen.getByText('999')).toBeInTheDocument()

      rerender(<ProjectTypeDashboardCard {...baseProps} count={1} />)
      expect(screen.getByText('1')).toBeInTheDocument()
    })

    it('passes different icons to SecondaryCard correctly', () => {
      const { rerender } = render(<ProjectTypeDashboardCard {...baseProps} icon={faHeartPulse} />)
      let secondaryCard = screen.getByTestId('secondary-card')
      expect(secondaryCard).toHaveAttribute('data-icon', JSON.stringify(faHeartPulse))

      rerender(<ProjectTypeDashboardCard {...baseProps} icon={faExclamationTriangle} />)
      secondaryCard = screen.getByTestId('secondary-card')
      expect(secondaryCard).toHaveAttribute('data-icon', JSON.stringify(faExclamationTriangle))
    })

    it('generates correct href for each type', () => {
      const { rerender } = render(<ProjectTypeDashboardCard {...baseProps} type="healthy" />)
      expect(screen.getByRole('link')).toHaveAttribute(
        'href',
        '/projects/dashboard/metrics?health=healthy'
      )

      rerender(<ProjectTypeDashboardCard {...baseProps} type="needsAttention" />)
      expect(screen.getByRole('link')).toHaveAttribute(
        'href',
        '/projects/dashboard/metrics?health=needsAttention'
      )

      rerender(<ProjectTypeDashboardCard {...baseProps} type="unhealthy" />)
      expect(screen.getByRole('link')).toHaveAttribute(
        'href',
        '/projects/dashboard/metrics?health=unhealthy'
      )
    })
  })

  describe('Event Handling', () => {
    it('renders as a clickable link', () => {
      render(<ProjectTypeDashboardCard {...baseProps} />)

      const link = screen.getByRole('link')
      expect(link).toBeInTheDocument()
      expect(link).toHaveAttribute('href', '/projects/dashboard/metrics?health=healthy')
    })

    it('maintains link functionality when clicked', () => {
      render(<ProjectTypeDashboardCard {...baseProps} />)

      const link = screen.getByRole('link')
      fireEvent.click(link)

      expect(link).toHaveAttribute('href', '/projects/dashboard/metrics?health=healthy')
    })
  })

  describe('Default Values and Fallbacks', () => {
    it('handles zero count gracefully', () => {
      render(<ProjectTypeDashboardCard {...baseProps} count={0} />)

      expect(screen.getByText('0')).toBeInTheDocument()
    })

    it('handles large count values', () => {
      render(<ProjectTypeDashboardCard {...baseProps} count={999999} />)

      expect(screen.getByText('999999')).toBeInTheDocument()
    })
  })

  describe('Edge Cases and Invalid Inputs', () => {
    it('handles negative count values', () => {
      render(<ProjectTypeDashboardCard {...baseProps} count={-5} />)

      expect(screen.getByText('-5')).toBeInTheDocument()
    })

    it('handles very large numbers', () => {
      const largeNumber = 1234567890
      render(<ProjectTypeDashboardCard {...baseProps} count={largeNumber} />)

      expect(screen.getByText(largeNumber.toString())).toBeInTheDocument()
    })

    type ProjectHealthType = 'healthy' | 'needsAttention' | 'unhealthy'
    it('renders correctly with all type variants', () => {
      const types: Array<ProjectHealthType> = ['healthy', 'needsAttention', 'unhealthy']

      types.forEach((type) => {
        const { unmount } = render(
          <ProjectTypeDashboardCard type={type} count={10} icon={faHeartPulse} />
        )
        expect(screen.getByTestId('secondary-card')).toBeInTheDocument()
        unmount()
      })
    })
  })

  describe('Accessibility', () => {
    it('renders as a semantic link element', () => {
      render(<ProjectTypeDashboardCard {...baseProps} />)

      const link = screen.getByRole('link')
      expect(link).toBeInTheDocument()
    })

    it('provides meaningful link destination', () => {
      render(<ProjectTypeDashboardCard {...baseProps} />)

      const link = screen.getByRole('link')
      expect(link).toHaveAttribute('href', '/projects/dashboard/metrics?health=healthy')
    })

    it('maintains semantic structure with titles', () => {
      render(<ProjectTypeDashboardCard {...baseProps} />)

      const title = screen.getByTestId('card-title')
      expect(title).toHaveTextContent('Healthy')
    })
  })

  describe('DOM Structure and CSS Classes', () => {
    it('applies correct base classes to link element', () => {
      render(<ProjectTypeDashboardCard {...baseProps} />)

      const link = screen.getByRole('link')
      expect(link).toHaveClass('group')
    })

    it('applies correct classes to count element', () => {
      render(<ProjectTypeDashboardCard {...baseProps} />)

      const count = screen.getByText('42')
      expect(count).toHaveClass('text-2xl', 'font-bold', 'md:text-3xl')
    })

    it('applies conditional CSS classes based on type prop - healthy', () => {
      render(<ProjectTypeDashboardCard type="healthy" count={10} icon={faHeartPulse} />)

      const secondaryCard = screen.getByTestId('secondary-card')
      const className = secondaryCard.getAttribute('class')

      expect(className).toContain('overflow-hidden')
      expect(className).toContain('transition-colors')
      expect(className).toContain('duration-300')
      expect(className).toContain('bg-green-100')
      expect(className).toContain('text-green-800')
      expect(className).toContain('hover:bg-green-200')
      expect(className).toContain('hover:text-green-800')
      expect(className).toContain('dark:bg-green-800')
      expect(className).toContain('dark:text-green-400')
      expect(className).toContain('dark:hover:bg-green-700')
    })

    it('applies conditional CSS classes based on type prop - unhealthy', () => {
      render(<ProjectTypeDashboardCard type="unhealthy" count={5} icon={faSkull} />)

      const secondaryCard = screen.getByTestId('secondary-card')
      const className = secondaryCard.getAttribute('class')

      expect(className).toContain('overflow-hidden')
      expect(className).toContain('transition-colors')
      expect(className).toContain('duration-300')
      expect(className).toContain('bg-red-100')
      expect(className).toContain('text-red-800')
      expect(className).toContain('hover:bg-red-200')
      expect(className).toContain('hover:text-red-800')
      expect(className).toContain('dark:bg-red-800')
      expect(className).toContain('dark:text-red-400')
      expect(className).toContain('dark:hover:bg-red-700')
    })

    it('applies conditional CSS classes based on type prop - needsAttention', () => {
      render(
        <ProjectTypeDashboardCard type="needsAttention" count={3} icon={faExclamationTriangle} />
      )

      const secondaryCard = screen.getByTestId('secondary-card')
      const className = secondaryCard.getAttribute('class')

      expect(className).toContain('overflow-hidden')
      expect(className).toContain('transition-colors')
      expect(className).toContain('duration-300')
      expect(className).toContain('bg-yellow-100')
      expect(className).toContain('text-yellow-800')
      expect(className).toContain('hover:bg-yellow-200')
      expect(className).toContain('hover:text-yellow-800')
      expect(className).toContain('dark:bg-yellow-800')
      expect(className).toContain('dark:text-yellow-400')
      expect(className).toContain('dark:hover:bg-yellow-700')
    })

    it('maintains responsive design classes', () => {
      render(<ProjectTypeDashboardCard {...baseProps} />)

      const count = screen.getByText('42')
      expect(count).toHaveClass('text-2xl', 'md:text-3xl')
    })
  })

  describe('Component Integration', () => {
    it('passes correct props to SecondaryCard', () => {
      render(<ProjectTypeDashboardCard {...baseProps} />)

      const secondaryCard = screen.getByTestId('secondary-card')
      expect(secondaryCard).toHaveAttribute('data-title', 'Healthy')
      expect(secondaryCard).toHaveAttribute('data-icon', JSON.stringify(faHeartPulse))
    })

    it('renders SecondaryCard with correct content structure', () => {
      render(<ProjectTypeDashboardCard {...baseProps} />)

      const cardTitle = screen.getByTestId('card-title')
      const cardContent = screen.getByTestId('card-content')

      expect(cardTitle).toHaveTextContent('Healthy')
      expect(cardContent).toContainElement(screen.getByText('42'))
    })

    it('maintains proper component hierarchy', () => {
      render(<ProjectTypeDashboardCard {...baseProps} />)

      const link = screen.getByRole('link')
      const secondaryCard = screen.getByTestId('secondary-card')
      const count = screen.getByText('42')

      expect(link).toContainElement(secondaryCard)
      expect(secondaryCard).toContainElement(count)
    })
  })

  describe('Type Safety and TypeScript Compliance', () => {
    it('only accepts valid type values', () => {
      const validTypes: Array<'healthy' | 'needsAttention' | 'unhealthy'> = [
        'healthy',
        'needsAttention',
        'unhealthy',
      ]

      const testTypeValue = (type: 'healthy' | 'needsAttention' | 'unhealthy') => {
        expect(() => {
          render(<ProjectTypeDashboardCard type={type} count={10} icon={faHeartPulse} />)
        }).not.toThrow()
      }

      validTypes.forEach(testTypeValue)
    })

    it('handles different icon types correctly', () => {
      const icons = [faHeartPulse, faExclamationTriangle, faSkull]

      icons.forEach((icon) => {
        const { unmount } = render(
          <ProjectTypeDashboardCard type="healthy" count={10} icon={icon} />
        )
        expect(screen.getByTestId('secondary-card')).toBeInTheDocument()
        unmount()
      })
    })
  })

  describe('Performance and Optimization', () => {
    it('renders efficiently with multiple re-renders', () => {
      const { rerender } = render(<ProjectTypeDashboardCard {...baseProps} />)

      // Test multiple re-renders don't cause issues
      for (let i = 0; i < 10; i++) {
        rerender(<ProjectTypeDashboardCard {...baseProps} count={i} />)
        expect(screen.getByText(i.toString())).toBeInTheDocument()
      }
    })

    it('handles rapid prop changes gracefully', () => {
      const { rerender } = render(<ProjectTypeDashboardCard {...baseProps} />)

      const types: Array<'healthy' | 'needsAttention' | 'unhealthy'> = [
        'healthy',
        'needsAttention',
        'unhealthy',
      ]

      types.forEach((type, index) => {
        rerender(<ProjectTypeDashboardCard type={type} count={index} icon={faHeartPulse} />)
        expect(screen.getByTestId('secondary-card')).toBeInTheDocument()
      })
    })
  })
})
