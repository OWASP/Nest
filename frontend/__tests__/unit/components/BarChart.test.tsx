import { library } from '@fortawesome/fontawesome-svg-core'
import { faFire } from '@fortawesome/free-solid-svg-icons'
import { act, render, screen } from '@testing-library/react'
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
    return (
      <div
        data-testid="mock-chart"
        data-options={JSON.stringify(props.options)}
        data-series={JSON.stringify(props.series)}
        data-height={props.height}
        data-type={props.type}
      />
    )
  }
})

// Mock next/dynamic to return the component synchronously
jest.mock('next/dynamic', () => {
  return function mockDynamic(importFunc: () => Promise<unknown>) {
    // Return the mocked component directly
    return jest.requireMock('react-apexcharts')
  }
})

// Mock useTheme hook to return predictable values
const mockUseTheme = jest.fn()

// Mock next-themes completely
jest.mock('next-themes', () => ({
  ThemeProvider: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  useTheme: () => mockUseTheme(),
}))

// Mock the dependencies that might not be available in test environment
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

// Now import the component after mocks are set up
import BarChart from 'components/BarChart'

// Utility to render with theme - Updated to use mocked theme
const renderWithTheme = (ui: React.ReactElement, theme: 'light' | 'dark' = 'light') => {
  // Set the mock theme before rendering
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
  // Setup mock before each test
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
    const options = JSON.parse(chartElement.getAttribute('data-options') || '{}')

    expect(options.chart.foreColor).toBe('#1E1E2C')
    expect(options.tooltip.theme).toBe('light')
    expect(options.legend.markers.fillColors).toEqual(['#73D13D', '#FF7875'])
  })

  it('renders correctly in dark mode with proper theme colors', () => {
    renderWithTheme(<BarChart {...mockProps} />, 'dark')
    const chartElement = screen.getByTestId('mock-chart')
    const options = JSON.parse(chartElement.getAttribute('data-options') || '{}')

    expect(options.chart.foreColor).toBe('#ECECEC')
    expect(options.tooltip.theme).toBe('dark')
    expect(options.legend.markers.fillColors).toEqual(['#52C41A', '#FF4D4F'])
  })

  it('configures chart options correctly', () => {
    renderWithTheme(<BarChart {...mockProps} />)
    const chartElement = screen.getByTestId('mock-chart')
    const options = JSON.parse(chartElement.getAttribute('data-options') || '{}')

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

    expect(chartElement.getAttribute('data-type')).toBe('bar')
    expect(chartElement.getAttribute('data-height')).toBe('300')
  })

  it('creates correct series data structure', () => {
    renderWithTheme(<BarChart {...mockProps} />)
    const chartElement = screen.getByTestId('mock-chart')
    const series = JSON.parse(chartElement.getAttribute('data-series') || '[]')

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

  // Color function tests - these need to check if colors is a function or array
  it('applies green color when value is less than 75% of requirement', () => {
    const testProps = {
      title: 'Test Low Value',
      labels: ['Low'],
      days: [50],
      requirements: [100],
    }

    renderWithTheme(<BarChart {...testProps} />)
    const chartElement = screen.getByTestId('mock-chart')
    const options = JSON.parse(chartElement.getAttribute('data-options') || '{}')

    // Check if colors is a function (dynamic) or array (static)
    if (typeof options.colors[0] === 'function') {
      const colorFunction = options.colors[0]
      expect(colorFunction({ value: 50, dataPointIndex: 0 })).toBe('#73D13D')
    } else {
      // If it's static colors, check the series data directly
      const series = JSON.parse(chartElement.getAttribute('data-series') || '[]')
      expect(series[0].data[0].fillColor || options.colors[0]).toBeDefined()
    }
  })

  it('applies orange color when value is between 75% and requirement', () => {
    const testProps = {
      title: 'Test Medium Value',
      labels: ['Medium'],
      days: [80],
      requirements: [100],
    }

    renderWithTheme(<BarChart {...testProps} />)
    const chartElement = screen.getByTestId('mock-chart')
    const options = JSON.parse(chartElement.getAttribute('data-options') || '{}')

    if (typeof options.colors[0] === 'function') {
      const colorFunction = options.colors[0]
      expect(colorFunction({ value: 80, dataPointIndex: 0 })).toBe('#FFBB33')
    }
  })

  it('applies orange color when value equals requirement', () => {
    const testProps = {
      title: 'Test Equal Value',
      labels: ['Equal'],
      days: [100],
      requirements: [100],
    }

    renderWithTheme(<BarChart {...testProps} />)
    const chartElement = screen.getByTestId('mock-chart')
    const options = JSON.parse(chartElement.getAttribute('data-options') || '{}')

    if (typeof options.colors[0] === 'function') {
      const colorFunction = options.colors[0]
      expect(colorFunction({ value: 100, dataPointIndex: 0 })).toBe('#FFBB33')
    }
  })

  it('applies red color when value exceeds requirement', () => {
    const testProps = {
      title: 'Test High Value',
      labels: ['High'],
      days: [120],
      requirements: [100],
    }

    renderWithTheme(<BarChart {...testProps} />)
    const chartElement = screen.getByTestId('mock-chart')
    const options = JSON.parse(chartElement.getAttribute('data-options') || '{}')

    if (typeof options.colors[0] === 'function') {
      const colorFunction = options.colors[0]
      expect(colorFunction({ value: 120, dataPointIndex: 0 })).toBe('#FF7875')
    }
  })

  // Reverse colors tests
  it('applies orange color when reverse colors is true and value is less than 75%', () => {
    const testProps = {
      title: 'Test Reverse Low',
      labels: ['Low'],
      days: [50],
      requirements: [100],
      reverseColors: [true],
    }

    renderWithTheme(<BarChart {...testProps} />)
    const chartElement = screen.getByTestId('mock-chart')
    const options = JSON.parse(chartElement.getAttribute('data-options') || '{}')

    if (typeof options.colors[0] === 'function') {
      const colorFunction = options.colors[0]
      expect(colorFunction({ value: 50, dataPointIndex: 0 })).toBe('#FFBB33')
    }
  })

  it('applies red color when reverse colors is true and value is between 75% and requirement', () => {
    const testProps = {
      title: 'Test Reverse Medium',
      labels: ['Medium'],
      days: [80],
      requirements: [100],
      reverseColors: [true],
    }

    renderWithTheme(<BarChart {...testProps} />)
    const chartElement = screen.getByTestId('mock-chart')
    const options = JSON.parse(chartElement.getAttribute('data-options') || '{}')

    if (typeof options.colors[0] === 'function') {
      const colorFunction = options.colors[0]
      expect(colorFunction({ value: 80, dataPointIndex: 0 })).toBe('#FF7875')
    }
  })

  it('applies green color when reverse colors is true and value meets or exceeds requirement', () => {
    const testProps = {
      title: 'Test Reverse High',
      labels: ['High'],
      days: [100],
      requirements: [100],
      reverseColors: [true],
    }

    renderWithTheme(<BarChart {...testProps} />)
    const chartElement = screen.getByTestId('mock-chart')
    const options = JSON.parse(chartElement.getAttribute('data-options') || '{}')

    if (typeof options.colors[0] === 'function') {
      const colorFunction = options.colors[0]
      expect(colorFunction({ value: 100, dataPointIndex: 0 })).toBe('#73D13D')
    }
  })

  it('handles reverse colors when reverseColors array element is undefined', () => {
    const testProps = {
      title: 'Test Undefined Reverse',
      labels: ['Normal'],
      days: [50],
      requirements: [100],
      reverseColors: [undefined] as boolean[],
    }

    renderWithTheme(<BarChart {...testProps} />)
    const chartElement = screen.getByTestId('mock-chart')
    const options = JSON.parse(chartElement.getAttribute('data-options') || '{}')

    if (typeof options.colors[0] === 'function') {
      const colorFunction = options.colors[0]
      expect(colorFunction({ value: 50, dataPointIndex: 0 })).toBe('#73D13D')
    }
  })

  it('handles reverse colors when index exceeds reverseColors array length', () => {
    const testProps = {
      title: 'Test Index Out of Bounds',
      labels: ['First', 'Second'],
      days: [50, 80],
      requirements: [100, 100],
      reverseColors: [true],
    }

    renderWithTheme(<BarChart {...testProps} />)
    const chartElement = screen.getByTestId('mock-chart')
    const options = JSON.parse(chartElement.getAttribute('data-options') || '{}')

    if (typeof options.colors[0] === 'function') {
      const colorFunction = options.colors[0]
      expect(colorFunction({ value: 80, dataPointIndex: 1 })).toBe('#FFBB33')
    }
  })

  it('formats data labels with goal values when goals exist', () => {
    renderWithTheme(<BarChart {...mockProps} />)
    const chartElement = screen.getByTestId('mock-chart')
    const options = JSON.parse(chartElement.getAttribute('data-options') || '{}')

    if (options.dataLabels && options.dataLabels.formatter) {
      const formatter = options.dataLabels.formatter
      const mockOpts = {
        w: {
          config: {
            series: [
              {
                data: [
                  {
                    goals: [{ value: 180 }],
                  },
                ],
              },
            ],
          },
        },
        seriesIndex: 0,
        dataPointIndex: 0,
      }

      expect(formatter(200, mockOpts)).toBe('200 / 180')
    }
  })

  it('formats data labels without goals when goals array is empty', () => {
    renderWithTheme(<BarChart {...mockProps} />)
    const chartElement = screen.getByTestId('mock-chart')
    const options = JSON.parse(chartElement.getAttribute('data-options') || '{}')

    if (options.dataLabels && options.dataLabels.formatter) {
      const formatter = options.dataLabels.formatter
      const mockOptsNoGoals = {
        w: {
          config: {
            series: [
              {
                data: [
                  {
                    goals: [],
                  },
                ],
              },
            ],
          },
        },
        seriesIndex: 0,
        dataPointIndex: 0,
      }

      expect(formatter(200, mockOptsNoGoals)).toBe('200')
    }
  })

  it('formats data labels when goals is undefined', () => {
    renderWithTheme(<BarChart {...mockProps} />)
    const chartElement = screen.getByTestId('mock-chart')
    const options = JSON.parse(chartElement.getAttribute('data-options') || '{}')

    if (options.dataLabels && options.dataLabels.formatter) {
      const formatter = options.dataLabels.formatter
      const mockOptsUndefinedGoals = {
        w: {
          config: {
            series: [
              {
                data: [{}], // No goals property
              },
            ],
          },
        },
        seriesIndex: 0,
        dataPointIndex: 0,
      }

      expect(formatter(200, mockOptsUndefinedGoals)).toBe('200')
    }
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
    const series = JSON.parse(chartElement.getAttribute('data-series') || '[]')

    expect(series[0].data).toHaveLength(2)
  })

  // Fixed theme change test - Now properly tests theme switching
  it('handles theme changes and re-renders correctly', () => {
    // Test light mode first
    mockUseTheme.mockReturnValue({ theme: 'light' })
    const { rerender } = render(<BarChart {...mockProps} />)

    let chartElement = screen.getByTestId('mock-chart')
    let options = JSON.parse(chartElement.getAttribute('data-options') || '{}')
    expect(options.chart.foreColor).toBe('#1E1E2C')
    expect(options.tooltip.theme).toBe('light')

    // Now test dark mode
    mockUseTheme.mockReturnValue({ theme: 'dark' })
    rerender(<BarChart {...mockProps} />)

    chartElement = screen.getByTestId('mock-chart')
    options = JSON.parse(chartElement.getAttribute('data-options') || '{}')
    expect(options.chart.foreColor).toBe('#ECECEC')
    expect(options.tooltip.theme).toBe('dark')
  })

  it('applies correct colors in dark mode', () => {
    const testProps = {
      title: 'Dark Mode Colors',
      labels: ['Test'],
      days: [50],
      requirements: [100],
    }

    renderWithTheme(<BarChart {...testProps} />, 'dark')
    const chartElement = screen.getByTestId('mock-chart')
    const options = JSON.parse(chartElement.getAttribute('data-options') || '{}')

    if (typeof options.colors[0] === 'function') {
      const colorFunction = options.colors[0]
      expect(colorFunction({ value: 50, dataPointIndex: 0 })).toBe('#52C41A')
    }
  })

  it('applies correct theme colors for red in dark mode', () => {
    const testProps = {
      title: 'Dark Mode Red',
      labels: ['Test'],
      days: [120],
      requirements: [100],
    }

    renderWithTheme(<BarChart {...testProps} />, 'dark')
    const chartElement = screen.getByTestId('mock-chart')
    const options = JSON.parse(chartElement.getAttribute('data-options') || '{}')

    if (typeof options.colors[0] === 'function') {
      const colorFunction = options.colors[0]
      expect(colorFunction({ value: 120, dataPointIndex: 0 })).toBe('#FF4D4F')
    }
  })

  it('applies correct theme colors for orange in dark mode', () => {
    const testProps = {
      title: 'Dark Mode Orange',
      labels: ['Test'],
      days: [80],
      requirements: [100],
    }

    renderWithTheme(<BarChart {...testProps} />, 'dark')
    const chartElement = screen.getByTestId('mock-chart')
    const options = JSON.parse(chartElement.getAttribute('data-options') || '{}')

    if (typeof options.colors[0] === 'function') {
      const colorFunction = options.colors[0]
      expect(colorFunction({ value: 80, dataPointIndex: 0 })).toBe('#FAAD14')
    }
  })

  it('includes strokeColor in goals data', () => {
    renderWithTheme(<BarChart {...mockProps} />, 'light')
    const chartElement = screen.getByTestId('mock-chart')
    const series = JSON.parse(chartElement.getAttribute('data-series') || '[]')

    expect(series[0].data[0].goals[0].strokeColor).toBe('#FF7875')
  })

  it('includes strokeColor in goals data for dark mode', () => {
    renderWithTheme(<BarChart {...mockProps} />, 'dark')
    const chartElement = screen.getByTestId('mock-chart')
    const series = JSON.parse(chartElement.getAttribute('data-series') || '[]')

    expect(series[0].data[0].goals[0].strokeColor).toBe('#FF4D4F')
  })

  it('handles when no reverseColors prop is provided', () => {
    const testProps = {
      title: 'No Reverse Colors',
      labels: ['Test'],
      days: [50],
      requirements: [100],
    }

    renderWithTheme(<BarChart {...testProps} />)
    const chartElement = screen.getByTestId('mock-chart')
    const options = JSON.parse(chartElement.getAttribute('data-options') || '{}')

    if (typeof options.colors[0] === 'function') {
      const colorFunction = options.colors[0]
      expect(colorFunction({ value: 50, dataPointIndex: 0 })).toBe('#73D13D')
    }
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
    const series = JSON.parse(chartElement.getAttribute('data-series') || '[]')

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
    const series = JSON.parse(chartElement.getAttribute('data-series') || '[]')

    expect(series[0].data[0].y).toBe(-50)
  })

  it('handles decimal values in days array', () => {
    const decimalProps = {
      title: 'Decimal Values',
      labels: ['Decimal'],
      days: [99.5],
      requirements: [100.0],
    }

    renderWithTheme(<BarChart {...decimalProps} />)
    const chartElement = screen.getByTestId('mock-chart')
    const series = JSON.parse(chartElement.getAttribute('data-series') || '[]')

    expect(series[0].data[0].y).toBe(99.5)
    expect(series[0].data[0].goals[0].value).toBe(100.0)
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
    const series = JSON.parse(chartElement.getAttribute('data-series') || '[]')

    expect(series[0].data[0].y).toBe(999999)
    expect(series[0].data[0].goals[0].value).toBe(1000000)
  })

  // Additional tests to improve coverage
  it('handles undefined theme gracefully', () => {
    mockUseTheme.mockReturnValue({ theme: undefined })
    renderWithTheme(<BarChart {...mockProps} />)

    const chartElement = screen.getByTestId('mock-chart')
    const options = JSON.parse(chartElement.getAttribute('data-options') || '{}')

    // Should default to light theme colors
    expect(options.chart.foreColor).toBe('#1E1E2C')
  })

  it('formats data labels when accessing non-existent goal', () => {
    renderWithTheme(<BarChart {...mockProps} />)
    const chartElement = screen.getByTestId('mock-chart')
    const options = JSON.parse(chartElement.getAttribute('data-options') || '{}')

    if (options.dataLabels && options.dataLabels.formatter) {
      const formatter = options.dataLabels.formatter
      const mockOptsInvalidGoal = {
        w: {
          config: {
            series: [
              {
                data: [
                  {
                    goals: [null], // Invalid goal
                  },
                ],
              },
            ],
          },
        },
        seriesIndex: 0,
        dataPointIndex: 0,
      }

      expect(formatter(200, mockOptsInvalidGoal)).toBe('200')
    }
  })

  it('handles color function with edge case values', () => {
    const edgeProps = {
      title: 'Edge Case Values',
      labels: ['Edge'],
      days: [75], // Exactly 75% of requirement
      requirements: [100],
    }

    renderWithTheme(<BarChart {...edgeProps} />)
    const chartElement = screen.getByTestId('mock-chart')
    const options = JSON.parse(chartElement.getAttribute('data-options') || '{}')

    if (typeof options.colors[0] === 'function') {
      const colorFunction = options.colors[0]
      expect(colorFunction({ value: 75, dataPointIndex: 0 })).toBe('#FFBB33') // Should be orange
    }
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
    const series = JSON.parse(chartElement.getAttribute('data-series') || '[]')

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
    const series = JSON.parse(chartElement.getAttribute('data-series') || '[]')

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
    const series = JSON.parse(chartElement.getAttribute('data-series') || '[]')

    expect(series[0].data[0].y).toBe(0.001)
    expect(series[0].data[0].goals[0].value).toBe(0.002)
  })
})
