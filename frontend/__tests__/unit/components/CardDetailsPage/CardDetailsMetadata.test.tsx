import { render, screen } from '@testing-library/react'
import React from 'react'
import '@testing-library/jest-dom'
import type { Stats } from 'types/card'
import type { Chapter } from 'types/chapter'
import CardDetailsMetadata from 'components/CardDetailsPage/CardDetailsMetadata'

jest.mock('react-icons/fa6', () => ({
  FaChartPie: () => <span data-testid="chart-pie-icon">ChartIcon</span>,
  FaRectangleList: () => <span data-testid="rectangle-list-icon">ListIcon</span>,
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

jest.mock('utils/urlIconMappings', () => ({
  getSocialIcon: (url: string) => {
    return () => (
      <span data-testid={`social-icon-${url}`}>
        {url.includes('github') ? 'GitHub' : url.includes('twitter') ? 'Twitter' : 'Link'}
      </span>
    )
  },
}))

describe('CardDetailsMetadata', () => {
  const mockStats: Stats[] = [
    {
      value: 100,
      unit: 'repositories',
      pluralizedName: 'Repositories',
      icon: 'FaGit',
    },
    {
      value: 50,
      unit: 'members',
      pluralizedName: 'Members',
      icon: 'FaUsers',
    },
  ]

  const mockGeoData: Chapter[] = [
    {
      id: '1',
      name: 'Chapter 1',
      location: 'City 1',
    },
    {
      id: '2',
      name: 'Chapter 2',
      location: 'City 2',
    },
  ]

  it('renders Details card when details prop is provided', () => {
    const details = [
      { label: 'Name', value: 'Test Name' },
      { label: 'Email', value: 'test@example.com' },
    ]

    render(<CardDetailsMetadata details={details} />)
    const secondaryCard = screen.getByTestId('secondary-card')
    expect(secondaryCard).toBeInTheDocument()
    expect(secondaryCard).toHaveTextContent('Name')
    expect(secondaryCard).toHaveTextContent('Test Name')
  })

  it('renders details with default "Unknown" when value is missing', () => {
    const details = [
      { label: 'Name', value: '' },
      { label: 'Empty Field', value: undefined as string | undefined },
    ]

    render(<CardDetailsMetadata details={details} />)
    const secondaryCard = screen.getByTestId('secondary-card')
    expect(secondaryCard).toHaveTextContent('Unknown')
  })

  it('renders LeadersList component for Leaders detail', () => {
    const details = [{ label: 'Leaders', value: 'leader1, leader2' }]

    render(<CardDetailsMetadata details={details} entityKey="test-entity" />)
    expect(screen.getByTestId('leaders-list')).toBeInTheDocument()
    expect(screen.getByText(/leader1, leader2/)).toBeInTheDocument()
  })

  it('renders Statistics card when showStatistics is true and stats provided', () => {
    render(<CardDetailsMetadata stats={mockStats} showStatistics={true} />)
    expect(screen.getAllByTestId('secondary-card').length).toBeGreaterThanOrEqual(1)
    expect(screen.getByText('Statistics')).toBeInTheDocument()
    expect(screen.getAllByTestId('info-block').length).toBe(2)
  })

  it('renders geolocation map when showGeolocation is true and geolocationData provided', () => {
    render(<CardDetailsMetadata geolocationData={mockGeoData} showGeolocation={true} />)
    expect(screen.getByTestId('chapter-map')).toBeInTheDocument()
    expect(screen.getByText('2 locations')).toBeInTheDocument()
  })

  it('renders social links when showSocialLinks is true', () => {
    const details = [{ label: 'Organization', value: 'Org Name' }]
    const socialLinks = ['https://github.com/test', 'https://twitter.com/test']

    render(
      <CardDetailsMetadata details={details} socialLinks={socialLinks} showSocialLinks={true} />
    )

    expect(screen.getByText('Social Links')).toBeInTheDocument()
    expect(screen.getByTestId('social-icon-https://github.com/test')).toBeInTheDocument()
    expect(screen.getByTestId('social-icon-https://twitter.com/test')).toBeInTheDocument()
  })

  it('does not render social links when socialLinks is empty array', () => {
    const details = [{ label: 'Organization', value: 'Org Name' }]

    render(<CardDetailsMetadata details={details} socialLinks={[]} showSocialLinks={true} />)

    expect(screen.queryByText('Social Links')).not.toBeInTheDocument()
  })
})
