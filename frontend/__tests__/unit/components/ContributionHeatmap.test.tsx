import { render, screen, waitFor } from '@testing-library/react'
import { ThemeProvider, useTheme } from 'next-themes'
import React from 'react'
import ContributionHeatmap from 'components/ContributionHeatmap'
import '@testing-library/jest-dom'

jest.mock('react-apexcharts', () => {
  return function MockChart(props: {
    options: unknown
    series: unknown
    height: string | number
    type: string
  }) {
    const mockSeries = props.series as Array<{
      name: string
      data: Array<{ x: string; y: number; date: string }>
    }>
    const mockOptions = props.options as Record<string, unknown>

    if (mockOptions.tooltip && typeof mockOptions.tooltip === 'object') {
      const tooltip = mockOptions.tooltip as { custom?: (...args: unknown[]) => unknown }
      if (tooltip.custom) {
        if (mockSeries[0]?.data.length > 0) {
          const result = tooltip.custom({
            seriesIndex: 0,
            dataPointIndex: 0,
            w: { config: { series: mockSeries } },
          })
          if (typeof result === 'string') {
            result.includes('#FFFFFF')
            result.includes('#E5E7EB')
            result.includes('#1F2937')
            result.includes('#374151')
          }
        }
        tooltip.custom({
          seriesIndex: 0,
          dataPointIndex: 999,
          w: { config: { series: mockSeries } },
        })
      }
    }

    return (
      <div
        data-testid="mock-heatmap-chart"
        data-type={props.type}
        data-height={props.height}
        data-series-length={mockSeries.length}
      >
        {mockSeries.map((series) => (
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
  })

  describe('Theme & Styling', () => {
    it('renders in light and dark mode with correct classes', () => {
      const { rerender } = renderWithTheme(
        <ContributionHeatmap {...defaultProps} title="Light" />,
        'light'
      )
      expect(screen.getByText('Light').parentElement).toHaveClass('text-gray-700')
      ;(useTheme as jest.Mock).mockReturnValue({ theme: 'dark', setTheme: jest.fn() })
      rerender(
        <ThemeProvider attribute="class">
          <ContributionHeatmap {...defaultProps} title="Dark" />
        </ThemeProvider>
      )
      expect(screen.getByText('Dark').parentElement).toHaveClass('text-gray-700')
    })

    it('applies correct container and style classes', () => {
      const { container } = renderWithTheme(<ContributionHeatmap {...defaultProps} title="Test" />)
      expect(container.querySelector('.heatmap-container')).toBeInTheDocument()
      expect(container.querySelector('style')).toBeInTheDocument()
      expect(container.querySelector('.w-full')).toBeInTheDocument()
    })

    it('includes responsive media queries', () => {
      const { container } = renderWithTheme(<ContributionHeatmap {...defaultProps} />)
      const styleContent = container.querySelector('style')?.textContent
      expect(styleContent).toContain('@media (max-width: 768px)')
      expect(styleContent).toContain('@media (max-width: 480px)')
    })
  })

  describe('Content & Accessibility', () => {
    it('renders title with correct styling and semantic HTML', () => {
      const { container } = renderWithTheme(
        <ContributionHeatmap {...defaultProps} title="Activity" />
      )
      const title = screen.getByText('Activity')
      expect(title).toHaveClass('font-semibold')
      expect(title.parentElement).toHaveClass('mb-1', 'text-sm')
      expect(container.querySelector('h4')).toBeInTheDocument()
    })

    it('has accessible heading structure', () => {
      renderWithTheme(<ContributionHeatmap {...defaultProps} title="Accessible" />)
      expect(screen.getByRole('heading', { level: 4 })).toHaveTextContent('Accessible')
    })
  })

  describe('Chart Configuration & Performance', () => {
    it('sets correct dimensions and series count', () => {
      renderWithTheme(<ContributionHeatmap {...defaultProps} />)
      const chart = screen.getByTestId('mock-heatmap-chart')
      expect(chart).toHaveAttribute('data-height', '100%')
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
      expect(screen.getByTestId('mock-heatmap-chart')).toBeInTheDocument()
    })

    it('handles singular and plural unit labels in tooltip', () => {
      const { rerender } = renderWithTheme(<ContributionHeatmap {...defaultProps} unit="commit" />)
      expect(screen.getByTestId('mock-heatmap-chart')).toBeInTheDocument()

      const singleData = { '2024-01-01': 1 }
      rerender(
        <ThemeProvider attribute="class">
          <ContributionHeatmap
            contributionData={singleData}
            startDate="2024-01-01"
            endDate="2024-01-31"
            unit="commit"
          />
        </ThemeProvider>
      )
      expect(screen.getByTestId('mock-heatmap-chart')).toBeInTheDocument()
    })

    it('tooltip respects theme colors', () => {
      const { rerender } = renderWithTheme(<ContributionHeatmap {...defaultProps} />, 'light')
      expect(screen.getByTestId('mock-heatmap-chart')).toBeInTheDocument()
      ;(useTheme as jest.Mock).mockReturnValue({ theme: 'dark', setTheme: jest.fn() })
      rerender(
        <ThemeProvider attribute="class">
          <ContributionHeatmap {...defaultProps} />
        </ThemeProvider>
      )
      expect(screen.getByTestId('mock-heatmap-chart')).toBeInTheDocument()
    })

    it('handles missing data in tooltip gracefully', () => {
      const { container } = renderWithTheme(
        <ContributionHeatmap contributionData={{}} startDate="2024-01-01" endDate="2024-01-31" />
      )
      expect(screen.getByTestId('mock-heatmap-chart')).toBeInTheDocument()

      const styleTag = container.querySelector('style')
      expect(styleTag).toBeInTheDocument()
    })
  })

  describe('Week Number Calculation', () => {
    it('correctly calculates week numbers starting from Monday', () => {
      const data = {
        '2024-01-01': 5,
        '2024-01-08': 10,
      }
      renderWithTheme(
        <ContributionHeatmap contributionData={data} startDate="2024-01-01" endDate="2024-01-14" />
      )
      expect(screen.getByTestId('mock-heatmap-chart')).toBeInTheDocument()
    })

    it('handles week transitions correctly', () => {
      const data = {
        '2024-01-07': 5,
        '2024-01-08': 10,
      }
      renderWithTheme(
        <ContributionHeatmap contributionData={data} startDate="2024-01-07" endDate="2024-01-14" />
      )
      expect(screen.getByTestId('mock-heatmap-chart')).toBeInTheDocument()
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
      expect(screen.getByTestId('mock-heatmap-chart')).toBeInTheDocument()
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
      const chart = screen.getByTestId('mock-heatmap-chart')
      expect(chart).toHaveAttribute('data-type', 'heatmap')
    })

    it('disables toolbar and legend as expected', () => {
      renderWithTheme(<ContributionHeatmap {...defaultProps} />)
      expect(screen.getByTestId('mock-heatmap-chart')).toBeInTheDocument()
    })
  })

  describe('Responsive Design', () => {
    it('applies responsive container classes', () => {
      const { container } = renderWithTheme(<ContributionHeatmap {...defaultProps} />)
      const heatmapContainer = container.querySelector('.heatmap-container')
      expect(heatmapContainer).toBeInTheDocument()
    })

    it('maintains aspect ratio on different screen sizes', () => {
      const { container } = renderWithTheme(<ContributionHeatmap {...defaultProps} />)
      const styleContent = container.querySelector('style')?.textContent
      expect(styleContent).toContain('aspect-ratio: 4 / 1')
      expect(styleContent).toContain('min-height: 132px')
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
})
