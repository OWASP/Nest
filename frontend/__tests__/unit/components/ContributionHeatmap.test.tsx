import { act, render, screen, waitFor, within } from '@testing-library/react'
import type { ApexOptions } from 'apexcharts'
import { ThemeProvider, useTheme } from 'next-themes'
import React from 'react'
import ContributionHeatmap from 'components/ContributionHeatmap'
import '@testing-library/jest-dom'

type HeatmapSeries = Array<{
  name: string
  data: Array<{ x: string; y: number | null; date: string }>
}>

interface MockChartProps {
  options: ApexOptions
  series: HeatmapSeries
  height: string | number
  width: string | number
  type: string
}

const mockChart = jest.fn<void, [MockChartProps]>()

jest.mock('react-apexcharts', () => {
  return function MockChart(props: MockChartProps) {
    mockChart(props)

    return (
      <div
        data-testid="mock-heatmap-chart"
        data-type={props.type}
        data-height={props.height}
        data-series-length={props.series.length}
      >
        {props.series.map((series) => (
          <div key={series.name} data-testid={`series-${series.name}`}>
            {series.name}: {series.data.length} data points
          </div>
        ))}
      </div>
    )
  }
})

jest.mock('next-themes', () => ({
  useTheme: jest.fn(),
  ThemeProvider: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
}))

const renderWithTheme = (ui: React.ReactElement, theme: 'light' | 'dark' = 'light') => {
  ;(useTheme as jest.Mock).mockReturnValue({ theme, setTheme: jest.fn() })
  return render(<ThemeProvider attribute="class">{ui}</ThemeProvider>)
}

/** Read the latest chart configuration instead of relying on mock call ordering. */
const getChartProps = (): MockChartProps => {
  const props = mockChart.mock.lastCall?.[0]
  if (!props) throw new Error('The heatmap chart has not rendered')
  return props
}

/** Exercise the actual tooltip callback with a selected calendar cell. */
const getTooltip = (seriesIndex: number, dataPointIndex: number): string => {
  const { options, series } = getChartProps()
  const custom = options.tooltip?.custom
  if (typeof custom !== 'function') throw new Error('A custom tooltip is required')
  const tooltip = custom({
    series: [],
    seriesIndex,
    dataPointIndex,
    w: { config: { series }, globals: {} },
  })
  if (typeof tooltip !== 'string') throw new Error('The tooltip must return HTML text')
  return tooltip
}

/** Locate a UTC calendar date before invoking its tooltip. */
const getTooltipForDate = (date: string): string => {
  const { series } = getChartProps()
  const seriesIndex = series.findIndex((day) => day.data.some((point) => point.date === date))
  if (seriesIndex < 0) throw new Error(`No calendar cell for ${date}`)
  const dataPointIndex = series[seriesIndex].data.findIndex((point) => point.date === date)
  return getTooltip(seriesIndex, dataPointIndex)
}

/** Supply the public plot geometry reported by ApexCharts after rendering or resizing. */
const updateChartGeometry = (
  width: number,
  height: number,
  cellWidth: number,
  cellHeight: number,
  event: 'mounted' | 'updated' = 'mounted'
) => {
  const { series, options } = getChartProps()
  const handler = options.chart?.events?.[event]
  if (!handler) throw new Error('Calendar geometry must be checked after rendering')
  act(() =>
    Reflect.apply(handler, undefined, [
      {
        getState: () => ({
          svgWidth: width,
          svgHeight: height,
          gridWidth: cellWidth * series[0].data.length,
          gridHeight: cellHeight * series.length,
        }),
      },
    ])
  )
}

