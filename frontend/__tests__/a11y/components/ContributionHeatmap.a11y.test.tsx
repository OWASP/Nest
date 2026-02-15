import { render, screen } from '@testing-library/react'
import { axe } from 'jest-axe'
import { useTheme } from 'next-themes'

import ContributionHeatmap from 'components/ContributionHeatmap'

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
          tooltip.custom({
            seriesIndex: 0,
            dataPointIndex: 0,
            w: { config: { series: mockSeries } },
          })
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

describe.each([
  { theme: 'light', name: 'light' },
  { theme: 'dark', name: 'dark' },
])('ContributionHeatmap Accessibility ($name theme)', ({ theme }) => {
  beforeEach(() => {
    ;(useTheme as jest.Mock).mockReturnValue({ theme, setTheme: jest.fn() })
  })
  it('should not have any accessibility violations', async () => {
    const { container } = render(<ContributionHeatmap {...defaultProps} />)

    await screen.findByTestId('mock-heatmap-chart')

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })

  it('should not have any accessibility violations when title is provided', async () => {
    const { container } = render(<ContributionHeatmap {...defaultProps} title="Test Title" />)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })
})
