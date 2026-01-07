import { screen } from '@testing-library/react'
import { render } from '@testing-library/react'
import { useTheme } from 'next-themes'
import { FaChartPie, FaChartBar, FaChartLine, FaTachometerAlt, FaHeart } from 'react-icons/fa'
import DonutBarChart from 'components/DonutBarChart'

// Mock next-themes
jest.mock('next-themes', () => ({
  useTheme: jest.fn(),
}))

// Mock next/dynamic for react-apexcharts
jest.mock('next/dynamic', () => {
  return jest.fn(() => {
    // Mock Chart component that mimics react-apexcharts
    const MockChart = ({ options, series, height, type, ...props }) => (
      <div
        data-testid="apex-chart"
        data-options={JSON.stringify(options)}
        data-series={JSON.stringify(series)}
        data-height={height}
        data-type={type}
        {...props}
      >
        ApexCharts Mock
      </div>
    )
    MockChart.displayName = 'Chart'
    return MockChart
  })
})

// Mock utils/round
jest.mock('utils/round', () => ({
  round: jest.fn((value: number, decimals: number) => {
    return Math.round(value * Math.pow(10, decimals)) / Math.pow(10, decimals)
  }),
}))

// Mock components
jest.mock('components/AnchorTitle', () => {
  const MockAnchorTitle = ({ title }: { title: string }) => (
    <div data-testid="anchor-title">{title}</div>
  )
  MockAnchorTitle.displayName = 'AnchorTitle'
  return MockAnchorTitle
})

jest.mock('components/SecondaryCard', () => {
  const MockSecondaryCard = ({ title, icon, children }) => {
    const iconName = icon?.displayName ?? icon?.name ?? icon

    return (
      <div data-testid="secondary-card" data-icon={iconName}>
        <div data-testid="card-title">{title}</div>
        <div data-testid="card-content">{children}</div>
      </div>
    )
  }
  MockSecondaryCard.displayName = 'SecondaryCard'
  return MockSecondaryCard
})

