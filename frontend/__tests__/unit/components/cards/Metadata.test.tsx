import { render, screen } from '@testing-library/react'
import React from 'react'
import '@testing-library/jest-dom'
import { FaCode, FaUsers } from 'react-icons/fa6'
import type { Stats } from 'types/card'
import type { Chapter } from 'types/chapter'
import Metadata from 'components/cards/Metadata'

jest.mock('react-icons/fa6', () => ({
  FaChartPie: () => <span data-testid="chart-pie-icon">ChartIcon</span>,
  FaRectangleList: () => <span data-testid="rectangle-list-icon">ListIcon</span>,
  FaChartLine: () => <span data-testid="chart-line-icon">LineIcon</span>,
  FaStar: () => <span data-testid="star-icon">StarIcon</span>,
}))

jest.mock('components/AnchorTitle', () => ({
  __esModule: true,
  default: ({ title }: { title: string }) => <span data-testid="anchor-title">{title}</span>,
}))

jest.mock('components/ChapterMapWrapper', () => ({
  __esModule: true,
  default: ({ geoLocData }: { geoLocData: Chapter[] }) => (
    <div data-testid="chapter-map">{geoLocData.length} locations</div>
  ),
}))

jest.mock('components/InfoBlock', () => ({
  __esModule: true,
  default: ({
    value,
    unit,
    pluralizedName,
  }: {
    value: number
    unit: string
    pluralizedName: string
  }) => (
    <div data-testid="info-block">
      {value} {unit} {pluralizedName}
    </div>
  ),
}))

jest.mock('components/LeadersList', () => ({
  __esModule: true,
  default: ({ leaders, entityKey }: { leaders: string; entityKey: string }) => (
    <div data-testid="leaders-list">
      {leaders} (key: {entityKey})
    </div>
  ),
}))

jest.mock('components/SecondaryCard', () => ({
  __esModule: true,
  default: ({
    title,
    children,
    className,
  }: {
    title: React.ReactNode
    children: React.ReactNode
    className?: string
  }) => (
    <div data-testid="secondary-card" className={className}>
      {title}
      {children}
    </div>
  ),
}))

const getSocialPlatformName = (url: string): string => {
  if (url.includes('github')) {
    return 'GitHub'
  }
  if (url.includes('twitter')) {
    return 'Twitter'
  }
  return 'Link'
}

jest.mock('utils/urlIconMappings', () => ({
  getSocialIcon: (url: string) => {
    return () => <span data-testid={`social-icon-${url}`}>{getSocialPlatformName(url)}</span>
  },
}))

