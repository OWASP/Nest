import { render, screen } from '@testing-library/react'
import MetricsCard from 'components/MetricsCard'
import '@testing-library/jest-dom'

describe('MetricsCard', () => {
  const baseMetric = {
    projectKey: 'test-project',
    projectName: 'Test Project',
    starsCount: 42,
    forksCount: 13,
    contributorsCount: 5,
    createdAt: '2023-03-25T12:00:00Z',
    score: 80,
  }

  it('renders successfully with valid props', () => {
    render(<MetricsCard metric={baseMetric} />)
    expect(screen.getByText('Test Project')).toBeInTheDocument()
    expect(screen.getByText('42')).toBeInTheDocument()
    expect(screen.getByText('13')).toBeInTheDocument()
    expect(screen.getByText('5')).toBeInTheDocument()
    expect(screen.getByText('Mar 25, 2023')).toBeInTheDocument()
    expect(screen.getByText('80')).toBeInTheDocument()
  })

  it('renders "No name" when projectName is empty', () => {
    render(<MetricsCard metric={{ ...baseMetric, projectName: '' }} />)
    expect(screen.getByText('No name')).toBeInTheDocument()
  })

  it('uses green styling for score >= 75', () => {
    render(<MetricsCard metric={{ ...baseMetric, score: 90 }} />)
    const score = screen.getByText('90')
    expect(score).toHaveClass('text-green-900')
  })
  
  it('uses orange styling for 50 <= score < 75', () => {
    render(<MetricsCard metric={{ ...baseMetric, score: 60 }} />)
    const score = screen.getByText('60')
    expect(score).toHaveClass('text-orange-900')
  })
  
  it('uses red styling for score < 50', () => {
    render(<MetricsCard metric={{ ...baseMetric, score: 30 }} />)
    const score = screen.getByText('30')
    expect(score).toHaveClass('text-red-900')
  })
  
  it('uses green styling for score exactly at 75 boundary', () => {
    render(<MetricsCard metric={{ ...baseMetric, score: 75 }} />)
    const score = screen.getByText('75')
    expect(score).toHaveClass('text-green-900')
  })

  it('uses orange styling for score exactly at 50 boundary', () => {
    render(<MetricsCard metric={{ ...baseMetric, score: 50 }} />)
    const score = screen.getByText('50')
    expect(score).toHaveClass('text-orange-900')
  })

  it('renders correct link based on projectKey', () => {
    render(<MetricsCard metric={baseMetric} />)
    const link = screen.getByRole('link')
    expect(link).toHaveAttribute('href', '/projects/dashboard/metrics/test-project')
  })

  it('updates correctly when props change', () => {
    const { rerender } = render(<MetricsCard metric={baseMetric} />)
    expect(screen.getByText('Test Project')).toBeInTheDocument()
    expect(screen.getByText('80')).toBeInTheDocument()

    rerender(
      <MetricsCard
        metric={{
          ...baseMetric,
          projectKey: 'another-project',
          projectName: 'Updated Project',
          score: 55,
        }}
      />
    )

    expect(screen.getByText('Updated Project')).toBeInTheDocument()
    expect(screen.getByText('55')).toBeInTheDocument()
    const updatedLink = screen.getByRole('link')
    expect(updatedLink).toHaveAttribute('href', '/projects/dashboard/metrics/another-project')
  })
})
