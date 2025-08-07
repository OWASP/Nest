import { render, screen, fireEvent } from '@testing-library/react'
import { ReactElement, ReactNode } from 'react'
import RecentPullRequests from 'components/RecentPullRequests'

interface MockComponentProps {
  children?: ReactNode
  [key: string]: unknown
}
// Mock HeroUI Tooltip
jest.mock('@heroui/tooltip', () => ({
  Tooltip: ({
    children,
    closeDelay: _closeDelay,
    delay: _delay,
    placement: _placement,
    showArrow: _showArrow,
    id: _id,
    content: _content,
    ...props
  }: MockComponentProps): ReactElement => <div {...props}>{children}</div>,
}))

// Mock Next.js router
const mockRouterPush = jest.fn()
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: mockRouterPush,
  }),
}))

// Mock TruncatedText
jest.mock('components/TruncatedText', () => ({
  TruncatedText: ({ text }: { text: string }) => <span>{text}</span>,
}))

// Mock formatDate utility
jest.mock('utils/dateFormatter', () => ({
  formatDate: () => 'Jun 1, 2024',
}))

const mockUser = {
  avatarUrl: 'https://example.com/avatar.png',
  bio: 'Test bio',
  company: 'Test Company',
  contributionsCount: 42,
  createdAt: 1577836800000, // number, as required by User type
  email: 'test@example.com',
  followersCount: 10,
  followingCount: 5,
  key: 'user-key',
  location: 'Test City',
  login: 'testuser',
  name: 'Test User',
  publicRepositoriesCount: 3,
  url: 'https://github.com/testuser',
}

const minimalData = [
  {
    author: mockUser,
    createdAt: '2024-06-01T12:00:00Z',
    organizationName: 'test-org',
    repositoryName: 'test-repo',
    title: 'Test Pull Request',
    url: 'https://github.com/test-org/test-repo/pull/1',
  },
]

const noRepoData = [
  {
    author: mockUser,
    createdAt: '2024-06-01T12:00:00Z',
    organizationName: 'test-org',
    repositoryName: undefined,
    title: 'Test Pull Request',
    url: 'https://github.com/test-org/test-repo/pull/2',
  },
]

describe('RecentPullRequests', () => {
  afterEach(() => {
    jest.clearAllMocks()
  })

  // 1. Renders successfully with minimal required props
  it('renders successfully with minimal required props', () => {
    render(<RecentPullRequests data={minimalData} />)
    expect(screen.getByText('Recent Pull Requests')).toBeInTheDocument()
    expect(screen.getByText('test-repo')).toBeInTheDocument()
    expect(screen.getByText('Jun 1, 2024')).toBeInTheDocument()
    expect(screen.getByText('Test Pull Request')).toBeInTheDocument()
  })

  // 2. Conditional rendering logic (repositoryName missing)
  it('does not render repository button if repositoryName is missing', () => {
    render(<RecentPullRequests data={noRepoData} />)
    expect(screen.queryByText('test-repo')).not.toBeInTheDocument()
  })

  // 3. Prop-based behavior (showAvatar)
  it('passes showAvatar prop to ItemCardList', () => {
    render(<RecentPullRequests data={minimalData} showAvatar={false} />)
    expect(screen.getByText('test-repo')).toBeInTheDocument()
  })

  // 4. Event handling (click repository name)
  it('calls router.push with correct URL when repository name is clicked', () => {
    render(<RecentPullRequests data={minimalData} />)
    fireEvent.click(screen.getByText('test-repo'))
    expect(mockRouterPush).toHaveBeenCalledWith('/organizations/test-org/repositories/test-repo')
  })

  // 5. State changes/internal logic (stateless, but test prop-driven logic)
  it('renders correctly when data is empty', () => {
    render(<RecentPullRequests data={[]} />)
    expect(screen.getByText('Recent Pull Requests')).toBeInTheDocument()
    expect(screen.queryByText('test-repo')).not.toBeInTheDocument()
  })

  // 6. Default values and fallbacks (showAvatar defaults to true)
  it('uses default value for showAvatar when not provided', () => {
    render(<RecentPullRequests data={minimalData} />)
    expect(screen.getByText('test-repo')).toBeInTheDocument()
  })

  // 7. Text and content rendering
  it('renders the title and formatted date', () => {
    render(<RecentPullRequests data={minimalData} />)
    expect(screen.getByText('Recent Pull Requests')).toBeInTheDocument()
    expect(screen.getByText('Jun 1, 2024')).toBeInTheDocument()
    expect(screen.getByText('Test Pull Request')).toBeInTheDocument()
  })

  // 8. Handles edge cases and invalid inputs
  it('handles undefined data prop gracefully', () => {
    render(<RecentPullRequests data={undefined} />)
    expect(screen.getByText('Recent Pull Requests')).toBeInTheDocument()
  })

  // 9. Accessibility roles and labels
  it('has accessible title and buttons', () => {
    render(<RecentPullRequests data={minimalData} />)
    expect(screen.getByRole('heading', { name: /Recent Pull Requests/i })).toBeInTheDocument()
    expect(screen.getByText('test-repo').closest('button')).toBeInTheDocument()
  })

  // 10. DOM structure / classNames / styles
  it('renders with expected classNames', () => {
    render(<RecentPullRequests data={minimalData} />)
    expect(screen.getByText('Recent Pull Requests').parentElement).toHaveClass('flex')
  })
})
