import { fireEvent, screen } from '@testing-library/react'
import { useRouter } from 'next/navigation'
import React from 'react'
import { render } from 'wrappers/testUtil'
import type { Organization } from 'types/organization'
import type { RepositoryCardProps } from 'types/project'
import RepositoryCard from 'components/RepositoryCard'

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

describe('RepositoryCard', () => {
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
    render(<RepositoryCard repositories={[]} />)
    expect(screen.queryByRole('button', { name: /Show/ })).not.toBeInTheDocument()
  })

  it('returns null when repositories prop is missing', () => {
    const { container } = render(
      <RepositoryCard repositories={null as unknown as RepositoryCardProps[]} />
    )
    expect(container.querySelector('.grid')).toBeNull()
  })

  it('shows first 4 repositories initially when there are more than 4', () => {
    const repositories = Array.from({ length: 6 }, (_, i) => createMockRepository(i))

    render(<RepositoryCard repositories={repositories} />)

    expect(screen.getByText('Repository 0')).toBeInTheDocument()
    expect(screen.getByText('Repository 3')).toBeInTheDocument()
    expect(screen.queryByText('Repository 4')).not.toBeInTheDocument()
    expect(screen.queryByText('Repository 5')).not.toBeInTheDocument()
  })

  it('shows all repositories when there are 4 or fewer', () => {
    const repositories = Array.from({ length: 3 }, (_, i) => createMockRepository(i))

    render(<RepositoryCard repositories={repositories} />)

    expect(screen.getByText('Repository 0')).toBeInTheDocument()
    expect(screen.getByText('Repository 1')).toBeInTheDocument()
    expect(screen.getByText('Repository 2')).toBeInTheDocument()
  })

  it('displays ShowMoreButton when there are more than 4 repositories', () => {
    const repositories = Array.from({ length: 6 }, (_, i) => createMockRepository(i))

    render(<RepositoryCard repositories={repositories} />)

    expect(screen.getByRole('button', { name: /Show/ })).toBeInTheDocument()
  })

  it('does not display ShowMoreButton when there are 4 or fewer repositories', () => {
    const repositories = Array.from({ length: 4 }, (_, i) => createMockRepository(i))

    render(<RepositoryCard repositories={repositories} />)

    expect(screen.queryByRole('button', { name: /Show/ })).not.toBeInTheDocument()
  })

  it('toggles between showing 4 and all repositories when clicked', () => {
    const repositories = Array.from({ length: 6 }, (_, i) => createMockRepository(i))

    render(<RepositoryCard repositories={repositories} />)

    // Initially shows first 4
    expect(screen.getByText('Repository 0')).toBeInTheDocument()
    expect(screen.queryByText('Repository 4')).not.toBeInTheDocument()

    // Click show more
    fireEvent.click(screen.getByRole('button', { name: /Show/ }))

    // Now shows all repositories
    expect(screen.getByText('Repository 4')).toBeInTheDocument()
    expect(screen.getByText('Repository 5')).toBeInTheDocument()

    // Click show less
    fireEvent.click(screen.getByRole('button', { name: /Show/ }))

    // Back to showing first 4
    expect(screen.queryByText('Repository 4')).not.toBeInTheDocument()
    expect(screen.queryByText('Repository 5')).not.toBeInTheDocument()
  })

  it('renders repository items with correct information', () => {
    const repositories = [createMockRepository(0)]

    render(<RepositoryCard repositories={repositories} />)

    expect(screen.getByText('Repository 0')).toBeInTheDocument()
    expect(screen.getByTestId('info-item-Star')).toBeInTheDocument()
    expect(screen.getByTestId('info-item-Fork')).toBeInTheDocument()
    expect(screen.getByTestId('info-item-Contributor')).toBeInTheDocument()
    expect(screen.getByTestId('info-item-Issue')).toBeInTheDocument()
  })

  it('navigates to correct URL when repository item is clicked', () => {
    const repositories = [createMockRepository(0)]

    render(<RepositoryCard repositories={repositories} />)

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

    expect(() => render(<RepositoryCard repositories={[repository]} />)).not.toThrow()
  })

  it('repository title button has cursor-pointer class', () => {
    const repositories = [createMockRepository(0)]

    const { container } = render(<RepositoryCard repositories={repositories} />)

    const button = container.querySelector('button.cursor-pointer')
    expect(button).toBeInTheDocument()
    expect(button).toHaveClass('cursor-pointer')
  })

  it('repository title is rendered as a button element', () => {
    const repositories = [createMockRepository(0)]

    render(<RepositoryCard repositories={repositories} />)

    const repositoryButton = screen.getByText('Repository 0').closest('button')
    expect(repositoryButton).toBeInTheDocument()
    expect(repositoryButton?.tagName).toBe('BUTTON')
  })

  describe('Archived Badge on Repository Cards', () => {
    it('displays archived badge for archived repository', () => {
      const archivedRepo: RepositoryCardProps = {
        ...createMockRepository(0),
        isArchived: true,
      }

      render(<RepositoryCard repositories={[archivedRepo]} />)

      expect(screen.getByText('Archived')).toBeInTheDocument()
    })

    it('does not display archived badge for non-archived repository', () => {
      const activeRepo: RepositoryCardProps = {
        ...createMockRepository(0),
        isArchived: false,
      }

      render(<RepositoryCard repositories={[activeRepo]} />)

      expect(screen.queryByText('Archived')).not.toBeInTheDocument()
    })

    it('does not display archived badge when isArchived is undefined', () => {
      const repo: RepositoryCardProps = {
        ...createMockRepository(0),
      }

      render(<RepositoryCard repositories={[repo]} />)

      expect(screen.queryByText('Archived')).not.toBeInTheDocument()
    })

    it('displays archived badge only for archived repos in mixed list', () => {
      const repositories = [
        { ...createMockRepository(0), isArchived: true },
        { ...createMockRepository(1), isArchived: false },
        { ...createMockRepository(2), isArchived: true },
        { ...createMockRepository(3) },
      ]

      render(<RepositoryCard repositories={repositories} />)

      const badges = screen.getAllByText('Archived')
      expect(badges).toHaveLength(2)
    })

    it('archived badge has small size on cards', () => {
      const archivedRepo: RepositoryCardProps = {
        ...createMockRepository(0),
        isArchived: true,
      }

      render(<RepositoryCard repositories={[archivedRepo]} />)

      const badge = screen.getByText('Archived')
      expect(badge).toHaveClass('px-2', 'py-1', 'text-xs')
    })

    it('archived badge does not show icon on cards', () => {
      const archivedRepo: RepositoryCardProps = {
        ...createMockRepository(0),
        isArchived: true,
      }

      render(<RepositoryCard repositories={[archivedRepo]} />)

      const badge = screen.getByText('Archived')
      const icon = badge.querySelector('svg')
      expect(icon).not.toBeInTheDocument()
    })

    it('archived badge does not break card layout', () => {
      const archivedRepo: RepositoryCardProps = {
        ...createMockRepository(0),
        isArchived: true,
      }

      render(<RepositoryCard repositories={[archivedRepo]} />)

      expect(screen.getByText('Repository 0')).toBeInTheDocument()
      expect(screen.getByTestId('info-item-Star')).toBeInTheDocument()
      expect(screen.getByTestId('info-item-Fork')).toBeInTheDocument()
      expect(screen.getByText('Archived')).toBeInTheDocument()
    })

    it('archived badge is positioned correctly with repository name', () => {
      const archivedRepo: RepositoryCardProps = {
        ...createMockRepository(0),
        isArchived: true,
      }

      const { container } = render(<RepositoryCard repositories={[archivedRepo]} />)

      const headerContainer = container.querySelector('.flex.items-start.justify-between')
      expect(headerContainer).toBeInTheDocument()
    })

    it('handles null isArchived gracefully', () => {
      const repo: RepositoryCardProps = {
        ...createMockRepository(0),
        isArchived: null,
      }

      render(<RepositoryCard repositories={[repo]} />)

      expect(screen.queryByText('Archived')).not.toBeInTheDocument()
    })

    it('archived badge persists when toggling show more/less', () => {
      const repositories = Array.from({ length: 6 }, (_, i) => ({
        ...createMockRepository(i),
        isArchived: i % 2 === 0,
      }))

      render(<RepositoryCard repositories={repositories} />)

      expect(screen.getAllByText('Archived')).toHaveLength(2)

      fireEvent.click(screen.getByRole('button', { name: /Show/ }))

      expect(screen.getAllByText('Archived')).toHaveLength(3)

      fireEvent.click(screen.getByRole('button', { name: /Show/ }))

      expect(screen.getAllByText('Archived')).toHaveLength(2)
    })

    it('clicking archived repository still navigates correctly', () => {
      const archivedRepo: RepositoryCardProps = {
        ...createMockRepository(0),
        isArchived: true,
      }

      render(<RepositoryCard repositories={[archivedRepo]} />)

      const repositoryButton = screen.getByText('Repository 0')
      fireEvent.click(repositoryButton)

      expect(mockPush).toHaveBeenCalledWith('/organizations/org-0/repositories/repo-0')
    })
  })

  describe('Keyboard Navigation', () => {
    it('navigates to repository page when Enter key is pressed', () => {
      const repositories = [createMockRepository(0)]

      render(<RepositoryCard repositories={repositories} />)

      const repositoryButton = screen.getByText('Repository 0').closest('button')
      fireEvent.keyDown(repositoryButton!, { key: 'Enter' })

      expect(mockPush).toHaveBeenCalledWith('/organizations/org-0/repositories/repo-0')
    })

    it('navigates to repository page when Space key is pressed', () => {
      const repositories = [createMockRepository(0)]

      render(<RepositoryCard repositories={repositories} />)

      const repositoryButton = screen.getByText('Repository 0').closest('button')
      fireEvent.keyDown(repositoryButton!, { key: ' ' })

      expect(mockPush).toHaveBeenCalledWith('/organizations/org-0/repositories/repo-0')
    })

    it('does not navigate when other keys are pressed', () => {
      const repositories = [createMockRepository(0)]

      render(<RepositoryCard repositories={repositories} />)

      const repositoryButton = screen.getByText('Repository 0').closest('button')
      fireEvent.keyDown(repositoryButton!, { key: 'Tab' })
      fireEvent.keyDown(repositoryButton!, { key: 'Escape' })
      fireEvent.keyDown(repositoryButton!, { key: 'a' })

      expect(mockPush).not.toHaveBeenCalled()
    })
  })
})
