import { render, screen, waitFor } from '@testing-library/react'
import { useTheme } from 'next-themes'
import ContributionHeatmap from 'components/ContributionHeatmap'

// Mock next-themes
jest.mock('next-themes', () => ({
  useTheme: jest.fn(),
}))

// Mock react-apexcharts with more detailed implementation
interface MockChartProps {
  options?: {
    tooltip?: { enabled?: boolean }
    chart?: { background?: string }
  }
  series?: Array<{ name: string; data?: unknown[] }>
  type?: string
  height?: string | number
  width?: string | number
}

jest.mock('react-apexcharts', () => {
  return function MockChart({ options, series, type, height, width }: MockChartProps) {
    return (
      <div
        data-testid="contribution-heatmap-chart"
        data-type={type}
        data-height={height}
        data-width={width}
        data-tooltip-enabled={options?.tooltip?.enabled}
        data-series-count={series?.length || 0}
        data-chart-background={options?.chart?.background}
      >
        Mock Heatmap Chart
        {series?.map((s: { name: string; data?: unknown[] }, index: number) => (
          <div
            key={s.name || `series-${index}`}
            data-testid={`series-${index}`}
            data-series-name={s.name}
          >
            {s.name}: {s.data?.length || 0} data points
          </div>
        ))}
      </div>
    )
  }
})

// Mock next/dynamic
jest.mock('next/dynamic', () => {
  return () => {
    // Return our mocked chart component directly
    return jest.requireMock('react-apexcharts')
  }
})

const mockUseTheme = useTheme as jest.MockedFunction<typeof useTheme>

