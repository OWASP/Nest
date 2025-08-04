import { render, screen, fireEvent } from '@testing-library/react'
import { useRouter } from 'next/navigation'
import React from 'react'
import RepositoriesCard from 'components/RepositoriesCard'
import type { RepositoryCardProps } from 'types/project'
import type { Organization } from 'types/organization'

// Define proper types for mock props
interface MockShowMoreButtonProps {
  onToggle: () => void
}

interface MockTruncatedTextProps {
  text: string
}

interface MockInfoItemProps {
  pluralizedName?: string
  unit: string
  value: number
  icon: unknown
}

// Mock next/navigation
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
}))

// Mock ShowMoreButton component
jest.mock('components/ShowMoreButton', () => {
  return function MockShowMoreButton({ onToggle }: MockShowMoreButtonProps) {
    const [isExpanded, setIsExpanded] = React.useState(false)

    const handleToggle = () => {
      setIsExpanded(!isExpanded)
      onToggle()
    }

    return (
      <div className="mt-4 flex justify-start">
        <button
          type="button"
          onClick={handleToggle}
          className="flex items-center bg-transparent px-0 text-blue-400"
          data-testid="show-more-button"
        >
          {isExpanded ? (
            <>
              Show less <span data-testid="chevron-up">↑</span>
            </>
          ) : (
            <>
              Show more <span data-testid="chevron-down">↓</span>
            </>
          )}
        </button>
      </div>
    )
  }
})

// Mock TruncatedText component
jest.mock('components/TruncatedText', () => ({
  TruncatedText: ({ text }: MockTruncatedTextProps) => <span>{text}</span>,
}))

// Mock InfoItem component
jest.mock('components/InfoItem', () => {
  return function MockInfoItem({ pluralizedName, unit, value }: MockInfoItemProps) {
    const displayName = pluralizedName || `${value} ${unit}${value !== 1 ? 's' : ''}`
    return (
      <div data-testid={`info-item-${unit}`}>
        {displayName}: {value}
      </div>
    )
  }
})

const mockPush = jest.fn()
const mockUseRouter = useRouter as jest.Mock

