import { faUser, faChartBar } from '@fortawesome/free-solid-svg-icons'
import { render, screen } from '@testing-library/react'
import React from 'react'
import '@testing-library/jest-dom'
import DashboardCard from 'components/DashboardCard'

jest.mock('components/AnchorTitle', () => ({
  __esModule: true,
  default: ({
    title,
    className,
    ...props
  }: {
    title: string
    className?: string
    [key: string]: unknown
  }) => (
    <span className={className} data-testid="anchor-title" {...props}>
      {title}
    </span>
  ),
}))

jest.mock('components/SecondaryCard', () => ({
  __esModule: true,
  default: ({
    title,
    children,
    className,
    ...props
  }: {
    _icon: unknown
    title: React.ReactNode
    children: React.ReactNode
    className?: string
    [key: string]: unknown
  }) => (
    <div data-testid="secondary-card" className={className} {...props}>
      <h3>{title}</h3>
      <div data-testid="secondary-content">{children}</div>
    </div>
  ),
}))

describe('DashboardCard', () => {
  const baseProps = {
    title: 'Test Card',
    icon: faUser,
    className: undefined,
    stats: undefined,
  }

  beforeEach(() => {
    jest.clearAllMocks()
  })

  describe('Essential Rendering', () => {
    it('renders successfully with minimal required props', () => {
      render(<DashboardCard title="Test Card" icon={faUser} />)
      expect(screen.getByTestId('secondary-card')).toBeInTheDocument()
      expect(screen.getByTestId('anchor-title')).toHaveTextContent('Test Card')
      expect(screen.getByTestId('secondary-content')).toBeInTheDocument()
    })

    it('renders all text content correctly', () => {
      render(<DashboardCard {...baseProps} stats="42" />)
      expect(screen.getByTestId('anchor-title')).toHaveTextContent('Test Card')
      expect(screen.getByText('42')).toBeInTheDocument()
    })
  })

  describe('Conditional Rendering', () => {
    it('renders stats when provided', () => {
      render(<DashboardCard {...baseProps} stats="123" />)
      expect(screen.getByText('123')).toBeInTheDocument()
    })

    it('does not render stats paragraph if stats is not provided', () => {
      render(<DashboardCard {...baseProps} />)
      const p = screen.getByTestId('secondary-content').querySelector('p')
      expect(p).not.toBeInTheDocument()
    })
    it('does not render <p> if stats is an empty string', () => {
      render(<DashboardCard {...baseProps} stats="" />)
      const p = screen.getByTestId('secondary-content').querySelector('p')
      expect(p).not.toBeInTheDocument()
    })
  })

  describe('Prop-based Behavior', () => {
    it('applies custom className', () => {
      render(<DashboardCard {...baseProps} className="custom-class" />)
      expect(screen.getByTestId('secondary-card')).toHaveClass('custom-class')
    })

    it('applies multiple custom classes', () => {
      render(<DashboardCard {...baseProps} className="foo bar baz" />)
      expect(screen.getByTestId('secondary-card')).toHaveClass('foo')
      expect(screen.getByTestId('secondary-card')).toHaveClass('bar')
      expect(screen.getByTestId('secondary-card')).toHaveClass('baz')
    })

    it('renders different icons based on prop', () => {
      const { rerender } = render(<DashboardCard {...baseProps} icon={faUser} />)
      expect(screen.getByTestId('secondary-content').querySelector('svg')).toBeInTheDocument()
      rerender(<DashboardCard {...baseProps} icon={faChartBar} />)
      expect(screen.getByTestId('secondary-content').querySelector('svg')).toBeInTheDocument()
    })
  })

  describe('DOM Structure', () => {
    it('renders FontAwesomeIcon with correct icon', () => {
      render(<DashboardCard {...baseProps} />)
      expect(screen.getByTestId('secondary-content').querySelector('svg')).toBeInTheDocument()
    })

    it('renders stats inside a <p> tag', () => {
      render(<DashboardCard {...baseProps} stats="StatsText" />)
      const p = screen.getByText('StatsText')
      expect(p.tagName).toBe('P')
    })

    it('always renders the span for icon/stats', () => {
      render(<DashboardCard {...baseProps} />)
      const span = screen.getByTestId('secondary-content').querySelector('span')
      expect(span).toBeInTheDocument()
      expect(span).toHaveClass('flex', 'items-center', 'gap-2', 'text-2xl', 'font-light')
    })

    it('renders correct DOM structure and classes', () => {
      render(<DashboardCard {...baseProps} stats="42" className="test-class" />)
      const card = screen.getByTestId('secondary-card')
      expect(card).toHaveClass('overflow-hidden')
      expect(card).toHaveClass('transition-colors')
      expect(card).toHaveClass('duration-300')
      expect(card).toHaveClass('hover:bg-blue-100')
      expect(card).toHaveClass('dark:hover:bg-blue-950')
      expect(card).toHaveClass('test-class')
    })
  })

  describe('Edge Cases', () => {
    it('renders stats as string and handles edge cases', () => {
      render(<DashboardCard {...baseProps} stats={'0'} />)
      expect(screen.getByText('0')).toBeInTheDocument()
      render(<DashboardCard {...baseProps} stats={'-999'} />)
      expect(screen.getByText('-999')).toBeInTheDocument()
      render(<DashboardCard {...baseProps} stats={'9999999999'} />)
      expect(screen.getByText('9999999999')).toBeInTheDocument()
    })

    it('renders with an empty string title', () => {
      render(<DashboardCard {...baseProps} title="" />)
      expect(screen.getByTestId('anchor-title')).toHaveTextContent('')
    })

    it('renders with a very long title', () => {
      const longTitle = 'A'.repeat(1000)
      render(<DashboardCard {...baseProps} title={longTitle} />)
      expect(screen.getByTestId('anchor-title')).toHaveTextContent(longTitle)
    })

    it('does not render <p> if stats is undefined or null', () => {
      const { unmount } = render(<DashboardCard {...baseProps} stats={undefined} />)
      expect(screen.getByTestId('secondary-content').querySelector('p')).not.toBeInTheDocument()
      unmount()
      render(<DashboardCard {...baseProps} stats={null as unknown as string} />)
      expect(screen.getByTestId('secondary-content').querySelector('p')).not.toBeInTheDocument()
    })
  })

  describe('Accessibility', () => {
    it('is accessible with semantic structure', () => {
      render(<DashboardCard {...baseProps} stats="A11y" />)
      expect(screen.getByTestId('secondary-card')).toBeInTheDocument()
      expect(screen.getByTestId('anchor-title')).toBeInTheDocument()

      const heading = screen.getByRole('heading', { level: 3 })
      expect(heading).toBeInTheDocument()

      const statsP = screen.getByText('A11y')
      expect(statsP.tagName).toBe('P')
    })
    it('maintains accessible markup with no stats', () => {
      render(<DashboardCard {...baseProps} />)

      const heading = screen.getByRole('heading', { level: 3 })
      expect(heading).toBeInTheDocument()

      const paragraphs = screen.queryAllByRole('paragraph')
      expect(paragraphs).toHaveLength(0)
    })
  })

  describe('Component Integration', () => {
    it('renders AnchorTitle and SecondaryCard with correct props', () => {
      render(<DashboardCard {...baseProps} stats="integration" className="integration-class" />)
      expect(screen.getByTestId('anchor-title')).toHaveTextContent('Test Card')
      expect(screen.getByTestId('secondary-card')).toHaveClass('integration-class')
      expect(screen.getByTestId('secondary-content')).toBeInTheDocument()
    })

    it('ignores unknown/extra props', () => {
      // @ts-expect-error purposely passing extra prop
      render(<DashboardCard {...baseProps} extraProp="shouldBeIgnored" />)
      expect(screen.getByTestId('secondary-card')).toBeInTheDocument()
    })
  })

  describe('Performance and Optimization', () => {
    it('renders efficiently with multiple re-renders', () => {
      const { rerender } = render(<DashboardCard {...baseProps} stats="0" />)
      for (let i = 0; i < 10; i++) {
        rerender(<DashboardCard {...baseProps} stats={i.toString()} />)
        expect(screen.getByText(i.toString())).toBeInTheDocument()
      }
    })

    it('handles rapid prop changes gracefully', () => {
      const { rerender } = render(<DashboardCard {...baseProps} stats="start" />)
      const icons = [faUser, faChartBar]
      const titles = ['A', 'B', 'C']
      for (let i = 0; i < 3; i++) {
        rerender(
          <DashboardCard
            title={titles[i]}
            icon={icons[i % 2]}
            stats={i.toString()}
            className={`class${i}`}
          />
        )
        expect(screen.getByTestId('anchor-title')).toHaveTextContent(titles[i])
        expect(screen.getByText(i.toString())).toBeInTheDocument()
        expect(screen.getByTestId('secondary-card')).toHaveClass(`class${i}`)
      }
    })
  })
})
