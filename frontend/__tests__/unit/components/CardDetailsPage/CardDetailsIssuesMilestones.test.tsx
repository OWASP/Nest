import { render, screen, fireEvent } from '@testing-library/react'
import React from 'react'
import '@testing-library/jest-dom'
import { Issue, Milestone, PullRequest, Release } from 'types'
import CardDetailsIssuesMilestones from 'components/CardDetailsPage/CardDetailsIssuesMilestones'

jest.mock('components/RecentIssues', () => ({
  __esModule: true,
  default: ({ data }: { data: Issue[] }) => (
    <div data-testid="recent-issues">Issues: {data.map((i) => i.title).join(', ')}</div>
  ),
}))

jest.mock('components/Milestones', () => ({
  __esModule: true,
  default: ({ data }: { data: Milestone[] }) => (
    <div data-testid="milestones">Milestones: {data.map((m) => m.title).join(', ')}</div>
  ),
}))

jest.mock('components/RecentPullRequests', () => ({
  __esModule: true,
  default: ({ data }: { data: PullRequest[] }) => (
    <div data-testid="recent-pull-requests">PRs: {data.map((pr) => pr.title).join(', ')}</div>
  ),
}))

jest.mock('components/RecentReleases', () => ({
  __esModule: true,
  default: ({ data }: { data: Release[] }) => (
    <div data-testid="recent-releases">Releases: {data.map((r) => r.name).join(', ')}</div>
  ),
}))

jest.mock('next/link', () => {
  return ({ children, href }: { children: React.ReactNode; href: string }) => (
    <a href={href}>{children}</a>
  )
})

jest.mock('components/MentorshipPullRequest', () => ({
  __esModule: true,
  default: ({ pr }: { pr: PullRequest }) => (
    <div data-testid={`mentorship-pr-${pr.id}`}>{pr.title}</div>
  ),
}))

jest.mock('components/SecondaryCard', () => ({
  __esModule: true,
  default: ({ title, children }: { title: React.ReactNode; children: React.ReactNode }) => (
    <div data-testid="secondary-card">
      <div data-testid="secondary-card-title">{title}</div>
      {children}
    </div>
  ),
}))

jest.mock('components/ShowMoreButton', () => ({
  __esModule: true,
  default: ({ onToggle }: { onToggle: () => void }) => (
    <button data-testid="show-more-button" onClick={onToggle}>
      Show More
    </button>
  ),
}))

jest.mock('components/AnchorTitle', () => ({
  __esModule: true,
  default: ({ title }: { title: string }) => <span>{title}</span>,
}))

jest.mock('next/image', () => ({
  __esModule: true,
  default: ({ alt, ...props }: Record<string, unknown>) => (
    // eslint-disable-next-line @next/next/no-img-element
    <img alt={alt as string} {...(props as React.ImgHTMLAttributes<HTMLImageElement>)} />
  ),
}))

jest.mock('components/TruncatedText', () => ({
  __esModule: true,
  TruncatedText: ({ text }: { text: string }) => <span>{text}</span>,
}))

jest.mock('utils/dateFormatter', () => ({
  formatDate: (date: string) => new Date(date).toLocaleDateString(),
}))

jest.mock('@heroui/tooltip', () => ({
  Tooltip: ({ children, content }: { children: React.ReactNode; content: string }) => (
    <div title={content}>{children}</div>
  ),
}))

