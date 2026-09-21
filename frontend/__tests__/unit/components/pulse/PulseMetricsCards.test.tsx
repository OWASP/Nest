import { render, screen } from '@testing-library/react'
import PulseMetricsCards from 'components/pulse/PulseMetricsCards'

jest.mock('@heroui/skeleton', () => ({
  Skeleton: ({ className }: { className?: string }) => (
    <div data-testid="skeleton" className={className} />
  ),
}))

describe('<PulseMetricsCards />', () => {
  it('renders metric cards, stat values, and fallback states', () => {
    const mockStats = {
      __typename: 'ActivityEventStatsNode' as const,
      totalActivities: 1200,
      pullRequests: 300,
      issues: 450,
      contributors: 75,
      releases: 20,
      activeRepos: 15,
    }

    const { rerender } = render(<PulseMetricsCards stats={mockStats} />)
    expect(screen.getByText('Total Activities')).toBeInTheDocument()
    expect(screen.getByText((1200).toLocaleString('en-US'))).toBeInTheDocument()
    expect(screen.getAllByText('All time')).toHaveLength(6)

    rerender(<PulseMetricsCards loading />)
    expect(screen.getAllByTestId('skeleton')).toHaveLength(6)

    rerender(<PulseMetricsCards error />)
    expect(screen.getAllByText('N/A')).toHaveLength(6)

    rerender(<PulseMetricsCards stats={null} />)
    expect(screen.getAllByText('N/A')).toHaveLength(6)

    rerender(<PulseMetricsCards />)
    expect(screen.getAllByText('N/A')).toHaveLength(6)
  })
})
