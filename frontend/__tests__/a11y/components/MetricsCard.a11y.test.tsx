import { render } from '@testing-library/react'
import { axe, toHaveNoViolations } from 'jest-axe'
import { HealthMetricsProps } from 'types/healthMetrics'
import MetricsCard from 'components/MetricsCard'

expect.extend(toHaveNoViolations)

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

describe('MetricsCard a11y', () => {
  it('should not have any accessibility violations', async () => {
    const { container } = render(<MetricsCard metric={makeMetric()} />)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })
})
