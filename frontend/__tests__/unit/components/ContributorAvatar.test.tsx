import { screen, render, cleanup } from '@testing-library/react'
import React from 'react'
import { Contributor } from 'types/contributor'
import ContributorAvatar from 'components/ContributorAvatar'

jest.mock('@heroui/tooltip', () => ({
  Tooltip: ({
    children,
    content,
    id,
  }: {
    children: React.ReactNode
    content: string
    id: string
  }) => (
    <div data-testid={id} title={content}>
      {children}
    </div>
  ),
}))

jest.mock('next/image', () => {
  return ({
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
      data-testid="contributor-avatar"
    />
  )
})

const mockAlgoliaContributor: Contributor = {
  login: 'johndoe',
  name: 'John Doe',
  avatarUrl: 'https://github.com/johndoe.png',
  contributionsCount: 25,
  projectKey: 'test-key',
}

const mockGitHubContributor: Contributor = {
  login: 'jane-doe',
  name: 'Jane Doe',
  avatarUrl: 'https://avatars.githubusercontent.com/u/12345',
  contributionsCount: 15,
  projectName: 'OWASP-Nest',
  projectKey: 'test-key',
}
describe('ContributorAvatar', () => {
  afterEach(() => {
    cleanup()
    jest.clearAllMocks()
  })

  it('renders successfully with minimal required props', () => {
    const uniqueKey = 'test-unique-key'
    render(<ContributorAvatar contributor={mockAlgoliaContributor} uniqueKey={uniqueKey} />)

    expect(screen.getByTestId('contributor-avatar')).toBeInTheDocument()
    expect(screen.getByTestId('contributor-link')).toBeInTheDocument()
  })

  it('displays contributor avatar with correct attributes', () => {
    render(<ContributorAvatar contributor={mockAlgoliaContributor} uniqueKey="test-key" />)

    const avatar = screen.getByTestId('contributor-avatar')
    expect(avatar).toHaveAttribute('src', 'https://github.com/johndoe.png&s=60')
    expect(avatar).toHaveAttribute('alt', "John Doe's avatar")
    expect(avatar).toHaveAttribute('width', '30')
    expect(avatar).toHaveAttribute('height', '30')
  })

  it('applies correct CSS classes for styling and animations', () => {
    render(<ContributorAvatar contributor={mockGitHubContributor} uniqueKey="style-test" />)
    const avatar = screen.getByTestId('contributor-avatar')
    expect(avatar).toHaveClass(
      'rounded-full',
      'grayscale',
      'transition-all',
      'duration-300',
      'hover:scale-110',
      'hover:grayscale-0'
    )
  })

  it('adds query parameter to avatar URL for all contributors', () => {
    render(<ContributorAvatar contributor={mockGitHubContributor} uniqueKey="github-test" />)
    const avatar = screen.getByTestId('contributor-avatar')
    expect(avatar).toHaveAttribute('src', 'https://avatars.githubusercontent.com/u/12345&s=60')
  })

  it('shows contributions count and name for contributor with contributions', () => {
    render(<ContributorAvatar contributor={mockGitHubContributor} uniqueKey="tooltip-test" />)
    const tooltip = screen.getByTestId('avatar-tooltip-jane-doe-tooltip-test')
    expect(tooltip).toHaveAttribute('title', '15 contributions by Jane Doe')
  })

  it('shows only name when no contributions count', () => {
    const contributorWithoutContributions = {
      login: 'newbie',
      name: 'New Contributor',
      avatarUrl: 'https://github.com/newbie.png',
      projectKey: 'test-key',
    }
    render(
      <ContributorAvatar
        contributor={contributorWithoutContributions}
        uniqueKey="no-contrib-test"
      />
    )
    const tooltip = screen.getByTestId('avatar-tooltip-newbie-no-contrib-test')
    expect(tooltip).toHaveAttribute('title', 'New Contributor')
  })

  it('handles contributor with zero contributions', () => {
    const contributorWithZeroContributions: Contributor = {
      login: 'newcomer',
      name: 'Brand New User',
      avatarUrl: 'https://github.com/newcomer.png',
      contributionsCount: 0,
      projectKey: 'test-key',
    }
    render(
      <ContributorAvatar
        contributor={contributorWithZeroContributions}
        uniqueKey="zero-contrib-test"
      />
    )
    const tooltip = screen.getByTestId('avatar-tooltip-newcomer-zero-contrib-test')
    expect(tooltip).toHaveAttribute('title', 'Brand New User')
  })

  it('handles empty string values gracefully', () => {
    const contributorWithEmptyStrings: Contributor = {
      login: '',
      name: '',
      avatarUrl: 'https://github.com/default.png',
      contributionsCount: 5,
      projectKey: 'test-key',
    }

    render(
      <ContributorAvatar contributor={contributorWithEmptyStrings} uniqueKey="empty-strings-test" />
    )
    expect(screen.getByTestId('contributor-avatar')).toBeInTheDocument()
    const link = screen.getByTestId('contributor-link')
    expect(link).toHaveAttribute('href', '/members/')
  })

  it('handles very long names and contributions', () => {
    const contributorWithLongData: Contributor = {
      login: 'very-long-username-that-might-break-layouts',
      name: 'Someone With A Really Really Long Name That Might Cause Issues',
      avatarUrl: 'https://github.com/very-long-username-that-might-break-layouts.png',
      contributionsCount: 999999,
      projectKey: 'test-key',
      projectName: 'Some-Very-Long-Project-Name-That-Could-Break-Tooltip-Layout',
    }
    render(<ContributorAvatar contributor={contributorWithLongData} uniqueKey="long-data-test" />)
    expect(screen.getByTestId('contributor-avatar')).toBeInTheDocument()
  })

  it('creates link to member profile with proper attributes', () => {
    render(<ContributorAvatar contributor={mockAlgoliaContributor} uniqueKey="link-test" />)
    const link = screen.getByTestId('contributor-link')
    expect(link).toHaveAttribute('href', '/members/johndoe')
    expect(link).toHaveAttribute('target', '_blank')
    expect(link).toHaveAttribute('rel', 'noopener noreferrer')
  })

  it('does not include project name in tooltip (all contributors treated as Algolia)', () => {
    render(
      <ContributorAvatar contributor={mockGitHubContributor} uniqueKey="project-tooltip-test" />
    )

    const tooltip = screen.getByTestId('avatar-tooltip-jane-doe-project-tooltip-test')
    expect(tooltip).toHaveAttribute('title', '15 contributions by Jane Doe')
  })

  it('provides meaningful alt text for screen readers', () => {
    render(<ContributorAvatar contributor={mockAlgoliaContributor} uniqueKey="alt-test" />)
    const avatar = screen.getByRole('img')
    expect(avatar).toHaveAttribute('alt', "John Doe's avatar")
  })

  it('has proper link attributes for external navigation', () => {
    render(<ContributorAvatar contributor={mockAlgoliaContributor} uniqueKey="a11y-link-test" />)
    const link = screen.getByRole('link')
    expect(link).toHaveAttribute('target', '_blank')
    expect(link).toHaveAttribute('rel', 'noopener noreferrer')
  })

  it('generates unique tooltip IDs to avoid conflicts', () => {
    const { rerender } = render(
      <ContributorAvatar contributor={mockAlgoliaContributor} uniqueKey="first-key" />
    )
    expect(screen.getByTestId('avatar-tooltip-johndoe-first-key')).toBeInTheDocument()
    rerender(<ContributorAvatar contributor={mockAlgoliaContributor} uniqueKey="second-key" />)
    expect(screen.getByTestId('avatar-tooltip-johndoe-second-key')).toBeInTheDocument()
  })

  it('is properly memoized with displayName', () => {
    expect(ContributorAvatar.displayName).toBe('ContributorAvatar')
  })
})
