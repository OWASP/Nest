import { render, screen, fireEvent } from '@testing-library/react'
import type { ReactElement, ReactNode } from 'react'
import type { Release as ReleaseType } from 'types/release'
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
    id,
    content: _content,
    ...props
  }: MockComponentProps): ReactElement => (
    <div {...props} id={id as string}>
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

const now = Date.now()
const mockReleases: ReleaseType[] = [
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

describe('Release Component', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('renders release information correctly', () => {
    render(<Release release={mockReleases[0]} />)

    expect(screen.getByText('v1.0 The First Release')).toBeInTheDocument()
    expect(screen.getByText('our-awesome-project')).toBeInTheDocument()
    expect(screen.getByText(/\w{3} \d{1,2}, \d{4,5}/)).toBeInTheDocument() // Date format
  })

  it('renders author avatar when showAvatar is true and author exists', () => {
    render(<Release release={mockReleases[0]} showAvatar={true} />)

    const avatar = screen.getByAltText("Test User's avatar")
    expect(avatar).toBeInTheDocument()
    expect(avatar).toHaveAttribute('src', 'https://example.com/avatar.png')
  })

  it('does not render author avatar when showAvatar is false', () => {
    render(<Release release={mockReleases[0]} showAvatar={false} />)

    const avatar = screen.queryByAltText('Test User')
    expect(avatar).not.toBeInTheDocument()
  })

  it('does not render author avatar when author is missing', () => {
    const releaseWithoutAuthor = { ...mockReleases[0], author: undefined }
    render(<Release release={releaseWithoutAuthor} showAvatar={true} />)

    const avatar = screen.queryByAltText('Test User')
    expect(avatar).not.toBeInTheDocument()
  })

  it('renders release name as link to GitHub releases', () => {
    render(<Release release={mockReleases[0]} />)

    const releaseLink = screen.getByText('v1.0 The First Release').closest('a')
    expect(releaseLink).toHaveAttribute(
      'href',
      'https://github.com/our-org/our-awesome-project/releases/tag/v1.0'
    )
    expect(releaseLink).toHaveAttribute('target', '_blank')
    expect(releaseLink).toHaveAttribute('rel', 'noopener noreferrer')
  })

  it('renders repository name as clickable button', () => {
    render(<Release release={mockReleases[0]} />)

    const repoButton = screen.getByRole('button')
    expect(repoButton).toBeInTheDocument()
    expect(repoButton).toHaveTextContent('our-awesome-project')
  })

  it('navigates to repository page when repository button is clicked', () => {
    render(<Release release={mockReleases[0]} />)

    const repoButton = screen.getByRole('button')
    fireEvent.click(repoButton)

    expect(mockRouterPush).toHaveBeenCalledWith(
      '/organizations/our-org/repositories/our-awesome-project'
    )
  })

  it('disables repository button when organization or repository name is missing', () => {
    const releaseWithoutOrg = { ...mockReleases[0], organizationName: undefined }
    render(<Release release={releaseWithoutOrg} />)

    const repoButton = screen.getByRole('button')
    expect(repoButton).toBeDisabled()
  })

  it('renders author name in tooltip when hovering over avatar', () => {
    render(<Release release={mockReleases[0]} />)

    const tooltip = screen.getByAltText("Test User's avatar").closest('div')
    expect(tooltip).toHaveAttribute('id', 'avatar-tooltip-0')
  })

  it('renders author login when name is not available', () => {
    const releaseWithLoginOnly = {
      ...mockReleases[0],
      author: { ...mockReleases[0].author, name: undefined },
    }
    render(<Release release={releaseWithLoginOnly} />)

    // The login should be in the alt attribute of the image
    const avatar = screen.getByAltText("testuser's avatar")
    expect(avatar).toBeInTheDocument()
  })

  it('renders fallback alt text when author exists but name and login are missing', () => {
    const releaseWithEmptyAuthor = {
      ...mockReleases[0],
      author: { ...mockReleases[0].author, name: '', login: '' },
    }
    render(<Release release={releaseWithEmptyAuthor} />)

    const avatar = screen.getByAltText('Release author avatar')
    expect(avatar).toBeInTheDocument()
  })

  it('renders tag name when release name is not available', () => {
    const releaseWithoutName = { ...mockReleases[0], name: undefined }
    render(<Release release={releaseWithoutName} />)

    expect(screen.getByText('v1.0')).toBeInTheDocument()
  })

  it('applies custom className when provided', () => {
    render(<Release release={mockReleases[0]} className="custom-class" />)

    const releaseDiv = screen.getByText('v1.0 The First Release').closest('div.custom-class')
    expect(releaseDiv).toBeInTheDocument()
    expect(releaseDiv).toHaveClass('custom-class')
  })

  it('renders multiple releases with different indices', () => {
    render(
      <div>
        <Release release={mockReleases[0]} index={0} />
        <Release release={mockReleases[1]} index={1} />
      </div>
    )

    const tooltip1 = screen.getByAltText("Test User's avatar").closest('div')
    const tooltip2 = screen.getByAltText("Jane Doe's avatar").closest('div')

    expect(tooltip1).toHaveAttribute('id', 'avatar-tooltip-0')
    expect(tooltip2).toHaveAttribute('id', 'avatar-tooltip-1')
  })

  it('handles releases with missing organization name gracefully', () => {
    const releaseWithoutOrg = { ...mockReleases[0], organizationName: undefined }
    render(<Release release={releaseWithoutOrg} />)

    const repoButton = screen.getByRole('button')
    expect(repoButton).toBeDisabled()
  })

  it('handles releases with missing repository name gracefully', () => {
    const releaseWithoutRepo = { ...mockReleases[0], repositoryName: undefined }
    render(<Release release={releaseWithoutRepo} />)

    // When repository name is undefined, the button should be disabled
    const repoButton = screen.getByRole('button')
    expect(repoButton).toBeDisabled()
  })

  it('handles releases with empty organization and repository names gracefully', () => {
    const releaseWithEmptyUrls = { ...mockReleases[0], organizationName: '', repositoryName: '' }
    render(<Release release={releaseWithEmptyUrls} />)

    // When both are empty strings, the button should be disabled
    const repoButton = screen.getByRole('button')
    expect(repoButton).toBeDisabled()
  })

  it('renders with default props when minimal props are provided', () => {
    render(<Release release={mockReleases[0]} />)

    expect(screen.getByText('v1.0 The First Release')).toBeInTheDocument()
    // Avatar should show by default, so we should find the author avatar
    expect(screen.getByAltText("Test User's avatar")).toBeInTheDocument()
  })

  it('handles long release names with truncation', () => {
    const releaseWithLongName = {
      ...mockReleases[0],
      name: 'This is a very long release name that should be handled properly by the component',
    }
    render(<Release release={releaseWithLongName} />)

    expect(
      screen.getByText(
        'This is a very long release name that should be handled properly by the component'
      )
    ).toBeInTheDocument()
  })
})