describe('DonutBarChart Component Test Suite', () => {
  const mockUseTheme = useTheme as jest.MockedFunction<typeof useTheme>

  beforeEach(() => {
    mockUseTheme.mockReturnValue({
      theme: 'light',
      setTheme: jest.fn(),
      themes: ['light', 'dark'],
      systemTheme: 'light',
      resolvedTheme: 'light',
    })
    jest.clearAllMocks()
  })

  describe('Basic rendering functionality', () => {
    it('renders the component with required props', () => {
      render(<DonutBarChart icon={FaChartPie} title="Test Chart" series={[50, 30, 20]} />)

      expect(screen.getByTestId('secondary-card')).toBeInTheDocument()
      expect(screen.getByTestId('apex-chart')).toBeInTheDocument()
    })

    it('renders title through AnchorTitle component', () => {
      render(<DonutBarChart icon={FaChartBar} title="Health Metrics" series={[60, 25, 15]} />)

      expect(screen.getByTestId('anchor-title')).toHaveTextContent('Health Metrics')
    })

    it('passes icon to SecondaryCard', () => {
      render(<DonutBarChart icon={FaChartLine} title="System Status" series={[80, 15, 5]} />)

      expect(screen.getByTestId('secondary-card')).toHaveAttribute('data-icon', 'FaChartLine')
    })
  })

  describe('Series data handling', () => {
    it('processes series data with rounding', () => {
      const series = [33.333, 33.333, 33.334]

      render(<DonutBarChart icon={FaChartPie} title="Balanced Data" series={series} />)

      const chart = screen.getByTestId('apex-chart')
      const chartSeries = JSON.parse(chart.dataset.series || '[]')

      // Should be rounded to 1 decimal place
      expect(chartSeries).toEqual([33.3, 33.3, 33.3])
    })

    it('handles integer values correctly', () => {
      const series = [50, 30, 20]

      render(<DonutBarChart icon={FaChartPie} title="Integer Data" series={series} />)

      const chart = screen.getByTestId('apex-chart')
      const chartSeries = JSON.parse(chart.dataset.series || '[]')

      expect(chartSeries).toEqual([50, 30, 20])
    })

    it('handles decimal values with proper rounding', () => {
      const series = [25.555, 30.777, 43.668]

      render(<DonutBarChart icon={FaChartPie} title="Decimal Data" series={series} />)

      const chart = screen.getByTestId('apex-chart')
      const chartSeries = JSON.parse(chart.dataset.series || '[]')

      // Rounded to 1 decimal place
      expect(chartSeries).toEqual([25.6, 30.8, 43.7])
    })

    it('handles zero values', () => {
      const series = [0, 50, 0]

      render(<DonutBarChart icon={FaChartPie} title="With Zeros" series={series} />)

      const chart = screen.getByTestId('apex-chart')
      const chartSeries = JSON.parse(chart.dataset.series || '[]')

      expect(chartSeries).toEqual([0, 50, 0])
    })

    it('handles single value', () => {
      const series = [100]

      render(<DonutBarChart icon={FaChartPie} title="Single Value" series={series} />)

      const chart = screen.getByTestId('apex-chart')
      const chartSeries = JSON.parse(chart.dataset.series || '[]')

      expect(chartSeries).toEqual([100])
    })

    it('handles empty series array', () => {
      const series: number[] = []

      render(<DonutBarChart icon={FaChartPie} title="Empty Data" series={series} />)

      const chart = screen.getByTestId('apex-chart')
      const chartSeries = JSON.parse(chart.dataset.series || '[]')

      expect(chartSeries).toEqual([])
    })
  })

  describe('Chart configuration', () => {
    it('configures chart with correct options', () => {
      render(<DonutBarChart icon={FaChartPie} title="Configuration Test" series={[40, 35, 25]} />)

      const chart = screen.getByTestId('apex-chart')
      const options = JSON.parse(chart.dataset.options || '{}')

      expect(options.chart.animations.enabled).toBe(true)
      expect(options.chart.animations.speed).toBe(1000)
      expect(options.legend.show).toBe(true)
      expect(options.legend.position).toBe('bottom')
      expect(options.stroke.show).toBe(false)
      expect(options.colors).toEqual(['#0ef94e', '#f9b90e', '#f94e0e'])
      expect(options.labels).toEqual(['Healthy', 'Need Attention', 'Unhealthy'])
    })

    it('sets correct chart type and height', () => {
      render(<DonutBarChart icon={FaChartPie} title="Type and Height Test" series={[60, 25, 15]} />)

      const chart = screen.getByTestId('apex-chart')

      expect(chart.dataset.type).toBe('donut')
      expect(chart.dataset.height).toBe('250')
    })

    it('uses fixed color scheme', () => {
      render(<DonutBarChart icon={FaChartPie} title="Color Test" series={[33, 33, 34]} />)

      const chart = screen.getByTestId('apex-chart')
      const options = JSON.parse(chart.dataset.options || '{}')

      expect(options.colors).toEqual([
        '#0ef94e', // green
        '#f9b90e', // orange
        '#f94e0e', // red
      ])
    })

    it('uses fixed labels', () => {
      render(<DonutBarChart icon={FaChartPie} title="Labels Test" series={[70, 20, 10]} />)

      const chart = screen.getByTestId('apex-chart')
      const options = JSON.parse(chart.dataset.options || '{}')

      expect(options.labels).toEqual(['Healthy', 'Need Attention', 'Unhealthy'])
    })
  })

  describe('Theme integration', () => {
    it('applies light theme colors to legend labels', () => {
      mockUseTheme.mockReturnValue({
        theme: 'light',
        setTheme: jest.fn(),
        themes: ['light', 'dark'],
        systemTheme: 'light',
        resolvedTheme: 'light',
      })

      render(<DonutBarChart icon={FaChartPie} title="Light Theme" series={[50, 30, 20]} />)

      const chart = screen.getByTestId('apex-chart')
      const options = JSON.parse(chart.dataset.options || '{}')

      expect(options.legend.labels.colors).toBe('#1E1E2C')
    })

    it('applies dark theme colors to legend labels', () => {
      mockUseTheme.mockReturnValue({
        theme: 'dark',
        setTheme: jest.fn(),
        themes: ['light', 'dark'],
        systemTheme: 'dark',
        resolvedTheme: 'dark',
      })

      render(<DonutBarChart icon={FaChartPie} title="Dark Theme" series={[45, 35, 20]} />)

      const chart = screen.getByTestId('apex-chart')
      const options = JSON.parse(chart.dataset.options || '{}')

      expect(options.legend.labels.colors).toBe('#ececec')
    })

    it('uses theme as key for Chart component', () => {
      mockUseTheme.mockReturnValue({
        theme: 'dark',
        setTheme: jest.fn(),
        themes: ['light', 'dark'],
        systemTheme: 'dark',
        resolvedTheme: 'dark',
      })

      render(<DonutBarChart icon={FaChartPie} title="Theme Key Test" series={[55, 30, 15]} />)

      const chart = screen.getByTestId('apex-chart')
      // The key should be applied but we can't directly test it in our mock
      // We verify the theme is being used in legend colors instead
      const options = JSON.parse(chart.dataset.options || '{}')
      expect(options.legend.labels.colors).toBe('#ececec')
    })
  })

  describe('Component structure and accessibility', () => {
    it('maintains proper component hierarchy', () => {
      render(<DonutBarChart icon={FaHeart} title="Structure Test" series={[75, 15, 10]} />)

      const card = screen.getByTestId('secondary-card')
      const title = screen.getByTestId('anchor-title')
      const chart = screen.getByTestId('apex-chart')

      expect(card).toBeInTheDocument()
      expect(title).toBeInTheDocument()
      expect(chart).toBeInTheDocument()

      // Verify hierarchy
      expect(card).toContainElement(title)
      expect(card).toContainElement(chart)
    })

    it('renders chart inside proper container div', () => {
      render(<DonutBarChart icon={FaTachometerAlt} title="Container Test" series={[40, 40, 20]} />)

      const cardContent = screen.getByTestId('card-content')
      const chart = screen.getByTestId('apex-chart')

      expect(cardContent).toContainElement(chart)
    })
  })

  describe('Prop validation and edge cases', () => {
    it('handles different icon types', () => {
      const iconTypes = [FaChartPie, FaChartBar, FaChartLine, FaTachometerAlt, FaHeart]

      for (const iconType of iconTypes) {
        const { unmount } = render(
          <DonutBarChart icon={iconType} title={`Test ${iconType.name}`} series={[50, 30, 20]} />
        )

        expect(screen.getByTestId('secondary-card')).toHaveAttribute('data-icon', iconType.name)
        unmount()
      }
    })

    it('handles various title formats', () => {
      const titles = [
        'Simple Title',
        'Title with Numbers 123',
        'Title with Special Characters !@#$%',
        'Very Long Title That Might Wrap Multiple Lines And Test Component Behavior',
        '',
      ]

      for (const title of titles) {
        const { unmount } = render(
          <DonutBarChart icon={FaChartPie} title={title} series={[33, 33, 34]} />
        )

        expect(screen.getByTestId('anchor-title')).toHaveTextContent(title)
        unmount()
      }
    })

    it('handles large series values', () => {
      const largeSeries = [999999.999, 1000000.001, 2000000.5]

      render(<DonutBarChart icon={FaChartPie} title="Large Values" series={largeSeries} />)

      const chart = screen.getByTestId('apex-chart')
      const chartSeries = JSON.parse(chart.dataset.series || '[]')

      // Should be rounded to 1 decimal place
      expect(chartSeries).toEqual([1000000, 1000000, 2000000.5])
    })

    it('handles negative values', () => {
      const negativeSeries = [-10.5, 50.7, -20.3]

      render(<DonutBarChart icon={FaChartPie} title="Negative Values" series={negativeSeries} />)

      const chart = screen.getByTestId('apex-chart')
      const chartSeries = JSON.parse(chart.dataset.series || '[]')

      expect(chartSeries).toEqual([-10.5, 50.7, -20.3])
    })
  })

  describe('Performance and re-rendering', () => {
    it('handles series updates correctly', () => {
      const { rerender } = render(
        <DonutBarChart icon={FaChartPie} title="Update Test" series={[50, 30, 20]} />
      )

      let chart = screen.getByTestId('apex-chart')
      let chartSeries = JSON.parse(chart.dataset.series || '[]')
      expect(chartSeries).toEqual([50, 30, 20])

      rerender(<DonutBarChart icon={FaChartPie} title="Update Test" series={[70, 20, 10]} />)

      chart = screen.getByTestId('apex-chart')
      chartSeries = JSON.parse(chart.dataset.series || '[]')
      expect(chartSeries).toEqual([70, 20, 10])
    })

    it('handles title updates correctly', () => {
      const { rerender } = render(
        <DonutBarChart icon={FaChartPie} title="Original Title" series={[40, 35, 25]} />
      )

      expect(screen.getByTestId('anchor-title')).toHaveTextContent('Original Title')

      rerender(<DonutBarChart icon={FaChartPie} title="Updated Title" series={[40, 35, 25]} />)

      expect(screen.getByTestId('anchor-title')).toHaveTextContent('Updated Title')
    })

    it('handles icon updates correctly', () => {
      const { rerender } = render(
        <DonutBarChart icon={FaChartPie} title="Icon Test" series={[60, 25, 15]} />
      )

      expect(screen.getByTestId('secondary-card')).toHaveAttribute('data-icon', 'FaChartPie')

      rerender(<DonutBarChart icon={FaChartBar} title="Icon Test" series={[60, 25, 15]} />)

      expect(screen.getByTestId('secondary-card')).toHaveAttribute('data-icon', 'FaChartBar')
    })

    it('handles theme changes correctly', () => {
      const { rerender } = render(
        <DonutBarChart icon={FaChartPie} title="Theme Change Test" series={[45, 35, 20]} />
      )

      let chart = screen.getByTestId('apex-chart')
      let options = JSON.parse(chart.dataset.options || '{}')
      expect(options.legend.labels.colors).toBe('#1E1E2C') // light theme

      mockUseTheme.mockReturnValue({
        theme: 'dark',
        setTheme: jest.fn(),
        themes: ['light', 'dark'],
        systemTheme: 'dark',
        resolvedTheme: 'dark',
      })

      rerender(<DonutBarChart icon={FaChartPie} title="Theme Change Test" series={[45, 35, 20]} />)

      chart = screen.getByTestId('apex-chart')
      options = JSON.parse(chart.dataset.options || '{}')
      expect(options.legend.labels.colors).toBe('#ececec') // dark theme
    })
  })

  describe('Integration with external dependencies', () => {
    it('calls round utility function for each series value', () => {
      const mockRound = jest.requireMock('utils/round').round

      render(
        <DonutBarChart icon={FaChartPie} title="Round Test" series={[33.333, 44.444, 22.222]} />
      )

      expect(mockRound).toHaveBeenCalledTimes(3)
      expect(mockRound).toHaveBeenCalledWith(33.333, 1)
      expect(mockRound).toHaveBeenCalledWith(44.444, 1)
      expect(mockRound).toHaveBeenCalledWith(22.222, 1)
    })

    it('integrates properly with next-themes useTheme hook', () => {
      render(<DonutBarChart icon={FaChartPie} title="Theme Integration" series={[50, 30, 20]} />)

      expect(mockUseTheme).toHaveBeenCalled()
    })

    it('uses dynamic import for Chart component (SSR safety)', () => {
      render(<DonutBarChart icon={FaChartPie} title="Dynamic Import Test" series={[40, 40, 20]} />)

      // Chart should render (mocked) proving dynamic import works
      expect(screen.getByTestId('apex-chart')).toBeInTheDocument()
    })
  })
})