describe('ContributionHeatmap', () => {
  const mockData: Record<string, number> = {
    '2024-01-01': 5,
    '2024-01-02': 8,
    '2024-01-03': 12,
    '2024-01-04': 15,
    '2024-01-05': 0,
    '2024-01-08': 3,
    '2024-01-15': 20,
  }
  const defaultProps = {
    contributionData: mockData,
    startDate: '2024-01-01',
    endDate: '2024-01-31',
  }

  beforeEach(() => {
    jest.clearAllMocks()
  })

  describe('Rendering & Props', () => {
    it('renders with minimal and all optional props', async () => {
      const { rerender } = renderWithTheme(<ContributionHeatmap {...defaultProps} />)
      await waitFor(() => expect(screen.getByTestId('mock-heatmap-chart')).toBeInTheDocument())
      expect(screen.queryByRole('heading')).not.toBeInTheDocument()

      rerender(
        <ThemeProvider attribute="class">
          <ContributionHeatmap {...defaultProps} title="Activity" unit="commit" />
        </ThemeProvider>
      )
      expect(screen.getByText('Activity')).toBeInTheDocument()
    })

    it('renders all 7 day series and correct chart type', () => {
      renderWithTheme(<ContributionHeatmap {...defaultProps} />)
      ;['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].forEach((day) =>
        expect(screen.getByTestId(`series-${day}`)).toBeInTheDocument()
      )
      expect(screen.getByTestId('mock-heatmap-chart')).toHaveAttribute('data-type', 'heatmap')
    })

    it('applies custom unit and handles undefined title', () => {
      renderWithTheme(
        <ContributionHeatmap {...defaultProps} unit="pull request" title={undefined} />
      )
      expect(screen.getByTestId('mock-heatmap-chart')).toBeInTheDocument()
      expect(screen.queryByRole('heading')).not.toBeInTheDocument()
    })
  })

  describe('Data Processing & Edge Cases', () => {
    it('handles empty, zero, and high values', () => {
      const testCases = [
        { data: {}, desc: 'empty' },
        { data: { '2024-01-01': 0, '2024-01-02': 0 }, desc: 'zero' },
        { data: { '2024-01-01': 1000, '2024-01-02': 9999 }, desc: 'high' },
      ]
      testCases.forEach(({ data }) => {
        const { unmount } = renderWithTheme(
          <ContributionHeatmap {...defaultProps} contributionData={data} />
        )
        expect(screen.getByTestId('mock-heatmap-chart')).toBeInTheDocument()
        unmount()
      })
    })

    it('handles various date ranges', () => {
      const ranges = [
        { start: '2024-01-01', end: '2024-01-01', data: { '2024-01-01': 5 } },
        { start: '2024-01-25', end: '2024-02-05', data: { '2024-01-25': 5, '2024-02-05': 10 } },
        { start: '2023-12-25', end: '2024-01-05', data: { '2023-12-25': 5, '2024-01-05': 10 } },
      ]
      ranges.forEach(({ start, end, data }) => {
        const { unmount } = renderWithTheme(
          <ContributionHeatmap contributionData={data} startDate={start} endDate={end} />
        )
        expect(screen.getByTestId('mock-heatmap-chart')).toBeInTheDocument()
        unmount()
      })
    })

    it('handles mid-week start and sparse data', () => {
      const props = {
        contributionData: { '2024-01-03': 5, '2024-01-15': 10, '2024-01-31': 3 },
        startDate: '2024-01-03',
        endDate: '2024-01-31',
      }
      renderWithTheme(<ContributionHeatmap {...props} />)
      expect(screen.getByTestId('mock-heatmap-chart')).toBeInTheDocument()
    })

    it('handles large datasets (365 days)', () => {
      const largeData: Record<string, number> = {}
      for (let i = 0; i < 365; i++) {
        const date = new Date('2024-01-01')
        date.setDate(date.getDate() + i)
        largeData[date.toISOString().split('T')[0]] = i % 20
      }
      renderWithTheme(
        <ContributionHeatmap
          contributionData={largeData}
          startDate="2024-01-01"
          endDate="2024-12-31"
        />
      )
      expect(screen.getByTestId('mock-heatmap-chart')).toBeInTheDocument()
    })

    it('handles missing startDate by using default dates', () => {
      renderWithTheme(
        <ContributionHeatmap contributionData={mockData} startDate="" endDate="2024-01-31" />
      )
      expect(screen.getByTestId('mock-heatmap-chart')).toBeInTheDocument()
      // Should render with default date range (1 year)
      expect(screen.getByTestId('mock-heatmap-chart')).toHaveAttribute('data-series-length', '7')
    })

    it('handles missing endDate by using default dates', () => {
      renderWithTheme(
        <ContributionHeatmap contributionData={mockData} startDate="2024-01-01" endDate="" />
      )
      expect(screen.getByTestId('mock-heatmap-chart')).toBeInTheDocument()
      expect(screen.getByTestId('mock-heatmap-chart')).toHaveAttribute('data-series-length', '7')
    })

    it('handles both missing startDate and endDate', () => {
      renderWithTheme(<ContributionHeatmap contributionData={mockData} startDate="" endDate="" />)
      expect(screen.getByTestId('mock-heatmap-chart')).toBeInTheDocument()
    })

    it('handles invalid startDate by using default dates', () => {
      renderWithTheme(
        <ContributionHeatmap
          contributionData={mockData}
          startDate="invalid-date"
          endDate="2024-01-31"
        />
      )
      expect(screen.getByTestId('mock-heatmap-chart')).toBeInTheDocument()
    })

    it('handles invalid endDate by using default dates', () => {
      renderWithTheme(
        <ContributionHeatmap
          contributionData={mockData}
          startDate="2024-01-01"
          endDate="not-a-date"
        />
      )
      expect(screen.getByTestId('mock-heatmap-chart')).toBeInTheDocument()
    })

    it('handles both invalid startDate and endDate', () => {
      renderWithTheme(
        <ContributionHeatmap
          contributionData={mockData}
          startDate="garbage"
          endDate="also-garbage"
        />
      )
      expect(screen.getByTestId('mock-heatmap-chart')).toBeInTheDocument()
    })

    it('handles swapped dates (startDate > endDate) by swapping them', () => {
      renderWithTheme(
        <ContributionHeatmap
          contributionData={mockData}
          startDate="2024-01-31"
          endDate="2024-01-01"
        />
      )
      expect(screen.getByTestId('mock-heatmap-chart')).toBeInTheDocument()
      expect(screen.getByTestId('mock-heatmap-chart')).toHaveAttribute('data-series-length', '7')
    })

    it('handles startDate after endDate and swaps them correctly', () => {
      const data = {
        '2024-01-15': 5,
        '2024-01-20': 10,
      }
      renderWithTheme(
        <ContributionHeatmap contributionData={data} startDate="2024-02-01" endDate="2024-01-01" />
      )
      expect(screen.getByTestId('mock-heatmap-chart')).toBeInTheDocument()
    })
  })

  describe('Theme & Styling', () => {
    it.each([
      ['light', 'dark'],
      ['dark', 'light'],
    ] as const)(
      'keeps repeated month labels stationary when switching %s to %s',
      async (from, to) => {
        const heatmapProps = {
          contributionData: { '2026-10-01': 5 },
          startDate: '2025-10-19',
          endDate: '2026-10-17',
        }
        const { rerender } = renderWithTheme(<ContributionHeatmap {...heatmapProps} />, from)
        await waitFor(() => expect(mockChart).toHaveBeenCalled())
        const originalSeries = getChartProps().series
        const originalChart = screen.getByTestId('mock-heatmap-chart')

        ;(useTheme as jest.Mock).mockReturnValue({ theme: to, setTheme: jest.fn() })
        rerender(
          <ThemeProvider attribute="class">
            <ContributionHeatmap {...heatmapProps} />
          </ThemeProvider>
        )

        const { options, series } = getChartProps()
        expect(series).toBe(originalSeries)
        expect(screen.getByTestId('mock-heatmap-chart')).toBe(originalChart)
        const monthLabels = series[0].data.map(({ x }) => options.xaxis?.labels?.formatter?.(x))
        expect(monthLabels.filter((label) => label === 'Oct')).toHaveLength(2)
        expect(options.chart?.animations?.dynamicAnimation?.enabled).toBe(false)
        expect(options.chart?.animations?.enabled).not.toBe(false)
        expect(options.stroke?.colors).toEqual([to === 'dark' ? '#1F2937' : '#FFFFFF'])
      }
    )

    it('renders in light and dark mode with correct classes', () => {
      const { rerender } = renderWithTheme(
        <ContributionHeatmap {...defaultProps} title="Light" />,
        'light'
      )
      expect(screen.getByText('Light').parentElement).toHaveClass('w-full')
      ;(useTheme as jest.Mock).mockReturnValue({ theme: 'dark', setTheme: jest.fn() })
      rerender(
        <ThemeProvider attribute="class">
          <ContributionHeatmap {...defaultProps} title="Dark" />
        </ThemeProvider>
      )
      expect(screen.getByText('Dark').parentElement).toHaveClass('w-full')
    })

    it('applies correct container and style classes', () => {
      const { container } = renderWithTheme(<ContributionHeatmap {...defaultProps} title="Test" />)
      expect(container.querySelector('.w-full')).toBeInTheDocument()
      expect(container.querySelector('style')).toBeInTheDocument()
    })

    it('includes responsive media queries', () => {
      const { container } = renderWithTheme(<ContributionHeatmap {...defaultProps} />)
      const styleContent = container.querySelector('style')?.textContent
      expect(styleContent).toContain('apexcharts-tooltip')
    })
  })

  describe('Content & Accessibility', () => {
    it('renders title with correct styling and semantic HTML', () => {
      const { container } = renderWithTheme(
        <ContributionHeatmap {...defaultProps} title="Activity" />
      )
      const title = screen.getByText('Activity')
      expect(title).toHaveClass('font-semibold')
      expect(title.parentElement).toHaveClass('w-full')
      expect(container.querySelector('h3')).toBeInTheDocument()
    })

    it('has accessible heading structure', () => {
      renderWithTheme(<ContributionHeatmap {...defaultProps} title="Accessible" />)
      expect(screen.getByRole('heading', { level: 3 })).toHaveTextContent('Accessible')
    })
  })

  describe('Chart Configuration & Performance', () => {
    it('sets correct dimensions and series count', () => {
      renderWithTheme(<ContributionHeatmap {...defaultProps} />)
      const chart = screen.getByTestId('mock-heatmap-chart')
      expect(chart).toHaveAttribute('data-height', '195')
      expect(chart).toHaveAttribute('data-series-length', '7')
    })

    it('re-renders correctly when props change', () => {
      const { rerender } = renderWithTheme(<ContributionHeatmap {...defaultProps} />)
      const newProps = {
        contributionData: { '2024-02-01': 10 },
        startDate: '2024-02-01',
        endDate: '2024-02-28',
      }
      rerender(
        <ThemeProvider attribute="class">
          <ContributionHeatmap {...newProps} />
        </ThemeProvider>
      )
      expect(screen.getByTestId('mock-heatmap-chart')).toBeInTheDocument()
    })

    it('handles dynamic import with SSR disabled', async () => {
      renderWithTheme(<ContributionHeatmap {...defaultProps} />)
      await waitFor(() => expect(screen.getByTestId('mock-heatmap-chart')).toBeInTheDocument())
    })
  })

  describe('Tooltip Behavior', () => {
    it('generates correct tooltip with date formatting', () => {
      renderWithTheme(<ContributionHeatmap {...defaultProps} />)

      const tooltip = document.createElement('div')
      tooltip.innerHTML = getTooltipForDate('2024-01-01')
      expect(tooltip).toHaveTextContent('Jan 1, 2024')
      expect(tooltip).not.toHaveTextContent('Mon,')
      expect(tooltip).toHaveTextContent('5 contributions')
    })

    it.each([
      { unit: 'commit', count: 1, expected: '1 commit' },
      { unit: 'commit', count: 5, expected: '5 commits' },
      { unit: 'message', count: 1, expected: '1 message' },
      { unit: 'message', count: 5, expected: '5 messages' },
    ])('formats $expected in the tooltip', ({ unit, count, expected }) => {
      renderWithTheme(
        <ContributionHeatmap
          {...defaultProps}
          contributionData={{ '2024-01-01': count }}
          unit={unit}
        />
      )

      const tooltip = document.createElement('div')
      tooltip.innerHTML = getTooltipForDate('2024-01-01')
      expect(tooltip).toHaveTextContent(expected)
    })

    it('tooltip respects theme colors', () => {
      const { rerender } = renderWithTheme(<ContributionHeatmap {...defaultProps} />, 'light')
      expect(getTooltipForDate('2024-01-01')).toContain('background: #FFFFFF')
      ;(useTheme as jest.Mock).mockReturnValue({ theme: 'dark', setTheme: jest.fn() })
      rerender(
        <ThemeProvider attribute="class">
          <ContributionHeatmap {...defaultProps} />
        </ThemeProvider>
      )
      expect(getTooltipForDate('2024-01-01')).toContain('background: #1F2937')
    })

    it('handles missing data in tooltip gracefully', () => {
      renderWithTheme(
        <ContributionHeatmap contributionData={{}} startDate="2024-01-01" endDate="2024-01-31" />
      )
      expect(getTooltip(0, 999)).toBe('')
    })

    it('suppresses padding tooltips while retaining tooltips for zero-activity days', async () => {
      renderWithTheme(
        <ContributionHeatmap contributionData={{}} startDate="2024-01-03" endDate="2024-01-10" />
      )

      await waitFor(() => expect(mockChart).toHaveBeenCalled())
      expect(getTooltipForDate('2024-01-01')).toBe('')
      expect(getTooltipForDate('2024-01-14')).toBe('')
      expect(getTooltipForDate('2024-01-04')).toContain('0 contributions')
    })
  })

  describe('Week Number Calculation', () => {
    it('aligns every weekday row across complete week columns', async () => {
      renderWithTheme(
        <ContributionHeatmap
          contributionData={{ '2024-01-03': 5, '2024-01-10': 2 }}
          startDate="2024-01-03"
          endDate="2024-01-10"
        />
      )

      await waitFor(() => expect(mockChart).toHaveBeenCalled())
      expect(getChartProps().series.map((day) => day.data.length)).toEqual([2, 2, 2, 2, 2, 2, 2])
    })

    it('correctly calculates week numbers starting from Monday', () => {
      const data = {
        '2024-01-01': 5,
        '2024-01-08': 10,
      }
      renderWithTheme(
        <ContributionHeatmap contributionData={data} startDate="2024-01-01" endDate="2024-01-14" />
      )
      const { series } = getChartProps()
      const monday = series.find((day) => day.name === 'Mon')
      expect(monday?.data.map(({ date, y }) => ({ date, y }))).toEqual([
        { y: 5, date: '2024-01-01' },
        { y: 10, date: '2024-01-08' },
      ])
    })

    it('handles week transitions correctly', () => {
      const data = {
        '2024-01-07': 5,
        '2024-01-08': 10,
      }
      renderWithTheme(
        <ContributionHeatmap contributionData={data} startDate="2024-01-07" endDate="2024-01-14" />
      )
      const cells = getChartProps().series.flatMap((day) => day.data)
      const sunday = cells.find((point) => point.date === '2024-01-07')
      const monday = cells.find((point) => point.date === '2024-01-08')
      expect(sunday?.y).toBe(5)
      expect(monday?.y).toBe(10)
      expect(sunday?.x).not.toBe(monday?.x)
    })
  })

  describe('Color Scale Logic', () => {
    it('applies correct color ranges for different activity levels', () => {
      const activityData = {
        '2024-01-01': 0,
        '2024-01-02': 2,
        '2024-01-03': 6,
        '2024-01-04': 10,
        '2024-01-05': 15,
      }
      renderWithTheme(
        <ContributionHeatmap
          contributionData={activityData}
          startDate="2024-01-01"
          endDate="2024-01-31"
        />
      )
      expect(screen.getByTestId('mock-heatmap-chart')).toBeInTheDocument()
    })

    it('handles boundary values in color ranges', () => {
      const boundaryData = {
        '2024-01-01': 0,
        '2024-01-02': 1,
        '2024-01-03': 4,
        '2024-01-04': 5,
        '2024-01-05': 8,
        '2024-01-06': 9,
        '2024-01-07': 12,
        '2024-01-08': 13,
        '2024-01-09': 1000,
      }
      renderWithTheme(
        <ContributionHeatmap
          contributionData={boundaryData}
          startDate="2024-01-01"
          endDate="2024-01-31"
        />
      )
      const { options, series } = getChartProps()
      const cells = series.flatMap((day) => day.data)
      const ranges = options.plotOptions?.heatmap?.colorScale?.ranges
      const expectedBands = [
        'No activity',
        'Low',
        'Low',
        'Medium',
        'Medium',
        'High',
        'High',
        'Very High',
        'Very High',
      ]

      Object.entries(boundaryData).forEach(([date, count], index) => {
        expect(cells.find((point) => point.date === date)?.y).toBe(count)
        expect(ranges?.find((range) => range.from <= count && count <= range.to)?.name).toBe(
          expectedBands[index]
        )
      })
    })
  })

  describe('Date Range Edge Cases', () => {
    it('handles leap year dates', () => {
      const leapYearData = {
        '2024-02-28': 5,
        '2024-02-29': 10,
        '2024-03-01': 3,
      }
      renderWithTheme(
        <ContributionHeatmap
          contributionData={leapYearData}
          startDate="2024-02-28"
          endDate="2024-03-01"
        />
      )
      expect(screen.getByTestId('mock-heatmap-chart')).toBeInTheDocument()
    })

    it('handles year boundaries correctly', () => {
      const yearBoundaryData = {
        '2023-12-30': 5,
        '2023-12-31': 10,
        '2024-01-01': 8,
        '2024-01-02': 12,
      }
      renderWithTheme(
        <ContributionHeatmap
          contributionData={yearBoundaryData}
          startDate="2023-12-30"
          endDate="2024-01-02"
        />
      )
      expect(screen.getByTestId('mock-heatmap-chart')).toBeInTheDocument()
    })

    it('handles dates in reverse chronological order in data object', () => {
      const reversedData: Record<string, number> = {}
      for (let i = 30; i >= 1; i--) {
        const date = new Date('2024-01-01')
        date.setDate(date.getDate() + i - 1)
        reversedData[date.toISOString().split('T')[0]] = i
      }
      renderWithTheme(
        <ContributionHeatmap
          contributionData={reversedData}
          startDate="2024-01-01"
          endDate="2024-01-31"
        />
      )
      expect(screen.getByTestId('mock-heatmap-chart')).toBeInTheDocument()
    })
  })

  describe('Extreme Values & Data Quality', () => {
    it('handles negative contribution values gracefully', () => {
      const negativeData = {
        '2024-01-01': -5,
        '2024-01-02': 10,
      }
      renderWithTheme(
        <ContributionHeatmap
          contributionData={negativeData}
          startDate="2024-01-01"
          endDate="2024-01-31"
        />
      )
      expect(screen.getByTestId('mock-heatmap-chart')).toBeInTheDocument()
    })

    it('handles floating point contribution values', () => {
      const floatData = {
        '2024-01-01': 5.5,
        '2024-01-02': 10.99,
      }
      renderWithTheme(
        <ContributionHeatmap
          contributionData={floatData}
          startDate="2024-01-01"
          endDate="2024-01-31"
        />
      )
      expect(screen.getByTestId('mock-heatmap-chart')).toBeInTheDocument()
    })

    it('handles extremely large contribution counts', () => {
      const extremeData = {
        '2024-01-01': 999999,
        '2024-01-02': 1000000,
      }
      renderWithTheme(
        <ContributionHeatmap
          contributionData={extremeData}
          startDate="2024-01-01"
          endDate="2024-01-31"
        />
      )
      expect(screen.getByTestId('mock-heatmap-chart')).toBeInTheDocument()
    })
  })

  describe('Component State & Lifecycle', () => {
    it('maintains consistent rendering across multiple updates', () => {
      const { rerender } = renderWithTheme(<ContributionHeatmap {...defaultProps} />)

      for (let i = 0; i < 5; i++) {
        const newData = { [`2024-01-${i + 1}`]: i * 5 }
        rerender(
          <ThemeProvider attribute="class">
            <ContributionHeatmap
              contributionData={newData}
              startDate="2024-01-01"
              endDate="2024-01-31"
            />
          </ThemeProvider>
        )
      }

      expect(screen.getByTestId('mock-heatmap-chart')).toBeInTheDocument()
    })

    it('handles unmounting and remounting', () => {
      const { unmount } = renderWithTheme(<ContributionHeatmap {...defaultProps} />)
      unmount()
      renderWithTheme(<ContributionHeatmap {...defaultProps} />)
      expect(screen.getByTestId('mock-heatmap-chart')).toBeInTheDocument()
    })
  })

  describe('String Formatting & Localization', () => {
    it('formats date strings correctly in different formats', () => {
      const dateFormatData = {
        '2024-01-01': 5,
        '2024-1-2': 10,
      }
      renderWithTheme(
        <ContributionHeatmap
          contributionData={dateFormatData}
          startDate="2024-01-01"
          endDate="2024-01-31"
        />
      )
      expect(screen.getByTestId('mock-heatmap-chart')).toBeInTheDocument()
    })

    it('handles custom unit strings with special characters', () => {
      const { unmount } = renderWithTheme(
        <ContributionHeatmap {...defaultProps} unit="pull-request" />
      )
      expect(screen.getByTestId('mock-heatmap-chart')).toBeInTheDocument()
      unmount()

      const { rerender } = renderWithTheme(<ContributionHeatmap {...defaultProps} unit="PR's" />)
      expect(screen.getByTestId('mock-heatmap-chart')).toBeInTheDocument()

      rerender(
        <ThemeProvider attribute="class">
          <ContributionHeatmap {...defaultProps} unit="contribution/day" />
        </ThemeProvider>
      )
      expect(screen.getByTestId('mock-heatmap-chart')).toBeInTheDocument()
    })
  })

  describe('Chart Options Validation', () => {
    it('configures chart with correct options structure', () => {
      renderWithTheme(<ContributionHeatmap {...defaultProps} />)
      expect(getChartProps().options).toMatchObject({
        chart: { type: 'heatmap', toolbar: { show: false } },
        dataLabels: { enabled: false },
        tooltip: { enabled: true },
        stroke: { show: true },
      })
    })

    it('renders heatmap chart', () => {
      renderWithTheme(<ContributionHeatmap {...defaultProps} />)
      expect(screen.getByTestId('mock-heatmap-chart')).toBeInTheDocument()
    })
  })

  describe('Calendar readability regressions (#5742)', () => {
    it('shows a month label above the calendar', async () => {
      renderWithTheme(<ContributionHeatmap {...defaultProps} />)
      await waitFor(() => expect(mockChart).toHaveBeenCalled())
      const { options, series } = getChartProps()
      expect(options.xaxis?.labels?.show).toBe(true)
      expect(options.xaxis?.labels?.formatter?.(series[0].data[0].x)).toBe('Jan')
    })

    it('shows selected weekday labels beside the calendar', async () => {
      renderWithTheme(<ContributionHeatmap {...defaultProps} />)
      await waitFor(() => expect(mockChart).toHaveBeenCalled())
      const { options } = getChartProps()
      const yaxis = Array.isArray(options.yaxis) ? options.yaxis[0] : options.yaxis
      expect(yaxis?.labels?.show).toBe(true)
      const formatter = yaxis?.labels?.formatter
      if (!formatter) throw new Error('Weekday labels need a formatter')
      expect(
        ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].map((day) =>
          Reflect.apply(formatter, undefined, [day])
        )
      ).toEqual(['Mon', '', 'Wed', '', 'Fri', '', ''])
    })

    it('explains the color scale with a Less to More legend', async () => {
      renderWithTheme(<ContributionHeatmap {...defaultProps} />)
      await waitFor(() => expect(mockChart).toHaveBeenCalled())
      expect(screen.getByText('Less')).toBeVisible()
      expect(screen.getByText('More')).toBeVisible()
    })

    it('shows the displayed period with its year', async () => {
      renderWithTheme(<ContributionHeatmap {...defaultProps} />)
      await waitFor(() => expect(mockChart).toHaveBeenCalled())
      expect(screen.getByText('Jan 1 — 31, 2024')).toBeVisible()
    })

    it('uses the normalized calendar bounds for the displayed period', async () => {
      renderWithTheme(
        <ContributionHeatmap
          {...defaultProps}
          startDate="2024-02-01T00:30:00+02:00"
          endDate="2023-12-31T23:30:00-02:00"
        />
      )
      await waitFor(() => expect(mockChart).toHaveBeenCalled())
      expect(screen.getByText('Jan 1 — 31, 2024')).toBeVisible()
    })

    it('includes the year in hover dates', async () => {
      renderWithTheme(<ContributionHeatmap {...defaultProps} />)
      await waitFor(() => expect(mockChart).toHaveBeenCalled())
      const tooltip = document.createElement('div')
      tooltip.innerHTML = getTooltipForDate('2024-01-01')
      expect(tooltip).toHaveTextContent('Jan 1, 2024')
      expect(tooltip).not.toHaveTextContent('Mon,')
    })

    it('uses the highest activity band for counts above 1000', async () => {
      renderWithTheme(
        <ContributionHeatmap
          {...defaultProps}
          contributionData={{ '2024-01-01': 1001, '2024-01-02': 1000000 }}
        />
      )
      await waitFor(() => expect(mockChart).toHaveBeenCalled())
      const ranges = getChartProps().options.plotOptions?.heatmap?.colorScale?.ranges
      for (const count of [13, 1000, 1001, 1000000, Number.MAX_SAFE_INTEGER]) {
        expect(ranges?.find((range) => range.from <= count && count <= range.to)?.name).toBe(
          'Very High'
        )
      }
    })

    it.each(['light', 'dark'] as const)(
      'matches the %s legend to the chart colors',
      async (theme) => {
        renderWithTheme(<ContributionHeatmap {...defaultProps} unit="message" />, theme)
        await waitFor(() => expect(mockChart).toHaveBeenCalled())
        const legend = screen.getByRole('list', { name: 'Daily message counts, from less to more' })
        const items = within(legend).getAllByRole('listitem')
        const ranges = getChartProps().options.plotOptions?.heatmap?.colorScale?.ranges

        expect(items).toHaveLength(5)
        expect(ranges?.map((range) => range.color)).toEqual(
          theme === 'dark'
            ? ['#2C3A4D', '#4A5F7A', '#5A6F8A', '#6A7F9A', '#7A8FAA']
            : ['#E7E7E6', '#7BA3C0', '#6C8EAB', '#5C7BA2', '#567498']
        )
        items.forEach((item, index) => {
          expect(item.querySelector('[aria-hidden="true"]')).toHaveStyle({
            backgroundColor: ranges?.[index].color,
          })
        })
        expect(items.map((item) => item.textContent)).toEqual([
          '0 messages per day',
          '1–4 messages per day',
          '5–8 messages per day',
          '9–12 messages per day',
          '13+ messages per day',
        ])
      }
    )
  })

  describe('Responsive Design', () => {
    it('applies responsive container classes', () => {
      const { container } = renderWithTheme(<ContributionHeatmap {...defaultProps} />)
      const heatmapContainer = container.querySelector('.w-full')
      expect(heatmapContainer).toBeInTheDocument()
    })

    it('includes tooltip styling in the responsive container', () => {
      const { container } = renderWithTheme(<ContributionHeatmap {...defaultProps} />)
      const styleContent = container.querySelector('style')?.textContent
      expect(styleContent).toContain('apexcharts-tooltip')
    })
  })

  describe('Integration & Real-world Scenarios', () => {
    it('renders complete heatmap with realistic GitHub contribution data', () => {
      const githubLikeData: Record<string, number> = {
        '2024-01-01': 5,
        '2024-01-03': 12,
        '2024-01-05': 3,
        '2024-01-08': 8,
        '2024-01-10': 15,
        '2024-01-12': 7,
        '2024-01-15': 20,
        '2024-01-18': 4,
        '2024-01-20': 9,
        '2024-01-22': 11,
        '2024-01-25': 6,
        '2024-01-28': 13,
      }
      renderWithTheme(
        <ContributionHeatmap
          contributionData={githubLikeData}
          startDate="2024-01-01"
          endDate="2024-01-31"
          title="GitHub Contributions"
          unit="commit"
        />
      )

      expect(screen.getByText('GitHub Contributions')).toBeInTheDocument()
      expect(screen.getByTestId('mock-heatmap-chart')).toBeInTheDocument()
      ;['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].forEach((day) =>
        expect(screen.getByTestId(`series-${day}`)).toBeInTheDocument()
      )
    })

    it('handles complete absence of data gracefully', () => {
      renderWithTheme(
        <ContributionHeatmap
          contributionData={{}}
          startDate="2024-01-01"
          endDate="2024-12-31"
          title="No Activity"
        />
      )

      expect(screen.getByText('No Activity')).toBeInTheDocument()
      expect(screen.getByTestId('mock-heatmap-chart')).toBeInTheDocument()
    })

    it('renders correctly with all edge cases combined', () => {
      const complexData: Record<string, number> = {
        '2024-02-29': 100,
        '2024-12-31': 50,
        '2024-01-01': 0,
        '2024-06-15': 1,
      }

      renderWithTheme(
        <ContributionHeatmap
          contributionData={complexData}
          startDate="2024-01-01"
          endDate="2024-12-31"
          title="Year Overview"
          unit="contribution"
        />
      )

      expect(screen.getByTestId('mock-heatmap-chart')).toBeInTheDocument()
    })
  })

  describe('Square cell layout', () => {
    const yearProps = { contributionData: {}, startDate: '2025-10-19', endDate: '2026-10-17' }

    it.each([
      { variant: 'default' as const, height: 195, maxWidth: 1031 },
      { variant: 'medium' as const, height: 172, maxWidth: 857 },
      { variant: 'compact' as const, height: 150, maxWidth: 691 },
    ])(
      'fits square cells within the $variant height budget',
      async ({ variant, height, maxWidth }) => {
        renderWithTheme(<ContributionHeatmap {...yearProps} variant={variant} />)
        await waitFor(() => expect(mockChart).toHaveBeenCalled())
        updateChartGeometry(570, height, 10, (height - 64) / 7)

        expect(getChartProps().height).toBe(134)
        expect(screen.getByTestId('mock-heatmap-chart').parentElement).toHaveStyle({
          maxWidth: `${maxWidth}px`,
        })
      }
    )

    it('limits short calendars instead of stretching their cells across the whole container', async () => {
      renderWithTheme(<ContributionHeatmap {...defaultProps} />)
      await waitFor(() => expect(mockChart).toHaveBeenCalled())
      updateChartGeometry(600, 195, 112, (195 - 64) / 7)

      expect(getChartProps().height).toBe(195)
      expect(screen.getByTestId('mock-heatmap-chart').parentElement).toHaveStyle({
        minWidth: '133px',
        maxWidth: '133px',
      })
    })

    it('keeps a single-week calendar square without exceeding its height budget', async () => {
      renderWithTheme(<ContributionHeatmap {...defaultProps} endDate="2024-01-07" />)
      await waitFor(() => expect(mockChart).toHaveBeenCalled())
      updateChartGeometry(600, 195, 560, (195 - 64) / 7)
      updateChartGeometry(58, 195, 18, (195 - 64) / 7, 'updated')

      expect(getChartProps().height).toBe(190)
      expect(screen.getByTestId('mock-heatmap-chart').parentElement).toHaveStyle({
        minWidth: '58px',
        maxWidth: '58px',
      })
    })

    it('refits resized charts and stops updating once their geometry is stable', async () => {
      renderWithTheme(<ContributionHeatmap {...yearProps} variant="medium" />)
      await waitFor(() => expect(mockChart).toHaveBeenCalled())
      updateChartGeometry(570, 172, 10, (172 - 64) / 7)
      updateChartGeometry(800, 134, (800 - 40) / 53, 10, 'updated')
      expect(getChartProps().height).toBe(164)

      const calls = mockChart.mock.calls.length
      updateChartGeometry(800, 164, (800 - 40) / 53, (164 - 64) / 7, 'updated')
      expect(mockChart).toHaveBeenCalledTimes(calls)
    })

    it('refits container resizes even when ApexCharts does not emit an update event', async () => {
      let onResize: ConstructorParameters<typeof globalThis.ResizeObserver>[0] | undefined
      const observe = jest.fn()
      const disconnect = jest.fn()
      const observer = jest.spyOn(globalThis, 'ResizeObserver').mockImplementation((callback) => {
        onResize = callback
        return { observe, disconnect, unobserve: jest.fn() }
      })
      try {
        const { unmount } = renderWithTheme(<ContributionHeatmap {...yearProps} variant="medium" />)
        await waitFor(() => expect(mockChart).toHaveBeenCalled())
        const handleResize = onResize
        if (!handleResize) throw new Error('The chart must observe container width changes')
        act(() => Reflect.apply(handleResize, undefined, []))
        updateChartGeometry(570, 172, 10, (172 - 64) / 7)

        const container = screen.getByTestId('mock-heatmap-chart').parentElement
        if (!container) throw new Error('The chart needs a sizing container')
        jest.spyOn(container, 'getBoundingClientRect').mockReturnValue(new DOMRect(0, 0, 854, 134))
        act(() => Reflect.apply(handleResize, undefined, []))
        expect(getChartProps().height).toBe(172)
        expect(observe).toHaveBeenCalledWith(container)

        unmount()
        expect(disconnect).toHaveBeenCalledTimes(1)
      } finally {
        observer.mockRestore()
      }
    })

    it.each([0, Number.NaN])('waits for usable SVG dimensions (%s)', async (width) => {
      renderWithTheme(<ContributionHeatmap {...yearProps} />)
      await waitFor(() => expect(mockChart).toHaveBeenCalled())
      updateChartGeometry(width, 195, width, 18)
      expect(getChartProps().height).toBe(195)
    })
  })

  describe('Variants', () => {
    it.each([
      { variant: 'default' as const, minWidth: 600 },
      { variant: 'medium' as const, minWidth: 500 },
      { variant: 'compact' as const, minWidth: 400 },
    ])(
      'starts with the $variant baseline width before measuring the plot',
      async ({ variant, minWidth }) => {
        renderWithTheme(<ContributionHeatmap {...defaultProps} variant={variant} />)

        await waitFor(() => expect(mockChart).toHaveBeenCalled())
        expect(screen.getByTestId('mock-heatmap-chart').parentElement).toHaveStyle({
          width: '100%',
          minWidth: `${minWidth}px`,
        })
      }
    )

    it.each([
      { variant: 'default' as const, minWidth: 600 },
      { variant: 'medium' as const, minWidth: 570 },
      { variant: 'compact' as const, minWidth: 570 },
    ])(
      'fits the $variant chart to its container while retaining 53 readable columns',
      async ({ variant, minWidth }) => {
        renderWithTheme(
          <ContributionHeatmap
            contributionData={{}}
            startDate="2025-10-19"
            endDate="2026-10-17"
            variant={variant}
          />
        )

        await waitFor(() => expect(mockChart).toHaveBeenCalled())
        expect(getChartProps().width).toBe('100%')
        expect(screen.getByTestId('mock-heatmap-chart').parentElement).toHaveStyle({
          width: '100%',
          minWidth: `${minWidth}px`,
        })
        expect(getChartProps().series.map((day) => day.data.length)).toEqual([
          53, 53, 53, 53, 53, 53, 53,
        ])
      }
    )

    it.each([
      { variant: 'default' as const, height: '195' },
      { variant: 'medium' as const, height: '172' },
      { variant: 'compact' as const, height: '150' },
    ])('starts the $variant variant at its height budget', ({ variant, height }) => {
      renderWithTheme(<ContributionHeatmap {...defaultProps} variant={variant} />)
      const chart = screen.getByTestId('mock-heatmap-chart')
      expect(chart).toHaveAttribute('data-height', height)
    })

    it('applies compact-specific container styling when variant is compact', () => {
      const { container } = renderWithTheme(
        <ContributionHeatmap {...defaultProps} title="Compact" variant="compact" />
      )
      expect(container.querySelector('.scrollbar-default > div')).toHaveStyle({ minWidth: '400px' })
    })

    it('applies default variant container styling when variant is default', () => {
      const { container } = renderWithTheme(
        <ContributionHeatmap {...defaultProps} title="Default" variant="default" />
      )
      expect(container.querySelector('.scrollbar-default > div')).toHaveStyle({ minWidth: '600px' })
    })

    it('applies medium variant container styling', () => {
      const { container } = renderWithTheme(
        <ContributionHeatmap {...defaultProps} title="Medium" variant="medium" />
      )
      expect(container.querySelector('.scrollbar-default > div')).toHaveStyle({ minWidth: '500px' })
    })

    it('defaults to default variant when no variant is specified', () => {
      renderWithTheme(<ContributionHeatmap {...defaultProps} />)
      const chart = screen.getByTestId('mock-heatmap-chart')
      // Should render with default variant dimensions
      expect(chart).toHaveAttribute('data-height', '195')
    })

    it('renders title with same styling regardless of variant', () => {
      const { rerender } = renderWithTheme(
        <ContributionHeatmap {...defaultProps} title="Test Title" variant="default" />
      )
      let title = screen.getByText('Test Title')
      expect(title).toHaveClass('mb-4', 'text-sm', 'font-semibold')

      rerender(
        <ThemeProvider attribute="class">
          <ContributionHeatmap {...defaultProps} title="Test Title" variant="medium" />
        </ThemeProvider>
      )
      title = screen.getByText('Test Title')
      expect(title).toHaveClass('mb-4', 'text-sm', 'font-semibold')
    })
  })
})
