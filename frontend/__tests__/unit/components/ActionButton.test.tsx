import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import * as nextNavigation from 'next/navigation'
import RepositoriesCard from 'components/RepositoriesCard'
import type { RepositoryCardProps } from 'types/project'

// Mock next/navigation
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
}))

// Mock FontAwesome icons
jest.mock('@fortawesome/react-fontawesome', () => ({
  FontAwesomeIcon: ({ icon, className }: { icon: any; className?: string }) => (
    <span data-testid={`icon-${icon.iconName}`} className={className} />
  ),
}))

// Mock InfoItem component
jest.mock('components/InfoItem', () => {
  return function MockInfoItem({ 
    icon, 
    pluralizedName, 
    unit, 
    value 
  }: { 
    icon: any; 
    pluralizedName: string; 
    unit: string; 
    value: number 
  }) {
    return (
      <div data-testid={`info-item-${pluralizedName.toLowerCase()}`}>
        <span data-testid={`icon-${icon.iconName}`} />
        <span>{pluralizedName}: {value}</span>
      </div>
    )
  }
})

// Mock TruncatedText component
jest.mock('components/TruncatedText', () => ({
  TruncatedText: ({ text }: { text?: string }) => (
    <span data-testid="truncated-text">{text}</span>
  ),
}))

