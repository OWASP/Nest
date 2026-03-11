import { useQuery } from '@apollo/client/react'
import { mockHealthMetricsData } from '@mockData/mockProjectsHealthMetricsData'
import { render } from '@testing-library/react'
import { axe } from 'jest-axe'
import { useTheme } from 'next-themes'
import MetricsPage from 'app/projects/dashboard/metrics/page'

jest.mock('@apollo/client/react', () => ({
  useQuery: jest.fn(),
}))

jest.mock('@heroui/toast', () => ({
  addToast: jest.fn(),
}))

jest.mock('hooks/useDjangoSession', () => ({
  useDjangoSession: () => ({
    isSyncing: false,
  }),
}))

jest.mock('@heroui/react', () => ({
  ...jest.requireActual('@heroui/react'),
  Pagination: ({ page, onChange }) => (
    <div>
      <button onClick={() => onChange(page + 1)}>Next Page</button>
    </div>
  ),
}))

describe.each([
  { theme: 'light', name: 'light' },
  { theme: 'dark', name: 'dark' },
])('MetricsPage Accessibility ($name theme)', ({ theme }) => {
  beforeEach(() => {
    ;(useTheme as jest.Mock).mockReturnValue({ theme, setTheme: jest.fn() })
    document.documentElement.classList.toggle('dark', theme === 'dark')
  })
  it('should have no accessibility violations', async () => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: mockHealthMetricsData,
      loading: false,
      error: null,
    })

    const { container } = render(<MetricsPage />)
    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })
})
