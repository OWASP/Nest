import type { IconDefinition } from '@fortawesome/fontawesome-svg-core'
import { render, screen, fireEvent, act } from '@testing-library/react'
import type { ReactElement, ReactNode } from 'react'
import type { Release as ReleaseTypes } from 'types/release'
import Release from 'components/Release'

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

// Mock FontAwesome icons - FIXED VERSION
jest.mock('@fortawesome/react-fontawesome', () => ({
  FontAwesomeIcon: ({ icon, className, ...props }: MockComponentProps): ReactElement => (
    <span
      className={`mock-icon ${className}`}
      data-icon={(icon as IconDefinition)?.iconName || 'unknown'}
      {...props}
    />
  ),
}))

jest.mock('@fortawesome/free-solid-svg-icons', () => ({
  faCalendar: { iconName: 'calendar' } as IconDefinition,
  faFolderOpen: { iconName: 'folder-open' } as IconDefinition,
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
  }: MockComponentProps): ReactElement => (
    <div data-testid="tooltip" data-tooltip-content={_content} {...props}>
      {children}
    </div>
  ),
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

jest.mock('next/link', () => ({
  __esModule: true,
  default: ({ children, href, ...props }: MockComponentProps): ReactElement => (
    <a href={href as string} {...props}>
      {children}
    </a>
  ),
}))

// Mock utility functions
jest.mock('utils/dateFormatter', () => ({
  formatDate: (timestamp: number) => new Date(timestamp).toLocaleDateString(),
}))

jest.mock('components/TruncatedText', () => ({
  TruncatedText: ({ text }: { text: string }): ReactElement => <span>{text}</span>,
}))

const now = Date.now()

const mockRelease: ReleaseTypes = {
  name: 'v1.0.0 - Major Release',
  publishedAt: now,
  repositoryName: 'test-repository',
  organizationName: 'test-organization',
  tagName: 'v1.0.0',
  isPreRelease: false,
  author: {
    login: 'testuser',
    name: 'Test User',
    avatarUrl: 'https://example.com/avatar.png',
    key: 'testuser',
    contributionsCount: 10,
    createdAt: now - 86400000, // 1 day ago
    followersCount: 5,
    followingCount: 3,
    publicRepositoriesCount: 2,
    url: 'https://github.com/testuser',
  },
}

describe('Release Component', () => {
  beforeEach(() => {
    mockRouterPush.mockClear()
  })

  it('should render release with all elements when showAvatar is true', () => {
    act(() => {
      render(<Release release={mockRelease} showAvatar={true} />)
    })

    const releaseLink = screen.getByRole('link', { name: /v1.0.0 - Major Release/i })
    expect(releaseLink).toBeInTheDocument()
    expect(releaseLink).toHaveAttribute(
      'href',
      'https://github.com/test-organization/test-repository/releases/tag/v1.0.0'
    )
    expect(releaseLink).toHaveAttribute('target', '_blank')
    expect(releaseLink).toHaveAttribute('rel', 'noopener noreferrer')

    const authorLink = screen.getByRole('link', { name: /Test User/i })
    expect(authorLink).toBeInTheDocument()
    expect(authorLink).toHaveAttribute('href', '/members/testuser')

    const avatarImage = screen.getByAltText('Test User')
    expect(avatarImage).toBeInTheDocument()
    expect(avatarImage).toHaveAttribute('src', 'https://example.com/avatar.png')

    expect(screen.getByText(new Date(now).toLocaleDateString())).toBeInTheDocument()

    const repoButton = screen.getByRole('button', { name: /test-repository/i })
    expect(repoButton).toBeInTheDocument()
    expect(repoButton).not.toBeDisabled()

    expect(screen.getByTestId('tooltip')).toBeInTheDocument()
    expect(screen.getByText(/test-repository/i)).toBeInTheDocument()
  })

  it('should not render avatar when showAvatar is false', () => {
    act(() => {
      render(<Release release={mockRelease} showAvatar={false} />)
    })

    expect(screen.queryByRole('link', { name: /Test User/i })).not.toBeInTheDocument()
    expect(screen.queryByAltText('Test User')).not.toBeInTheDocument()
    expect(screen.queryByTestId('tooltip')).not.toBeInTheDocument()
  })

  it('should use default showAvatar value (true) when not provided', () => {
    act(() => {
      render(<Release release={mockRelease} />)
    })

    const authorLink = screen.getByRole('link', { name: /Test User/i })
    expect(authorLink).toBeInTheDocument()
  })

  it('should navigate to repository page when repository name is clicked', () => {
    act(() => {
      render(<Release release={mockRelease} />)
    })

    const repoButton = screen.getByRole('button', { name: /test-repository/i })

    act(() => {
      fireEvent.click(repoButton)
    })

    expect(mockRouterPush).toHaveBeenCalledTimes(1)
    expect(mockRouterPush).toHaveBeenCalledWith(
      '/organizations/test-organization/repositories/test-repository'
    )
  })

  it('should handle release with missing name (fallback to tagName)', () => {
    const releaseWithoutName = {
      ...mockRelease,
      name: null,
    }

    act(() => {
      render(<Release release={releaseWithoutName} />)
    })

    const releaseLink = screen.getByRole('link', { name: /v1.0.0/i })
    expect(releaseLink).toBeInTheDocument()
  })

  it('should handle release with missing author', () => {
    const releaseWithoutAuthor = {
      ...mockRelease,
      author: null,
    }

    act(() => {
      render(<Release release={releaseWithoutAuthor} />)
    })

    expect(screen.queryByRole('link', { name: /Test User/i })).not.toBeInTheDocument()
    expect(screen.queryByAltText('Test User')).not.toBeInTheDocument()

    expect(screen.getByText(/v1.0.0 - Major Release/i)).toBeInTheDocument()
  })

  it('should handle author with missing name (fallback to login)', () => {
    const releaseWithAuthorLogin = {
      ...mockRelease,
      author: {
        ...mockRelease.author,
        name: null,
      },
    }

    act(() => {
      render(<Release release={releaseWithAuthorLogin} />)
    })

    const authorLink = screen.getByRole('link', { name: /testuser/i })
    expect(authorLink).toBeInTheDocument()

    const avatarImage = screen.getByAltText('testuser')
    expect(avatarImage).toBeInTheDocument()
  })

  it('should handle author with missing login', () => {
    const releaseWithoutLogin = {
      ...mockRelease,
      author: {
        ...mockRelease.author,
        login: null,
      },
    }

    act(() => {
      render(<Release release={releaseWithoutLogin} />)
    })

    const links = screen.getAllByRole('link')
    const authorLink = links.find((link) => link.getAttribute('href') === '#')
    expect(authorLink).toBeInTheDocument()
    expect(authorLink).toHaveAttribute('href', '#')
  })

  it('should disable repository button when organization name is missing', () => {
    const releaseWithoutOrg = {
      ...mockRelease,
      organizationName: null,
    }

    act(() => {
      render(<Release release={releaseWithoutOrg} />)
    })

    const repoButton = screen.getByRole('button', { name: /test-repository/i })
    expect(repoButton).toBeDisabled()

    act(() => {
      fireEvent.click(repoButton)
    })

    expect(mockRouterPush).not.toHaveBeenCalled()
  })

  it('should disable repository button when repository name is missing', () => {
    const releaseWithoutRepo = {
      ...mockRelease,
      repositoryName: null,
    }

    act(() => {
      render(<Release release={releaseWithoutRepo} />)
    })

    const repoButton = screen.getByRole('button')
    expect(repoButton).toBeDisabled()

    act(() => {
      fireEvent.click(repoButton)
    })

    expect(mockRouterPush).not.toHaveBeenCalled()
  })

  it('should not navigate when both organization and repository names are missing', () => {
    const releaseWithoutOrgAndRepo = {
      ...mockRelease,
      organizationName: '',
      repositoryName: '',
    }

    act(() => {
      render(<Release release={releaseWithoutOrgAndRepo} />)
    })

    const repoButton = screen.getByRole('button')

    act(() => {
      fireEvent.click(repoButton)
    })

    expect(mockRouterPush).not.toHaveBeenCalled()
  })

  // ENHANCED TEST: Test empty string handling specifically
  it('should handle empty string values properly', () => {
    const releaseWithEmptyStrings = {
      ...mockRelease,
      name: '',
      organizationName: '',
      repositoryName: '',
      author: {
        ...mockRelease.author,
        name: '',
        login: '',
      },
    }

    act(() => {
      render(<Release release={releaseWithEmptyStrings} />)
    })

    // Should fallback to tagName when name is empty
    const releaseLink = screen.getByRole('link', { name: /v1.0.0/i })
    expect(releaseLink).toBeInTheDocument()

    // Button should be disabled when repo/org names are empty
    const repoButton = screen.getByRole('button')
    expect(repoButton).toBeDisabled()

    // Author link should have href="#" when login is empty
    const links = screen.getAllByRole('link')
    const authorLink = links.find((link) => link.getAttribute('href') === '#')
    expect(authorLink).toBeInTheDocument()
    expect(authorLink).toHaveAttribute('href', '#')
  })

  // ENHANCED TEST: Test undefined values specifically
  it('should handle undefined values properly', () => {
    const releaseWithUndefinedValues = {
      ...mockRelease,
      name: undefined,
      organizationName: undefined,
      repositoryName: undefined,
      author: {
        ...mockRelease.author,
        name: undefined,
        login: undefined,
      },
    }

    act(() => {
      render(<Release release={releaseWithUndefinedValues} />)
    })

    // Should fallback to tagName when name is undefined
    const releaseLink = screen.getByRole('link', { name: /v1.0.0/i })
    expect(releaseLink).toBeInTheDocument()
  })

  it('should render with proper CSS classes for styling', () => {
    let container: HTMLElement
    act(() => {
      const result = render(<Release release={mockRelease} />)
      container = result.container
    })

    const cardElement = container.querySelector(
      '.mb-4.w-full.rounded-lg.bg-gray-200.p-4.dark\\:bg-gray-700'
    )
    expect(cardElement).toBeInTheDocument()

    const flexContainer = container.querySelector('.flex.w-full.flex-col.justify-between')
    expect(flexContainer).toBeInTheDocument()
  })

  it('should render FontAwesome icons correctly', () => {
    act(() => {
      render(<Release release={mockRelease} />)
    })

    const calendarIcon = screen.getByText('', { selector: '[data-icon="calendar"]' })
    const folderIcon = screen.getByText('', { selector: '[data-icon="folder-open"]' })

    expect(calendarIcon).toBeInTheDocument()
    expect(folderIcon).toBeInTheDocument()
  })

  it('should have proper tooltip attributes', () => {
    act(() => {
      render(<Release release={mockRelease} />)
    })

    const tooltip = screen.getByTestId('tooltip')
    expect(tooltip).toHaveAttribute('data-tooltip-content', 'Test User')
  })

  // ENHANCED TEST: Test tooltip with author.login fallback
  it('should show tooltip with login when name is not available', () => {
    const releaseWithLoginOnly = {
      ...mockRelease,
      author: {
        ...mockRelease.author,
        name: null,
      },
    }

    act(() => {
      render(<Release release={releaseWithLoginOnly} />)
    })

    const tooltip = screen.getByTestId('tooltip')
    expect(tooltip).toHaveAttribute('data-tooltip-content', 'testuser')
  })

  it('should handle long release names with TruncatedText', () => {
    const releaseWithLongName = {
      ...mockRelease,
      name: 'This is a very long release name that should be truncated properly to prevent layout issues and maintain consistent UI design across different screen sizes and devices',
    }

    act(() => {
      render(<Release release={releaseWithLongName} />)
    })

    expect(screen.getByText(/This is a very long release name/)).toBeInTheDocument()
  })

  it('should handle long repository names with TruncatedText', () => {
    const releaseWithLongRepoName = {
      ...mockRelease,
      repositoryName: 'this-is-a-very-long-repository-name-that-should-be-truncated-properly',
    }

    act(() => {
      render(<Release release={releaseWithLongRepoName} />)
    })

    expect(screen.getByText(/this-is-a-very-long-repository-name/)).toBeInTheDocument()
  })

  it('should format date correctly', () => {
    const specificDate = new Date('2023-12-25').getTime()
    const releaseWithSpecificDate = {
      ...mockRelease,
      publishedAt: specificDate,
    }

    act(() => {
      render(<Release release={releaseWithSpecificDate} />)
    })

    expect(screen.getByText(new Date(specificDate).toLocaleDateString())).toBeInTheDocument()
  })

  // ENHANCED TEST: Test image attributes
  it('should render image with correct attributes', () => {
    act(() => {
      render(<Release release={mockRelease} />)
    })

    const avatarImage = screen.getByAltText('Test User')
    expect(avatarImage).toHaveAttribute('src', 'https://example.com/avatar.png')
    expect(avatarImage).toHaveAttribute('width', '24')
    expect(avatarImage).toHaveAttribute('height', '24')
  })

  // ENHANCED TEST: Test accessibility
  it('should have proper accessibility attributes', () => {
    act(() => {
      render(<Release release={mockRelease} />)
    })

    const releaseLink = screen.getByRole('link', { name: /v1.0.0 - Major Release/i })
    expect(releaseLink).toHaveAttribute('target', '_blank')
    expect(releaseLink).toHaveAttribute('rel', 'noopener noreferrer')
  })

  // ENHANCED TEST: Test button states
  it('should handle button states correctly based on data availability', () => {
    const releaseWithPartialData = {
      ...mockRelease,
      organizationName: 'test-org',
      repositoryName: null,
    }

    act(() => {
      render(<Release release={releaseWithPartialData} />)
    })

    const repoButton = screen.getByRole('button')
    expect(repoButton).toBeDisabled()
  })
})