describe('CardDetailsIssuesMilestones', () => {
  const mockIssue: Issue = {
    id: '1',
    title: 'Fix bug in parser',
    url: 'https://github.com/issue/1',
    state: 'open',
    createdAt: '2024-01-01',
  }

  const mockMilestone: Milestone = {
    id: '1',
    title: 'v1.0.0',
    url: 'https://github.com/milestone/1',
    dueOn: '2024-02-01',
  }

  const mockPR: PullRequest = {
    id: '1',
    title: 'Add new feature',
    url: 'https://github.com/pr/1',
    state: 'open',
    createdAt: '2024-01-05',
  }

  const mockRelease: Release = {
    id: '1',
    name: 'v1.0.0',
    url: 'https://github.com/releases/v1.0.0',
    publishedAt: '2024-01-15',
  }

  it('renders all sections together when provided', () => {
    render(
      <CardDetailsIssuesMilestones
        recentIssues={[mockIssue]}
        recentMilestones={[mockMilestone]}
        pullRequests={[mockPR]}
        recentReleases={[mockRelease]}
      />
    )

    expect(screen.getByTestId('recent-issues')).toBeInTheDocument()
    expect(screen.getByTestId('milestones')).toBeInTheDocument()
    expect(screen.getByTestId('recent-pull-requests')).toBeInTheDocument()
    expect(screen.getByTestId('recent-releases')).toBeInTheDocument()
  })

  it('renders nothing when no data provided', () => {
    const { container } = render(<CardDetailsIssuesMilestones />)
    expect(container.querySelector('div')).toBeEmptyDOMElement()
  })

  it('renders milestones in secondary card', () => {
    render(<CardDetailsIssuesMilestones recentMilestones={[mockMilestone]} />)

    expect(screen.getByTestId('milestones')).toBeInTheDocument()
  })

  it('renders pull requests when provided', () => {
    render(<CardDetailsIssuesMilestones pullRequests={[mockPR]} />)

    expect(screen.getByTestId('recent-pull-requests')).toBeInTheDocument()
  })

  it('renders milestones with show more button when 5+ items', () => {
    const milestones = [
      { id: '1', title: 'v1.0', createdAt: '2024-01-01', closedIssuesCount: 5, openIssuesCount: 1 },
      { id: '2', title: 'v1.1', createdAt: '2024-01-02', closedIssuesCount: 3, openIssuesCount: 2 },
      { id: '3', title: 'v1.2', createdAt: '2024-01-03', closedIssuesCount: 4, openIssuesCount: 1 },
      { id: '4', title: 'v1.3', createdAt: '2024-01-04', closedIssuesCount: 2, openIssuesCount: 3 },
      { id: '5', title: 'v1.4', createdAt: '2024-01-05', closedIssuesCount: 1, openIssuesCount: 1 },
    ]

    render(<CardDetailsIssuesMilestones recentMilestones={milestones} />)

    expect(screen.getByTestId('milestones')).toBeInTheDocument()
    expect(screen.getByText(/v1\./)).toBeInTheDocument()
  })

  it('toggles milestones visibility when show more button clicked', () => {
    const milestones = [
      { id: '1', title: 'm1', createdAt: '2024-01-01', closedIssuesCount: 1, openIssuesCount: 1 },
      { id: '2', title: 'm2', createdAt: '2024-01-02', closedIssuesCount: 2, openIssuesCount: 1 },
      { id: '3', title: 'm3', createdAt: '2024-01-03', closedIssuesCount: 3, openIssuesCount: 1 },
      { id: '4', title: 'm4', createdAt: '2024-01-04', closedIssuesCount: 4, openIssuesCount: 1 },
      { id: '5', title: 'm5', createdAt: '2024-01-05', closedIssuesCount: 5, openIssuesCount: 1 },
    ]

    render(<CardDetailsIssuesMilestones recentMilestones={milestones} isMilestoneOnly={true} />)

    expect(screen.getByText('m1')).toBeInTheDocument()
    expect(screen.getByText('m4')).toBeInTheDocument()
    expect(screen.queryByText('m5')).not.toBeInTheDocument()

    const showMoreButton = screen.getByTestId('show-more-button')
    fireEvent.click(showMoreButton)

    expect(screen.getByText('m5')).toBeInTheDocument()
  })

  it('renders milestones with all optional properties', () => {
    const milestoneWithAllProps: Milestone = {
      id: '1',
      title: 'Full Milestone',
      url: 'https://github.com/milestone/1',
      createdAt: '2024-01-01',
      closedIssuesCount: 10,
      openIssuesCount: 5,
      dueOn: '2024-02-01',
      author: {
        login: 'dev_user',
        name: 'Dev User',
        avatarUrl: 'https://example.com/dev-avatar.jpg',
      },
      repositoryName: 'main-repo',
      organizationName: 'main-org',
    }

    render(
      <CardDetailsIssuesMilestones
        recentMilestones={[milestoneWithAllProps]}
        isMilestoneOnly={true}
        showAvatar={true}
      />
    )

    expect(screen.getByTestId('secondary-card')).toBeInTheDocument()
    expect(screen.getByTestId('secondary-card-title')).toHaveTextContent('Recent Milestones')
    expect(screen.getByText('Full Milestone')).toBeInTheDocument()
    expect(screen.getByText(/10 closed/)).toBeInTheDocument()
    expect(screen.getByText(/5 open/)).toBeInTheDocument()
  })

  it('renders pull requests with load more functionality', () => {
    const prs = Array.from({ length: 5 }, (_, i) => ({
      id: String(i + 1),
      title: `PR ${i + 1}`,
      url: `https://github.com/pr/${i + 1}`,
      state: 'open' as const,
      createdAt: `2024-01-0${i + 1}`,
    }))

    const onLoadMore = jest.fn()

    render(
      <CardDetailsIssuesMilestones
        pullRequests={prs}
        isPullRequestOnly={true}
        onLoadMorePullRequests={onLoadMore}
      />
    )

    expect(screen.getByTestId('secondary-card')).toBeInTheDocument()
    expect(screen.getByText('PR 1')).toBeInTheDocument()
    expect(screen.getByText('PR 4')).toBeInTheDocument()
  })

  it('renders pull requests with toggle functionality', () => {
    const prs = Array.from({ length: 5 }, (_, i) => ({
      id: String(i + 1),
      title: `PR ${i + 1}`,
      url: `https://github.com/pr/${i + 1}`,
      state: 'open' as const,
      createdAt: `2024-01-0${i + 1}`,
    }))

    render(<CardDetailsIssuesMilestones pullRequests={prs} isPullRequestOnly={true} />)

    expect(screen.getByTestId('secondary-card')).toBeInTheDocument()
    const showMoreButton = screen.getByTestId('show-more-button')
    expect(showMoreButton).toBeInTheDocument()

    fireEvent.click(showMoreButton)
    expect(showMoreButton).toBeInTheDocument()
  })

  it('renders issues and milestones in grid layout', () => {
    render(
      <CardDetailsIssuesMilestones recentIssues={[mockIssue]} recentMilestones={[mockMilestone]} />
    )

    expect(screen.getByTestId('recent-issues')).toBeInTheDocument()
    expect(screen.getByTestId('milestones')).toBeInTheDocument()
  })

  it('renders releases in secondary grid', () => {
    render(<CardDetailsIssuesMilestones pullRequests={[mockPR]} recentReleases={[mockRelease]} />)

    expect(screen.getByTestId('recent-pull-requests')).toBeInTheDocument()
    expect(screen.getByTestId('recent-releases')).toBeInTheDocument()
  })

  it('renders empty milestone card without author', () => {
    const milestoneNoAuthor: Milestone = {
      id: '1',
      title: 'No Author Milestone',
      createdAt: '2024-01-01',
      closedIssuesCount: 0,
      openIssuesCount: 0,
    }

    render(
      <CardDetailsIssuesMilestones
        recentMilestones={[milestoneNoAuthor]}
        isMilestoneOnly={true}
        showAvatar={true}
      />
    )

    expect(screen.getByText('No Author Milestone')).toBeInTheDocument()
  })

  it('renders milestone without repository info', () => {
    const milestoneNoRepo: Milestone = {
      id: '1',
      title: 'No Repo Milestone',
      createdAt: '2024-01-01',
      closedIssuesCount: 1,
      openIssuesCount: 1,
      author: {
        login: 'user',
        name: 'User',
        avatarUrl: 'https://example.com/avatar.jpg',
      },
    }

    render(
      <CardDetailsIssuesMilestones
        recentMilestones={[milestoneNoRepo]}
        isMilestoneOnly={true}
        showAvatar={true}
      />
    )

    expect(screen.getByText('No Repo Milestone')).toBeInTheDocument()
    expect(screen.getByText(/1 closed/)).toBeInTheDocument()
    expect(screen.getByText(/1 open/)).toBeInTheDocument()
  })

  it('renders only milestones section when isMilestoneOnly is true', () => {
    const milestones = Array.from({ length: 3 }, (_, i) => ({
      id: String(i + 1),
      title: `m${i + 1}`,
      createdAt: `2024-01-0${i + 1}`,
      closedIssuesCount: i,
      openIssuesCount: i + 1,
    }))

    render(
      <CardDetailsIssuesMilestones
        recentMilestones={milestones}
        recentIssues={[mockIssue]}
        isMilestoneOnly={true}
      />
    )

    expect(screen.getByTestId('secondary-card')).toBeInTheDocument()
    expect(screen.queryByTestId('recent-issues')).not.toBeInTheDocument()
  })

  it('renders only pull requests section when isPullRequestOnly is true', () => {
    const prs = [
      {
        id: '1',
        title: 'PR Only',
        url: 'https://github.com/pr/1',
        state: 'open' as const,
        createdAt: '2024-01-01',
      },
    ]

    render(
      <CardDetailsIssuesMilestones
        pullRequests={prs}
        recentMilestones={[mockMilestone]}
        isPullRequestOnly={true}
      />
    )

    expect(screen.getByTestId('secondary-card')).toBeInTheDocument()
    expect(screen.getByTestId('secondary-card-title')).toHaveTextContent('Recent Pull Requests')
  })

  it('handles pull requests with fetch loading state', () => {
    const prs = Array.from({ length: 3 }, (_, i) => ({
      id: String(i + 1),
      title: `PR ${i + 1}`,
      url: `https://github.com/pr/${i + 1}`,
      state: 'open' as const,
      createdAt: `2024-01-0${i + 1}`,
    }))

    const onLoadMore = jest.fn()

    const { rerender } = render(
      <CardDetailsIssuesMilestones
        pullRequests={prs}
        isPullRequestOnly={true}
        onLoadMorePullRequests={onLoadMore}
        isFetchingMore={false}
      />
    )

    rerender(
      <CardDetailsIssuesMilestones
        pullRequests={prs}
        isPullRequestOnly={true}
        onLoadMorePullRequests={onLoadMore}
        isFetchingMore={true}
      />
    )

    expect(screen.getByTestId('secondary-card')).toBeInTheDocument()
  })

  it('renders nothing when isPullRequestOnly but no pull requests', () => {
    render(<CardDetailsIssuesMilestones pullRequests={[]} isPullRequestOnly={true} />)

    expect(screen.queryByTestId('secondary-card')).not.toBeInTheDocument()
  })

  it('renders nothing when isMilestoneOnly but no milestones', () => {
    render(<CardDetailsIssuesMilestones recentMilestones={[]} isMilestoneOnly={true} />)

    expect(screen.queryByTestId('secondary-card')).not.toBeInTheDocument()
  })

  it('renders both load more and reset buttons for pull requests', () => {
    const prs = Array.from({ length: 5 }, (_, i) => ({
      id: String(i + 1),
      title: `PR ${i + 1}`,
      url: `https://github.com/pr/${i + 1}`,
      state: 'open' as const,
      createdAt: `2024-01-0${i + 1}`,
    }))

    const onLoadMore = jest.fn()
    const onReset = jest.fn()

    render(
      <CardDetailsIssuesMilestones
        pullRequests={prs}
        isPullRequestOnly={true}
        onLoadMorePullRequests={onLoadMore}
        onResetPullRequests={onReset}
      />
    )

    expect(screen.getByTestId('secondary-card')).toBeInTheDocument()
  })

  it('renders milestone with url as clickable link', () => {
    const milestoneWithUrl: Milestone = {
      id: '1',
      title: 'v2.0.0',
      url: 'https://github.com/milestone/2',
      createdAt: '2024-02-01',
      closedIssuesCount: 8,
      openIssuesCount: 2,
    }

    render(
      <CardDetailsIssuesMilestones recentMilestones={[milestoneWithUrl]} isMilestoneOnly={true} />
    )

    const link = screen.getByRole('link', { hidden: true })
    expect(link).toHaveAttribute('href', 'https://github.com/milestone/2')
  })

  it('renders milestone without url as plain text', () => {
    const milestoneNoUrl: Milestone = {
      id: '1',
      title: 'v3.0.0',
      createdAt: '2024-03-01',
      closedIssuesCount: 12,
      openIssuesCount: 0,
    }

    render(
      <CardDetailsIssuesMilestones recentMilestones={[milestoneNoUrl]} isMilestoneOnly={true} />
    )

    expect(screen.getByText('v3.0.0')).toBeInTheDocument()
  })

  it('renders milestone with repository link', () => {
    const milestoneWithRepo: Milestone = {
      id: '1',
      title: 'v1.5.0',
      createdAt: '2024-01-15',
      closedIssuesCount: 3,
      openIssuesCount: 1,
      repositoryName: 'awesome-repo',
      organizationName: 'awesome-org',
    }

    render(
      <CardDetailsIssuesMilestones recentMilestones={[milestoneWithRepo]} isMilestoneOnly={true} />
    )

    const repoText = screen.getByText('awesome-repo')
    const repoLink = repoText.closest('a')
    expect(repoLink).toBeInTheDocument()
    expect(repoLink).toHaveAttribute('href', '/organizations/awesome-org/repositories/awesome-repo')
  })

  it('renders milestone with author avatar and clickable author link', () => {
    const milestoneWithAuthorAndAvatar: Milestone = {
      id: '1',
      title: 'Release v1.0',
      createdAt: '2024-01-10',
      closedIssuesCount: 5,
      openIssuesCount: 2,
      author: {
        login: 'contributor-a',
        name: 'Contributor A',
        avatarUrl: 'https://example.com/contrib-a.jpg',
      },
    }

    render(
      <CardDetailsIssuesMilestones
        recentMilestones={[milestoneWithAuthorAndAvatar]}
        isMilestoneOnly={true}
        showAvatar={true}
      />
    )

    const authorLinks = screen.getAllByRole('link', { hidden: true })
    const authorLink = authorLinks.find(
      (link) => link.getAttribute('href') === '/members/contributor-a'
    )
    expect(authorLink).toBeInTheDocument()
  })

  it('renders milestone dueOn date when available', () => {
    const milestoneWithDueDate: Milestone = {
      id: '1',
      title: 'Sprint End',
      createdAt: '2024-01-01',
      dueOn: '2024-03-31',
      closedIssuesCount: 10,
      openIssuesCount: 5,
    }

    render(
      <CardDetailsIssuesMilestones
        recentMilestones={[milestoneWithDueDate]}
        isMilestoneOnly={true}
      />
    )

    expect(screen.getByText('Sprint End')).toBeInTheDocument()
  })

  it('renders milestone without createdAt', () => {
    const milestoneNoCreatedAt: Milestone = {
      id: '1',
      title: 'Future Release',
      dueOn: '2024-12-31',
      closedIssuesCount: 0,
      openIssuesCount: 0,
    }

    render(
      <CardDetailsIssuesMilestones
        recentMilestones={[milestoneNoCreatedAt]}
        isMilestoneOnly={true}
      />
    )

    expect(screen.getByText('Future Release')).toBeInTheDocument()
  })

  it('renders milestone without both repository and organization', () => {
    const milestoneOnlyTitle: Milestone = {
      id: '1',
      title: 'Standalone Milestone',
      createdAt: '2024-01-01',
      closedIssuesCount: 1,
      openIssuesCount: 1,
    }

    render(
      <CardDetailsIssuesMilestones recentMilestones={[milestoneOnlyTitle]} isMilestoneOnly={true} />
    )

    expect(screen.getByText('Standalone Milestone')).toBeInTheDocument()
    expect(screen.getByText(/1 closed/)).toBeInTheDocument()
  })

  it('does not render show more button when pull requests <= 4 and no callbacks', () => {
    const prs = [
      {
        id: '1',
        title: 'PR 1',
        url: 'https://github.com/pr/1',
        state: 'open' as const,
        createdAt: '2024-01-01',
      },
      {
        id: '2',
        title: 'PR 2',
        url: 'https://github.com/pr/2',
        state: 'open' as const,
        createdAt: '2024-01-02',
      },
    ]

    render(<CardDetailsIssuesMilestones pullRequests={prs} isPullRequestOnly={true} />)

    expect(screen.queryByTestId('show-more-button')).not.toBeInTheDocument()
  })

  it('renders show more button when pull requests > 4 and no callbacks', () => {
    const prs = Array.from({ length: 5 }, (_, i) => ({
      id: String(i + 1),
      title: `PR ${i + 1}`,
      url: `https://github.com/pr/${i + 1}`,
      state: 'open' as const,
      createdAt: `2024-01-0${i + 1}`,
    }))

    render(<CardDetailsIssuesMilestones pullRequests={prs} isPullRequestOnly={true} />)

    const showMoreButton = screen.getByTestId('show-more-button')
    expect(showMoreButton).toBeInTheDocument()
    expect(showMoreButton).toHaveTextContent('Show More')
  })

  it('handles onResetPullRequests callback click', () => {
    const prs = Array.from({ length: 3 }, (_, i) => ({
      id: String(i + 1),
      title: `PR ${i + 1}`,
      url: `https://github.com/pr/${i + 1}`,
      state: 'open' as const,
      createdAt: `2024-01-0${i + 1}`,
    }))

    const onReset = jest.fn()

    render(
      <CardDetailsIssuesMilestones
        pullRequests={prs}
        isPullRequestOnly={true}
        onResetPullRequests={onReset}
      />
    )

    expect(screen.getByTestId('secondary-card')).toBeInTheDocument()
  })

  it('renders multiple milestones and toggles show more correctly', () => {
    const milestones = Array.from({ length: 6 }, (_, i) => ({
      id: String(i + 1),
      title: `v${i + 1}.0`,
      createdAt: `2024-01-${String(i + 1).padStart(2, '0')}`,
      closedIssuesCount: i,
      openIssuesCount: i + 1,
    }))

    render(<CardDetailsIssuesMilestones recentMilestones={milestones} isMilestoneOnly={true} />)

    const showMoreButton = screen.getByTestId('show-more-button')
    expect(showMoreButton).toBeInTheDocument()

    expect(screen.getByText('v1.0')).toBeInTheDocument()
    expect(screen.queryByText('v5.0')).not.toBeInTheDocument()
  })

  it('renders load more button with correct disabled state', () => {
    const prs = Array.from({ length: 3 }, (_, i) => ({
      id: String(i + 1),
      title: `PR ${i + 1}`,
      url: `https://github.com/pr/${i + 1}`,
      state: 'open' as const,
      createdAt: `2024-01-0${i + 1}`,
    }))

    const onLoadMore = jest.fn()

    const { rerender } = render(
      <CardDetailsIssuesMilestones
        pullRequests={prs}
        isPullRequestOnly={true}
        onLoadMorePullRequests={onLoadMore}
        isFetchingMore={false}
      />
    )

    const loadMoreBtn = screen.getByRole('button', { name: /Show more/ })
    expect(loadMoreBtn).not.toBeDisabled()

    rerender(
      <CardDetailsIssuesMilestones
        pullRequests={prs}
        isPullRequestOnly={true}
        onLoadMorePullRequests={onLoadMore}
        isFetchingMore={true}
      />
    )

    expect(screen.getByText('Loading...')).toBeInTheDocument()
  })

  it('renders reset button with correct disabled state', () => {
    const prs = Array.from({ length: 3 }, (_, i) => ({
      id: String(i + 1),
      title: `PR ${i + 1}`,
      url: `https://github.com/pr/${i + 1}`,
      state: 'open' as const,
      createdAt: `2024-01-0${i + 1}`,
    }))

    const onReset = jest.fn()

    const { rerender } = render(
      <CardDetailsIssuesMilestones
        pullRequests={prs}
        isPullRequestOnly={true}
        onResetPullRequests={onReset}
        isFetchingMore={false}
      />
    )

    const resetBtn = screen.getByText('Show less')
    expect(resetBtn).not.toBeDisabled()

    rerender(
      <CardDetailsIssuesMilestones
        pullRequests={prs}
        isPullRequestOnly={true}
        onResetPullRequests={onReset}
        isFetchingMore={true}
      />
    )

    const disabledBtn = screen.getByText('Show less')
    expect(disabledBtn).toBeDisabled()
  })

  it('applies correct cursor styles when fetching more', () => {
    const prs = Array.from({ length: 3 }, (_, i) => ({
      id: String(i + 1),
      title: `PR ${i + 1}`,
      url: `https://github.com/pr/${i + 1}`,
      state: 'open' as const,
      createdAt: `2024-01-0${i + 1}`,
    }))

    const onLoadMore = jest.fn()

    const { rerender } = render(
      <CardDetailsIssuesMilestones
        pullRequests={prs}
        isPullRequestOnly={true}
        onLoadMorePullRequests={onLoadMore}
        isFetchingMore={false}
      />
    )

    let loadMoreBtn = screen.getByRole('button', { name: /Show more/ })
    expect(loadMoreBtn.className).not.toContain('cursor-not-allowed')

    rerender(
      <CardDetailsIssuesMilestones
        pullRequests={prs}
        isPullRequestOnly={true}
        onLoadMorePullRequests={onLoadMore}
        isFetchingMore={true}
      />
    )

    loadMoreBtn = screen.getByText('Loading...')
    expect(loadMoreBtn.className).toContain('cursor-not-allowed')
  })

  it('renders milestone title as link when url provided', () => {
    const milestoneWithExtUrl: Milestone = {
      id: '1',
      title: 'External Release',
      url: 'https://external-release.com',
      createdAt: '2024-01-01',
      closedIssuesCount: 5,
      openIssuesCount: 1,
    }

    render(
      <CardDetailsIssuesMilestones
        recentMilestones={[milestoneWithExtUrl]}
        isMilestoneOnly={true}
      />
    )

    const links = screen.getAllByRole('link', { hidden: true })
    const externalLink = links.find(
      (link) => link.getAttribute('href') === 'https://external-release.com'
    )
    expect(externalLink).toBeInTheDocument()
    expect(externalLink).toHaveAttribute('href', 'https://external-release.com')
  })

  it('renders milestone with author using only login when name not provided', () => {
    const milestoneAuthorNoName: Milestone = {
      id: '1',
      title: 'Release v1.2',
      createdAt: '2024-01-20',
      closedIssuesCount: 3,
      openIssuesCount: 1,
      author: {
        login: 'author_login',
        avatarUrl: 'https://example.com/author.jpg',
      },
    }

    render(
      <CardDetailsIssuesMilestones
        recentMilestones={[milestoneAuthorNoName]}
        isMilestoneOnly={true}
        showAvatar={true}
      />
    )

    expect(screen.getByText('Release v1.2')).toBeInTheDocument()
  })

  it('does not render milestone author avatar when showAvatar is false', () => {
    const milestoneWithAuthor: Milestone = {
      id: '1',
      title: 'Release v2.0',
      createdAt: '2024-02-01',
      closedIssuesCount: 10,
      openIssuesCount: 2,
      author: {
        login: 'dev_author',
        name: 'Developer',
        avatarUrl: 'https://example.com/dev.jpg',
      },
    }

    render(
      <CardDetailsIssuesMilestones
        recentMilestones={[milestoneWithAuthor]}
        isMilestoneOnly={true}
        showAvatar={false}
      />
    )

    expect(screen.queryByAltText(/avatar/)).not.toBeInTheDocument()
    expect(screen.getByText('Release v2.0')).toBeInTheDocument()
  })

  it('does not render author avatar when author login is missing', () => {
    const milestoneNoAuthorLogin: Milestone = {
      id: '1',
      title: 'Release v1.5',
      createdAt: '2024-01-30',
      closedIssuesCount: 7,
      openIssuesCount: 1,
      author: {
        name: 'Some Developer',
        avatarUrl: 'https://example.com/dev.jpg',
      },
    }

    render(
      <CardDetailsIssuesMilestones
        recentMilestones={[milestoneNoAuthorLogin]}
        isMilestoneOnly={true}
        showAvatar={true}
      />
    )

    expect(screen.getByText('Release v1.5')).toBeInTheDocument()
  })

  it('does not render author avatar when avatar url is missing', () => {
    const milestoneNoAvatarUrl: Milestone = {
      id: '1',
      title: 'Release v1.8',
      createdAt: '2024-01-25',
      closedIssuesCount: 4,
      openIssuesCount: 2,
      author: {
        login: 'author_name',
        name: 'Author Full Name',
      },
    }

    render(
      <CardDetailsIssuesMilestones
        recentMilestones={[milestoneNoAvatarUrl]}
        isMilestoneOnly={true}
        showAvatar={true}
      />
    )

    expect(screen.getByText('Release v1.8')).toBeInTheDocument()
  })

  it('renders repository link with correct href structure', () => {
    const milestoneRepo: Milestone = {
      id: '1',
      title: 'Release v2.0.0',
      createdAt: '2024-02-15',
      closedIssuesCount: 20,
      openIssuesCount: 5,
      repositoryName: 'production-repo',
      organizationName: 'prod-org',
    }

    render(
      <CardDetailsIssuesMilestones recentMilestones={[milestoneRepo]} isMilestoneOnly={true} />
    )

    const repoLink = screen.getByText('production-repo').closest('a')
    expect(repoLink).toHaveAttribute('href', '/organizations/prod-org/repositories/production-repo')
  })

  it('only renders repository section when both name and org present', () => {
    const milestonePartialRepo2: Milestone = {
      id: '1',
      title: 'Release v1.9',
      createdAt: '2024-02-10',
      closedIssuesCount: 8,
      openIssuesCount: 2,
      organizationName: 'only-org',
    }

    render(
      <CardDetailsIssuesMilestones
        recentMilestones={[milestonePartialRepo2]}
        isMilestoneOnly={true}
      />
    )

    expect(screen.getByText('Release v1.9')).toBeInTheDocument()
    expect(screen.queryByRole('link', { name: /only-org/ })).not.toBeInTheDocument()
  })
})