describe('Metadata', () => {
  const mockStats: Stats[] = [
    {
      value: 100,
      unit: 'repositories',
      pluralizedName: 'Repositories',
      icon: FaCode,
    },
    {
      value: 50,
      unit: 'members',
      pluralizedName: 'Members',
      icon: FaUsers,
    },
  ]

  const mockGeoData: Chapter[] = [
    {
      key: 'chapter-1',
      name: 'Chapter 1',
      suggestedLocation: 'City 1',
    },
    {
      key: 'chapter-2',
      name: 'Chapter 2',
      suggestedLocation: 'City 2',
    },
  ]

  it('renders Details card when details prop is provided', () => {
    const details = [
      { label: 'Name', value: 'Test Name' },
      { label: 'Email', value: 'test@example.com' },
    ]

    render(<Metadata details={details} />)
    const secondaryCard = screen.getByTestId('secondary-card')
    expect(secondaryCard).toBeInTheDocument()
    expect(secondaryCard).toHaveClass('md:col-span-7')
    expect(secondaryCard).toHaveTextContent('Name')
    expect(secondaryCard).toHaveTextContent('Test Name')
  })

  it('renders details with default "Unknown" when value is missing', () => {
    const details = [
      { label: 'Name', value: '' },
      { label: 'Empty Field', value: undefined as string | undefined },
    ]

    render(<Metadata details={details} />)
    const secondaryCard = screen.getByTestId('secondary-card')
    expect(secondaryCard).toHaveTextContent('Unknown')
  })

  it('renders LeadersList component for Leaders detail', () => {
    const details = [{ label: 'Leaders', value: 'leader1, leader2' }]

    render(<Metadata details={details} entityKey="test-entity" />)
    expect(screen.getByTestId('leaders-list')).toBeInTheDocument()
    expect(screen.getByText(/leader1, leader2/)).toBeInTheDocument()
  })

  it('renders Statistics card when showStatistics is true and stats provided', () => {
    render(<Metadata stats={mockStats} showStatistics={true} />)
    const cards = screen.getAllByTestId('secondary-card')
    expect(cards[0]).toHaveClass('md:col-span-5')
    expect(screen.getByText('Statistics')).toBeInTheDocument()
    expect(screen.getAllByTestId('info-block').length).toBe(2)
  })

  it('uses full-width details column when statistics are not shown', () => {
    render(<Metadata details={[{ label: 'Name', value: 'Test' }]} showStatistics={false} />)
    expect(screen.getByTestId('secondary-card')).toHaveClass('md:col-span-7')
    expect(screen.queryByText('Statistics')).not.toBeInTheDocument()
  })

  it('renders geolocation map when showGeolocation is true and geolocationData provided', () => {
    render(<Metadata geolocationData={mockGeoData} showGeolocation={true} />)
    expect(screen.getByTestId('chapter-map')).toBeInTheDocument()
    expect(screen.getByText('2 locations')).toBeInTheDocument()
  })

  it('renders social links when showSocialLinks is true', () => {
    const details = [{ label: 'Organization', value: 'Org Name' }]
    const socialLinks = ['https://github.com/test', 'https://twitter.com/test']

    render(<Metadata details={details} socialLinks={socialLinks} showSocialLinks={true} />)

    expect(screen.getByText('Social Links')).toBeInTheDocument()
    expect(screen.getByTestId('social-icon-https://github.com/test')).toBeInTheDocument()
    expect(screen.getByTestId('social-icon-https://twitter.com/test')).toBeInTheDocument()
  })

  it('does not render social links when socialLinks is empty array', () => {
    const details = [{ label: 'Organization', value: 'Org Name' }]

    render(<Metadata details={details} socialLinks={[]} showSocialLinks={true} />)

    expect(screen.queryByText('Social Links')).not.toBeInTheDocument()
  })

  it('renders contribution score and tier level when both are provided', () => {
    const details = [{ label: 'Name', value: 'Test User' }]
    render(<Metadata details={details} contributionScore={1234} tierLevel="level 1" />)

    expect(screen.getByText('Contribution Score')).toBeInTheDocument()
    expect(screen.getByText((1234).toLocaleString())).toBeInTheDocument()
    expect(screen.getByText('Tier Level')).toBeInTheDocument()
    expect(screen.getByText('level 1')).toBeInTheDocument()
  })

  it('renders only contribution score when tier level is not provided', () => {
    const details = [{ label: 'Name', value: 'Test User' }]
    render(<Metadata details={details} contributionScore={5678} />)

    expect(screen.getByText('Contribution Score')).toBeInTheDocument()
    expect(screen.getByText((5678).toLocaleString())).toBeInTheDocument()
    expect(screen.queryByText('Tier Level')).not.toBeInTheDocument()
  })

  it('renders only tier level when contribution score is not provided', () => {
    const details = [{ label: 'Name', value: 'Test User' }]
    render(<Metadata details={details} tierLevel="level 2" />)

    expect(screen.queryByText('Contribution Score')).not.toBeInTheDocument()
    expect(screen.getByText('Tier Level')).toBeInTheDocument()
    expect(screen.getByText('level 2')).toBeInTheDocument()
  })

  it('renders neither contribution score nor tier level when neither is provided', () => {
    const details = [{ label: 'Name', value: 'Test User' }]
    render(<Metadata details={details} />)

    expect(screen.queryByText('Contribution Score')).not.toBeInTheDocument()
    expect(screen.queryByText('Tier Level')).not.toBeInTheDocument()
  })
})
