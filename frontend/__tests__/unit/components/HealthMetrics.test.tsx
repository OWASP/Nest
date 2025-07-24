import { faCodeCommit } from '@fortawesome/free-solid-svg-icons'
import { render, screen } from '@testing-library/react'
import { HealthMetricsProps } from 'types/healthMetrics'
import HealthMetrics from 'components/HealthMetrics'

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

// Using `any` intentionally for testing incomplete health metric data.
// The structure may not match the full HealthMetric type, hence typing it strictly would be misleading.
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const getMockIncompleteHealthMetric = (): any[] => [
  {
    createdAt: '2025-07-23T00:00:00Z',
    openIssuesCount: 5,
    unassignedIssuesCount: 0,
    unansweredIssuesCount: 0,
    openPullRequestsCount: 0,
    starsCount: 10,
    forksCount: 3,
    id: '123',
    projectKey: 'owasp',
  },
]

jest.mock('components/BarChart', () => (props: { title: string }) => (
  <div data-testid="BarChart" data-props={JSON.stringify(props)}>
    {props.title}
  </div>
))
jest.mock('components/LineChart', () => (props: { title: string }) => (
  <div data-testid="LineChart" data-props={JSON.stringify(props)}>
    {props.title}
  </div>
))

describe('HealthMetrics', () => {
  describe('with valid data', () => {
    it('renders without crashing with valid data', () => {
      render(<HealthMetrics data={getMockHealthMetric()} />)
      expect(screen.getAllByTestId('LineChart')).toHaveLength(4)
      expect(screen.getByTestId('BarChart')).toBeInTheDocument()
      expect(screen.getByText('Issues Trend')).toBeInTheDocument()
      expect(screen.getByText('Pull Requests Trend')).toBeInTheDocument()
      expect(screen.getByText('Stars Trend')).toBeInTheDocument()
      expect(screen.getByText('Forks Trend')).toBeInTheDocument()
      expect(screen.getByText('Days Since Last Commit and Release')).toBeInTheDocument()
    })

    it('renders correct icon and labels for BarChart', () => {
      render(<HealthMetrics data={getMockHealthMetric()} />)
      const barChart = screen.getByTestId('BarChart')
      const props = JSON.parse(barChart.getAttribute('data-props') || '{}')
      expect(props.icon).toEqual(faCodeCommit)
      expect(props.labels).toEqual(['Days Since Last Commit', 'Days Since Last Release'])
      expect(props.days).toEqual([1, 7])
      expect(props.requirements).toEqual([10, 14])
    })

    it('renders formatted date labels correctly', () => {
      render(<HealthMetrics data={getMockHealthMetric()} />)
      const lineCharts = screen.getAllByTestId('LineChart')
      const labels = JSON.parse(lineCharts[0].getAttribute('data-props') || '{}').labels
      expect(typeof labels[0]).toBe('string')
      expect(labels[0]).toBeTruthy()
    })

    it('includes all required series in LineChart', () => {
      render(<HealthMetrics data={getMockHealthMetric()} />)
      const issuesTrend = screen.getByText('Issues Trend')
      const props = JSON.parse(issuesTrend.getAttribute('data-props') || '{}')
      const seriesNames = props.series.map((s: { name: string }) => s.name)
      expect(seriesNames).toEqual(['Open Issues', 'Unassigned Issues', 'Unanswered Issues'])
    })

    it('applies accessibility role/content where needed', () => {
      render(<HealthMetrics data={getMockHealthMetric()} />)
      expect(screen.getByText('Issues Trend')).toBeVisible()
    })

    it('renders expected DOM structure and classes', () => {
      render(<HealthMetrics data={getMockHealthMetric()} />)
      const barChart = screen.getByTestId('BarChart')
      expect(barChart.className).toBeDefined()
    })
  })

  describe('with empty data', () => {
    it('handles empty data gracefully', () => {
      render(<HealthMetrics data={[]} />)
      expect(screen.queryAllByTestId('LineChart')).toHaveLength(4)
      expect(screen.queryByTestId('BarChart')).toBeInTheDocument()
    })
  })

  describe('with incomplete data', () => {
    it('handles missing last data point fields with fallback values', () => {
      render(<HealthMetrics data={getMockIncompleteHealthMetric()} />)
      const barChart = screen.getByTestId('BarChart')
      const props = JSON.parse(barChart.getAttribute('data-props') || '{}')
      expect(props.days).toEqual([0, 0])
      expect(props.requirements).toEqual([0, 0])
    })
  })
})
