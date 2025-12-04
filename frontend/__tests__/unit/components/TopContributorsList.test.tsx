import { faUsers } from '@fortawesome/free-solid-svg-icons'
import { fireEvent, screen } from '@testing-library/react'
import React from 'react'
import { render } from 'wrappers/testUtil'
import type { Contributor } from 'types/contributor'
import TopContributorsList from 'components/TopContributorsList'

jest.mock('next/link', () => ({
  __esModule: true,
  default: ({
    children,
    href,
    ...props
  }: {
    children: React.ReactNode
    href: string
    [key: string]: unknown
  }) => (
    <a href={href} {...props} data-testid="contributor-link">
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
    ...props
  }: {
    src: string
    alt: string
    width: number
    height: number
    [key: string]: unknown
  }) => (
    // eslint-disable-next-line @next/next/no-img-element
    <img
      src={src}
      alt={alt}
      width={width}
      height={height}
      data-testid="contributor-avatar"
      {...props}
    />
  ),
}))

// Mock FontAwesome icons
jest.mock('@fortawesome/react-fontawesome', () => ({
  FontAwesomeIcon: ({
    icon,
    className,
    ...props
  }: {
    icon: { iconName: string }
    className?: string
    [key: string]: unknown
  }) => (
    <span data-testid={`icon-${icon.iconName}`} className={className} {...props}>
      {icon.iconName}
    </span>
  ),
}))

// Mock utility functions
jest.mock('utils/urlFormatter', () => ({
  getMemberUrl: (login: string) => `/members/${login}`,
}))

// Mock components
jest.mock('components/AnchorTitle', () => ({
  __esModule: true,
  default: ({
    title,
    className,
    ...props
  }: {
    title: string
    className?: string
    [key: string]: unknown
  }) => (
    <h2 className={className} data-testid="anchor-title" {...props}>
      {title}
    </h2>
  ),
}))

jest.mock('components/SecondaryCard', () => ({
  __esModule: true,
  default: ({
    children,
    title,
    icon,
    className,
    ...props
  }: {
    children: React.ReactNode
    title?: React.ReactNode
    icon?: { iconName: string }
    className?: string
    [key: string]: unknown
  }) => (
    <div className={className} data-testid="secondary-card" {...props}>
      {title && (
        <h2 className="mb-4 flex flex-row items-center gap-2 text-2xl font-semibold">
          {icon && (
            <span data-testid="card-icon" className="h-5 w-5">
              {icon.iconName}
            </span>
          )}
          {title}
        </h2>
      )}
      {children}
    </div>
  ),
}))

const mockContributors: Contributor[] = [
  {
    avatarUrl: 'https://github.com/developer1.avatar',
    login: 'developer1',
    name: 'Alex Developer',
    projectKey: 'project1',
    contributionsCount: 50,
  },
  {
    avatarUrl: 'https://github.com/contributor2.avatar',
    login: 'contributor2',
    name: 'Jane Developer',
    projectKey: 'project1',
    contributionsCount: 30,
  },
  {
    avatarUrl: 'https://github.com/user3.avatar',
    login: 'user3',
    name: '',
    projectKey: 'project1',
    contributionsCount: 20,
  },
]

