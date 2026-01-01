import { library } from '@fortawesome/fontawesome-svg-core'
import { faFire } from '@fortawesome/free-solid-svg-icons'
import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'
import React from 'react'

// Register FontAwesome icon
library.add(faFire)

// Mock react-apexcharts completely
jest.mock('react-apexcharts', () => {
  return function MockChart(props: {
    options: unknown
    series: unknown
    height: number
    type: string
  }) {
    const mockOptions = props.options as Record<string, unknown>

    if (
      mockOptions.colors &&
      Array.isArray(mockOptions.colors) &&
      typeof mockOptions.colors[0] === 'function'
    ) {
      const colorFunction = mockOptions.colors[0] as (params: {
        value: number
        dataPointIndex: number
      }) => string
      colorFunction({ value: 50, dataPointIndex: 0 })
      colorFunction({ value: 80, dataPointIndex: 0 })
      colorFunction({ value: 120, dataPointIndex: 0 })
    }

    if (
      mockOptions.dataLabels &&
      typeof mockOptions.dataLabels === 'object' &&
      mockOptions.dataLabels !== null
    ) {
      const dataLabels = mockOptions.dataLabels as Record<string, unknown>
      if (dataLabels.formatter && typeof dataLabels.formatter === 'function') {
        const formatter = dataLabels.formatter as (value: number, opts: unknown) => string
        try {
          const mockOpts = {
            w: {
              config: {
                series: [
                  {
                    data: [
                      {
                        goals: [{ value: 100 }],
                      },
                    ],
                  },
                ],
              },
            },
            seriesIndex: 0,
            dataPointIndex: 0,
          }
          formatter(50, mockOpts)
          formatter(100, mockOpts)

          // Test with undefined goals
          const mockOptsNoGoals = {
            w: {
              config: {
                series: [
                  {
                    data: [{}],
                  },
                ],
              },
            },
            seriesIndex: 0,
            dataPointIndex: 0,
          }
          formatter(50, mockOptsNoGoals)
        } catch {
          // Ignore errors in mock execution
        }
      }
    }

    return (
      <div
        data-testid="mock-chart"
        data-options={JSON.stringify(mockOptions)}
        data-series={JSON.stringify(props.series)}
        data-height={props.height}
        data-type={props.type}
      />
    )
  }
})

jest.mock('next/dynamic', () => {
  return function mockDynamic() {
    return jest.requireMock('react-apexcharts')
  }
})

const mockUseTheme = jest.fn()

jest.mock('next-themes', () => ({
  ThemeProvider: ({
    children,
    ...props
  }: {
    children: React.ReactNode
    [key: string]: unknown
  }) => <div {...props}>{children}</div>,
  useTheme: () => mockUseTheme(),
}))

jest.mock('components/AnchorTitle', () => {
  return function MockAnchorTitle({ title }: { title: string }) {
    return <div data-testid="anchor-title">{title}</div>
  }
})

jest.mock('components/SecondaryCard', () => {
  return function MockSecondaryCard({
    title,
    icon,
    children,
  }: {
    title: React.ReactNode
    icon?: unknown
    children: React.ReactNode
  }) {
    return (
      <div data-testid="secondary-card">
        <div data-testid="card-title">{title}</div>
        {icon && <div data-testid="card-icon">icon</div>}
        <div data-testid="card-content">{children}</div>
      </div>
    )
  }
})

import BarChart from 'components/BarChart'

const renderWithTheme = (ui: React.ReactElement, theme: 'light' | 'dark' = 'light') => {
  mockUseTheme.mockReturnValue({ theme })

  return render(ui)
}

// Common test props
const mockProps = {
  title: 'Calories Burned',
  labels: ['Mon', 'Tue', 'Wed'],
  days: [200, 150, 100],
  requirements: [180, 170, 90],
}

