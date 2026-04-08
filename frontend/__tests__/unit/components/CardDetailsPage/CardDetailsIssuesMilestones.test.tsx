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

  it('renders grid containers when component rendered', () => {
    const { container } = render(<CardDetailsIssuesMilestones type="project" />)
    expect(container.querySelector('.lg\\:grid')).toBeInTheDocument()
  })

  it('renders all sections together for allowed types', () => {
    render(
      <CardDetailsIssuesMilestones
        type="project"
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

  it('does not render for chapter type', () => {
    const { container } = render(
      <CardDetailsIssuesMilestones type="chapter" recentIssues={[mockIssue]} />
    )
    expect(container.firstChild).toBeNull()
  })

  it('renders program type with milestones in secondary card', () => {
    render(<CardDetailsIssuesMilestones type="program" recentMilestones={[mockMilestone]} />)

    expect(screen.getByTestId('secondary-card')).toBeInTheDocument()
    expect(screen.getByTestId('secondary-card-title')).toHaveTextContent('Recent Milestones')
  })

  it('renders module type pull requests in secondary card', () => {
    render(<CardDetailsIssuesMilestones type="module" pullRequests={[mockPR]} />)

    expect(screen.getByTestId('secondary-card')).toBeInTheDocument()
    expect(screen.getByTestId('secondary-card-title')).toHaveTextContent('Recent Pull Requests')
    expect(screen.getByTestId('mentorship-pr-1')).toBeInTheDocument()
  })

  it('renders milestone with author avatar and repository info', () => {
    const milestoneWithDetails: Milestone = {
      id: '1',
      title: 'v1.0.0',
      url: 'https://github.com/milestone/1',
      createdAt: '2024-01-01',
      closedIssuesCount: 5,
      openIssuesCount: 2,
      author: {
        login: 'john_doe',
        name: 'John Doe',
        avatarUrl: 'https://example.com/avatar.jpg',
      },
      repositoryName: 'test-repo',
      organizationName: 'test-org',
    }

    render(
      <CardDetailsIssuesMilestones
        type="program"
        recentMilestones={[milestoneWithDetails]}
        showAvatar={true}
      />
    )

    expect(screen.getByAltText("John Doe's avatar")).toBeInTheDocument()
    expect(screen.getByText('5 closed')).toBeInTheDocument()
    expect(screen.getByText('2 open')).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'test-repo' })).toHaveAttribute(
      'href',
      '/organizations/test-org/repositories/test-repo'
    )
  })

  it('renders milestone with clickable title link', () => {
    const milestoneWithUrl: Milestone = {
      id: '1',
      title: 'External Link Milestone',
      url: 'https://external.example.com/milestone',
      createdAt: '2024-01-01',
      closedIssuesCount: 0,
      openIssuesCount: 0,
    }

    render(<CardDetailsIssuesMilestones type="program" recentMilestones={[milestoneWithUrl]} />)

    expect(screen.getByRole('link', { name: 'External Link Milestone' })).toHaveAttribute(
      'href',
      'https://external.example.com/milestone'
    )
  })

  it('renders program with 5+ milestones and shows more button', () => {
    const milestones = [
      { id: '1', title: 'v1.0', createdAt: '2024-01-01', closedIssuesCount: 5, openIssuesCount: 1 },
      { id: '2', title: 'v1.1', createdAt: '2024-01-02', closedIssuesCount: 3, openIssuesCount: 2 },
      { id: '3', title: 'v1.2', createdAt: '2024-01-03', closedIssuesCount: 4, openIssuesCount: 1 },
      { id: '4', title: 'v1.3', createdAt: '2024-01-04', closedIssuesCount: 2, openIssuesCount: 3 },
      { id: '5', title: 'v1.4', createdAt: '2024-01-05', closedIssuesCount: 1, openIssuesCount: 1 },
    ]

    render(<CardDetailsIssuesMilestones type="program" recentMilestones={milestones} />)

    expect(screen.getByText('v1.0')).toBeInTheDocument()
    expect(screen.getByText('v1.3')).toBeInTheDocument()
    expect(screen.queryByText('v1.4')).not.toBeInTheDocument()
    expect(screen.getByTestId('show-more-button')).toBeInTheDocument()
  })

  it('renders module with 5+ pull requests and toggles visibility', () => {
    const prs = [
      {
        id: '1',
        title: 'PR 1',
        url: 'https://github.com/pr/1',
        state: 'open',
        createdAt: '2024-01-01',
      },
      {
        id: '2',
        title: 'PR 2',
        url: 'https://github.com/pr/2',
        state: 'open',
        createdAt: '2024-01-02',
      },
      {
        id: '3',
        title: 'PR 3',
        url: 'https://github.com/pr/3',
        state: 'open',
        createdAt: '2024-01-03',
      },
      {
        id: '4',
        title: 'PR 4',
        url: 'https://github.com/pr/4',
        state: 'open',
        createdAt: '2024-01-04',
      },
      {
        id: '5',
        title: 'PR 5',
        url: 'https://github.com/pr/5',
        state: 'open',
        createdAt: '2024-01-05',
      },
    ]

    render(<CardDetailsIssuesMilestones type="module" pullRequests={prs} />)

    expect(screen.getByTestId('mentorship-pr-1')).toBeInTheDocument()
    expect(screen.getByTestId('mentorship-pr-4')).toBeInTheDocument()
    expect(screen.queryByTestId('mentorship-pr-5')).not.toBeInTheDocument()

    const showMoreBtn = screen.getByTestId('show-more-button')
    fireEvent.click(showMoreBtn)

    expect(screen.getByTestId('mentorship-pr-5')).toBeInTheDocument()
  })

  it('toggles all milestones visibility when show more button clicked in program type', () => {
    const milestones = [
      { id: '1', title: 'm1', createdAt: '2024-01-01', closedIssuesCount: 1, openIssuesCount: 1 },
      { id: '2', title: 'm2', createdAt: '2024-01-02', closedIssuesCount: 2, openIssuesCount: 1 },
      { id: '3', title: 'm3', createdAt: '2024-01-03', closedIssuesCount: 3, openIssuesCount: 1 },
      { id: '4', title: 'm4', createdAt: '2024-01-04', closedIssuesCount: 4, openIssuesCount: 1 },
      { id: '5', title: 'm5', createdAt: '2024-01-05', closedIssuesCount: 5, openIssuesCount: 1 },
    ]

    render(<CardDetailsIssuesMilestones type="program" recentMilestones={milestones} />)

    expect(screen.getByText('m1')).toBeInTheDocument()
    expect(screen.getByText('m4')).toBeInTheDocument()
    expect(screen.queryByText('m5')).not.toBeInTheDocument()

    const showMoreBtn = screen.getByTestId('show-more-button')
    fireEvent.click(showMoreBtn)

    expect(screen.getByText('m5')).toBeInTheDocument()
  })
})
