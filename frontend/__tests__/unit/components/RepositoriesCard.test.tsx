import { fireEvent, screen } from '@testing-library/react'
import { useRouter } from 'next/navigation'
import React from 'react'
import { render } from 'wrappers/testUtil'
import type { Organization } from 'types/organization'
import type { RepositoryCardProps } from 'types/project'
import RepositoriesCard from 'components/RepositoriesCard'

jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
}))

jest.mock('components/ShowMoreButton', () => {
  return function MockShowMoreButton({ onToggle }: { onToggle: () => void }) {
    const [isExpanded, setIsExpanded] = React.useState(false)

    const handleToggle = () => {
      setIsExpanded(!isExpanded)
      onToggle()
    }

    return (
      <button type="button" onClick={handleToggle} data-testid="show-more-button">
        {isExpanded ? 'Show less' : 'Show more'}
      </button>
    )
  }
})

jest.mock('components/TruncatedText', () => ({
  TruncatedText: ({ text }: { text: string }) => <span>{text}</span>,
}))

jest.mock('components/InfoItem', () => {
  return function MockInfoItem({ unit, value }: { unit: string; value: number }) {
    return <div data-testid={`info-item-${unit}`}>{value}</div>
  }
})

const mockPush = jest.fn()
const mockUseRouter = useRouter as jest.Mock

describe('RepositoriesCard', () => {
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
    expect(screen.queryByTestId('show-more-button')).not.toBeInTheDocument()
  })

  it('shows first 4 repositories initially when there are more than 4', () => {
    const repositories = Array.from({ length: 6 }, (_, i) => createMockRepository(i))

    render(<RepositoriesCard repositories={repositories} />)

    expect(screen.getByText('Repository 0')).toBeInTheDocument()
    expect(screen.getByText('Repository 3')).toBeInTheDocument()
    expect(screen.queryByText('Repository 4')).not.toBeInTheDocument()
    expect(screen.queryByText('Repository 5')).not.toBeInTheDocument()
  })

  it('shows all repositories when there are 4 or fewer', () => {
    const repositories = Array.from({ length: 3 }, (_, i) => createMockRepository(i))

    render(<RepositoriesCard repositories={repositories} />)

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
    expect(screen.queryByText('Repository 4')).not.toBeInTheDocument()

    // Click show more
    fireEvent.click(screen.getByTestId('show-more-button'))

    // Now shows all repositories
    expect(screen.getByText('Repository 4')).toBeInTheDocument()
    expect(screen.getByText('Repository 5')).toBeInTheDocument()

    // Click show less
    fireEvent.click(screen.getByTestId('show-more-button'))

    // Back to showing first 4
    expect(screen.queryByText('Repository 4')).not.toBeInTheDocument()
    expect(screen.queryByText('Repository 5')).not.toBeInTheDocument()
  })

  it('renders repository items with correct information', () => {
    const repositories = [createMockRepository(0)]

    render(<RepositoriesCard repositories={repositories} />)

    expect(screen.getByText('Repository 0')).toBeInTheDocument()
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

  it('handles repositories without organization data gracefully', () => {
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

    expect(() => render(<RepositoriesCard repositories={[repository]} />)).not.toThrow()
  })
})
