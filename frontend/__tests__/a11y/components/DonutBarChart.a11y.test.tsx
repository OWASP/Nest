import { render } from '@testing-library/react'
import { axe } from 'jest-axe'
import { useTheme } from 'next-themes'
import { FaChartPie } from 'react-icons/fa'
import DonutBarChart from 'components/DonutBarChart'

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

describe.each([
  { theme: 'light', name: 'light' },
  { theme: 'dark', name: 'dark' },
])('DonutBarChart a11y ($name theme)', ({ theme }) => {
  beforeEach(() => {
    ;(useTheme as jest.Mock).mockReturnValue({ theme, setTheme: jest.fn() })
  })
  it('should not have any accessibility violations', async () => {
    const { container } = render(
      <DonutBarChart icon={FaChartPie} title="Test Chart" series={[50, 30, 20]} />
    )

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })
})
