import { render, screen } from 'wrappers/testUtil'
import type { PullRequest } from 'types/pullRequest'
import MentorshipPullRequest, { getPRStatus } from 'components/MentorshipPullRequest'

describe('MentorshipPullRequest Component', () => {
  const mockPullRequestOpen: PullRequest = {
    id: '1',
    title: 'Add new feature to dashboard',
    state: 'open',
    url: 'https://github.com/test/repo/pull/1',
    createdAt: '2024-01-15',
    mergedAt: null,
    author: {
      login: 'testuser',
      avatarUrl: 'https://avatars.githubusercontent.com/u/12345?v=4',
    },
  }

  const mockPullRequestMerged: PullRequest = {
    id: '2',
    title: 'Fix critical bug in authentication',
    state: 'closed',
    url: 'https://github.com/test/repo/pull/2',
    createdAt: '2024-01-10',
    mergedAt: '2024-01-12',
    author: {
      login: 'Golovanova',
      avatarUrl: 'https://avatars.githubusercontent.com/u/54321?v=4',
    },
  }

  const mockPullRequestClosed: PullRequest = {
    id: '3',
    title: 'Rejected feature proposal',
    state: 'closed',
    url: 'https://github.com/test/repo/pull/3',
    createdAt: '2024-01-05',
    mergedAt: null,
    author: {
      login: 'Oleksiuk',
      avatarUrl: 'https://avatars.githubusercontent.com/u/99999?v=4',
    },
  }

  const mockPullRequestNoAuthor: PullRequest = {
    id: '4',
    title: 'Unknown author PR',
    state: 'open',
    url: 'https://github.com/test/repo/pull/4',
    createdAt: '2024-01-20',
    mergedAt: null,
    author: {
      login: null,
      avatarUrl: null,
    },
  }

  describe('getPRStatus function', () => {
    test('returns correct status for merged PR', () => {
      const status = getPRStatus(mockPullRequestMerged)
      expect(status.label).toBe('Merged')
      expect(status.backgroundColor).toBe('#8657E5')
    })

    test('returns correct status for closed PR', () => {
      const status = getPRStatus(mockPullRequestClosed)
      expect(status.label).toBe('Closed')
      expect(status.backgroundColor).toBe('#DA3633')
    })

    test('returns correct status for open PR', () => {
      const status = getPRStatus(mockPullRequestOpen)
      expect(status.label).toBe('Open')
      expect(status.backgroundColor).toBe('#238636')
    })
  })

  describe('MentorshipPullRequest component rendering', () => {
    test('renders open PR with all details', () => {
      render(<MentorshipPullRequest pr={mockPullRequestOpen} />)
      expect(screen.getByText('Add new feature to dashboard')).toBeInTheDocument()
      expect(screen.getByText(/by testuser/)).toBeInTheDocument()
      expect(screen.getByText('Open')).toBeInTheDocument()
    })

    test('renders merged PR with merged status', () => {
      render(<MentorshipPullRequest pr={mockPullRequestMerged} />)
      expect(screen.getByText('Fix critical bug in authentication')).toBeInTheDocument()
      expect(screen.getByText(/by Golovanova/)).toBeInTheDocument()
      expect(screen.getByText('Merged')).toBeInTheDocument()
    })

    test('renders closed PR with closed status', () => {
      render(<MentorshipPullRequest pr={mockPullRequestClosed} />)
      expect(screen.getByText('Rejected feature proposal')).toBeInTheDocument()
      expect(screen.getByText(/by Oleksiuk/)).toBeInTheDocument()
      expect(screen.getByText('Closed')).toBeInTheDocument()
    })

    test('renders PR with author avatar', () => {
      render(<MentorshipPullRequest pr={mockPullRequestOpen} />)
      const avatar = screen.getByAltText('testuser')
      expect(avatar).toBeInTheDocument()
      expect(avatar).toHaveAttribute('src')
    })

    test('renders placeholder when author has no avatar URL', () => {
      const { container } = render(<MentorshipPullRequest pr={mockPullRequestNoAuthor} />)
      // When no avatar URL, a div placeholder should be rendered instead of Image
      const images = container.querySelectorAll('img')
      // Only the TruncatedText link should have an image, not the avatar
      expect(images.length).toBeLessThan(2)
    })

    test('renders Unknown when author login is null', () => {
      render(<MentorshipPullRequest pr={mockPullRequestNoAuthor} />)
      expect(screen.getByText(/by Unknown/)).toBeInTheDocument()
    })

    test('renders PR title as a link with correct href', () => {
      render(<MentorshipPullRequest pr={mockPullRequestOpen} />)
      const link = screen.getByRole('link')
      expect(link).toHaveAttribute('href', mockPullRequestOpen.url)
      expect(link).toHaveAttribute('target', '_blank')
      expect(link).toHaveAttribute('rel', 'noopener noreferrer')
    })

    test('renders date in correct format', () => {
      render(<MentorshipPullRequest pr={mockPullRequestOpen} />)
      const dateStr = new Date('2024-01-15').toLocaleDateString()
      expect(screen.getByText(new RegExp(dateStr))).toBeInTheDocument()
    })

    test('applies correct styling to status badge for open PR', () => {
      render(<MentorshipPullRequest pr={mockPullRequestOpen} />)
      const badge = screen.getByText('Open')
      expect(badge).toHaveStyle('backgroundColor: #238636')
      expect(badge).toHaveClass('text-white')
      expect(badge).toHaveClass('text-xs')
      expect(badge).toHaveClass('font-medium')
    })

    test('applies correct styling to status badge for merged PR', () => {
      render(<MentorshipPullRequest pr={mockPullRequestMerged} />)
      const badge = screen.getByText('Merged')
      expect(badge).toHaveStyle('backgroundColor: #8657E5')
    })

    test('applies correct styling to status badge for closed PR', () => {
      render(<MentorshipPullRequest pr={mockPullRequestClosed} />)
      const badge = screen.getByText('Closed')
      expect(badge).toHaveStyle('backgroundColor: #DA3633')
    })

    test('renders with PR link that opens in new tab', () => {
      render(<MentorshipPullRequest pr={mockPullRequestMerged} />)
      const links = screen.getAllByRole('link')
      expect(links[0]).toHaveAttribute('target', '_blank')
      expect(links[0]).toHaveAttribute('rel', 'noopener noreferrer')
    })
    test('renders Unknown alt text when author login is empty but avatar exists', () => {
      const mockPrWithAvatarButNoLogin = {
        ...mockPullRequestOpen,
        author: {
          ...mockPullRequestOpen.author,
          login: '',
        },
      } as unknown as PullRequest

      render(<MentorshipPullRequest pr={mockPrWithAvatarButNoLogin} />)
      const avatar = screen.getByAltText('Unknown')
      expect(avatar).toBeInTheDocument()
    })
  })
})
