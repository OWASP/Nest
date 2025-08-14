import { render, screen } from '@testing-library/react'
import { useTheme } from 'next-themes'
import LineChart from 'components/LineChart'
import type { ApexLineChartSeries } from 'types/healthMetrics'

// Mock dependencies
jest.mock('next-themes', () => ({
  useTheme: jest.fn(),
}))

jest.mock('next/dynamic', () => {
  return jest.fn().mockImplementation(() => {
    const MockChart = ({ options, series, height }: any) => (
      <div
        data-testid="mock-chart"
        data-options={JSON.stringify(options)}
        data-series={JSON.stringify(series)}
        data-height={height}
      />
    )
    return MockChart
  })
})

jest.mock('components/AnchorTitle', () => {
  return jest.fn().mockImplementation(({ title }) => (
    <div data-testid="anchor-title">{title}</div>
  ))
})

jest.mock('components/SecondaryCard', () => {
  return jest.fn().mockImplementation(({ title, icon, children }) => (
    <div data-testid="secondary-card" data-icon={icon?.toString()}>
      <div data-testid="card-title">{title}</div>
      <div data-testid="card-content">{children}</div>
    </div>
  ))
})

describe('LineChart', () => {
  const mockUseTheme = useTheme as jest.MockedFunction<typeof useTheme>
  
  const defaultProps = {
    title: 'Test Chart',
    series: [
      {
        name: 'Test Series',
        data: [10, 20, 30, 40, 50],
      },
    ] as ApexLineChartSeries[],
  }

  beforeEach(() => {
    mockUseTheme.mockReturnValue({
      theme: 'light',
      setTheme: jest.fn(),
      resolvedTheme: 'light',
      themes: ['light', 'dark'],
      systemTheme: 'light',
    })
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  describe('Renders successfully with minimal required props', () => {
    it('renders with title and series only', () => {
      render(<LineChart {...defaultProps} />)
      
      expect(screen.getByTestId('secondary-card')).toBeInTheDocument()
      expect(screen.getByTestId('anchor-title')).toBeInTheDocument()
      expect(screen.getByTestId('mock-chart')).toBeInTheDocument()
      expect(screen.getByText('Test Chart')).toBeInTheDocument()
    })
  })

  describe('Prop-based behavior', () => {
    it('passes title to AnchorTitle component', () => {
      render(<LineChart {...defaultProps} title="Custom Title" />)
      
      expect(screen.getByText('Custom Title')).toBeInTheDocument()
    })

    it('passes icon to SecondaryCard when provided', () => {
      const iconProp = 'chart-line'
      render(<LineChart {...defaultProps} icon={iconProp as any} />)
      
      const secondaryCard = screen.getByTestId('secondary-card')
      expect(secondaryCard).toHaveAttribute('data-icon', iconProp)
    })

    it('renders without icon when not provided', () => {
      render(<LineChart {...defaultProps} />)
      
      const secondaryCard = screen.getByTestId('secondary-card')
      expect(secondaryCard).toHaveAttribute('data-icon', 'undefined')
    })

    it('passes series data to Chart component', () => {
      const testSeries = [
        { name: 'Series 1', data: [1, 2, 3] },
        { name: 'Series 2', data: [4, 5, 6] },
      ] as ApexLineChartSeries[]
      
      render(<LineChart {...defaultProps} series={testSeries} />)
      
      const chart = screen.getByTestId('mock-chart')
      expect(chart).toHaveAttribute('data-series', JSON.stringify(testSeries))
    })

    it('passes labels to chart options when provided', () => {
      const labels = ['Jan', 'Feb', 'Mar']
      render(<LineChart {...defaultProps} labels={labels} />)
      
      const chart = screen.getByTestId('mock-chart')
      const options = JSON.parse(chart.getAttribute('data-options') || '{}')
      expect(options.xaxis.categories).toEqual(labels)
    })

    it('does not set categories when labels not provided', () => {
      render(<LineChart {...defaultProps} />)
      
      const chart = screen.getByTestId('mock-chart')
      const options = JSON.parse(chart.getAttribute('data-options') || '{}')
      expect(options.xaxis.categories).toBeUndefined()
    })
  })

  describe('Theme-based behavior', () => {
    it('uses light theme colors when theme is light', () => {
      mockUseTheme.mockReturnValue({
        theme: 'light',
        setTheme: jest.fn(),
        resolvedTheme: 'light',
        themes: ['light', 'dark'],
        systemTheme: 'light',
      })
      
      render(<LineChart {...defaultProps} />)
      
      const chart = screen.getByTestId('mock-chart')
      const options = JSON.parse(chart.getAttribute('data-options') || '{}')
      expect(options.chart.foreColor).toBe('#1E1E2C')
      expect(options.tooltip.theme).toBe('light')
    })

    it('uses dark theme colors when theme is dark', () => {
      mockUseTheme.mockReturnValue({
        theme: 'dark',
        setTheme: jest.fn(),
        resolvedTheme: 'dark',
        themes: ['light', 'dark'],
        systemTheme: 'dark',
      })
      
      render(<LineChart {...defaultProps} />)
      
      const chart = screen.getByTestId('mock-chart')
      const options = JSON.parse(chart.getAttribute('data-options') || '{}')
      expect(options.chart.foreColor).toBe('#ECECEC')
      expect(options.tooltip.theme).toBe('dark')
    })
  })

  describe('Chart configuration', () => {
    it('sets fixed height to 200', () => {
      render(<LineChart {...defaultProps} />)
      
      const chart = screen.getByTestId('mock-chart')
      expect(chart).toHaveAttribute('data-height', '200')
    })

    it('configures chart options correctly', () => {
      render(<LineChart {...defaultProps} />)
      
      const chart = screen.getByTestId('mock-chart')
      const options = JSON.parse(chart.getAttribute('data-options') || '{}')
      
      expect(options.chart.toolbar.show).toBe(false)
      expect(options.xaxis.tickAmount).toBe(10)
      expect(options.stroke.curve).toBe('smooth')
    })

    it('includes yaxis formatter function', () => {
      render(<LineChart {...defaultProps} />)
      
      const chart = screen.getByTestId('mock-chart')
      const options = JSON.parse(chart.getAttribute('data-options') || '{}')
      
      expect(options.yaxis.labels.formatter).toBeDefined()
      expect(typeof options.yaxis.labels.formatter).toBe('function')
    })
  })

  describe('Y-axis formatter logic', () => {
    let formatter: (value: number) => string

    beforeEach(() => {
      render(<LineChart {...defaultProps} />)
      const chart = screen.getByTestId('mock-chart')
      const options = JSON.parse(chart.getAttribute('data-options') || '{}')
      formatter = options.yaxis.labels.formatter
    })

    it('formats values >= 1000 with K suffix', () => {
      expect(formatter(1000)).toBe('1.0K')
      expect(formatter(1500)).toBe('1.5K')
      expect(formatter(10000)).toBe('10.0K')
    })

    it('formats values < 1000 with 2 decimal places by default', () => {
      expect(formatter(999)).toBe('999.00')
      expect(formatter(50.5)).toBe('50.50')
      expect(formatter(0)).toBe('0.00')
    })

    it('formats values < 1000 with 0 decimal places when round is true', () => {
      render(<LineChart {...defaultProps} round={true} />)
      const chart = screen.getByTestId('mock-chart')
      const options = JSON.parse(chart.getAttribute('data-options') || '{}')
      const roundFormatter = options.yaxis.labels.formatter
      
      expect(roundFormatter(999)).toBe('999')
      expect(roundFormatter(50.5)).toBe('51')
      expect(roundFormatter(0.7)).toBe('1')
    })
  })

  describe('Default values and fallbacks', () => {
    it('works without optional labels prop', () => {
      render(<LineChart title="Test" series={defaultProps.series} />)
      
      expect(screen.getByTestId('mock-chart')).toBeInTheDocument()
    })

    it('works without optional icon prop', () => {
      render(<LineChart title="Test" series={defaultProps.series} />)
      
      expect(screen.getByTestId('secondary-card')).toBeInTheDocument()
    })

    it('works without optional round prop (defaults to false)', () => {
      render(<LineChart title="Test" series={defaultProps.series} />)
      
      const chart = screen.getByTestId('mock-chart')
      const options = JSON.parse(chart.getAttribute('data-options') || '{}')
      const formatter = options.yaxis.labels.formatter
      
      expect(formatter(50.5)).toBe('50.50') // 2 decimal places when round is falsy
    })
  })

  describe('Edge cases and invalid inputs', () => {
    it('handles empty series array', () => {
      render(<LineChart title="Test" series={[]} />)
      
      const chart = screen.getByTestId('mock-chart')
      expect(chart).toHaveAttribute('data-series', '[]')
    })

    it('handles empty labels array', () => {
      render(<LineChart {...defaultProps} labels={[]} />)
      
      const chart = screen.getByTestId('mock-chart')
      const options = JSON.parse(chart.getAttribute('data-options') || '{}')
      expect(options.xaxis.categories).toEqual([])
    })

    it('handles undefined theme gracefully', () => {
      mockUseTheme.mockReturnValue({
        theme: undefined as any,
        setTheme: jest.fn(),
        resolvedTheme: undefined,
        themes: ['light', 'dark'],
        systemTheme: 'light',
      })
      
      render(<LineChart {...defaultProps} />)
      
      const chart = screen.getByTestId('mock-chart')
      const options = JSON.parse(chart.getAttribute('data-options') || '{}')
      // Should default to light theme color when theme is undefined
      expect(options.chart.foreColor).toBe('#1E1E2C')
    })
  })

  describe('DOM structure and accessibility', () => {
    it('renders SecondaryCard as container', () => {
      render(<LineChart {...defaultProps} />)
      
      expect(screen.getByTestId('secondary-card')).toBeInTheDocument()
    })

    it('renders AnchorTitle with proper title', () => {
      render(<LineChart {...defaultProps} />)
      
      expect(screen.getByTestId('anchor-title')).toBeInTheDocument()
      expect(screen.getByText('Test Chart')).toBeInTheDocument()
    })

    it('renders chart within card content', () => {
      render(<LineChart {...defaultProps} />)
      
      const cardContent = screen.getByTestId('card-content')
      const chart = screen.getByTestId('mock-chart')
      
      expect(cardContent).toContainElement(chart)
    })
  })

  describe('Component integration', () => {
    it('uses theme key for Chart component to handle theme changes', () => {
      const { rerender } = render(<LineChart {...defaultProps} />)
      
      mockUseTheme.mockReturnValue({
        theme: 'dark',
        setTheme: jest.fn(),
        resolvedTheme: 'dark',
        themes: ['light', 'dark'],
        systemTheme: 'dark',
      })
      
      rerender(<LineChart {...defaultProps} />)
      
      // Chart should re-render with new theme-based key
      expect(screen.getByTestId('mock-chart')).toBeInTheDocument()
    })
  })
})
