import { render } from '@testing-library/react'
import { axe, toHaveNoViolations } from 'jest-axe'
import { ApexLineChartSeries } from 'types/healthMetrics'
import LineChart from 'components/LineChart'

expect.extend(toHaveNoViolations)

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

describe('LineChart a11y', () => {
  it('should not have any accessibility violations', async () => {
    const { container } = render(<LineChart {...defaultProps} />)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })
})
