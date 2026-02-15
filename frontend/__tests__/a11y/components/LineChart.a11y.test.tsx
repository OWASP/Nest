import { render } from '@testing-library/react'
import { axe } from 'jest-axe'
import { useTheme } from 'next-themes'
import { ApexLineChartSeries } from 'types/healthMetrics'
import LineChart from 'components/LineChart'

jest.mock('next/dynamic', () => {
  return jest.fn().mockImplementation(() => {
    const MockChart = ({ options, series, height }) => {
      return (
        <div
          data-testid="mock-chart"
          data-options={JSON.stringify({
            ...options,
            yaxis: {
              ...options.yaxis,
              labels: {
                ...options.yaxis?.labels,
                // Don't serialize the function, just indicate it exists
                formatter: 'function',
              },
            },
          })}
          data-series={JSON.stringify(series)}
          data-height={height}
        />
      )
    }
    return MockChart
  })
})

const defaultProps = {
  title: 'Test Chart',
  series: [
    {
      name: 'Test Series',
      data: [10, 20, 30, 40, 50],
    },
  ] as ApexLineChartSeries[],
}

describe.each([
  { theme: 'light', name: 'light' },
  { theme: 'dark', name: 'dark' },
])('LineChart a11y ($name theme)', ({ theme }) => {
  beforeEach(() => {
    ;(useTheme as jest.Mock).mockReturnValue({ theme, setTheme: jest.fn() })
  })
  it('should not have any accessibility violations', async () => {
    const { container } = render(<LineChart {...defaultProps} />)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })
})
