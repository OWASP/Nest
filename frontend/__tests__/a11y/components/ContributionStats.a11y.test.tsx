import { render } from '@testing-library/react'
import { axe } from 'jest-axe'
import { useTheme } from 'next-themes'
import ContributionStats from 'components/ContributionStats'

const mockStats = {
  commits: 120,
  pullRequests: 45,
  issues: 30,
  total: 195,
}

describe.each([
  { theme: 'light', name: 'light' },
  { theme: 'dark', name: 'dark' },
])('ContributionStats a11y ($name theme)', ({ theme }) => {
  beforeEach(() => {
    ;(useTheme as jest.Mock).mockReturnValue({ theme, setTheme: jest.fn() })
  })
  it('should have no accessibility violations with stats', async () => {
    const { container } = render(
      <ContributionStats title="Contribution Statistics" stats={mockStats} />
    )

    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })

  it('should have no accessibility violations without stats', async () => {
    const { container } = render(<ContributionStats title="Contribution Statistics" />)

    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })
})