describe('<RepositoriesCard />', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    mockUseRouter.mockReturnValue({
      push: mockPush,
    })
  })

  const createMockRepository = (index: number): RepositoryCardProps => ({
    contributorsCount: 10 + index,
    forksCount: 5 + index,
    key: `repo-${index}`,
    name: `Repository ${index}`,
    openIssuesCount: 3 + index,
    organization: {
      login: `org-${index}`,
      name: `Organization ${index}`,
      key: `org-${index}`,
      url: `https://github.com/org-${index}`,
      avatarUrl: `https://github.com/org-${index}.png`,
      description: `Organization ${index} description`,
      objectID: `org-${index}`,
      collaboratorsCount: 10,
      followersCount: 50,
      publicRepositoriesCount: 20,
      createdAt: Date.now(),
      updatedAt: Date.now(),
    } as Organization,
    starsCount: 100 + index,
    subscribersCount: 20 + index,
    url: `https://github.com/org-${index}/repo-${index}`,
  })

  it('renders without crashing with empty repositories', () => {
    render(<RepositoriesCard repositories={[]} />)

    // Should not show ShowMoreButton
    expect(screen.queryByTestId('show-more-button')).not.toBeInTheDocument()
  })

  it('shows first 4 repositories initially when there are more than 4', () => {
    const repositories = Array.from({ length: 6 }, (_, i) => createMockRepository(i))

    render(<RepositoriesCard repositories={repositories} />)

    // Should show first 4 repositories
    expect(screen.getByText('Repository 0')).toBeInTheDocument()
    expect(screen.getByText('Repository 1')).toBeInTheDocument()
    expect(screen.getByText('Repository 2')).toBeInTheDocument()
    expect(screen.getByText('Repository 3')).toBeInTheDocument()

    // Should not show repositories 4 and 5
    expect(screen.queryByText('Repository 4')).not.toBeInTheDocument()
    expect(screen.queryByText('Repository 5')).not.toBeInTheDocument()
  })

  it('shows all repositories when there are 4 or fewer', () => {
    const repositories = Array.from({ length: 3 }, (_, i) => createMockRepository(i))

    render(<RepositoriesCard repositories={repositories} />)

    // Should show all 3 repositories
    expect(screen.getByText('Repository 0')).toBeInTheDocument()
    expect(screen.getByText('Repository 1')).toBeInTheDocument()
    expect(screen.getByText('Repository 2')).toBeInTheDocument()
  })

  it('displays ShowMoreButton when there are more than 4 repositories', () => {
    const repositories = Array.from({ length: 6 }, (_, i) => createMockRepository(i))

    render(<RepositoriesCard repositories={repositories} />)

    expect(screen.getByTestId('show-more-button')).toBeInTheDocument()
  })

  it('does not display ShowMoreButton when there are 4 or fewer repositories', () => {
    const repositories = Array.from({ length: 4 }, (_, i) => createMockRepository(i))

    render(<RepositoriesCard repositories={repositories} />)

    expect(screen.queryByTestId('show-more-button')).not.toBeInTheDocument()
  })

  it('toggles between showing 4 and all repositories when clicked', () => {
    const repositories = Array.from({ length: 6 }, (_, i) => createMockRepository(i))

    render(<RepositoriesCard repositories={repositories} />)

    // Initially shows first 4
    expect(screen.getByText('Repository 0')).toBeInTheDocument()
    expect(screen.getByText('Repository 3')).toBeInTheDocument()
    expect(screen.queryByText('Repository 4')).not.toBeInTheDocument()
    expect(screen.queryByText('Repository 5')).not.toBeInTheDocument()

    // Click show more
    fireEvent.click(screen.getByTestId('show-more-button'))

    // Now shows all repositories
    expect(screen.getByText('Repository 0')).toBeInTheDocument()
    expect(screen.getByText('Repository 3')).toBeInTheDocument()
    expect(screen.getByText('Repository 4')).toBeInTheDocument()
    expect(screen.getByText('Repository 5')).toBeInTheDocument()

    // Click show less
    fireEvent.click(screen.getByTestId('show-more-button'))

    // Back to showing first 4
    expect(screen.getByText('Repository 0')).toBeInTheDocument()
    expect(screen.getByText('Repository 3')).toBeInTheDocument()
    expect(screen.queryByText('Repository 4')).not.toBeInTheDocument()
    expect(screen.queryByText('Repository 5')).not.toBeInTheDocument()
  })

  it('displays correct text and icons on ShowMoreButton', () => {
    const repositories = Array.from({ length: 6 }, (_, i) => createMockRepository(i))

    render(<RepositoriesCard repositories={repositories} />)

    // Initially shows "Show more" with down chevron
    const button = screen.getByTestId('show-more-button')
    expect(button).toHaveTextContent('Show more')
    expect(screen.getByTestId('chevron-down')).toBeInTheDocument()
    expect(screen.queryByTestId('chevron-up')).not.toBeInTheDocument()

    // Click to expand
    fireEvent.click(button)

    // Now shows "Show less" with up chevron
    expect(button).toHaveTextContent('Show less')
    expect(screen.getByTestId('chevron-up')).toBeInTheDocument()
    expect(screen.queryByTestId('chevron-down')).not.toBeInTheDocument()
  })

  it('renders repository items with correct information', () => {
    const repositories = [createMockRepository(0)]

    render(<RepositoriesCard repositories={repositories} />)

    // Check repository name
    expect(screen.getByText('Repository 0')).toBeInTheDocument()

    // Check InfoItem components are rendered
    expect(screen.getByTestId('info-item-Star')).toBeInTheDocument()
    expect(screen.getByTestId('info-item-Fork')).toBeInTheDocument()
    expect(screen.getByTestId('info-item-Contributor')).toBeInTheDocument()
    expect(screen.getByTestId('info-item-Issue')).toBeInTheDocument()
  })

  it('navigates to correct URL when repository item is clicked', () => {
    const repositories = [createMockRepository(0)]

    render(<RepositoriesCard repositories={repositories} />)

    const repositoryButton = screen.getByText('Repository 0')
    fireEvent.click(repositoryButton)

    expect(mockPush).toHaveBeenCalledWith('/organizations/org-0/repositories/repo-0')
  })

  it('applies correct styling to repository items', () => {
    const repositories = [createMockRepository(0)]

    render(<RepositoriesCard repositories={repositories} />)

    const repositoryButton = screen.getByText('Repository 0')
    expect(repositoryButton).toBeInTheDocument()
    expect(repositoryButton).toHaveClass('text-start', 'font-semibold', 'text-blue-400')
  })

  it('handles exactly 4 repositories correctly', () => {
    const repositories = Array.from({ length: 4 }, (_, i) => createMockRepository(i))

    render(<RepositoriesCard repositories={repositories} />)

    // Should show all 4 repositories
    expect(screen.getByText('Repository 0')).toBeInTheDocument()
    expect(screen.getByText('Repository 1')).toBeInTheDocument()
    expect(screen.getByText('Repository 2')).toBeInTheDocument()
    expect(screen.getByText('Repository 3')).toBeInTheDocument()

    // Should not show ShowMoreButton
    expect(screen.queryByTestId('show-more-button')).not.toBeInTheDocument()
  })

  it('handles repositories without organization data gracefully', () => {
    // This test verifies that the component doesn't crash when organization data is missing
    // and doesn't attempt navigation to invalid URLs containing 'undefined'
    // The component should either prevent navigation or use a fallback mechanism
    const repository: RepositoryCardProps = {
      contributorsCount: 10,
      forksCount: 5,
      key: 'repo-test',
      name: 'Test Repository',
      openIssuesCount: 3,
      starsCount: 100,
      subscribersCount: 20,
      url: 'https://github.com/test/repo',
    }

    render(<RepositoriesCard repositories={[repository]} />)

    expect(screen.getByText('Test Repository')).toBeInTheDocument()

    // Repository should still render with all InfoItem components
    expect(screen.getByTestId('info-item-Star')).toBeInTheDocument()
    expect(screen.getByTestId('info-item-Fork')).toBeInTheDocument()
    expect(screen.getByTestId('info-item-Contributor')).toBeInTheDocument()
    expect(screen.getByTestId('info-item-Issue')).toBeInTheDocument()

    // When organization data is missing, the component should handle clicks gracefully
    const repositoryButton = screen.getByText('Test Repository')

    // Mock console.error to capture any error handling
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {})

    // Click the repository button
    fireEvent.click(repositoryButton)

    // The component should handle missing organization data by either:
    // 1. Not attempting navigation (preferred)
    // 2. Using a fallback URL
    // 3. Logging an error and preventing navigation

    // Check if any errors were logged (good error handling)
    const errorLogged = consoleSpy.mock.calls.length > 0

    // Check if navigation was attempted
    const navigationAttempted = mockPush.mock.calls.length > 0

    if (navigationAttempted) {
      // If navigation was attempted, ensure it doesn't contain 'undefined'
      const navigationUrl = mockPush.mock.calls[0][0]
      expect(navigationUrl).not.toContain('undefined')
      expect(navigationUrl).not.toContain('null')
    } else {
      // If no navigation was attempted, that's acceptable defensive behavior
      expect(mockPush).not.toHaveBeenCalled()
    }

    // Clean up the console spy
    consoleSpy.mockRestore()
  })
})
