import { useQuery } from '@apollo/client/react'
import { mockProjectsDashboardOverviewData } from '@mockData/mockProjectsDashboardOverviewData'
import { render } from '@testing-library/react'
import { axe } from 'jest-axe'
import { useTheme } from 'next-themes'
import ProjectsDashboardPage from 'app/projects/dashboard/page'

jest.mock('@apollo/client/react', () => ({
  useQuery: jest.fn(),
}))

jest.mock('components/LineChart', () => {
  return {
    __esModule: true,
    default: () => {
      return <div data-testid="mock-line_chart">Mock ApexChart</div>
    },
  }
})

jest.mock('components/DonutBarChart', () => {
  return {
    __esModule: true,
    default: () => {
      return <div data-testid="mock-donut_bar_chart">Mock DonutBarChart</div>
    },
  }
})

jest.mock('hooks/useDjangoSession', () => ({
  useDjangoSession: () => ({
    isSyncing: false,
  }),
}))

describe.each([
  { theme: 'light', name: 'light' },
  { theme: 'dark', name: 'dark' },
])('ProjectHealthDashboardOverviewPage Accessibility ($name theme)', ({ theme }) => {
  beforeEach(() => {
    ;(useTheme as jest.Mock).mockReturnValue({ theme, setTheme: jest.fn() })
    document.documentElement.classList.toggle('dark', theme === 'dark')
  })
  it('should have no accessibility violations', async () => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: mockProjectsDashboardOverviewData,
      loading: false,
      error: null,
    })

    const { container } = render(<ProjectsDashboardPage />)
    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })

  it('should have no accessibility violations when no data exists', async () => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: null,
      loading: false,
      error: null,
    })

    const { container } = render(<ProjectsDashboardPage />)
    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })
})
