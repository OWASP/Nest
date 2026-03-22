import { useQuery } from '@apollo/client/react'
import { mockProjectsDashboardMetricsDetailsData } from '@mockData/mockProjectsDashboardMetricsDetailsData'
import { render, screen, waitFor } from '@testing-library/react'
import { axe } from 'jest-axe'
import { useTheme } from 'next-themes'
import ProjectHealthMetricsDetails from 'app/projects/dashboard/metrics/[projectKey]/page'

jest.mock('@apollo/client/react', () => ({
  useQuery: jest.fn(),
}))

jest.mock('react-apexcharts', () => {
  return {
    __esModule: true,
    default: () => {
      return <div data-testid="mock-apexcharts">Mock ApexChart</div>
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
])('ProjectHealthDashboardMetricsDetailsPage Accessibility ($name theme)', ({ theme }) => {
  beforeEach(() => {
    ;(useTheme as jest.Mock).mockReturnValue({ theme, setTheme: jest.fn() })
    document.documentElement.classList.toggle('dark', theme === 'dark')
  })
  it('should have no accessibility violations', async () => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: mockProjectsDashboardMetricsDetailsData,
      loading: false,
      error: null,
    })

    const { container } = render(<ProjectHealthMetricsDetails />)

    const headers = [
      'Days Metrics',
      'Issues',
      'Stars',
      'Forks',
      'Contributors',
      'Releases',
      'Open Pull Requests',
      'Health',
      'Score',
    ]
    const metrics = mockProjectsDashboardMetricsDetailsData.project.healthMetricsLatest
    await waitFor(() => {
      for (const header of headers) {
        expect(screen.getByText(header)).toBeInTheDocument()
      }
      expect(screen.getByText(metrics.projectName)).toBeInTheDocument()
      expect(screen.getByText(metrics.score.toString())).toBeInTheDocument()
    })

    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })
})
