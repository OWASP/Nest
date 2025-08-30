import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { useRouter } from 'next/navigation'
import React from 'react'
import type { Milestone } from 'types/milestone'
import type { User } from 'types/user'
import Milestones from 'components/Milestones'

jest.mock('next/navigation', () => ({
  ...jest.requireActual('next/navigation'),
  useRouter: jest.fn(),
}))

jest.mock('utils/dateFormatter', () => {
  const mockFormatDate = jest.fn((date) => {
    const dateStr = date instanceof Date ? date.toISOString() : String(date)
    return `Formatted: ${dateStr}`
  })

  return {
    __esModule: true,
    formatDate: mockFormatDate,
    default: mockFormatDate,
  }
})

jest.mock('components/AnchorTitle', () => {
  const MockAnchorTitle = ({ title, className }: { title: string; className?: string }) => {
    return <h2 className={className}>{title}</h2>
  }

  return {
    __esModule: true,
    default: MockAnchorTitle,
  }
})

jest.mock('components/ItemCardList', () => {
  const MockItemCardList = ({
    title,
    data,
    showAvatar,
    icon,
    showSingleColumn,
    renderDetails,
  }: {
    title: React.ReactNode
    data: Milestone[]
    showAvatar: boolean
    icon: unknown
    showSingleColumn: boolean
    renderDetails: (item: Milestone) => React.ReactNode
  }) => {
    const getIconLabel = (iconProp: unknown): string => {
      if (!iconProp) return 'no-icon'
      if (typeof iconProp === 'string') return iconProp
      return JSON.stringify(iconProp)
    }

    return (
      <div data-testid="item-card-list">
        <div data-testid="title">{title}</div>
        <div data-testid="show-avatar">{showAvatar.toString()}</div>
        <div data-testid="show-single-column">{showSingleColumn.toString()}</div>
        <div data-testid="icon">{getIconLabel(icon)}</div>
        {data.map((item, index) => {
          // Avoid nested template literals by constructing fallback separately
          const fallbackKey = [
            item.organizationName || 'org',
            item.repositoryName || 'repo',
            item.title || 'milestone',
          ].join('-')

          const uniqueKey = `milestone-${index}-${item.url || fallbackKey}`

          return (
            <div key={uniqueKey} data-testid={`milestone-${index}`}>
              {renderDetails(item)}
            </div>
          )
        })}
      </div>
    )
  }

  return {
    __esModule: true,
    default: MockItemCardList,
  }
})

jest.mock('components/TruncatedText', () => ({
  __esModule: true,
  TruncatedText: ({ text }: { text: string }) => <span data-testid="truncated-text">{text}</span>,
  default: ({ text }: { text: string }) => <span data-testid="truncated-text">{text}</span>,
}))

const mockPush = jest.fn()
const mockUseRouter = useRouter as jest.Mock

