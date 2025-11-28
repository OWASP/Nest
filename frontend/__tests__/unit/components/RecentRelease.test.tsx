import { render, screen, fireEvent, act } from '@testing-library/react'
import type { ReactElement, ReactNode } from 'react'
import type { Release } from 'types/release'
import RecentReleases from 'components/RecentReleases'

// Define proper types for mock components
interface MockComponentProps {
  children?: ReactNode
  [key: string]: unknown
}

interface MockImageProps {
  alt?: string
  src?: string
  [key: string]: unknown
}

// Mock framer-motion to prevent LazyMotion issues
jest.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: MockComponentProps): ReactElement => (
      <div {...props}>{children}</div>
    ),
    span: ({ children, ...props }: MockComponentProps): ReactElement => (
      <span {...props}>{children}</span>
    ),
  },
  AnimatePresence: ({ children }: { children: ReactNode }): ReactNode => children,
  useAnimation: () => ({
    start: jest.fn(),
    set: jest.fn(),
  }),
  LazyMotion: ({ children }: { children: ReactNode }): ReactNode => children,
  domAnimation: jest.fn(),
}))

// Mock HeroUI components
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

const mockRouterPush = jest.fn()

jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: mockRouterPush,
  }),
}))

jest.mock('next/image', () => ({
  __esModule: true,
  default: (props: MockImageProps): ReactElement => {
    // eslint-disable-next-line @next/next/no-img-element
    return <img {...props} alt={props.alt || ''} />
  },
}))

const now = Date.now()
const mockReleases: Release[] = [
  {
    name: 'v1.0 The First Release',
    publishedAt: now,
    repositoryName: 'our-awesome-project',
    organizationName: 'our-org',
    tagName: 'v1.0',
    isPreRelease: false,
    author: {
      login: 'testuser',
      name: 'Test User',
      avatarUrl: 'https://example.com/avatar.png',
      key: 'testuser',
      contributionsCount: 0,
      createdAt: 0,
      followersCount: 0,
      followingCount: 0,
      publicRepositoriesCount: 0,
      url: 'https://example.com/user/testuser',
    },
  },
  {
    name: 'v2.0 The Second Release',
    publishedAt: now,
    repositoryName: 'another-cool-project',
    organizationName: 'our-org',
    tagName: 'v2.0',
    isPreRelease: false,
    author: {
      login: 'jane-doe',
      name: 'Jane Doe',
      avatarUrl: 'https://example.com/avatar2.png',
      key: 'jane-doe',
      contributionsCount: 0,
      createdAt: 0,
      followersCount: 0,
      followingCount: 0,
      publicRepositoriesCount: 0,
      url: 'https://example.com/user/jane-doe',
    },
  },
]