describe('RepositoriesCard', () => {
  const mockPush = jest.fn()
  
  beforeEach(() => {
    jest.clearAllMocks()
    ;(nextNavigation.useRouter as jest.Mock).mockReturnValue({
      push: mockPush,
    })
  })

  // Test data
  const mockRepository: RepositoryCardProps = {
    key: 'test-repo',
    name: 'Test Repository',
    starsCount: 100,
    forksCount: 50,
    contributorsCount: 25,
    openIssuesCount: 10,
    subscribersCount: 5,
    url: 'https://github.com/test/repo',
    organization: {
      login: 'test-org',
      createdAt: new Date('2020-01-01T00:00:00Z').getTime(),
      updatedAt: new Date('2020-01-01T00:00:00Z').getTime(),
      avatarUrl: '',
      collaboratorsCount: 0,
      followersCount: 0,
      key: '',
      name: '',
      objectID: '',
      publicRepositoriesCount: 0,
      url: ''
    },
  }

  const createMockRepositories = (count: number): RepositoryCardProps[] => {
    return Array.from({ length: count }, (_, index) => ({
      ...mockRepository,
      key: `repo-${index}`,
      name: `Repository ${index + 1}`,
    }))
  }

  describe('Renders successfully with minimal required props', () => {
    it('renders without crashing with empty repositories array', () => {
      render(<RepositoriesCard repositories={[]} />)
      expect(screen.getByRole('generic')).toBeInTheDocument()
    })

    it('renders with single repository', () => {
      render(<RepositoriesCard repositories={[mockRepository]} />)
      expect(screen.getByText('Test Repository')).toBeInTheDocument()
    })

    it('renders with multiple repositories', () => {
      const repositories = createMockRepositories(3)
      render(<RepositoriesCard repositories={repositories} />)
      
      expect(screen.getByText('Repository 1')).toBeInTheDocument()
      expect(screen.getByText('Repository 2')).toBeInTheDocument()
      expect(screen.getByText('Repository 3')).toBeInTheDocument()
    })
  })

  describe('Conditional rendering logic', () => {
    it('shows only first 4 repositories by default', () => {
      const repositories = createMockRepositories(6)
      render(<RepositoriesCard repositories={repositories} />)
      
      expect(screen.getByText('Repository 1')).toBeInTheDocument()
      expect(screen.getByText('Repository 2')).toBeInTheDocument()
      expect(screen.getByText('Repository 3')).toBeInTheDocument()
      expect(screen.getByText('Repository 4')).toBeInTheDocument()
      expect(screen.queryByText('Repository 5')).not.toBeInTheDocument()
      expect(screen.queryByText('Repository 6')).not.toBeInTheDocument()
    })

    it('shows "Show more" button when more than 4 repositories', () => {
      const repositories = createMockRepositories(5)
      render(<RepositoriesCard repositories={repositories} />)
      
      expect(screen.getByRole('button', { name: /show more/i })).toBeInTheDocument()
    })

    it('does not show "Show more" button when 4 or fewer repositories', () => {
      const repositories = createMockRepositories(4)
      render(<RepositoriesCard repositories={repositories} />)
      
      expect(screen.queryByRole('button', { name: /show more/i })).not.toBeInTheDocument()
    })

    it('shows all repositories when "Show more" is clicked', () => {
      const repositories = createMockRepositories(6)
      render(<RepositoriesCard repositories={repositories} />)
      
      const showMoreButton = screen.getByRole('button', { name: /show more/i })
      fireEvent.click(showMoreButton)
      
      expect(screen.getByText('Repository 5')).toBeInTheDocument()
      expect(screen.getByText('Repository 6')).toBeInTheDocument()
    })

    it('shows "Show less" button when all repositories are displayed', () => {
      const repositories = createMockRepositories(6)
      render(<RepositoriesCard repositories={repositories} />)
      
      const showMoreButton = screen.getByRole('button', { name: /show more/i })
      fireEvent.click(showMoreButton)
      
      expect(screen.getByRole('button', { name: /show less/i })).toBeInTheDocument()
    })

    it('hides repositories when "Show less" is clicked', () => {
      const repositories = createMockRepositories(6)
      render(<RepositoriesCard repositories={repositories} />)
      
      const showMoreButton = screen.getByRole('button', { name: /show more/i })
      fireEvent.click(showMoreButton)
      
      const showLessButton = screen.getByRole('button', { name: /show less/i })
      fireEvent.click(showLessButton)
      
      expect(screen.queryByText('Repository 5')).not.toBeInTheDocument()
      expect(screen.queryByText('Repository 6')).not.toBeInTheDocument()
    })
  })

  describe('Prop-based behavior', () => {
    it('renders repository information correctly', () => {
      render(<RepositoriesCard repositories={[mockRepository]} />)
      
      expect(screen.getByTestId('info-item-stars')).toBeInTheDocument()
      expect(screen.getByTestId('info-item-forks')).toBeInTheDocument()
      expect(screen.getByTestId('info-item-contributors')).toBeInTheDocument()
      expect(screen.getByTestId('info-item-issues')).toBeInTheDocument()
    })

    it('handles repositories with missing optional props', () => {
      const repositoryWithoutKey = {
        ...mockRepository,
        key: undefined,
      }
      render(<RepositoriesCard repositories={[repositoryWithoutKey]} />)
      
      expect(screen.getByText('Test Repository')).toBeInTheDocument()
    })

    it('handles repositories with zero values', () => {
      const repositoryWithZeros = {
        ...mockRepository,
        starsCount: 0,
        forksCount: 0,
        contributorsCount: 0,
        openIssuesCount: 0,
      }
      render(<RepositoriesCard repositories={[repositoryWithZeros]} />)
      
      expect(screen.getByTestId('info-item-stars')).toBeInTheDocument()
      expect(screen.getByTestId('info-item-forks')).toBeInTheDocument()
      expect(screen.getByTestId('info-item-contributors')).toBeInTheDocument()
      expect(screen.getByTestId('info-item-issues')).toBeInTheDocument()
    })
  })

  describe('Event handling', () => {
    it('navigates to repository page when repository is clicked', () => {
      render(<RepositoriesCard repositories={[mockRepository]} />)
      
      const repositoryButton = screen.getByRole('button', { name: /test repository/i })
      fireEvent.click(repositoryButton)
      
      expect(mockPush).toHaveBeenCalledWith('/organizations/test-org/repositories/test-repo')
    })

    it('handles click on "Show more" button', () => {
      const repositories = createMockRepositories(5)
      render(<RepositoriesCard repositories={repositories} />)
      
      const showMoreButton = screen.getByRole('button', { name: /show more/i })
      fireEvent.click(showMoreButton)
      
      expect(screen.getByText('Repository 5')).toBeInTheDocument()
    })

    it('handles click on "Show less" button', () => {
      const repositories = createMockRepositories(5)
      render(<RepositoriesCard repositories={repositories} />)
      
      const showMoreButton = screen.getByRole('button', { name: /show more/i })
      fireEvent.click(showMoreButton)
      
      const showLessButton = screen.getByRole('button', { name: /show less/i })
      fireEvent.click(showLessButton)
      
      expect(screen.queryByText('Repository 5')).not.toBeInTheDocument()
    })
  })

  describe('State changes and internal logic', () => {
    it('toggles showAllRepositories state correctly', () => {
      const repositories = createMockRepositories(5)
      render(<RepositoriesCard repositories={repositories} />)
      
      // Initially shows first 4
      expect(screen.queryByText('Repository 5')).not.toBeInTheDocument()
      
      // Click show more
      const showMoreButton = screen.getByRole('button', { name: /show more/i })
      fireEvent.click(showMoreButton)
      expect(screen.getByText('Repository 5')).toBeInTheDocument()
      
      // Click show less
      const showLessButton = screen.getByRole('button', { name: /show less/i })
      fireEvent.click(showLessButton)
      expect(screen.queryByText('Repository 5')).not.toBeInTheDocument()
    })

    it('maintains state correctly when toggling multiple times', () => {
      const repositories = createMockRepositories(5)
      render(<RepositoriesCard repositories={repositories} />)
      
      const showMoreButton = screen.getByRole('button', { name: /show more/i })
      
      // Toggle multiple times
      fireEvent.click(showMoreButton)
      fireEvent.click(showMoreButton)
      fireEvent.click(showMoreButton)
      
      // Should still show all repositories
      expect(screen.getByText('Repository 5')).toBeInTheDocument()
    })
  })

  describe('Default values and fallbacks', () => {
    it('handles undefined repositories prop', () => {
      render(<RepositoriesCard repositories={undefined} />)
      expect(screen.getByRole('generic')).toBeInTheDocument()
    })

    it('handles empty repositories array', () => {
      render(<RepositoriesCard repositories={[]} />)
      expect(screen.getByRole('generic')).toBeInTheDocument()
    })

    it('handles repository with missing name', () => {
      const repositoryWithoutName = {
        ...mockRepository,
        name: '',
      }
      render(<RepositoriesCard repositories={[repositoryWithoutName]} />)
      
      const truncatedText = screen.getByTestId('truncated-text')
      expect(truncatedText).toHaveTextContent('')
    })
  })

  describe('Text and content rendering', () => {
    it('displays repository name correctly', () => {
      render(<RepositoriesCard repositories={[mockRepository]} />)
      expect(screen.getByTestId('truncated-text')).toHaveTextContent('Test Repository')
    })

    it('displays correct button text for show more/less', () => {
      const repositories = createMockRepositories(5)
      render(<RepositoriesCard repositories={repositories} />)
      
      expect(screen.getByRole('button', { name: /show more/i })).toBeInTheDocument()
      
      const showMoreButton = screen.getByRole('button', { name: /show more/i })
      fireEvent.click(showMoreButton)
      
      expect(screen.getByRole('button', { name: /show less/i })).toBeInTheDocument()
    })
  })

  describe('Edge cases and invalid inputs', () => {
    it('handles very large number of repositories', () => {
      const repositories = createMockRepositories(100)
      render(<RepositoriesCard repositories={repositories} />)
      
      // Should show first 4 by default
      expect(screen.getByText('Repository 1')).toBeInTheDocument()
      expect(screen.getByText('Repository 4')).toBeInTheDocument()
      expect(screen.queryByText('Repository 5')).not.toBeInTheDocument()
      
      // Should show all when expanded
      const showMoreButton = screen.getByRole('button', { name: /show more/i })
      fireEvent.click(showMoreButton)
      
      expect(screen.getByText('Repository 100')).toBeInTheDocument()
    })

    it('handles repositories with very long names', () => {
      const repositoryWithLongName = {
        ...mockRepository,
        name: 'This is a very long repository name that should be truncated when displayed in the UI',
      }
      render(<RepositoriesCard repositories={[repositoryWithLongName]} />)
      
      expect(screen.getByTestId('truncated-text')).toHaveTextContent(repositoryWithLongName.name)
    })

    it('handles repositories with special characters in names', () => {
      const repositoryWithSpecialChars = {
        ...mockRepository,
        name: 'repo-with-special-chars-!@#$%^&*()',
      }
      render(<RepositoriesCard repositories={[repositoryWithSpecialChars]} />)
      
      expect(screen.getByTestId('truncated-text')).toHaveTextContent(repositoryWithSpecialChars.name)
    })

    it('handles repositories with very large numbers', () => {
      const repositoryWithLargeNumbers = {
        ...mockRepository,
        starsCount: 999999999,
        forksCount: 888888888,
        contributorsCount: 777777777,
        openIssuesCount: 666666666,
      }
      render(<RepositoriesCard repositories={[repositoryWithLargeNumbers]} />)
      
      expect(screen.getByTestId('info-item-stars')).toBeInTheDocument()
      expect(screen.getByTestId('info-item-forks')).toBeInTheDocument()
      expect(screen.getByTestId('info-item-contributors')).toBeInTheDocument()
      expect(screen.getByTestId('info-item-issues')).toBeInTheDocument()
    })
  })

  describe('Accessibility roles and labels', () => {
    it('has proper button roles for interactive elements', () => {
      const repositories = createMockRepositories(5)
      render(<RepositoriesCard repositories={repositories} />)
      
      // Repository buttons
      expect(screen.getByRole('button', { name: /repository 1/i })).toBeInTheDocument()
      
      // Show more/less button
      expect(screen.getByRole('button', { name: /show more/i })).toBeInTheDocument()
    })

    it('has accessible button labels', () => {
      const repositories = createMockRepositories(5)
      render(<RepositoriesCard repositories={repositories} />)
      
      const showMoreButton = screen.getByRole('button', { name: /show more/i })
      expect(showMoreButton).toHaveAccessibleName(/show more/i)
      
      fireEvent.click(showMoreButton)
      
      const showLessButton = screen.getByRole('button', { name: /show less/i })
      expect(showLessButton).toHaveAccessibleName(/show less/i)
    })

    it('has proper semantic structure', () => {
      render(<RepositoriesCard repositories={[mockRepository]} />)
      
      // Main container
      expect(screen.getByRole('generic')).toBeInTheDocument()
      
      // Repository button
      expect(screen.getByRole('button', { name: /test repository/i })).toBeInTheDocument()
    })
  })

  describe('DOM structure, classNames, and styles', () => {
    it('has correct CSS classes for grid layout', () => {
      render(<RepositoriesCard repositories={[mockRepository]} />)
      
      const gridContainer = screen.getByRole('generic').querySelector('.grid')
      expect(gridContainer).toHaveClass('grid-cols-1', 'gap-4', 'sm:grid-cols-2', 'md:grid-cols-3', 'lg:grid-cols-4')
    })

    it('has correct CSS classes for repository cards', () => {
      render(<RepositoriesCard repositories={[mockRepository]} />)
      
      const repositoryCard = screen.getByRole('button', { name: /test repository/i }).closest('div')
      expect(repositoryCard).toHaveClass(
        'h-46',
        'flex',
        'w-full',
        'flex-col',
        'gap-3',
        'rounded-lg',
        'border',
        'p-4',
        'shadow-sm',
        'ease-in-out',
        'hover:shadow-md',
        'dark:border-gray-700',
        'dark:bg-gray-800'
      )
    })

    it('has correct CSS classes for show more/less button', () => {
      const repositories = createMockRepositories(5)
      render(<RepositoriesCard repositories={repositories} />)
      
      const showMoreButton = screen.getByRole('button', { name: /show more/i })
      expect(showMoreButton).toHaveClass(
        'mt-4',
        'flex',
        'items-center',
        'justify-center',
        'text-blue-400',
        'hover:underline'
      )
    })

    it('has correct container structure', () => {
      render(<RepositoriesCard repositories={[mockRepository]} />)
      
      const mainContainer = screen.getByRole('generic')
      expect(mainContainer).toBeInTheDocument()
      
      const gridContainer = mainContainer.querySelector('.grid')
      expect(gridContainer).toBeInTheDocument()
    })

    it('has correct button container structure', () => {
      const repositories = createMockRepositories(5)
      render(<RepositoriesCard repositories={repositories} />)
      
      const buttonContainer = screen.getByRole('button', { name: /show more/i }).closest('.mt-6')
      expect(buttonContainer).toHaveClass('mt-6', 'flex', 'items-center', 'justify-center', 'text-center')
    })
  })

  describe('Integration with child components', () => {
    it('renders InfoItem components with correct props', () => {
      render(<RepositoriesCard repositories={[mockRepository]} />)
      
      expect(screen.getByTestId('info-item-stars')).toBeInTheDocument()
      expect(screen.getByTestId('info-item-forks')).toBeInTheDocument()
      expect(screen.getByTestId('info-item-contributors')).toBeInTheDocument()
      expect(screen.getByTestId('info-item-issues')).toBeInTheDocument()
    })

    it('renders TruncatedText component with repository name', () => {
      render(<RepositoriesCard repositories={[mockRepository]} />)
      
      const truncatedText = screen.getByTestId('truncated-text')
      expect(truncatedText).toHaveTextContent('Test Repository')
    })

    it('renders FontAwesome icons correctly', () => {
      render(<RepositoriesCard repositories={[mockRepository]} />)
      
      // Check for chevron icons in show more/less button
      const repositories = createMockRepositories(5)
      render(<RepositoriesCard repositories={repositories} />)
      
      const showMoreButton = screen.getByRole('button', { name: /show more/i })
      expect(showMoreButton.querySelector('[data-testid="icon-chevron-down"]')).toBeInTheDocument()
      
      fireEvent.click(showMoreButton)
      
      const showLessButton = screen.getByRole('button', { name: /show less/i })
      expect(showLessButton.querySelector('[data-testid="icon-chevron-up"]')).toBeInTheDocument()
    })
  })

  describe('Error handling and robustness', () => {
    it('handles navigation errors gracefully', () => {
      mockPush.mockImplementation(() => {
        throw new Error('Navigation error')
      })
      
      render(<RepositoriesCard repositories={[mockRepository]} />)
      
      const repositoryButton = screen.getByRole('button', { name: /test repository/i })
      
      // Should not crash when navigation fails
      expect(() => fireEvent.click(repositoryButton)).not.toThrow()
    })

    it('handles missing organization data', () => {      
      render(<RepositoriesCard repositories={[{
          ...mockRepository,
          organization: undefined,
        }]} />)
      
      fireEvent.click(screen.getByRole('button', { name: /test repository/i }))
      
      // Should handle missing organization gracefully
      expect(mockPush).toHaveBeenCalledWith('/organizations/undefined/repositories/test-repo')
    })
  })
}) 