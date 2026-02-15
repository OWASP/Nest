import { render } from '@testing-library/react'
import { axe } from 'jest-axe'
import { useTheme } from 'next-themes'
import { ReactNode } from 'react'
import BarChart from 'components/BarChart'

const mockProps = {
  title: 'Calories Burned',
  labels: ['Mon', 'Tue', 'Wed'],
  days: [200, 150, 100],
  requirements: [180, 170, 90],
}

jest.mock('react-apexcharts', () => {
  return function MockChart(props: {
    options: unknown
    series: unknown
    height: number
    type: string
  }) {
    const mockOptions = props.options as Record<string, unknown>

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
    title: ReactNode
    icon?: unknown
    children: ReactNode
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

describe.each([
  { theme: 'light', name: 'light' },
  { theme: 'dark', name: 'dark' },
])('BarChart Accessibility ($name theme)', ({ theme }) => {
  beforeEach(() => {
    ;(useTheme as jest.Mock).mockReturnValue({ theme, setTheme: jest.fn() })
  })
  it('should not have any accessibility violations', async () => {
    const { container } = render(<BarChart {...mockProps} />)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })
})
