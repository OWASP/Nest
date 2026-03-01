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
    expect(screen.getByText(/Score:/)).toBeInTheDocument()

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
      [90, 'bg-green-500'],
      [75, 'bg-green-500'],
      [60, 'bg-orange-500'],
      [50, 'bg-orange-500'],
      [74, 'bg-orange-500'],
      [30, 'bg-red-500'],
    ]

    for (const [score, expectedClass] of cases) {
      const metric = makeMetric({ score })
      const { unmount } = render(<MetricsCard metric={metric} />)
      const scoreText = screen.getByText(/Score:/)
      const scoreEl = scoreText.closest('div')
      expect(scoreEl).toHaveClass(expectedClass)
      unmount()
    }
  })

  it('updates displayed values and link when metric props change via rerender', () => {
    const { rerender } = render(<MetricsCard metric={makeMetric()} />)
    expect(screen.getAllByText('Test Project')[0]).toBeInTheDocument()
    expect(screen.getByText(/Score:/).textContent).toContain('80')

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
    expect(screen.getByText(/Score:/).textContent).toContain('55')
    expect(screen.getByRole('link')).toHaveAttribute('href', '/projects/dashboard/metrics/another')
  })

  it('handles undefined optional props using defaults', () => {
    const metric = makeMetric({
      score: undefined,
      createdAt: undefined,
    })
    render(<MetricsCard metric={metric} />)

    const scoreText = screen.getByText(/Score: 0/)
    expect(scoreText).toBeInTheDocument()
    expect(scoreText.closest('div')).toHaveClass('bg-red-500')

    expect(screen.getByText('N/A')).toBeInTheDocument()
  })
})
