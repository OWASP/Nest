import { faCircleExclamation } from '@fortawesome/free-solid-svg-icons'
import React from 'react'
import { render, screen, cleanup } from 'wrappers/testUtil'
import type { Issue } from 'types/issue'
import type { Milestone } from 'types/milestone'
import type { PullRequest } from 'types/pullRequest'
import type { Release } from 'types/release'
import ItemCardList from 'components/ItemCardList'
import '@testing-library/jest-dom'

jest.mock('next/link', () => ({
  __esModule: true,
  default: ({
    children,
    href,
    target,
    className,
  }: {
    children: React.ReactNode
    href: string
    target?: string
    className?: string
  }) => (
    <a href={href} target={target} className={className} data-testid="link">
      {children}
    </a>
  ),
}))

jest.mock('next/image', () => ({
  __esModule: true,
  default: ({
    src,
    alt,
    width,
    height,
    className,
  }: {
    src: string
    alt: string
    width: number
    height: number
    className?: string
  }) => (
    // eslint-disable-next-line @next/next/no-img-element
    <img
      src={src}
      alt={alt}
      width={width}
      height={height}
      className={className}
      data-testid="avatar-image"
    />
  ),
}))

jest.mock('@heroui/tooltip', () => ({
  Tooltip: ({
    children,
    content,
    id,
  }: {
    children: React.ReactNode
    content: string
    id?: string
  }) => (
    <div data-testid="tooltip" data-content={content} data-id={id}>
      {children}
    </div>
  ),
}))

jest.mock('components/SecondaryCard', () => ({
  __esModule: true,
  default: ({
    children,
    title,
    icon,
  }: {
    children: React.ReactNode
    title?: React.ReactNode
    icon?: { iconName: string }
  }) => (
    <div data-testid="secondary-card">
      {title && (
        <div data-testid="card-title">
          {icon && <span data-testid="card-icon">{icon.iconName}</span>}
          {title}
        </div>
      )}
      {children}
    </div>
  ),
}))

jest.mock('components/TruncatedText', () => ({
  TruncatedText: ({ text }: { text: string }) => <span data-testid="truncated-text">{text}</span>,
}))

const mockUser = {
  avatarUrl: 'https://github.com/author1.png',
  contributionsCount: 50,
  createdAt: 1640995200000,
  followersCount: 100,
  followingCount: 50,
  key: 'author1',
  login: 'author1',
  name: 'Author One',
  publicRepositoriesCount: 25,
  url: 'https://github.com/author1',
}

const mockIssue: Issue = {
  author: mockUser,
  createdAt: 1640995200000,
  hint: 'Good first issue',
  labels: ['bug', 'help-wanted'],
  number: '123',
  organizationName: 'test-org',
  projectName: 'Test Project',
  projectUrl: 'https://github.com/test-org/test-project',
  summary: 'This is a test issue summary',
  title: 'Test Issue Title',
  updatedAt: 1641081600000,
  url: 'https://github.com/test-org/test-project/issues/123',
  objectID: 'issue-123',
}

const mockMilestone: Milestone = {
  author: {
    ...mockUser,
    login: 'author2',
    name: 'Author Two',
    key: 'author2',
    avatarUrl: 'https://github.com/author2.png',
    url: 'https://github.com/author2',
  },
  body: 'Milestone description',
  closedIssuesCount: 5,
  createdAt: '2022-01-01T00:00:00Z',
  openIssuesCount: 3,
  organizationName: 'test-org',
  progress: 62.5,
  repositoryName: 'test-repo',
  state: 'open',
  title: 'Version 1.0',
  url: 'https://github.com/test-org/test-repo/milestone/1',
}

const mockPullRequest: PullRequest = {
  id: 'mock-pull-request-id',
  author: {
    ...mockUser,
    login: 'author3',
    name: 'Author Three',
    key: 'author3',
    avatarUrl: 'https://github.com/author3.png',
    url: 'https://github.com/author3',
  },
  createdAt: '2022-01-01T00:00:00Z',
  organizationName: 'test-org',
  repositoryName: 'test-repo',
  title: 'Add new feature',
  url: 'https://github.com/test-org/test-repo/pull/456',
  state: 'open',
  mergedAt: '2022-01-02T00:00:00Z',
}

