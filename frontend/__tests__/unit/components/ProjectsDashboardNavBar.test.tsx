import { render } from '@testing-library/react'
import * as nextNavigation from 'next/navigation'
import ProjectsDashboardNavBar from 'components/ProjectsDashboardNavBar'
import '@testing-library/jest-dom'

jest.mock('next/navigation', () => ({
  usePathname: jest.fn(),
}))

describe('ProjectsDashboardNavbar', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('should render both navigation links with correct hrefs', () => {
    ;(nextNavigation.usePathname as jest.Mock).mockReturnValue('/')

    const { getByRole } = render(<ProjectsDashboardNavBar />)

    const overviewLink = getByRole('link', { name: /overview/i })
    const metricsLink = getByRole('link', { name: /metrics/i })

    expect(overviewLink).toBeInTheDocument()
    expect(overviewLink).toHaveAttribute('href', '/projects/dashboard')

    expect(metricsLink).toBeInTheDocument()
    expect(metricsLink).toHaveAttribute('href', '/projects/dashboard/metrics')
  })

  it('should apply active state to the Overview link on the correct path', () => {
    ;(nextNavigation.usePathname as jest.Mock).mockReturnValue('/projects/dashboard')

    const { getByRole } = render(<ProjectsDashboardNavBar />)

    expect(getByRole('link', { name: /overview/i })).toHaveAttribute('aria-current', 'page')
    expect(getByRole('link', { name: /metrics/i })).not.toHaveAttribute('aria-current', 'page')
  })

  it('should apply active state to the metrics link on the correct path', () => {
    ;(nextNavigation.usePathname as jest.Mock).mockReturnValue('/projects/dashboard/metrics')

    const { getByRole } = render(<ProjectsDashboardNavBar />)

    expect(getByRole('link', { name: /metrics/i })).toHaveAttribute('aria-current', 'page')
    expect(getByRole('link', { name: /overview/i })).not.toHaveAttribute('aria-current', 'page')
  })

  it('should not apply active state to any link when on an unrelated path', () => {
    ;(nextNavigation.usePathname as jest.Mock).mockReturnValue('/some/other/unrelated/path')

    const { getByRole } = render(<ProjectsDashboardNavBar />)

    expect(getByRole('link', { name: /overview/i })).not.toHaveAttribute('aria-current', 'page')
    expect(getByRole('link', { name: /metrics/i })).not.toHaveAttribute('aria-current', 'page')
  })
})
