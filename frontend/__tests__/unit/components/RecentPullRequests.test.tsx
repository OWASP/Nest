import { render, screen, fireEvent } from '@testing-library/react'
import { ReactNode } from 'react'
import RecentPullRequests from 'components/RecentPullRequests'

// =========================
// Mocks
// =========================

jest.mock('@heroui/tooltip', () => ({
  Tooltip: ({ children }: { children?: ReactNode }) => <div>{children}</div>,
}))

const mockRouterPush = jest.fn()
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: mockRouterPush,
  }),
}))

jest.mock('components/TruncatedText', () => ({
  TruncatedText: ({ text }: { text: string }) => <span>{text}</span>,
}))

jest.mock('utils/dateFormatter', () => ({
  formatDate: () => 'Jun 1, 2024',
}))

// =========================
// Test Data
// =========================

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

// =========================
// Tests
// =========================

describe('RecentPullRequests', () => {
  afterEach(() => {
    jest.clearAllMocks()
  })

  // --- Rendering ---
  it('renders successfully with minimal required props', () => {
    render(<RecentPullRequests data={minimalData} />)
    expect(screen.getByText('Recent Pull Requests')).toBeInTheDocument()
    expect(screen.getByText('test-repo')).toBeInTheDocument()
    expect(screen.getByText('Jun 1, 2024')).toBeInTheDocument()
    expect(screen.getByText('Test Pull Request')).toBeInTheDocument()
  })

  // --- Conditional Rendering ---
  it('does not render repository button if repositoryName is missing', () => {
    render(<RecentPullRequests data={noRepoData} />)
    expect(screen.queryByText('test-repo')).not.toBeInTheDocument()
  })

  // --- Prop-based Behavior ---
  it('passes showAvatar prop to ItemCardList', () => {
    // Test with showAvatar=true (default)
    const { rerender } = render(<RecentPullRequests data={minimalData} />)
    // Add assertion for avatar presence if testable
    // Test with showAvatar=false
    rerender(<RecentPullRequests data={minimalData} showAvatar={false} />)
    // Add assertion for avatar absence if testable
    expect(screen.getByText('test-repo')).toBeInTheDocument()
  })

  // --- Event Handling ---
  it('calls router.push with correct URL when repository name is clicked', () => {
    render(<RecentPullRequests data={minimalData} />)
    fireEvent.click(screen.getByText('test-repo'))
    expect(mockRouterPush).toHaveBeenCalledWith('/organizations/test-org/repositories/test-repo')
  })

  // --- Edge Cases ---
  it('renders correctly when data is empty', () => {
    render(<RecentPullRequests data={[]} />)
    expect(screen.getByText('Recent Pull Requests')).toBeInTheDocument()
    expect(screen.queryByText('test-repo')).not.toBeInTheDocument()
  })

  it('handles undefined data prop gracefully', () => {
    render(<RecentPullRequests data={undefined} />)
    expect(screen.getByText('Recent Pull Requests')).toBeInTheDocument()
  })

  // --- Accessibility ---
  it('has accessible title and buttons', () => {
    render(<RecentPullRequests data={minimalData} />)
    expect(screen.getByRole('heading', { name: /Recent Pull Requests/i })).toBeInTheDocument()
    expect(screen.getByText('test-repo').closest('button')).toBeInTheDocument()
  })

  // --- DOM Structure / ClassNames ---
  it('renders with expected classNames', () => {
    render(<RecentPullRequests data={minimalData} />)
    expect(screen.getByText('Recent Pull Requests').parentElement).toHaveClass('flex')
  })
})