describe('TopContributorsList Component', () => {
  const defaultProps = {
    contributors: mockContributors,
  }

  afterEach(() => {
    jest.clearAllMocks()
  })

  describe('Renders successfully with minimal required props', () => {
    it('renders with minimal props (only contributors)', () => {
      render(<TopContributorsList contributors={mockContributors} />)

      expect(screen.getByTestId('secondary-card')).toBeInTheDocument()
      expect(screen.getByTestId('anchor-title')).toBeInTheDocument()
      expect(screen.getAllByTestId('contributor-avatar')).toHaveLength(3)
      expect(screen.getAllByTestId('contributor-link')).toHaveLength(3)
    })

    it('renders component without crashing', () => {
      const { container } = render(<TopContributorsList {...defaultProps} />)
      expect(container).toBeInTheDocument()
    })

    it('renders without crashing with empty contributors array', () => {
      render(<TopContributorsList contributors={[]} />)
      // Component returns early for empty array, so no secondary card should be rendered
      expect(screen.queryByTestId('secondary-card')).not.toBeInTheDocument()
    })
  })

  describe('Conditional rendering logic', () => {
    it('does not render anything when contributors array is empty', () => {
      render(<TopContributorsList contributors={[]} />)
      // Component returns early for empty array, so no secondary card should be rendered
      expect(screen.queryByTestId('secondary-card')).not.toBeInTheDocument()
    })

    it('renders show more/less button only when contributors exceed maxInitialDisplay', () => {
      // Test with few contributors (should not show button)
      const { rerender } = render(
        <TopContributorsList contributors={mockContributors.slice(0, 2)} maxInitialDisplay={12} />
      )
      expect(screen.queryByRole('button')).not.toBeInTheDocument()

      // Test with many contributors (should show button)
      const manyContributors = Array(15)
        .fill(null)
        .map((_, index) => ({
          ...mockContributors[0],
          login: `user${index}`,
          name: `User ${index}`,
        }))

      rerender(<TopContributorsList contributors={manyContributors} maxInitialDisplay={12} />)
      expect(screen.getByRole('button')).toBeInTheDocument()
      expect(screen.getByText('Show more')).toBeInTheDocument()
    })

    it('displays correct number of contributors based on maxInitialDisplay', () => {
      const manyContributors = Array(15)
        .fill(null)
        .map((_, index) => ({
          ...mockContributors[0],
          login: `user${index}`,
          name: `User ${index}`,
        }))

      render(<TopContributorsList contributors={manyContributors} maxInitialDisplay={5} />)

      // Should only show 5 initially
      expect(screen.getAllByTestId('contributor-avatar')).toHaveLength(5)
      expect(screen.getAllByTestId('contributor-link')).toHaveLength(5)
    })

    it('renders contributor name when available, falls back to login', () => {
      const contributorsWithMissingNames: Contributor[] = [
        {
          avatarUrl: 'https://github.com/developer1.avatar',
          login: 'developer1',
          name: 'Alex Developer',
          projectKey: 'project1',
        },
        {
          avatarUrl: 'https://github.com/contributor2.avatar',
          login: 'contributor2',
          name: '',
          projectKey: 'project1',
        },
      ]

      render(<TopContributorsList contributors={contributorsWithMissingNames} />)

      expect(screen.getByText('Alex Developer')).toBeInTheDocument()
      expect(screen.getByText('Contributor2')).toBeInTheDocument() // capitalize utility should be applied
    })
  })

  describe('Prop-based behavior', () => {
    it('uses custom label when provided', () => {
      const customLabel = 'Featured Contributors'
      render(<TopContributorsList {...defaultProps} label={customLabel} />)

      expect(screen.getByText(customLabel)).toBeInTheDocument()
    })

    it('uses default label when not provided', () => {
      render(<TopContributorsList {...defaultProps} />)

      expect(screen.getByText('Top Contributors')).toBeInTheDocument()
    })

    it('respects custom maxInitialDisplay prop', () => {
      const manyContributors = Array(10)
        .fill(null)
        .map((_, index) => ({
          ...mockContributors[0],
          login: `user${index}`,
          name: `User ${index}`,
        }))

      render(<TopContributorsList contributors={manyContributors} maxInitialDisplay={3} />)

      expect(screen.getAllByTestId('contributor-avatar')).toHaveLength(3)
      expect(screen.getByRole('button')).toBeInTheDocument()
    })

    it('displays icon when provided', () => {
      render(<TopContributorsList {...defaultProps} icon={faUsers} />)

      expect(screen.getByTestId('card-icon')).toBeInTheDocument()
    })

    it('does not display icon when not provided', () => {
      render(<TopContributorsList {...defaultProps} />)

      expect(screen.queryByTestId('card-icon')).not.toBeInTheDocument()
    })
  })

  describe('Event handling', () => {
    it('toggles contributors display when show more/less button is clicked', () => {
      const manyContributors = Array(15)
        .fill(null)
        .map((_, index) => ({
          ...mockContributors[0],
          login: `user${index}`,
          name: `User ${index}`,
        }))

      render(<TopContributorsList contributors={manyContributors} maxInitialDisplay={5} />)

      // Initially shows 5 contributors
      expect(screen.getAllByTestId('contributor-avatar')).toHaveLength(5)
      expect(screen.getByText('Show more')).toBeInTheDocument()

      // Click show more
      const toggleButton = screen.getByRole('button')
      fireEvent.click(toggleButton)

      // Should now show all 15 contributors
      expect(screen.getAllByTestId('contributor-avatar')).toHaveLength(15)
      expect(screen.getByText('Show less')).toBeInTheDocument()
      expect(screen.getByTestId('icon-chevron-up')).toHaveTextContent('chevron-up')

      // Click show less
      fireEvent.click(toggleButton)

      // Should go back to 5 contributors
      expect(screen.getAllByTestId('contributor-avatar')).toHaveLength(5)
      expect(screen.getByText('Show more')).toBeInTheDocument()
      expect(screen.getByTestId('icon-chevron-down')).toHaveTextContent('chevron-down')
    })

    it('calls toggle function correctly on multiple clicks', () => {
      const manyContributors = Array(10)
        .fill(null)
        .map((_, index) => ({
          ...mockContributors[0],
          login: `user${index}`,
          name: `User ${index}`,
        }))

      render(<TopContributorsList contributors={manyContributors} maxInitialDisplay={3} />)

      const toggleButton = screen.getByRole('button')

      // Multiple clicks should toggle state
      fireEvent.click(toggleButton)
      expect(screen.getByText('Show less')).toBeInTheDocument()

      fireEvent.click(toggleButton)
      expect(screen.getByText('Show more')).toBeInTheDocument()

      fireEvent.click(toggleButton)
      expect(screen.getByText('Show less')).toBeInTheDocument()
    })
  })

  describe('State changes / internal logic', () => {
    it('manages showAllContributors state correctly', () => {
      const manyContributors = Array(10)
        .fill(null)
        .map((_, index) => ({
          ...mockContributors[0],
          login: `user${index}`,
          name: `User ${index}`,
        }))

      render(<TopContributorsList contributors={manyContributors} maxInitialDisplay={5} />)

      // Initial state - collapsed
      expect(screen.getAllByTestId('contributor-avatar')).toHaveLength(5)

      // Expand state
      fireEvent.click(screen.getByRole('button'))
      expect(screen.getAllByTestId('contributor-avatar')).toHaveLength(10)

      // Collapse state
      fireEvent.click(screen.getByRole('button'))
      expect(screen.getAllByTestId('contributor-avatar')).toHaveLength(5)
    })

    it('correctly slices contributors array based on state', () => {
      const contributors = Array(8)
        .fill(null)
        .map((_, index) => ({
          ...mockContributors[0],
          login: `user${index}`,
          name: `User ${index}`,
        }))

      render(<TopContributorsList contributors={contributors} maxInitialDisplay={3} />)

      // Should show first 3 contributors
      expect(screen.getByText('User 0')).toBeInTheDocument()
      expect(screen.getByText('User 1')).toBeInTheDocument()
      expect(screen.getByText('User 2')).toBeInTheDocument()
      expect(screen.queryByText('User 3')).not.toBeInTheDocument()
    })
  })

  describe('Default values and fallbacks', () => {
    it('uses default maxInitialDisplay value when not provided', () => {
      const contributors = Array(15)
        .fill(null)
        .map((_, index) => ({
          ...mockContributors[0],
          login: `user${index}`,
          name: `User ${index}`,
        }))

      render(<TopContributorsList contributors={contributors} />)

      // Should show 12 by default (based on component default)
      expect(screen.getAllByTestId('contributor-avatar')).toHaveLength(12)
      expect(screen.getByRole('button')).toBeInTheDocument()
    })

    it('falls back to login when name is empty or missing', () => {
      const contributorWithoutName: Contributor[] = [
        {
          avatarUrl: 'https://github.com/user1.avatar',
          login: 'testuser',
          name: '',
          projectKey: 'project1',
        },
      ]

      render(<TopContributorsList contributors={contributorWithoutName} />)

      expect(screen.getByText('Testuser')).toBeInTheDocument()
    })

    it('handles missing avatar URL gracefully', () => {
      const contributorWithEmptyAvatar: Contributor[] = [
        {
          avatarUrl: '',
          login: 'developer1',
          name: 'Alex Developer',
          projectKey: 'project1',
        },
      ]

      render(<TopContributorsList contributors={contributorWithEmptyAvatar} />)

      const avatar = screen.getByTestId('contributor-avatar')
      expect(avatar).toHaveAttribute('src', '&s=60') // Should append size parameter even with empty URL
    })
  })

  describe('Text and content rendering', () => {
    it('renders contributor names correctly', () => {
      render(<TopContributorsList {...defaultProps} />)

      expect(screen.getByText('Alex Developer')).toBeInTheDocument()
      expect(screen.getByText('Jane Developer')).toBeInTheDocument()
      expect(screen.getByText('User3')).toBeInTheDocument() // Falls back to capitalized login
    })

    it('renders correct button text based on state', () => {
      const manyContributors = Array(15)
        .fill(null)
        .map((_, index) => ({
          ...mockContributors[0],
          login: `user${index}`,
          name: `User ${index}`,
        }))

      render(<TopContributorsList contributors={manyContributors} maxInitialDisplay={5} />)

      expect(screen.getByText('Show more')).toBeInTheDocument()

      fireEvent.click(screen.getByRole('button'))
      expect(screen.getByText('Show less')).toBeInTheDocument()
    })

    it('renders title with proper structure', () => {
      render(<TopContributorsList {...defaultProps} label="Custom Title" />)

      expect(screen.getByTestId('anchor-title')).toBeInTheDocument()
      expect(screen.getByText('Custom Title')).toBeInTheDocument()
    })
  })

  describe('Handles edge cases and invalid inputs', () => {
    it('handles contributors with missing required fields', () => {
      const incompleteContributors: Contributor[] = [
        {
          avatarUrl: 'https://github.com/user1.avatar',
          login: '',
          name: '',
          projectKey: 'project1',
        },
        {
          avatarUrl: '',
          login: 'user2',
          name: 'User 2',
          projectKey: 'project1',
        },
      ]

      render(<TopContributorsList contributors={incompleteContributors} />)

      // Should still render without crashing
      expect(screen.getByTestId('secondary-card')).toBeInTheDocument()
    })

    it('handles zero maxInitialDisplay value', () => {
      render(<TopContributorsList contributors={mockContributors} maxInitialDisplay={0} />)

      // Should still show button since contributors length > 0
      expect(screen.getByRole('button')).toBeInTheDocument()
      expect(screen.queryByTestId('contributor-avatar')).not.toBeInTheDocument()
    })

    it('handles negative maxInitialDisplay value', () => {
      render(<TopContributorsList contributors={mockContributors} maxInitialDisplay={-1} />)

      // slice with negative number should still work
      expect(screen.getByTestId('secondary-card')).toBeInTheDocument()
    })

    it('handles very large maxInitialDisplay value', () => {
      render(<TopContributorsList contributors={mockContributors} maxInitialDisplay={1000} />)

      // Should show all contributors and no button
      expect(screen.getAllByTestId('contributor-avatar')).toHaveLength(3)
      expect(screen.queryByRole('button')).not.toBeInTheDocument()
    })
  })

  describe('Accessibility roles and labels', () => {
    it('renders proper image alt text and titles', () => {
      render(<TopContributorsList {...defaultProps} />)

      const avatars = screen.getAllByTestId('contributor-avatar')
      expect(avatars[0]).toHaveAttribute('alt', "Alex Developer's avatar")
      expect(avatars[0]).toHaveAttribute('title', 'Alex Developer')
      expect(avatars[1]).toHaveAttribute('alt', "Jane Developer's avatar")
      expect(avatars[1]).toHaveAttribute('title', 'Jane Developer')
      expect(avatars[2]).toHaveAttribute('alt', 'Contributor avatar')
      expect(avatars[2]).toHaveAttribute('title', 'user3')
    })

    it('renders proper link titles and hrefs', () => {
      render(<TopContributorsList {...defaultProps} />)

      const links = screen.getAllByTestId('contributor-link')
      expect(links[0]).toHaveAttribute('href', '/members/developer1')
      expect(links[0]).toHaveAttribute('title', 'Alex Developer')
      expect(links[1]).toHaveAttribute('href', '/members/contributor2')
      expect(links[1]).toHaveAttribute('title', 'Jane Developer')
      expect(links[2]).toHaveAttribute('href', '/members/user3')
      expect(links[2]).toHaveAttribute('title', 'user3')
    })

    it('renders button with proper role', () => {
      const manyContributors = Array(15)
        .fill(null)
        .map((_, index) => ({
          ...mockContributors[0],
          login: `user${index}`,
          name: `User ${index}`,
        }))

      render(<TopContributorsList contributors={manyContributors} maxInitialDisplay={5} />)

      const button = screen.getByRole('button')
      expect(button).toBeInTheDocument()
      expect(button).toHaveTextContent('Show more')
    })
  })

  describe('DOM structure / classNames / styles', () => {
    it('renders correct CSS classes on components', () => {
      render(<TopContributorsList {...defaultProps} />)

      const contributorItems = screen
        .getAllByTestId('contributor-avatar')
        .map((avatar) => avatar.parentElement?.parentElement)

      for (const item of contributorItems) {
        expect(item).toHaveClass(
          'overflow-hidden',
          'rounded-lg',
          'bg-gray-200',
          'p-4',
          'dark:bg-gray-700'
        )
      }
    })

    it('renders proper grid structure', () => {
      const { container } = render(<TopContributorsList {...defaultProps} />)

      const gridContainer = container.querySelector('.grid')
      expect(gridContainer).toHaveClass(
        'gap-4',
        'sm:grid-cols-1',
        'md:grid-cols-3',
        'lg:grid-cols-4'
      )
    })

    it('renders avatar with correct dimensions and styling', () => {
      render(<TopContributorsList {...defaultProps} />)

      const avatars = screen.getAllByTestId('contributor-avatar')
      for (const avatar of avatars) {
        expect(avatar).toHaveAttribute('width', '24')
        expect(avatar).toHaveAttribute('height', '24')
        expect(avatar).toHaveClass('rounded-full')
      }
    })

    it('renders contributor links with proper styling', () => {
      render(<TopContributorsList {...defaultProps} />)

      const links = screen.getAllByTestId('contributor-link')

      for (const link of links) {
        expect(link).toHaveClass(
          'cursor-pointer',
          'overflow-hidden',
          'text-ellipsis',
          'whitespace-nowrap',
          'font-semibold',
          'text-blue-400',
          'hover:underline'
        )
      }
    })
  })
})