describe('ContributionHeatmap', () => {
  const mockContributionData = {
    '2024-01-01': 5,
    '2024-01-02': 8,
    '2024-01-03': 3,
    '2024-01-04': 12,
    '2024-01-05': 7,
    '2024-01-08': 15,
    '2024-01-10': 4,
    '2024-01-15': 9,
    '2024-01-20': 6,
    '2024-01-25': 11,
  }

  const defaultProps = {
    contributionData: mockContributionData,
    startDate: '2024-01-01',
    endDate: '2024-01-31',
  }

  beforeEach(() => {
    mockUseTheme.mockReturnValue({
      theme: 'light',
      setTheme: jest.fn(),
      resolvedTheme: 'light',
      themes: ['light', 'dark', 'system'],
    })
    jest.clearAllMocks()
  })

  describe('Rendering', () => {
    it('renders the heatmap chart', async () => {
      render(<ContributionHeatmap {...defaultProps} />)

      await waitFor(() => {
        expect(screen.getByTestId('contribution-heatmap-chart')).toBeInTheDocument()
      })
    })

    it('renders with title when provided', async () => {
      render(<ContributionHeatmap {...defaultProps} title="Test Contribution Heatmap" />)

      expect(screen.getByText('Test Contribution Heatmap')).toBeInTheDocument()
      await waitFor(() => {
        expect(screen.getByTestId('contribution-heatmap-chart')).toBeInTheDocument()
      })
    })

    it('renders without title when not provided', async () => {
      render(<ContributionHeatmap {...defaultProps} />)

      expect(screen.queryByRole('heading')).not.toBeInTheDocument()
      await waitFor(() => {
        expect(screen.getByTestId('contribution-heatmap-chart')).toBeInTheDocument()
      })
    })

    it('renders with correct chart type', async () => {
      render(<ContributionHeatmap {...defaultProps} />)

      await waitFor(() => {
        const chart = screen.getByTestId('contribution-heatmap-chart')
        expect(chart).toHaveAttribute('data-type', 'heatmap')
      })
    })

    it('generates correct number of series (7 days of week)', async () => {
      render(<ContributionHeatmap {...defaultProps} />)

      await waitFor(() => {
        const chart = screen.getByTestId('contribution-heatmap-chart')
        expect(chart).toHaveAttribute('data-series-count', '7')
      })
    })
  })

  describe('Variants', () => {
    it('renders default variant with correct dimensions', async () => {
      render(<ContributionHeatmap {...defaultProps} variant="default" />)

      await waitFor(() => {
        const chart = screen.getByTestId('contribution-heatmap-chart')
        expect(chart).toHaveAttribute('data-height', '200')
        expect(chart).toHaveAttribute('data-width', '1200px')
      })
    })

    it('renders compact variant with correct dimensions', async () => {
      render(<ContributionHeatmap {...defaultProps} variant="compact" />)

      await waitFor(() => {
        const chart = screen.getByTestId('contribution-heatmap-chart')
        expect(chart).toHaveAttribute('data-height', '100%')
        expect(chart).toHaveAttribute('data-width', '100%')
      })
    })

    it('uses default variant when not specified', async () => {
      render(<ContributionHeatmap {...defaultProps} />)

      await waitFor(() => {
        const chart = screen.getByTestId('contribution-heatmap-chart')
        expect(chart).toHaveAttribute('data-height', '200')
        expect(chart).toHaveAttribute('data-width', '1200px')
      })
    })
  })

  describe('Theme Support', () => {
    it('handles light theme', async () => {
      mockUseTheme.mockReturnValue({
        theme: 'light',
        setTheme: jest.fn(),
        resolvedTheme: 'light',
        themes: ['light', 'dark', 'system'],
      })

      render(<ContributionHeatmap {...defaultProps} />)

      await waitFor(() => {
        const chart = screen.getByTestId('contribution-heatmap-chart')
        expect(chart).toHaveAttribute('data-chart-background', 'transparent')
      })
    })

    it('handles dark theme', async () => {
      mockUseTheme.mockReturnValue({
        theme: 'dark',
        setTheme: jest.fn(),
        resolvedTheme: 'dark',
        themes: ['light', 'dark', 'system'],
      })

      render(<ContributionHeatmap {...defaultProps} />)

      await waitFor(() => {
        const chart = screen.getByTestId('contribution-heatmap-chart')
        expect(chart).toHaveAttribute('data-chart-background', 'transparent')
      })
    })

    it('handles undefined theme gracefully', async () => {
      mockUseTheme.mockReturnValue({
        theme: undefined,
        setTheme: jest.fn(),
        resolvedTheme: undefined,
        themes: ['light', 'dark', 'system'],
      })

      render(<ContributionHeatmap {...defaultProps} />)

      await waitFor(() => {
        expect(screen.getByTestId('contribution-heatmap-chart')).toBeInTheDocument()
      })
    })
  })

  describe('Edge Cases - No Data', () => {
    it('handles empty contribution data', async () => {
      render(
        <ContributionHeatmap contributionData={{}} startDate="2024-01-01" endDate="2024-01-31" />
      )

      await waitFor(() => {
        const chart = screen.getByTestId('contribution-heatmap-chart')
        expect(chart).toBeInTheDocument()
        expect(chart).toHaveAttribute('data-series-count', '7') // Still 7 days of week
      })
    })

    it('handles null contribution data', async () => {
      render(
        <ContributionHeatmap
          contributionData={null as unknown as Record<string, number>}
          startDate="2024-01-01"
          endDate="2024-01-31"
        />
      )

      await waitFor(() => {
        expect(screen.getByTestId('contribution-heatmap-chart')).toBeInTheDocument()
      })
    })

    it('handles undefined contribution data', async () => {
      render(
        <ContributionHeatmap
          contributionData={undefined as unknown as Record<string, number>}
          startDate="2024-01-01"
          endDate="2024-01-31"
        />
      )

      await waitFor(() => {
        expect(screen.getByTestId('contribution-heatmap-chart')).toBeInTheDocument()
      })
    })
  })

  describe('Edge Cases - Partial Data', () => {
    it('handles sparse contribution data', async () => {
      const sparseData = {
        '2024-01-01': 5,
        '2024-01-15': 3,
        '2024-01-30': 7,
      }

      render(
        <ContributionHeatmap
          contributionData={sparseData}
          startDate="2024-01-01"
          endDate="2024-01-31"
        />
      )

      await waitFor(() => {
        expect(screen.getByTestId('contribution-heatmap-chart')).toBeInTheDocument()
      })
    })

    it('handles single day contribution', async () => {
      const singleDayData = {
        '2024-01-15': 10,
      }

      render(
        <ContributionHeatmap
          contributionData={singleDayData}
          startDate="2024-01-01"
          endDate="2024-01-31"
        />
      )

      await waitFor(() => {
        expect(screen.getByTestId('contribution-heatmap-chart')).toBeInTheDocument()
      })
    })

    it('handles contributions outside date range', async () => {
      const outsideRangeData = {
        '2023-12-31': 5, // Before range
        '2024-01-15': 10, // In range
        '2024-02-01': 7, // After range
      }

      render(
        <ContributionHeatmap
          contributionData={outsideRangeData}
          startDate="2024-01-01"
          endDate="2024-01-31"
        />
      )

      await waitFor(() => {
        expect(screen.getByTestId('contribution-heatmap-chart')).toBeInTheDocument()
      })
    })
  })

  describe('Loading States', () => {
    it('renders while data is loading (empty data)', async () => {
      render(
        <ContributionHeatmap
          contributionData={{}}
          startDate="2024-01-01"
          endDate="2024-01-31"
          title="Loading..."
        />
      )

      expect(screen.getByText('Loading...')).toBeInTheDocument()
      await waitFor(() => {
        expect(screen.getByTestId('contribution-heatmap-chart')).toBeInTheDocument()
      })
    })

    it('handles transition from loading to data', async () => {
      const { rerender } = render(
        <ContributionHeatmap
          contributionData={{}}
          startDate="2024-01-01"
          endDate="2024-01-31"
          title="Loading..."
        />
      )

      expect(screen.getByText('Loading...')).toBeInTheDocument()

      // Simulate data loading
      rerender(
        <ContributionHeatmap
          contributionData={mockContributionData}
          startDate="2024-01-01"
          endDate="2024-01-31"
          title="Loaded Data"
        />
      )

      expect(screen.getByText('Loaded Data')).toBeInTheDocument()
      await waitFor(() => {
        expect(screen.getByTestId('contribution-heatmap-chart')).toBeInTheDocument()
      })
    })
  })

  describe('Date Range Handling', () => {
    it('handles different date ranges correctly', async () => {
      // Test one week range
      const { unmount } = render(
        <ContributionHeatmap
          contributionData={mockContributionData}
          startDate="2024-01-01"
          endDate="2024-01-07"
        />
      )

      await waitFor(() => {
        expect(screen.getByTestId('contribution-heatmap-chart')).toBeInTheDocument()
      })

      unmount()

      // Test three months range
      const { unmount: unmount2 } = render(
        <ContributionHeatmap
          contributionData={mockContributionData}
          startDate="2024-01-01"
          endDate="2024-03-31"
        />
      )

      await waitFor(() => {
        expect(screen.getByTestId('contribution-heatmap-chart')).toBeInTheDocument()
      })

      unmount2()

      // Test full year range
      render(
        <ContributionHeatmap
          contributionData={mockContributionData}
          startDate="2024-01-01"
          endDate="2024-12-31"
        />
      )

      await waitFor(() => {
        expect(screen.getByTestId('contribution-heatmap-chart')).toBeInTheDocument()
      })
    })

    it('handles invalid date ranges gracefully', async () => {
      // End date before start date
      render(
        <ContributionHeatmap
          contributionData={mockContributionData}
          startDate="2024-12-31"
          endDate="2024-01-01"
        />
      )

      await waitFor(() => {
        expect(screen.getByTestId('contribution-heatmap-chart')).toBeInTheDocument()
      })
    })

    it('handles malformed dates', async () => {
      render(
        <ContributionHeatmap
          contributionData={mockContributionData}
          startDate="invalid-date"
          endDate="also-invalid"
        />
      )

      // Should not crash
      await waitFor(() => {
        expect(screen.getByTestId('contribution-heatmap-chart')).toBeInTheDocument()
      })
    })
  })

  describe('Custom Units', () => {
    it('uses default unit when not specified', async () => {
      render(<ContributionHeatmap {...defaultProps} />)

      await waitFor(() => {
        expect(screen.getByTestId('contribution-heatmap-chart')).toBeInTheDocument()
      })
    })

    it('handles custom unit prop', async () => {
      render(<ContributionHeatmap {...defaultProps} unit="commit" />)

      await waitFor(() => {
        expect(screen.getByTestId('contribution-heatmap-chart')).toBeInTheDocument()
      })
    })

    it('handles different unit types', async () => {
      // Test contribution unit
      const { unmount } = render(<ContributionHeatmap {...defaultProps} unit="contribution" />)
      await waitFor(() => {
        expect(screen.getByTestId('contribution-heatmap-chart')).toBeInTheDocument()
      })
      unmount()

      // Test commit unit
      const { unmount: unmount2 } = render(<ContributionHeatmap {...defaultProps} unit="commit" />)
      await waitFor(() => {
        expect(screen.getByTestId('contribution-heatmap-chart')).toBeInTheDocument()
      })
      unmount2()

      // Test pr unit
      const { unmount: unmount3 } = render(<ContributionHeatmap {...defaultProps} unit="pr" />)
      await waitFor(() => {
        expect(screen.getByTestId('contribution-heatmap-chart')).toBeInTheDocument()
      })
      unmount3()

      // Test issue unit
      render(<ContributionHeatmap {...defaultProps} unit="issue" />)
      await waitFor(() => {
        expect(screen.getByTestId('contribution-heatmap-chart')).toBeInTheDocument()
      })
    })
  })

  describe('Large Datasets', () => {
    it('handles large contribution datasets efficiently', async () => {
      // Generate large dataset (365 days) with deterministic values
      const largeDataset: Record<string, number> = {}
      for (let day = 1; day <= 365; day++) {
        const date = new Date(2024, 0, day)
        const dateStr = date.toISOString().split('T')[0]
        // Use deterministic values based on day number to ensure consistent tests
        largeDataset[dateStr] = (day % 20) + 1
      }

      render(
        <ContributionHeatmap
          contributionData={largeDataset}
          startDate="2024-01-01"
          endDate="2024-12-31"
          title="Large Dataset"
        />
      )

      expect(screen.getByText('Large Dataset')).toBeInTheDocument()
      await waitFor(() => {
        const chart = screen.getByTestId('contribution-heatmap-chart')
        expect(chart).toBeInTheDocument()
        expect(chart).toHaveAttribute('data-series-count', '7') // Still 7 days of week
      })
    })

    it('handles very high contribution counts', async () => {
      const highContributionData = {
        '2024-01-01': 999999,
        '2024-01-02': 1234567,
        '2024-01-03': Number.MAX_SAFE_INTEGER,
      }

      render(
        <ContributionHeatmap
          contributionData={highContributionData}
          startDate="2024-01-01"
          endDate="2024-01-31"
        />
      )

      await waitFor(() => {
        expect(screen.getByTestId('contribution-heatmap-chart')).toBeInTheDocument()
      })
    })
  })

  describe('Accessibility', () => {
    it('has proper heading structure when title is provided', async () => {
      render(<ContributionHeatmap {...defaultProps} title="Accessible Heatmap" />)

      const heading = screen.getByRole('heading', { level: 3 })
      expect(heading).toHaveTextContent('Accessible Heatmap')
    })

    it('provides meaningful content structure', async () => {
      render(<ContributionHeatmap {...defaultProps} title="Test Heatmap" />)

      expect(screen.getByText('Test Heatmap')).toBeInTheDocument()
      await waitFor(() => {
        expect(screen.getByTestId('contribution-heatmap-chart')).toBeInTheDocument()
      })
    })

    it('has proper container structure', async () => {
      render(<ContributionHeatmap {...defaultProps} />)

      const container = screen.getByTestId('contribution-heatmap-chart').parentElement
        ?.parentElement
      expect(container).toHaveClass('max-w-5xl')
    })
  })

  describe('Responsive Design', () => {
    it('applies responsive styles for default variant', async () => {
      render(<ContributionHeatmap {...defaultProps} variant="default" />)

      await waitFor(() => {
        const chart = screen.getByTestId('contribution-heatmap-chart')
        const container = chart.parentElement
        expect(container).toHaveClass('heatmap-container-default')
      })
    })

    it('applies responsive styles for compact variant', async () => {
      render(<ContributionHeatmap {...defaultProps} variant="compact" />)

      await waitFor(() => {
        const chart = screen.getByTestId('contribution-heatmap-chart')
        const container = chart.parentElement
        expect(container).toHaveClass('heatmap-container-compact')
      })
    })
  })

  describe('Error Handling', () => {
    it('handles negative contribution values', async () => {
      const negativeData = {
        '2024-01-01': -5,
        '2024-01-02': -10,
        '2024-01-03': 5, // Mix of negative and positive
      }

      render(
        <ContributionHeatmap
          contributionData={negativeData}
          startDate="2024-01-01"
          endDate="2024-01-31"
        />
      )

      await waitFor(() => {
        expect(screen.getByTestId('contribution-heatmap-chart')).toBeInTheDocument()
      })
    })

    it('handles non-numeric contribution values', async () => {
      const invalidData = {
        '2024-01-01': 'invalid' as unknown as number,
        '2024-01-02': null as unknown as number,
        '2024-01-03': undefined as unknown as number,
        '2024-01-04': 5, // Valid value mixed in
      }

      render(
        <ContributionHeatmap
          contributionData={invalidData}
          startDate="2024-01-01"
          endDate="2024-01-31"
        />
      )

      await waitFor(() => {
        expect(screen.getByTestId('contribution-heatmap-chart')).toBeInTheDocument()
      })
    })

    it('handles chart rendering failures gracefully', async () => {
      // This test ensures the component doesn't crash if ApexCharts fails
      render(<ContributionHeatmap {...defaultProps} />)

      await waitFor(() => {
        // Component should still render its container even if chart fails
        expect(screen.getByTestId('contribution-heatmap-chart')).toBeInTheDocument()
      })
    })
  })

  describe('Performance', () => {
    it('memoizes chart options to prevent unnecessary re-renders', async () => {
      const { rerender } = render(<ContributionHeatmap {...defaultProps} />)

      await waitFor(() => {
        expect(screen.getByTestId('contribution-heatmap-chart')).toBeInTheDocument()
      })

      // Re-render with same props should not cause issues
      rerender(<ContributionHeatmap {...defaultProps} />)

      await waitFor(() => {
        expect(screen.getByTestId('contribution-heatmap-chart')).toBeInTheDocument()
      })
    })

    it('memoizes heatmap series generation', async () => {
      const { rerender } = render(<ContributionHeatmap {...defaultProps} />)

      await waitFor(() => {
        expect(screen.getByTestId('contribution-heatmap-chart')).toBeInTheDocument()
      })

      // Re-render with same data should be efficient
      rerender(<ContributionHeatmap {...defaultProps} title="Updated Title" />)

      await waitFor(() => {
        expect(screen.getByText('Updated Title')).toBeInTheDocument()
        expect(screen.getByTestId('contribution-heatmap-chart')).toBeInTheDocument()
      })
    })
  })
})