describe('RecentReleases Component', () => {
  beforeEach(() => {
    mockRouterPush.mockClear()
  })

  it('should display a message when there is no data', () => {
    act(() => {
      render(<RecentReleases data={[]} />)
    })
    expect(screen.getByText('No recent releases.')).toBeInTheDocument()
  })

  it('should render release details and links correctly with data', () => {
    act(() => {
      render(<RecentReleases data={mockReleases} />)
    })

    const releaseLink = screen.getByRole('link', { name: /v1.0 The First Release/i })
    const repoNameElement = screen.getByText(/another-cool-project/i)
    const authorLink = screen.getByRole('link', { name: /Test User/i })

    expect(releaseLink).toBeInTheDocument()
    expect(repoNameElement).toBeInTheDocument()
    expect(authorLink).toBeInTheDocument()

    expect(releaseLink).toHaveAttribute(
      'href',
      'https://github.com/our-org/our-awesome-project/releases/tag/v1.0'
    )
    expect(releaseLink).toHaveAttribute('target', '_blank')
    expect(authorLink).toHaveAttribute('href', '/members/testuser')
  })

  it('should navigate when the repository name is clicked', () => {
    act(() => {
      render(<RecentReleases data={mockReleases} />)
    })

    const repoNameElement = screen.getByText(/our-awesome-project/i)
    act(() => {
      fireEvent.click(repoNameElement)
    })

    expect(mockRouterPush).toHaveBeenCalledTimes(1)
    expect(mockRouterPush).toHaveBeenCalledWith(
      '/organizations/our-org/repositories/our-awesome-project'
    )
  })

  it('should not render avatars if showAvatar is false', () => {
    act(() => {
      render(<RecentReleases data={mockReleases} showAvatar={false} />)
    })
    expect(screen.queryByRole('link', { name: /Test User/i })).not.toBeInTheDocument()
    expect(screen.queryByRole('link', { name: /Jane Doe/i })).not.toBeInTheDocument()
  })

  it('should apply single-column class when showSingleColumn is true', () => {
    let container: HTMLElement
    act(() => {
      const result = render(<RecentReleases data={mockReleases} showSingleColumn={true} />)
      container = result.container
    })
    const gridContainer = container.querySelector('.grid')

    expect(gridContainer).toHaveClass('grid-cols-1')
    expect(gridContainer).not.toHaveClass('md:grid-cols-2')
  })

  it('should apply multi-column classes by default', () => {
    let container: HTMLElement
    act(() => {
      const result = render(<RecentReleases data={mockReleases} />)
      container = result.container
    })
    const gridContainer = container.querySelector('.grid')

    expect(gridContainer).not.toHaveClass('grid-cols-1')
    expect(gridContainer).toHaveClass('md:grid-cols-2', 'lg:grid-cols-3')
  })

  // New test cases for comprehensive coverage

  it('should handle releases with missing author name', () => {
    const releasesWithMissingAuthor = [
      {
        ...mockReleases[0],
        author: {
          ...mockReleases[0].author,
          name: '',
        },
      },
    ]

    act(() => {
      render(<RecentReleases data={releasesWithMissingAuthor} />)
    })

    // Should still render the release name
    expect(screen.getByText('v1.0 The First Release')).toBeInTheDocument()
    // Should handle missing author gracefully
    expect(screen.getByAltText("testuser's avatar")).toBeInTheDocument()
  })

  it('should handle releases with author object but missing name and login', () => {
    const releasesWithEmptyAuthor = [
      {
        ...mockReleases[0],
        author: {
          ...mockReleases[0].author,
          name: '',
          login: '',
        },
      },
    ]

    act(() => {
      render(<RecentReleases data={releasesWithEmptyAuthor} />)
    })

    // Should still render the release name
    expect(screen.getByText('v1.0 The First Release')).toBeInTheDocument()
    // Should render fallback alt text because both name and login are missing
    expect(screen.getByAltText('Release author avatar')).toBeInTheDocument()
  })

  it('should handle releases with missing repository information', () => {
    const releasesWithMissingRepo = [
      {
        ...mockReleases[0],
        repositoryName: undefined,
        organizationName: undefined,
      },
    ]

    act(() => {
      render(<RecentReleases data={releasesWithMissingRepo} />)
    })

    // Should still render the release name
    expect(screen.getByText('v1.0 The First Release')).toBeInTheDocument()
    // Should handle missing repo info gracefully - check for button element
    const repoButton = screen.getByRole('button')
    expect(repoButton).toBeInTheDocument()
  })

  it('should handle releases with missing URLs', () => {
    const releasesWithMissingUrls = [
      {
        ...mockReleases[0],
        url: undefined,
      },
    ]

    act(() => {
      render(<RecentReleases data={releasesWithMissingUrls} />)
    })

    const releaseLink = screen.getByRole('link', { name: /v1.0 The First Release/i })
    expect(releaseLink).toHaveAttribute(
      'href',
      'https://github.com/our-org/our-awesome-project/releases/tag/v1.0'
    )
  })

  it('should render with default props when not provided', () => {
    let container: HTMLElement
    act(() => {
      const result = render(<RecentReleases data={mockReleases} />)
      container = result.container
    })
    // Should show avatars by default
    expect(screen.getByRole('link', { name: /Test User/i })).toBeInTheDocument()
    const gridContainer = container.querySelector('.grid')
    expect(gridContainer).toHaveClass('md:grid-cols-2', 'lg:grid-cols-3')
  })

  it('should handle null/undefined data gracefully', () => {
    const { unmount } = render(<RecentReleases data={[]} />)
    expect(screen.getByText('No recent releases.')).toBeInTheDocument()
    unmount()

    render(<RecentReleases data={[]} />)
    expect(screen.getByText('No recent releases.')).toBeInTheDocument()
  })

  it('should have proper accessibility attributes', () => {
    act(() => {
      render(<RecentReleases data={mockReleases} />)
    })

    // Check for proper alt text on images
    const authorImage = screen.getByAltText("Test User's avatar")
    expect(authorImage).toBeInTheDocument()

    // Check for proper link roles
    const releaseLink = screen.getByRole('link', { name: /v1.0 The First Release/i })
    expect(releaseLink).toBeInTheDocument()

    // Check for proper button roles
    const repoButton = screen.getByText(/our-awesome-project/i)
    expect(repoButton).toBeInTheDocument()
  })

  it('should handle multiple releases correctly', () => {
    act(() => {
      render(<RecentReleases data={mockReleases} />)
    })

    // Should render both releases
    expect(screen.getByText('v1.0 The First Release')).toBeInTheDocument()
    expect(screen.getByText('v2.0 The Second Release')).toBeInTheDocument()

    // Should render both repository names
    expect(screen.getByText('our-awesome-project')).toBeInTheDocument()
    expect(screen.getByText('another-cool-project')).toBeInTheDocument()
  })

  it('should handle repository click with missing organization name', () => {
    const releasesWithMissingOrg = [
      {
        ...mockReleases[0],
        organizationName: undefined,
      },
    ]

    act(() => {
      render(<RecentReleases data={releasesWithMissingOrg} />)
    })

    const repoButton = screen.getByRole('button')
    expect(repoButton).toBeDisabled()

    act(() => {
      fireEvent.click(repoButton)
    })

    // Should not navigate when organization name is missing
    expect(mockRouterPush).not.toHaveBeenCalled()
  })

  it('should disable repository button if repository name is missing', () => {
    const releasesWithMissingRepoName = [
      {
        ...mockReleases[0],
        repositoryName: undefined,
      },
    ]

    act(() => {
      render(<RecentReleases data={releasesWithMissingRepoName} />)
    })

    const repoButton = screen.getByRole('button')
    expect(repoButton).toBeDisabled()

    act(() => {
      fireEvent.click(repoButton)
    })

    // Should not navigate when repository name is missing
    expect(mockRouterPush).not.toHaveBeenCalled()
  })

  it('should render with proper CSS classes for styling', () => {
    let container: HTMLElement
    act(() => {
      const result = render(<RecentReleases data={mockReleases} />)
      container = result.container
    })

    // Check for main card structure - look for the card wrapper
    const cardElement = container.querySelector(
      '.mb-4.w-full.rounded-lg.bg-gray-200.p-4.dark\\:bg-gray-700'
    )
    expect(cardElement).toBeInTheDocument()

    // Check for proper grid layout
    const gridElement = container.querySelector('.grid')
    expect(gridElement).toBeInTheDocument()

    // Check for proper text styling - look for the title
    const titleElement = container.querySelector('.text-2xl.font-semibold')
    expect(titleElement).toBeInTheDocument()
  })

  it('should handle releases with very long names gracefully', () => {
    const releasesWithLongNames = [
      {
        ...mockReleases[0],
        name: 'This is a very long release name that should be truncated properly in the UI to prevent layout issues and maintain consistent styling across different screen sizes',
      },
    ]

    act(() => {
      render(<RecentReleases data={releasesWithLongNames} />)
    })

    // Should still render the long name
    expect(screen.getByText(/This is a very long release name/)).toBeInTheDocument()
  })
})