const mockRelease: Release = {
  author: {
    ...mockUser,
    login: 'author4',
    name: 'Author Four',
    key: 'author4',
    avatarUrl: 'https://github.com/author4.png',
    url: 'https://github.com/author4',
  },
  isPreRelease: false,
  name: 'v1.0.0',
  organizationName: 'test-org',
  publishedAt: 1640995200000,
  repositoryName: 'test-repo',
  tagName: 'v1.0.0',
}

describe('ItemCardList Component', () => {
  const defaultProps = {
    title: 'Test Title',
    data: [mockIssue],
    renderDetails: jest.fn((item) => (
      <div data-testid="render-details">
        <span>Created: {item.createdAt}</span>
        <span>Org: {item.organizationName}</span>
      </div>
    )),
  }

  afterEach(() => {
    cleanup()
    jest.clearAllMocks()
  })

  describe('Renders successfully with minimal required props', () => {
    it('renders with valid data', () => {
      render(<ItemCardList {...defaultProps} />)

      expect(screen.getByTestId('secondary-card')).toBeInTheDocument()
      expect(screen.getByTestId('card-title')).toBeInTheDocument()
      expect(screen.getByText('Test Title')).toBeInTheDocument()
      expect(screen.getByTestId('avatar-image')).toBeInTheDocument()
      expect(screen.getByTestId('truncated-text')).toBeInTheDocument()
      expect(screen.getByTestId('render-details')).toBeInTheDocument()
    })

    it('renders with empty data', () => {
      render(<ItemCardList {...defaultProps} title="Empty List" data={[]} />)

      expect(screen.getByTestId('secondary-card')).toBeInTheDocument()
      expect(screen.getByText('Nothing to display.')).toBeInTheDocument()
      expect(screen.queryByTestId('avatar-image')).not.toBeInTheDocument()
    })

    it('renders with all props provided', () => {
      render(
        <ItemCardList
          title="Complete List"
          data={[mockIssue]}
          icon={faCircleExclamation}
          renderDetails={defaultProps.renderDetails}
          showAvatar={true}
          showSingleColumn={false}
        />
      )

      expect(screen.getByTestId('secondary-card')).toBeInTheDocument()
      expect(screen.getByTestId('card-icon')).toBeInTheDocument()
      expect(screen.getByTestId('avatar-image')).toBeInTheDocument()
    })
  })

  describe('Conditional rendering logic', () => {
    test.each([
      [[], 'Empty List'],
      [null, 'Null Data'],
      [undefined, 'Undefined Data'],
    ])('renders "Nothing to display." when data is %s', (data, testName) => {
      render(
        <ItemCardList
          title={testName}
          data={data as Issue[] | Milestone[] | PullRequest[] | Release[] | null}
          renderDetails={defaultProps.renderDetails}
        />
      )

      expect(screen.getByText('Nothing to display.')).toBeInTheDocument()
      expect(screen.queryByTestId('avatar-image')).not.toBeInTheDocument()
      expect(screen.queryByTestId('tooltip')).not.toBeInTheDocument()
    })

    it('conditionally renders avatar when showAvatar is true', () => {
      render(
        <ItemCardList
          title="Avatar should be visible"
          data={[mockIssue]}
          renderDetails={defaultProps.renderDetails}
          showAvatar={true}
        />
      )

      expect(screen.getByTestId('avatar-image')).toBeInTheDocument()
      expect(screen.getByTestId('tooltip')).toBeInTheDocument()
    })

    it('conditionally renders avatar when showAvatar is false', () => {
      render(
        <ItemCardList
          title="Avatar should not be visible"
          data={[mockIssue]}
          renderDetails={defaultProps.renderDetails}
          showAvatar={false}
        />
      )

      expect(screen.queryByTestId('avatar-image')).not.toBeInTheDocument()
      expect(screen.queryByTestId('tooltip')).not.toBeInTheDocument()
    })

    test.each([
      [true, 'Single Column'],
      [false, 'Multi Column'],
    ])('applies correct layout when showSingleColumn is %s', (showSingleColumn, layoutType) => {
      render(
        <ItemCardList
          title={layoutType}
          data={[mockIssue]}
          renderDetails={defaultProps.renderDetails}
          showSingleColumn={showSingleColumn}
        />
      )

      expect(screen.getByTestId('secondary-card')).toBeInTheDocument()
      expect(screen.getByTestId('truncated-text')).toBeInTheDocument()
    })

    it('conditionally renders card icon when icon prop is provided', () => {
      render(
        <ItemCardList
          title="With Icon"
          data={[mockIssue]}
          icon={faCircleExclamation}
          renderDetails={defaultProps.renderDetails}
        />
      )

      expect(screen.getByTestId('card-icon')).toBeInTheDocument()
    })

    it('conditionally renders card icon when icon prop is undefined', () => {
      render(
        <ItemCardList
          title="Without Icon"
          data={[mockIssue]}
          icon={undefined}
          renderDetails={defaultProps.renderDetails}
        />
      )

      expect(screen.queryByTestId('card-icon')).not.toBeInTheDocument()
    })
  })

  describe('Prop-based behavior', () => {
    it('renders custom title correctly', () => {
      const customTitle = <span data-testid="custom-title">Custom Title Element</span>

      render(
        <ItemCardList
          title={customTitle}
          data={[mockIssue]}
          renderDetails={defaultProps.renderDetails}
        />
      )

      expect(screen.getByTestId('custom-title')).toBeInTheDocument()
      expect(screen.getByText('Custom Title Element')).toBeInTheDocument()
    })

    it('renders different data types correctly - Issues', () => {
      render(
        <ItemCardList
          title="Issues"
          data={[mockIssue]}
          renderDetails={defaultProps.renderDetails}
        />
      )

      expect(screen.getByTestId('truncated-text')).toHaveTextContent('Test Issue Title')
      expect(defaultProps.renderDetails).toHaveBeenCalledWith(
        expect.objectContaining({
          title: 'Test Issue Title',
          organizationName: 'test-org',
        })
      )
    })

    it('renders different data types correctly - Milestones', () => {
      render(
        <ItemCardList
          title="Milestones"
          data={[mockMilestone]}
          renderDetails={defaultProps.renderDetails}
        />
      )

      expect(screen.getByTestId('truncated-text')).toHaveTextContent('Version 1.0')
      expect(defaultProps.renderDetails).toHaveBeenCalledWith(
        expect.objectContaining({
          title: 'Version 1.0',
          organizationName: 'test-org',
        })
      )
    })

    it('renders different data types correctly - Pull Requests', () => {
      render(
        <ItemCardList
          title="Pull Requests"
          data={[mockPullRequest]}
          renderDetails={defaultProps.renderDetails}
        />
      )

      expect(screen.getByTestId('truncated-text')).toHaveTextContent('Add new feature')
      expect(defaultProps.renderDetails).toHaveBeenCalledWith(
        expect.objectContaining({
          title: 'Add new feature',
          organizationName: 'test-org',
        })
      )
    })

    it('renders different data types correctly - Releases', () => {
      render(
        <ItemCardList
          title="Releases"
          data={[mockRelease]}
          renderDetails={defaultProps.renderDetails}
        />
      )

      expect(screen.getByTestId('truncated-text')).toHaveTextContent('v1.0.0')
      expect(defaultProps.renderDetails).toHaveBeenCalledWith(
        expect.objectContaining({
          name: 'v1.0.0',
          organizationName: 'test-org',
        })
      )
    })

    it('calls renderDetails function for each item', () => {
      const multipleItems = [
        mockIssue,
        { ...mockIssue, title: 'Second Issue', objectID: 'issue-456' },
      ]

      render(
        <ItemCardList
          title="Multiple Items"
          data={multipleItems}
          renderDetails={defaultProps.renderDetails}
        />
      )

      expect(defaultProps.renderDetails).toHaveBeenCalledTimes(2)
      expect(defaultProps.renderDetails).toHaveBeenNthCalledWith(1, mockIssue)
      expect(defaultProps.renderDetails).toHaveBeenNthCalledWith(
        2,
        expect.objectContaining({ title: 'Second Issue' })
      )
    })
  })

  describe('Event handling', () => {
    it('renders clickable links for item titles', () => {
      render(
        <ItemCardList
          title="Clickable Items"
          data={[mockIssue]}
          renderDetails={defaultProps.renderDetails}
        />
      )

      const titleLinks = screen.getAllByTestId('link')
      const titleLink = titleLinks.find((link) => link.getAttribute('href') === mockIssue.url)

      expect(titleLink).toBeInTheDocument()
      expect(titleLink).toHaveAttribute('href', mockIssue.url)
      expect(titleLink).toHaveAttribute('target', '_blank')
    })

    it('renders clickable avatar links', () => {
      render(
        <ItemCardList
          title="Clickable Avatars"
          data={[mockIssue]}
          renderDetails={defaultProps.renderDetails}
          showAvatar={true}
        />
      )

      const avatarLinks = screen.getAllByTestId('link')
      const avatarLink = avatarLinks.find(
        (link) => link.getAttribute('href') === `/members/${mockIssue.author.login}`
      )

      expect(avatarLink).toBeInTheDocument()
      expect(avatarLink).toHaveAttribute('href', `/members/${mockIssue.author.login}`)
    })
  })

  describe('Default values and fallbacks', () => {
    it('uses default values for optional props', () => {
      render(
        <ItemCardList
          title="Default Props"
          data={[mockIssue]}
          renderDetails={defaultProps.renderDetails}
        />
      )

      expect(screen.getByTestId('avatar-image')).toBeInTheDocument()
      expect(screen.getByTestId('secondary-card')).toBeInTheDocument()
    })

    it('falls back to item name when title is not available', () => {
      const itemWithoutTitle = { ...mockRelease, title: undefined }

      render(
        <ItemCardList
          title="Name Fallback"
          data={[itemWithoutTitle]}
          renderDetails={defaultProps.renderDetails}
        />
      )

      expect(screen.getByTestId('truncated-text')).toHaveTextContent('v1.0.0')
    })

    it('handles missing author name gracefully', () => {
      const itemWithoutAuthorName = {
        ...mockIssue,
        author: { ...mockIssue.author, name: '' },
      }

      render(
        <ItemCardList
          title="Missing Author Name"
          data={[itemWithoutAuthorName]}
          renderDetails={defaultProps.renderDetails}
          showAvatar={true}
        />
      )

      const tooltip = screen.getByTestId('tooltip')
      expect(tooltip).toHaveAttribute('data-content', mockIssue.author.login)
    })

    it('handles missing item url gracefully', () => {
      const itemWithoutUrl = { ...mockIssue, url: '' }

      render(
        <ItemCardList
          title="Missing URL"
          data={[itemWithoutUrl]}
          renderDetails={defaultProps.renderDetails}
        />
      )

      const titleLinks = screen.getAllByTestId('link')
      const titleLink = titleLinks.find((link) => link.textContent?.includes('Test Issue Title'))

      expect(titleLink).toHaveAttribute('href', '')
    })
  })

  describe('Text and content rendering', () => {
    it('renders item titles correctly', () => {
      render(
        <ItemCardList
          title="Title Rendering"
          data={[mockIssue]}
          renderDetails={defaultProps.renderDetails}
        />
      )

      expect(screen.getByTestId('truncated-text')).toHaveTextContent('Test Issue Title')
    })

    it('renders custom renderDetails content', () => {
      const customRenderDetails = (item: {
        createdAt: string
        commentsCount: number
        organizationName: string
        publishedAt: string
        repositoryName: string
        tagName: string
        openIssuesCount: number
        closedIssuesCount: number
        title?: string
        name?: string
        author: {
          avatarUrl: string
          login: string
          name: string
        }
      }) => (
        <div data-testid="custom-details">
          <span>
            Custom content for{' '}
            {(item as { title?: string }).title || (item as { name?: string }).name}
          </span>
        </div>
      )

      render(
        <ItemCardList
          title="Custom Details"
          data={[mockIssue]}
          renderDetails={customRenderDetails}
        />
      )

      expect(screen.getByTestId('custom-details')).toBeInTheDocument()
      expect(screen.getByText('Custom content for Test Issue Title')).toBeInTheDocument()
    })

    it('displays author names in tooltips', () => {
      render(
        <ItemCardList
          title="Author Tooltips"
          data={[mockIssue]}
          renderDetails={defaultProps.renderDetails}
          showAvatar={true}
        />
      )

      const tooltip = screen.getByTestId('tooltip')
      expect(tooltip).toHaveAttribute('data-content', mockIssue.author.name)
    })
  })

  describe('Edge cases and invalid inputs', () => {
    it('handles missing required fields', () => {
      const incompleteItem = {
        author: {
          ...mockUser,
          login: 'test',
          avatarUrl: 'https://github.com/test.png',
          name: 'Test User',
        },
        title: 'Incomplete Item',
        url: 'https://github.com/test/repo/issue/1',
      } as Issue

      render(
        <ItemCardList
          title="Incomplete Items"
          data={[incompleteItem]}
          renderDetails={defaultProps.renderDetails}
        />
      )

      expect(screen.getByTestId('truncated-text')).toHaveTextContent('Incomplete Item')
      expect(defaultProps.renderDetails).toHaveBeenCalledWith(incompleteItem)
    })

    it('handles very long titles', () => {
      const longTitleItem = {
        ...mockIssue,
        title:
          'This is a very long title that should be truncated when displayed in the component to prevent layout issues',
      }

      render(
        <ItemCardList
          title="Long Titles"
          data={[longTitleItem]}
          renderDetails={defaultProps.renderDetails}
        />
      )

      expect(screen.getByTestId('truncated-text')).toBeInTheDocument()
    })

    it('handles large datasets', () => {
      const largeDataset = Array(100)
        .fill(null)
        .map((_, index) => ({
          ...mockIssue,
          title: `Issue ${index}`,
          objectID: `issue-${index}`,
        }))

      render(
        <ItemCardList
          title="Large Dataset"
          data={largeDataset}
          renderDetails={defaultProps.renderDetails}
        />
      )

      expect(screen.getAllByTestId('truncated-text')).toHaveLength(100)
      expect(defaultProps.renderDetails).toHaveBeenCalledTimes(100)
    })
  })

  describe('Accessibility', () => {
    it('provides proper alt text for avatar images', () => {
      render(
        <ItemCardList
          title="Accessibility Test"
          data={[mockIssue]}
          renderDetails={defaultProps.renderDetails}
          showAvatar={true}
        />
      )

      const avatarImage = screen.getByTestId('avatar-image')
      expect(avatarImage).toHaveAttribute(
        'alt',
        `${mockIssue.author.name || mockIssue.author.login}'s avatar`
      )
    })

    it('uses fallback alt text when author name is missing', () => {
      const issueWithoutAuthor = {
        ...mockIssue,
        author: {
          ...mockIssue.author,
          name: null,
        },
      }

      render(
        <ItemCardList
          title="Fallback Alt Text Test"
          data={[issueWithoutAuthor]}
          renderDetails={defaultProps.renderDetails}
          showAvatar={true}
        />
      )

      const avatarImage = screen.getByTestId('avatar-image')
      expect(avatarImage).toHaveAttribute('alt', `${issueWithoutAuthor.author.login}'s avatar`)
    })

    it('uses generic fallback alt text when author is missing', () => {
      const issueWithoutAuthor = {
        ...mockIssue,
        author: null,
      }

      render(
        <ItemCardList
          title="Missing Author Test"
          data={[issueWithoutAuthor]}
          renderDetails={defaultProps.renderDetails}
          showAvatar={true}
        />
      )

      const avatarImage = screen.getByTestId('avatar-image')
      expect(avatarImage).toHaveAttribute('alt', "Author's avatar")
    })

    it('uses generic fallback alt text when author name and login are missing', () => {
      const issueWithEmptyAuthor = {
        ...mockIssue,
        author: {
          ...mockIssue.author,
          name: '',
          login: '',
        },
      }

      render(
        <ItemCardList
          title="Empty Author Test"
          data={[issueWithEmptyAuthor]}
          renderDetails={defaultProps.renderDetails}
          showAvatar={true}
        />
      )

      const avatarImage = screen.getByTestId('avatar-image')
      expect(avatarImage).toHaveAttribute('alt', "Author's avatar")
    })

    it('opens external links in new tab', () => {
      render(
        <ItemCardList
          title="External Links"
          data={[mockIssue]}
          renderDetails={defaultProps.renderDetails}
        />
      )

      const titleLinks = screen.getAllByTestId('link')
      const externalLink = titleLinks.find((link) => link.getAttribute('href') === mockIssue.url)

      expect(externalLink).toHaveAttribute('target', '_blank')
    })

    it('provides tooltip content for screen readers', () => {
      render(
        <ItemCardList
          title="Screen Reader Support"
          data={[mockIssue]}
          renderDetails={defaultProps.renderDetails}
          showAvatar={true}
        />
      )

      const tooltip = screen.getByTestId('tooltip')
      expect(tooltip).toHaveAttribute('data-content', mockIssue.author.name)
      expect(tooltip).toHaveAttribute('data-id', 'avatar-tooltip-0')
    })
  })
})
