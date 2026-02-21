import { render } from '@testing-library/react'
import { axe } from 'jest-axe'
import { useTheme } from 'next-themes'
import { HealthMetricsProps } from 'types/healthMetrics'
import MetricsCard from 'components/MetricsCard'

const makeMetric = (overrides: Partial<HealthMetricsProps> = {}): HealthMetricsProps => ({
  projectKey: 'test-project',
  projectName: 'Test Project',
  starsCount: 42,
  forksCount: 13,
  contributorsCount: 5,
  createdAt: '2023-03-25T12:00:00Z',
  score: 80,
  id: 'id-123',
  ageDays: 500,
  ageDaysRequirement: 365,
  isFundingRequirementsCompliant: true,
  isLeaderRequirementsCompliant: true,
  openIssuesCount: 0,
  unassignedIssuesCount: 0,
  unansweredIssuesCount: 0,
  openPullRequestsCount: 0,
  lastCommitDays: 0,
  lastReleaseDays: 0,
  lastCommitDaysRequirement: 0,
  lastReleaseDaysRequirement: 0,
  lastPullRequestDays: 0,
  lastPullRequestDaysRequirement: 0,
  owaspPageLastUpdateDays: 0,
  owaspPageLastUpdateDaysRequirement: 0,
  recentReleasesCount: 0,
  totalIssuesCount: 0,
  totalReleasesCount: 0,
  ...overrides,
})

describe.each([
  { theme: 'light', name: 'light' },
  { theme: 'dark', name: 'dark' },
])('MetricsCard a11y ($name theme)', ({ theme }) => {
  beforeEach(() => {
    ;(useTheme as jest.Mock).mockReturnValue({ theme, setTheme: jest.fn() })
    document.documentElement.classList.toggle('dark', theme === 'dark')
  })
  it('should not have any accessibility violations', async () => {
    const { container } = render(<MetricsCard metric={makeMetric()} />)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })
})