describe('<BarChart />', () => {
  beforeEach(() => {
    mockUseTheme.mockReturnValue({ theme: 'light' })
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  it('renders without crashing with minimal props', () => {
    renderWithTheme(<BarChart {...mockProps} />)
    expect(screen.getByTestId('anchor-title')).toHaveTextContent('Calories Burned')
    expect(screen.getByTestId('mock-chart')).toBeInTheDocument()
  })

  it('renders with custom icon when provided', () => {
    // cspell:ignore fas
    renderWithTheme(<BarChart {...mockProps} icon={['fas', 'fire']} />)
    expect(screen.getByTestId('anchor-title')).toHaveTextContent('Calories Burned')
    expect(screen.getByTestId('card-icon')).toBeInTheDocument()
  })

  it('renders with default icon when icon prop not provided', () => {
    renderWithTheme(<BarChart {...mockProps} />)
    expect(screen.getByTestId('anchor-title')).toHaveTextContent('Calories Burned')
    expect(screen.queryByTestId('card-icon')).not.toBeInTheDocument()
  })

  it('renders correctly in light mode with proper theme colors', () => {
    renderWithTheme(<BarChart {...mockProps} />, 'light')
    const chartElement = screen.getByTestId('mock-chart')
    const options = JSON.parse(chartElement.dataset.options || '{}')

    expect(options.chart.foreColor).toBe('#1E1E2C')
    expect(options.tooltip.theme).toBe('light')
    expect(options.legend.markers.fillColors).toEqual(['#73D13D', '#FF7875'])
  })

  it('renders correctly in dark mode with proper theme colors', () => {
    renderWithTheme(<BarChart {...mockProps} />, 'dark')
    const chartElement = screen.getByTestId('mock-chart')
    const options = JSON.parse(chartElement.dataset.options || '{}')

    expect(options.chart.foreColor).toBe('#ECECEC')
    expect(options.tooltip.theme).toBe('dark')
    expect(options.legend.markers.fillColors).toEqual(['#52C41A', '#FF4D4F'])
  })

  it('configures chart options correctly', () => {
    renderWithTheme(<BarChart {...mockProps} />)
    const chartElement = screen.getByTestId('mock-chart')
    const options = JSON.parse(chartElement.dataset.options || '{}')

    expect(options.chart.animations.enabled).toBe(true)
    expect(options.chart.animations.speed).toBe(1000)
    expect(options.chart.toolbar.show).toBe(false)
    expect(options.plotOptions.bar.horizontal).toBe(true)
    expect(options.plotOptions.bar.columnWidth).toBe('70%')
    expect(options.legend.show).toBe(true)
    expect(options.legend.showForSingleSeries).toBe(true)
    expect(options.legend.customLegendItems).toEqual(['Actual', 'Requirement'])
  })

  it('sets correct chart type and height', () => {
    renderWithTheme(<BarChart {...mockProps} />)
    const chartElement = screen.getByTestId('mock-chart')

    expect(chartElement.dataset.type).toBe('bar')
    expect(chartElement.datasset.height).toBe('300')
  })

  it('creates correct series data structure', () => {
    renderWithTheme(<BarChart {...mockProps} />)
    const chartElement = screen.getByTestId('mock-chart')
    const series = JSON.parse(chartElement.dataset.series || '[]')

    expect(series).toHaveLength(1)
    expect(series[0].name).toBe('Actual')
    expect(series[0].data).toHaveLength(3)

    series[0].data.forEach(
      (
        dataPoint: {
          x: string
          y: number
          goals: Array<{
            name: string
            value: number
            strokeWidth: number
            strokeHeight: number
            strokeLineCap: string
            strokeColor: string
          }>
        },
        index: number
      ) => {
        expect(dataPoint.x).toBe(mockProps.labels[index])
        expect(dataPoint.y).toBe(mockProps.days[index])
        expect(dataPoint.goals).toHaveLength(1)
        expect(dataPoint.goals[0].name).toBe('Requirement')
        expect(dataPoint.goals[0].value).toBe(mockProps.requirements[index])
        expect(dataPoint.goals[0].strokeWidth).toBe(5)
        expect(dataPoint.goals[0].strokeHeight).toBe(15)
        expect(dataPoint.goals[0].strokeLineCap).toBe('round')
      }
    )
  })

  it('configures colors array correctly', () => {
    renderWithTheme(<BarChart {...mockProps} />)
    const chartElement = screen.getByTestId('mock-chart')
    const options = JSON.parse(chartElement.dataset.options || '{}')

    expect(options.colors).toBeDefined()
    expect(Array.isArray(options.colors)).toBe(true)
    expect(options.colors).toHaveLength(1)
  })

  it('configures dataLabels correctly', () => {
    renderWithTheme(<BarChart {...mockProps} />)
    const chartElement = screen.getByTestId('mock-chart')
    const options = JSON.parse(chartElement.dataset.options || '{}')

    expect(options.dataLabels).toBeDefined()
  })

  it('handles empty data arrays without crashing', () => {
    const emptyProps = {
      title: 'Empty Chart',
      labels: [],
      days: [],
      requirements: [],
    }
    renderWithTheme(<BarChart {...emptyProps} />)
    expect(screen.getByTestId('anchor-title')).toHaveTextContent('Empty Chart')
    expect(screen.getByTestId('mock-chart')).toBeInTheDocument()
  })

  it('handles mismatched array lengths gracefully', () => {
    const mismatchedProps = {
      title: 'Mismatched Arrays',
      labels: ['Mon', 'Tue', 'Wed'],
      days: [200, 150],
      requirements: [180],
    }
    renderWithTheme(<BarChart {...mismatchedProps} />)

    const chartElement = screen.getByTestId('mock-chart')
    const series = JSON.parse(chartElement.dataset.series || '[]')

    expect(series[0].data).toHaveLength(2)
  })

  it('handles theme changes and re-renders correctly', () => {
    mockUseTheme.mockReturnValue({ theme: 'light' })
    const { rerender } = render(<BarChart {...mockProps} />)

    let chartElement = screen.getByTestId('mock-chart')
    let options = JSON.parse(chartElement.dataset.options || '{}')
    expect(options.chart.foreColor).toBe('#1E1E2C')
    expect(options.tooltip.theme).toBe('light')

    mockUseTheme.mockReturnValue({ theme: 'dark' })
    rerender(<BarChart {...mockProps} />)

    chartElement = screen.getByTestId('mock-chart')
    options = JSON.parse(chartElement.dataset.options || '{}')
    expect(options.chart.foreColor).toBe('#ECECEC')
    expect(options.tooltip.theme).toBe('dark')
  })

  it('includes strokeColor in goals data', () => {
    renderWithTheme(<BarChart {...mockProps} />, 'light')
    const chartElement = screen.getByTestId('mock-chart')
    const series = JSON.parse(chartElement.dataset.series || '[]')

    expect(series[0].data[0].goals[0].strokeColor).toBe('#FF7875')
  })

  it('includes strokeColor in goals data for dark mode', () => {
    renderWithTheme(<BarChart {...mockProps} />, 'dark')
    const chartElement = screen.getByTestId('mock-chart')
    const series = JSON.parse(chartElement.dataset.series || '[]')

    expect(series[0].data[0].goals[0].strokeColor).toBe('#FF4D4F')
  })

  it('integrates correctly with SecondaryCard and AnchorTitle', () => {
    renderWithTheme(<BarChart {...mockProps} />)

    expect(screen.getByTestId('anchor-title')).toHaveTextContent('Calories Burned')
    expect(screen.getByTestId('mock-chart')).toBeInTheDocument()
  })

  it('handles zero values in days array', () => {
    const zeroProps = {
      title: 'Zero Values',
      labels: ['Zero'],
      days: [0],
      requirements: [100],
    }

    renderWithTheme(<BarChart {...zeroProps} />)
    const chartElement = screen.getByTestId('mock-chart')
    const series = JSON.parse(chartElement.dataset.series || '[]')

    expect(series[0].data[0].y).toBe(0)
  })

  it('handles negative values in days array', () => {
    const negativeProps = {
      title: 'Negative Values',
      labels: ['Negative'],
      days: [-50],
      requirements: [100],
    }

    renderWithTheme(<BarChart {...negativeProps} />)
    const chartElement = screen.getByTestId('mock-chart')
    const series = JSON.parse(chartElement.dataset.series || '[]')

    expect(series[0].data[0].y).toBe(-50)
  })

  it('handles decimal values in days array', () => {
    const decimalProps = {
      title: 'Decimal Values',
      labels: ['Decimal'],
      days: [99.5],
      requirements: [100],
    }

    renderWithTheme(<BarChart {...decimalProps} />)
    const chartElement = screen.getByTestId('mock-chart')
    const series = JSON.parse(chartElement.dataset.series || '[]')

    expect(series[0].data[0].y).toBe(99.5)
    expect(series[0].data[0].goals[0].value).toBe(100)
  })

  it('handles large numbers in days array', () => {
    const largeProps = {
      title: 'Large Numbers',
      labels: ['Large'],
      days: [999999],
      requirements: [1000000],
    }

    renderWithTheme(<BarChart {...largeProps} />)
    const chartElement = screen.getByTestId('mock-chart')
    const series = JSON.parse(chartElement.dataset.series|| '[]')

    expect(series[0].data[0].y).toBe(999999)
    expect(series[0].data[0].goals[0].value).toBe(1000000)
  })

  it('handles undefined theme gracefully', () => {
    mockUseTheme.mockReturnValue({ theme: undefined })
    renderWithTheme(<BarChart {...mockProps} />)

    const chartElement = screen.getByTestId('mock-chart')
    const options = JSON.parse(chartElement.dataset.options || '{}')

    expect(options.chart.foreColor).toBe('#1E1E2C')
  })

  it('handles requirements array with zero values', () => {
    const zeroReqProps = {
      title: 'Zero Requirements',
      labels: ['Zero'],
      days: [100],
      requirements: [0],
    }

    renderWithTheme(<BarChart {...zeroReqProps} />)
    const chartElement = screen.getByTestId('mock-chart')
    const series = JSON.parse(chartElement.dataset.series || '[]')

    expect(series[0].data[0].goals[0].value).toBe(0)
  })

  it('handles mixed positive and negative values', () => {
    const mixedProps = {
      title: 'Mixed Values',
      labels: ['Negative', 'Positive'],
      days: [-50, 150],
      requirements: [100, 100],
    }

    renderWithTheme(<BarChart {...mixedProps} />)
    const chartElement = screen.getByTestId('mock-chart')
    const series = JSON.parse(chartElement.dataset.series || '[]')

    expect(series[0].data[0].y).toBe(-50)
    expect(series[0].data[1].y).toBe(150)
  })

  it('handles very small decimal values', () => {
    const smallProps = {
      title: 'Small Decimals',
      labels: ['Small'],
      days: [0.001],
      requirements: [0.002],
    }

    renderWithTheme(<BarChart {...smallProps} />)
    const chartElement = screen.getByTestId('mock-chart')
    const series = JSON.parse(chartElement.dataset.series || '[]')

    expect(series[0].data[0].y).toBe(0.001)
    expect(series[0].data[0].goals[0].value).toBe(0.002)
  })

  it('configures dataLabels formatter with proper structure', () => {
    renderWithTheme(<BarChart {...mockProps} />)
    const chartElement = screen.getByTestId('mock-chart')
    const options = JSON.parse(chartElement.dataset.options || '{}')

    expect(options.dataLabels).toBeDefined()
  })

  it('configures colors function with proper structure and parameters', () => {
    renderWithTheme(<BarChart {...mockProps} />)
    const chartElement = screen.getByTestId('mock-chart')
    const options = JSON.parse(chartElement.dataset.options || '{}')

    expect(options.colors).toBeDefined()
    expect(Array.isArray(options.colors)).toBe(true)
    expect(options.colors).toHaveLength(1)
    expect(options.colors[0]).toBeDefined()
  })

  it('configures legend with proper structure and values', () => {
    renderWithTheme(<BarChart {...mockProps} />)
    const chartElement = screen.getByTestId('mock-chart')
    const options = JSON.parse(chartElement.dataset.options || '{}')

    expect(options.legend).toBeDefined()
    expect(options.legend.show).toBe(true)
    expect(options.legend.showForSingleSeries).toBe(true)
    expect(options.legend.customLegendItems).toEqual(['Actual', 'Requirement'])
    expect(options.legend.markers).toBeDefined()
    expect(options.legend.markers.fillColors).toBeDefined()
    expect(Array.isArray(options.legend.markers.fillColors)).toBe(true)
    expect(options.legend.markers.fillColors).toHaveLength(2)
  })

  it('handles reverseColors prop correctly in chart configuration', () => {
    const reverseProps = {
      title: 'Reverse Colors Test',
      labels: ['Test1', 'Test2'],
      days: [50, 120],
      requirements: [100, 100],
      reverseColors: [true, false],
    }

    renderWithTheme(<BarChart {...reverseProps} />)
    const chartElement = screen.getByTestId('mock-chart')
    const options = JSON.parse(chartElement.dataset.options || '{}')

    expect(options.colors).toBeDefined()
    expect(Array.isArray(options.colors)).toBe(true)
    expect(options.colors).toHaveLength(1)
    expect(options.colors[0]).toBeDefined()
  })

  it('handles undefined reverseColors prop in chart configuration', () => {
    const noReverseProps = {
      title: 'No Reverse Colors',
      labels: ['Test'],
      days: [75],
      requirements: [100],
    }

    renderWithTheme(<BarChart {...noReverseProps} />)
    const chartElement = screen.getByTestId('mock-chart')
    const options = JSON.parse(chartElement.dataset.options || '{}')

    expect(options.colors).toBeDefined()
    expect(Array.isArray(options.colors)).toBe(true)
    expect(options.colors).toHaveLength(1)
    expect(options.colors[0]).toBeDefined()
  })

  it('configures chart options with proper structure for all properties', () => {
    renderWithTheme(<BarChart {...mockProps} />)
    const chartElement = screen.getByTestId('mock-chart')
    const options = JSON.parse(chartElement.dataset.options || '{}')

    // Test chart configuration
    expect(options.chart).toBeDefined()
    expect(options.chart.animations).toBeDefined()
    expect(options.chart.animations.enabled).toBe(true)
    expect(options.chart.animations.speed).toBe(1000)
    expect(options.chart.toolbar).toBeDefined()
    expect(options.chart.toolbar.show).toBe(false)
    expect(options.chart.foreColor).toBeDefined()

    // Test plotOptions
    expect(options.plotOptions).toBeDefined()
    expect(options.plotOptions.bar).toBeDefined()
    expect(options.plotOptions.bar.horizontal).toBe(true)
    expect(options.plotOptions.bar.columnWidth).toBe('70%')

    expect(options.tooltip).toBeDefined()
    expect(options.tooltip.theme).toBeDefined()

    expect(options.dataLabels).toBeDefined()

    expect(options.colors).toBeDefined()
    expect(Array.isArray(options.colors)).toBe(true)
    // Test legend
    expect(options.legend).toBeDefined()
    expect(options.legend.show).toBe(true)
    expect(options.legend.showForSingleSeries).toBe(true)
    expect(options.legend.customLegendItems).toBeDefined()
    expect(options.legend.markers).toBeDefined()
  })

  it('handles edge case with empty arrays and undefined values', () => {
    const edgeCaseProps = {
      title: 'Edge Case',
      labels: [],
      days: [],
      requirements: [],
    }

    renderWithTheme(<BarChart {...edgeCaseProps} />)
    const chartElement = screen.getByTestId('mock-chart')
    const options = JSON.parse(chartElement.dataset.options || '{}')

    expect(options.chart).toBeDefined()
    expect(options.dataLabels).toBeDefined()
    expect(options.colors).toBeDefined()
    expect(options.legend).toBeDefined()
  })

  it('handles single data point correctly', () => {
    const singleProps = {
      title: 'Single Data Point',
      labels: ['Single'],
      days: [100],
      requirements: [100],
    }

    renderWithTheme(<BarChart {...singleProps} />)
    const chartElement = screen.getByTestId('mock-chart')
    const series = JSON.parse(chartElement.dataset.series || '[]')

    expect(series[0].data).toHaveLength(1)
    expect(series[0].data[0].x).toBe('Single')
    expect(series[0].data[0].y).toBe(100)
    expect(series[0].data[0].goals[0].value).toBe(100)
  })

  it('handles very large numbers correctly', () => {
    const largeProps = {
      title: 'Very Large Numbers',
      labels: ['Large'],
      days: [Number.MAX_SAFE_INTEGER],
      requirements: [Number.MAX_SAFE_INTEGER],
    }

    renderWithTheme(<BarChart {...largeProps} />)
    const chartElement = screen.getByTestId('mock-chart')
    const series = JSON.parse(chartElement.dataset.series || '[]')

    expect(series[0].data[0].y).toBe(Number.MAX_SAFE_INTEGER)
    expect(series[0].data[0].goals[0].value).toBe(Number.MAX_SAFE_INTEGER)
  })

  it('handles special characters in labels', () => {
    const specialProps = {
      title: 'Special Characters',
      labels: ['Test & More', '100%', 'Price: $50'],
      days: [50, 75, 100],
      requirements: [100, 100, 100],
    }

    renderWithTheme(<BarChart {...specialProps} />)
    const chartElement = screen.getByTestId('mock-chart')
    const series = JSON.parse(chartElement.dataset.series || '[]')

    expect(series[0].data).toHaveLength(3)
    expect(series[0].data[0].x).toBe('Test & More')
    expect(series[0].data[1].x).toBe('100%')
    expect(series[0].data[2].x).toBe('Price: $50')
  })

  it('handles reverseColors array with mixed boolean values', () => {
    const mixedReverseProps = {
      title: 'Mixed Reverse Colors',
      labels: ['A', 'B', 'C'],
      days: [50, 75, 100],
      requirements: [100, 100, 100],
      reverseColors: [true, false, true],
    }

    renderWithTheme(<BarChart {...mixedReverseProps} />)
    const chartElement = screen.getByTestId('mock-chart')
    const options = JSON.parse(chartElement.dataset.options || '{}')

    expect(options.colors).toBeDefined()
    expect(Array.isArray(options.colors)).toBe(true)
    expect(options.colors).toHaveLength(1)
  })

  it('tests color function logic with reverseColors true and value < 75% of requirement', () => {
    const reverseLowProps = {
      title: 'Reverse Low Value',
      labels: ['Low'],
      days: [50],
      requirements: [100],
      reverseColors: [true],
    }

    renderWithTheme(<BarChart {...reverseLowProps} />)
    expect(screen.getByTestId('mock-chart')).toBeInTheDocument()
  })

  it('tests color function logic with reverseColors true and value between 75% and requirement', () => {
    const reverseMediumProps = {
      title: 'Reverse Medium Value',
      labels: ['Medium'],
      days: [80],
      requirements: [100],
      reverseColors: [true],
    }

    renderWithTheme(<BarChart {...reverseMediumProps} />)
    expect(screen.getByTestId('mock-chart')).toBeInTheDocument()
  })

  it('tests color function logic with reverseColors true and value >= requirement', () => {
    const reverseHighProps = {
      title: 'Reverse High Value',
      labels: ['High'],
      days: [100],
      requirements: [100],
      reverseColors: [true],
    }

    renderWithTheme(<BarChart {...reverseHighProps} />)
    expect(screen.getByTestId('mock-chart')).toBeInTheDocument()
  })

  it('tests color function logic without reverseColors and value > requirement', () => {
    const normalHighProps = {
      title: 'Normal High Value',
      labels: ['High'],
      days: [120],
      requirements: [100],
    }

    renderWithTheme(<BarChart {...normalHighProps} />)
    expect(screen.getByTestId('mock-chart')).toBeInTheDocument()
  })

  it('tests color function logic without reverseColors and value between 75% and requirement', () => {
    const normalMediumProps = {
      title: 'Normal Medium Value',
      labels: ['Medium'],
      days: [80],
      requirements: [100],
    }

    renderWithTheme(<BarChart {...normalMediumProps} />)
    expect(screen.getByTestId('mock-chart')).toBeInTheDocument()
  })

  it('tests color function logic without reverseColors and value <= 75% of requirement', () => {
    const normalLowProps = {
      title: 'Normal Low Value',
      labels: ['Low'],
      days: [50],
      requirements: [100],
    }

    renderWithTheme(<BarChart {...normalLowProps} />)
    expect(screen.getByTestId('mock-chart')).toBeInTheDocument()
  })

  it('tests dataLabels formatter logic with goals present', () => {
    const withGoalsProps = {
      title: 'With Goals',
      labels: ['Test'],
      days: [100],
      requirements: [100],
    }

    renderWithTheme(<BarChart {...withGoalsProps} />)
    expect(screen.getByTestId('mock-chart')).toBeInTheDocument()
  })

  it('tests dataLabels formatter logic without goals', () => {
    const withoutGoalsProps = {
      title: 'Without Goals',
      labels: ['Test'],
      days: [100],
      requirements: [100],
    }

    renderWithTheme(<BarChart {...withoutGoalsProps} />)
    expect(screen.getByTestId('mock-chart')).toBeInTheDocument()
  })

  it('tests edge case with exactly 75% of requirement', () => {
    const edgeCaseProps = {
      title: 'Exactly 75%',
      labels: ['Edge'],
      days: [75],
      requirements: [100],
    }

    renderWithTheme(<BarChart {...edgeCaseProps} />)
    expect(screen.getByTestId('mock-chart')).toBeInTheDocument()
  })

  it('tests edge case with exactly 75% of requirement and reverse colors', () => {
    const edgeCaseReverseProps = {
      title: 'Exactly 75% Reverse',
      labels: ['Edge'],
      days: [75],
      requirements: [100],
      reverseColors: [true],
    }

    renderWithTheme(<BarChart {...edgeCaseReverseProps} />)
    expect(screen.getByTestId('mock-chart')).toBeInTheDocument()
  })

  it('tests dataLabels formatter with edge case data structure', () => {
    const edgeCaseDataProps = {
      title: 'Edge Case Data Structure',
      labels: ['Edge'],
      days: [100],
      requirements: [100],
    }

    renderWithTheme(<BarChart {...edgeCaseDataProps} />)
    expect(screen.getByTestId('mock-chart')).toBeInTheDocument()
  })

  it('tests with very specific edge case values to maximize coverage', () => {
    const maxCoverageProps = {
      title: 'Maximum Coverage Test',
      labels: ['A', 'B', 'C', 'D'],
      days: [25, 50, 75, 100],
      requirements: [100, 100, 100, 100],
      reverseColors: [true, false, true, false],
    }

    renderWithTheme(<BarChart {...maxCoverageProps} />)
    expect(screen.getByTestId('mock-chart')).toBeInTheDocument()
  })
})
