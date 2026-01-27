import { render } from '@testing-library/react'
import { axe } from 'jest-axe'
import { IconType } from 'react-icons'
import { HealthMetricsProps } from 'types/healthMetrics'
import HealthMetrics from 'components/HealthMetrics'

jest.mock('components/BarChart', () => (props: { title: string; icon?: IconType }) => (
  <div
    data-testid="BarChart"
    data-props={JSON.stringify({
      ...props,
      icon: props.icon?.name || null,
    })}
  >
    {props.title}
  </div>
))
jest.mock('components/LineChart', () => (props: { title: string }) => (
  <div data-testid="LineChart" data-props={JSON.stringify(props)}>
    {props.title}
  </div>
))

const getMockHealthMetric = (): HealthMetricsProps[] => [
  {
    createdAt: '2025-07-23T00:00:00Z',
    openIssuesCount: 12,
    unassignedIssuesCount: 4,
    unansweredIssuesCount: 2,
    openPullRequestsCount: 3,
    starsCount: 45,
    forksCount: 5,
    lastCommitDays: 1,
    lastReleaseDays: 7,
    lastCommitDaysRequirement: 10,
    lastReleaseDaysRequirement: 14,
    ageDays: 730,
    ageDaysRequirement: 365,
    contributorsCount: 8,
    isFundingRequirementsCompliant: true,
    isLeaderRequirementsCompliant: true,
    lastPullRequestDays: 5,
    lastPullRequestDaysRequirement: 30,
    owaspPageLastUpdateDays: 20,
    owaspPageLastUpdateDaysRequirement: 90,
    projectName: 'nest',
    recentReleasesCount: 5,
    score: 85,
    totalIssuesCount: 100,
    totalReleasesCount: 15,
    id: '123',
    projectKey: 'owasp',
  },
]

describe('HealthMetrics a11y', () => {
  it('should not have any accessibility violations', async () => {
    const { container } = render(<HealthMetrics data={getMockHealthMetric()} />)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })
})
