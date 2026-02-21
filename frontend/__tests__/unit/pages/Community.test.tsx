import { render, screen } from '@testing-library/react'
import React from 'react'
import CommunityPage from 'app/community/page'

jest.mock('react-icons/fa', () => ({
  FaArrowRight: () => <span data-testid="icon-arrow-right" />,
  FaSlack: () => <span data-testid="icon-slack" />,
  FaChevronRight: () => <span data-testid="icon-chevron-right" />,
}))

jest.mock('react-icons/fa6', () => ({
  FaLocationDot: () => <span data-testid="icon-location" />,
  FaFolder: () => <span data-testid="icon-folder" />,
  FaPeopleGroup: () => <span data-testid="icon-people" />,
  FaBuilding: () => <span data-testid="icon-building" />,
  FaUsers: () => <span data-testid="icon-users" />,
  FaHandshakeAngle: () => <span data-testid="icon-handshake" />,
}))

jest.mock('components/SecondaryCard', () => ({
  __esModule: true,
  default: ({
    title,
    children,
    className,
  }: {
    title?: React.ReactNode
    children: React.ReactNode
    className?: string
  }) => (
    <div data-testid="secondary-card" className={className}>
      {title && <div data-testid="card-title">{title}</div>}
      {children}
    </div>
  ),
}))

jest.mock('components/AnchorTitle', () => ({
  __esModule: true,
  default: ({ title }: { title: string }) => <span data-testid="anchor-title">{title}</span>,
}))

jest.mock('wrappers/IconWrapper', () => ({
  IconWrapper: ({ icon: Icon, className }: { icon: React.ElementType; className: string }) => (
    <div data-testid="icon-wrapper" className={className}>
      <Icon />
    </div>
  ),
}))

jest.mock('utils/communityData', () => ({
  exploreCards: [
    {
      title: 'Test Chapter',
      description: 'Test Description',
      href: '/test-chapter',
      icon: () => <span data-testid="mock-icon" />,
      color: 'text-red-500',
    },
  ],
  engagementWays: [
    {
      title: 'Test Engagement',
      description: 'Test Engagement Description',
    },
  ],
  journeySteps: [
    {
      label: 'Test Step 1',
      description: 'Test Step 1 Description',
    },
    {
      label: 'Test Step 2',
      description: 'Test Step 2 Description',
    },
  ],
}))

describe('CommunityPage', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  test('renders the main page title and intro', () => {
    render(<CommunityPage />)

    expect(screen.getByRole('heading', { level: 1, name: /OWASP Community/i })).toBeInTheDocument()
    expect(screen.getByText(/Explore the vibrant OWASP community/i)).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /Chapters/i })).toHaveAttribute('href', '/chapters')
    expect(screen.getByRole('link', { name: /Members/i })).toHaveAttribute('href', '/members')
    expect(screen.getByRole('link', { name: /Organizations/i })).toHaveAttribute(
      'href',
      '/organizations'
    )
  })

  test('renders Explore Resources section correctly', () => {
    render(<CommunityPage />)

    expect(screen.getByTestId('anchor-title')).toHaveTextContent('Explore Resources')
    expect(screen.getByText('Test Chapter')).toBeInTheDocument()
    expect(screen.getByText('Test Description')).toBeInTheDocument()
    const link = screen.getByRole('link', { name: /Test Chapter/i })
    expect(link).toHaveAttribute('href', '/test-chapter')
    expect(screen.getByTestId('icon-chevron-right')).toBeInTheDocument()
  })

  test('renders Ways to Engage section correctly', () => {
    render(<CommunityPage />)

    expect(screen.getByText('Ways to Engage')).toBeInTheDocument()
    expect(screen.getByText('Test Engagement')).toBeInTheDocument()
    expect(screen.getByText('Test Engagement Description')).toBeInTheDocument()
  })

  test('renders Community Journey section correctly', () => {
    render(<CommunityPage />)

    expect(screen.getByText('Your Community Journey')).toBeInTheDocument()

    expect(screen.getAllByText('Test Step 1')).toHaveLength(2)
    expect(screen.getAllByText('Test Step 1 Description')).toHaveLength(2)
    expect(screen.getAllByText('Test Step 2')).toHaveLength(2)

    expect(screen.getAllByText('1')).toHaveLength(2)
    expect(screen.getAllByText('2')).toHaveLength(2)
  })

  test('renders Join the Community section correctly', () => {
    render(<CommunityPage />)

    expect(screen.getByText('Join the Community')).toBeInTheDocument()
    expect(screen.getByTestId('icon-slack')).toBeInTheDocument()
    expect(screen.getByText(/Connect with fellow security professionals/i)).toBeInTheDocument()

    const slackLink = screen.getByRole('link', {
      name: /Join OWASP Community Slack workspace/i,
    })
    expect(slackLink).toHaveAttribute('href', 'https://owasp.org/slack/invite')
    expect(screen.getByTestId('icon-arrow-right')).toBeInTheDocument()
  })

  test('renders Final Call to Action section correctly', () => {
    render(<CommunityPage />)

    expect(
      screen.getByRole('heading', { level: 2, name: /Ready to Get Involved\?/i })
    ).toBeInTheDocument()
    expect(screen.getByText(/Join thousands of security professionals/i)).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /contributing to a project/i })).toHaveAttribute(
      'href',
      '/contribute'
    )
  })
})
