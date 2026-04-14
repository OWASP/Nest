import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'
import CardDetailsContributions from 'components/CardDetailsPage/CardDetailsContributions'

jest.mock('components/ContributionHeatmap', () => ({
  __esModule: true,
  default: ({ contributionData }: { contributionData: object }) => (
    <div data-testid="contribution-heatmap">Heatmap: {JSON.stringify(contributionData)}</div>
  ),
}))

jest.mock('components/ContributionStats', () => ({
  __esModule: true,
  default: ({ stats }: { stats: object }) => (
    <div data-testid="contribution-stats">Stats: {JSON.stringify(stats)}</div>
  ),
}))

describe('CardDetailsContributions', () => {
  afterEach(() => {
    jest.clearAllMocks()
  })

  it('renders nothing when hasContributions is false', () => {
    const { container } = render(<CardDetailsContributions hasContributions={false} />)
    expect(container.firstChild).toBeNull()
  })

  it('renders contribution stats when stats provided and hasContributions is true', () => {
    const stats = {
      total: 150,
      average: 10,
    }

    render(<CardDetailsContributions hasContributions={true} contributionStats={stats} />)

    expect(screen.getByTestId('contribution-stats')).toBeInTheDocument()
  })

  it('renders contribution heatmap with required props', () => {
    render(
      <CardDetailsContributions
        hasContributions={true}
        contributionData={{ '2024-01-01': 5 }}
        startDate="2024-01-01"
        endDate="2024-01-31"
      />
    )

    expect(screen.getByTestId('contribution-heatmap')).toBeInTheDocument()
  })

  it('renders both stats and heatmap components together', () => {
    const stats = {
      total: 100,
      average: 50,
    }

    render(
      <CardDetailsContributions
        hasContributions={true}
        contributionStats={stats}
        contributionData={{ '2024-01-01': 5 }}
        startDate="2024-01-01"
        endDate="2024-01-31"
      />
    )

    expect(screen.getByTestId('contribution-stats')).toBeInTheDocument()
    expect(screen.getByTestId('contribution-heatmap')).toBeInTheDocument()
  })

  it('does not render heatmap when contributionData is empty', () => {
    const stats = {
      total: 100,
    }

    const { queryByTestId } = render(
      <CardDetailsContributions
        hasContributions={true}
        contributionStats={stats}
        contributionData={{}}
      />
    )

    expect(screen.getByTestId('contribution-stats')).toBeInTheDocument()
    expect(queryByTestId('contribution-heatmap')).not.toBeInTheDocument()
  })

  it('does not render heatmap without startDate and endDate', () => {
    const stats = {
      total: 100,
    }

    const { queryByTestId } = render(
      <CardDetailsContributions
        hasContributions={true}
        contributionStats={stats}
        contributionData={{ '2024-01-01': 5 }}
      />
    )

    expect(screen.getByTestId('contribution-stats')).toBeInTheDocument()
    expect(queryByTestId('contribution-heatmap')).not.toBeInTheDocument()
  })

  it('renders with custom title', () => {
    const stats = {
      total: 50,
    }

    render(
      <CardDetailsContributions
        hasContributions={true}
        contributionStats={stats}
        title="Custom Activity Title"
      />
    )

    expect(screen.getByTestId('contribution-stats')).toBeInTheDocument()
  })

  it('renders nothing when hasContributions is false even with stats', () => {
    const { container } = render(
      <CardDetailsContributions hasContributions={false} contributionStats={{ total: 100 }} />
    )
    expect(container.firstChild).toBeNull()
  })
})
