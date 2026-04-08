import { render, screen } from '@testing-library/react'
import React from 'react'
import '@testing-library/jest-dom'
import CardDetailsContributions from 'components/CardDetailsPage/CardDetailsContributions'

jest.mock('components/ContributionHeatmap', () => ({
  __esModule: true,
  default: ({ stats }: { stats: object }) => (
    <div data-testid="contribution-heatmap">Heatmap: {JSON.stringify(stats)}</div>
  ),
}))

jest.mock('components/ContributionStats', () => ({
  __esModule: true,
  default: ({ stats }: { stats: object }) => (
    <div data-testid="contribution-stats">Stats: {JSON.stringify(stats)}</div>
  ),
}))

jest.mock('utils/contributionDataUtils', () => ({
  shouldShowContributions: jest.fn((type: string) => type === 'project'),
}))

jest.mock('next/link', () => {
  return ({ children, href }: { children: React.ReactNode; href: string }) => (
    <a href={href}>{children}</a>
  )
})

describe('CardDetailsContributions', () => {
  afterEach(() => {
    jest.clearAllMocks()
  })

  it('renders nothing when no contribution stats provided', () => {
    const { container } = render(
      <CardDetailsContributions type="project" hasContributions={false} />
    )
    expect(container.firstChild).toBeNull()
  })

  it('renders nothing when shouldShowContributions returns false', () => {
    const { container } = render(
      <CardDetailsContributions
        type="repository"
        hasContributions={true}
        contributionStats={{
          totalContributions: 100,
          heatmapData: [],
        }}
      />
    )
    expect(container.firstChild).toBeNull()
  })

  it('renders contribution stats when stats provided for project type', () => {
    const stats = {
      totalContributions: 150,
      heatmapData: [1, 2, 3, 4, 5],
    }

    render(
      <CardDetailsContributions type="project" hasContributions={true} contributionStats={stats} />
    )

    expect(screen.getByTestId('contribution-stats')).toBeInTheDocument()
  })

  it('renders contribution heatmap with required props', () => {
    render(
      <CardDetailsContributions
        type="project"
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
      totalContributions: 100,
      averageContribution: 50,
      heatmapData: [],
    }

    render(
      <CardDetailsContributions
        type="project"
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

  it('does not render when hasContributions is false', () => {
    const { container } = render(
      <CardDetailsContributions
        type="project"
        hasContributions={false}
        contributionStats={{ totalContributions: 100 }}
      />
    )
    expect(container.firstChild).toBeNull()
  })

  it('does not render for repository type even with contributions', () => {
    const { container } = render(
      <CardDetailsContributions
        type="repository"
        hasContributions={true}
        contributionStats={{ totalContributions: 100 }}
      />
    )
    expect(container.firstChild).toBeNull()
  })

  it('does not render for program type even with contributions', () => {
    const { container } = render(
      <CardDetailsContributions
        type="program"
        hasContributions={true}
        contributionStats={{ totalContributions: 100 }}
      />
    )
    expect(container.firstChild).toBeNull()
  })

  it('renders for chapter type with contributions', () => {
    const stats = {
      totalContributions: 50,
      heatmapData: [],
    }

    render(
      <CardDetailsContributions type="chapter" hasContributions={true} contributionStats={stats} />
    )

    expect(screen.getByTestId('contribution-stats')).toBeInTheDocument()
  })
})
