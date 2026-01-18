import { render, screen } from '@testing-library/react'
import type { HealthMetricsProps } from 'types/healthMetrics'
import MetricsCard from 'components/MetricsCard'
import '@testing-library/jest-dom'

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

describe('MetricsCard component', () => {
  it('renders name, counts, formatted date, score, and link correctly', () => {
    const metric = makeMetric()
    render(<MetricsCard metric={metric} />)

    expect(screen.getAllByText('Test Project')[0]).toBeInTheDocument()
    expect(screen.getAllByText('42')[0]).toBeInTheDocument()
    expect(screen.getAllByText('13')[0]).toBeInTheDocument()
    expect(screen.getAllByText('5')[0]).toBeInTheDocument()
    expect(screen.getAllByText('Mar 25, 2023')[0]).toBeInTheDocument()
    expect(screen.getAllByText('80')[0]).toBeInTheDocument()

    const link = screen.getByRole('link')
    expect(link).toHaveAttribute('href', '/projects/dashboard/metrics/test-project')
  })

  it('renders "No name" placeholder when projectName is empty', () => {
    const metric = makeMetric({ projectName: '' })
    render(<MetricsCard metric={metric} />)
    expect(screen.getAllByText('No name')[0]).toBeInTheDocument()
  })

  it('applies correct styling class depending on score thresholds', () => {
    const cases: Array<[number, string]> = [
      [90, 'text-green-900'],
      [75, 'text-green-900'],
      [60, 'text-orange-900'],
      [50, 'text-orange-900'],
      [30, 'text-red-900'],
    ]

    for (const [score, expectedClass] of cases) {
      const metric = makeMetric({ score })
      render(<MetricsCard metric={metric} />)
      const scoreEl = screen.getByText(score.toString()).closest('div')
      expect(scoreEl).toHaveClass(expectedClass)
    }
  })

  it('updates displayed values and link when metric props change via rerender', () => {
    const { rerender } = render(<MetricsCard metric={makeMetric()} />)
    expect(screen.getAllByText('Test Project')[0]).toBeInTheDocument()
    expect(screen.getAllByText('80')[0]).toBeInTheDocument()

    const updated = makeMetric({
      projectKey: 'another',
      projectName: 'Another Project',
      starsCount: 99,
      forksCount: 20,
      contributorsCount: 7,
      score: 55,
      createdAt: '2024-01-01T00:00:00Z',
    })
    rerender(<MetricsCard metric={updated} />)

    expect(screen.getAllByText('Another Project')[0]).toBeInTheDocument()
    expect(screen.getAllByText('99')[0]).toBeInTheDocument()
    expect(screen.getAllByText('20')[0]).toBeInTheDocument()
    expect(screen.getAllByText('7')[0]).toBeInTheDocument()
    expect(screen.getAllByText('Jan 1, 2024')[0]).toBeInTheDocument()
    expect(screen.getAllByText('55')[0]).toBeInTheDocument()
    expect(screen.getByRole('link')).toHaveAttribute('href', '/projects/dashboard/metrics/another')
  })
})