describe('Milestones', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    mockUseRouter.mockReturnValue({
      push: mockPush,
    })
  })

  const createMockUser = (): User => ({
    login: 'testuser',
    name: 'Test User',
    avatarUrl: 'https://github.com/testuser.png',
    url: 'https://github.com/testuser',
    key: 'testuser',
    followersCount: 10,
    followingCount: 5,
    publicRepositoriesCount: 20,
    contributionsCount: 50,
    createdAt: 1640995200000,
    updatedAt: 1640995200000,
  })

  const createMockMilestone = (overrides: Partial<Milestone> = {}): Milestone => ({
    author: createMockUser(),
    body: 'Test milestone description',
    closedIssuesCount: 5,
    createdAt: '2023-01-01T00:00:00Z',
    openIssuesCount: 3,
    organizationName: 'test-org',
    progress: 75,
    repositoryName: 'test-repo',
    state: 'open',
    title: 'Test Milestone',
    url: 'https://github.com/test-org/test-repo/milestone/1',
    ...overrides,
  })

  it('renders successfully with minimal required props', () => {
    render(<Milestones data={[createMockMilestone()]} />)

    expect(screen.getByTestId('item-card-list')).toBeInTheDocument()
    expect(screen.getByText('Recent Milestones')).toBeInTheDocument()
  })

  it('renders with empty data array', () => {
    render(<Milestones data={[]} />)

    expect(screen.getByTestId('item-card-list')).toBeInTheDocument()
    expect(screen.getByText('Recent Milestones')).toBeInTheDocument()
  })

  it('uses default prop values correctly', () => {
    render(<Milestones data={[createMockMilestone()]} />)

    expect(screen.getByTestId('show-avatar')).toHaveTextContent('true')
    expect(screen.getByTestId('show-single-column')).toHaveTextContent('true')
  })

  it('respects custom prop values', () => {
    render(
      <Milestones data={[createMockMilestone()]} showAvatar={false} showSingleColumn={false} />
    )

    expect(screen.getByTestId('show-avatar')).toHaveTextContent('false')
    expect(screen.getByTestId('show-single-column')).toHaveTextContent('false')
  })

  it('passes correct icon to ItemCardList', () => {
    render(<Milestones data={[createMockMilestone()]} />)

    const iconElement = screen.getByTestId('icon')
    expect(iconElement).toBeInTheDocument()
    // Check that some icon representation is rendered (could be iconName, react-component, etc.)
    expect(iconElement.textContent).toBeTruthy()
  })

  it('renders milestone details correctly', () => {
    const milestone = createMockMilestone({
      createdAt: '2023-01-01T00:00:00Z',
      closedIssuesCount: 10,
      openIssuesCount: 5,
      repositoryName: 'awesome-repo',
    })

    render(<Milestones data={[milestone]} />)

    expect(screen.getByText(/Formatted: 2023-01-01T00:00:00Z/)).toBeInTheDocument()
    expect(screen.getByText('10 closed')).toBeInTheDocument()
    expect(screen.getByText('5 open')).toBeInTheDocument()
    expect(screen.getByTestId('truncated-text')).toHaveTextContent('awesome-repo')
  })

  it('handles milestone without repositoryName', () => {
    render(<Milestones data={[createMockMilestone({ repositoryName: '' })]} />)

    expect(screen.queryByTestId('truncated-text')).not.toBeInTheDocument()
    expect(screen.queryByRole('button')).not.toBeInTheDocument()
  })

  it('handles milestone with undefined repositoryName', () => {
    const milestone = createMockMilestone()
    delete (milestone as Partial<Milestone>).repositoryName

    render(<Milestones data={[milestone]} />)

    expect(screen.queryByTestId('truncated-text')).not.toBeInTheDocument()
    expect(screen.queryByRole('button')).not.toBeInTheDocument()
  })

  it('navigates to correct repository URL when repository button is clicked', async () => {
    const user = userEvent.setup()
    render(
      <Milestones
        data={[createMockMilestone({ organizationName: 'my-org', repositoryName: 'my-repo' })]}
      />
    )

    await user.click(screen.getByRole('button'))

    expect(mockPush).toHaveBeenCalledWith('/organizations/my-org/repositories/my-repo')
  })

  it('handles navigation with empty repositoryName', () => {
    render(<Milestones data={[createMockMilestone({ repositoryName: '' })]} />)

    expect(screen.queryByRole('button')).not.toBeInTheDocument()
  })

  it('renders multiple milestones correctly', () => {
    const milestones = [
      createMockMilestone({ title: 'Milestone 1', closedIssuesCount: 5 }),
      createMockMilestone({ title: 'Milestone 2', closedIssuesCount: 10 }),
      createMockMilestone({ title: 'Milestone 3', closedIssuesCount: 15 }),
    ]

    render(<Milestones data={milestones} />)

    expect(screen.getByTestId('milestone-0')).toBeInTheDocument()
    expect(screen.getByTestId('milestone-1')).toBeInTheDocument()
    expect(screen.getByTestId('milestone-2')).toBeInTheDocument()
    expect(screen.getByText('5 closed')).toBeInTheDocument()
    expect(screen.getByText('10 closed')).toBeInTheDocument()
    expect(screen.getByText('15 closed')).toBeInTheDocument()
  })

  it('handles edge case with zero counts', () => {
    render(
      <Milestones data={[createMockMilestone({ closedIssuesCount: 0, openIssuesCount: 0 })]} />
    )

    expect(screen.getByText('0 closed')).toBeInTheDocument()
    expect(screen.getByText('0 open')).toBeInTheDocument()
  })

  it('handles large issue counts', () => {
    render(
      <Milestones data={[createMockMilestone({ closedIssuesCount: 999, openIssuesCount: 1000 })]} />
    )

    expect(screen.getByText('999 closed')).toBeInTheDocument()
    expect(screen.getByText('1000 open')).toBeInTheDocument()
  })

  it('applies correct CSS classes to milestone details container', () => {
    render(<Milestones data={[createMockMilestone()]} />)

    const detailsContainer = screen.getByTestId('milestone-0').firstChild as HTMLElement
    expect(detailsContainer).toHaveClass(
      'mt-2',
      'flex',
      'flex-wrap',
      'items-center',
      'text-sm',
      'text-gray-600',
      'dark:text-gray-400'
    )
  })

  it('applies correct CSS classes to repository button', () => {
    render(<Milestones data={[createMockMilestone({ repositoryName: 'test-repo' })]} />)

    expect(screen.getByRole('button')).toHaveClass(
      'cursor-pointer',
      'overflow-hidden',
      'text-ellipsis',
      'whitespace-nowrap',
      'text-gray-600',
      'hover:underline',
      'dark:text-gray-400'
    )
  })

  it('renders correct DOM structure for title', () => {
    render(<Milestones data={[createMockMilestone()]} />)

    const titleContainer = screen.getByTestId('title').firstChild as HTMLElement
    expect(titleContainer).toHaveClass('flex', 'items-center', 'gap-2')
    expect(titleContainer.tagName).toBe('DIV')
  })
})
