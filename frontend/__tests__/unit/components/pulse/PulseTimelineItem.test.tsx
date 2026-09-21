import { render, screen } from '@testing-library/react'
import type { ActivityEventItem } from 'types/pulse'
import PulseTimelineItem from 'components/pulse/PulseTimelineItem'

jest.mock('next/image', () => ({
  __esModule: true,
  default: ({ src, alt, ...props }: { src: string; alt: string; [key: string]: unknown }) => (
    // eslint-disable-next-line @next/next/no-img-element
    <img src={src} alt={alt} data-testid="user-avatar" {...props} />
  ),
}))

const baseEvent: ActivityEventItem = {
  __typename: 'ActivityEventNode',
  id: 'event-1',
  activityType: 'pr_opened',
  occurredAt: new Date().toISOString(),
  title: 'Fix critical bug',
  url: 'https://github.com/owasp/nest/pull/42',
  number: 42,
  githubUser: {
    __typename: 'UserNode',
    id: 'user-1',
    login: 'devuser',
    name: 'Dev User',
    avatarUrl: 'https://example.com/avatar.png',
  },
  githubRepository: {
    __typename: 'RepositoryNode',
    id: 'repo-1',
    key: 'nest',
    name: 'nest',
    url: 'https://github.com/owasp/nest',
  },
}

describe('<PulseTimelineItem />', () => {
  const cases: Array<[ActivityEventItem['activityType'], string, string]> = [
    ['pr_opened', 'opened a pull request', 'PR OPENED'],
    ['pr_closed', 'closed a pull request', 'PR CLOSED'],
    ['pr_merged', 'merged a pull request', 'PR MERGED'],
    ['issue_opened', 'opened an issue', 'ISSUE OPENED'],
    ['issue_closed', 'closed an issue', 'ISSUE CLOSED'],
    ['release_published', 'published a release', 'RELEASE'],
    ['unknown_type' as never, 'created an activity event', 'UNKNOWN_TYPE'],
  ]

  it.each(cases)('renders action text and badge for %s', (type, actionText, badgeText) => {
    render(<PulseTimelineItem event={{ ...baseEvent, activityType: type }} />)
    expect(screen.getByText(actionText)).toBeInTheDocument()
    expect(screen.getByText(badgeText)).toBeInTheDocument()
  })

  it('renders timeline item details, fallbacks, and relative timestamps', () => {
    const { rerender } = render(<PulseTimelineItem event={baseEvent} />)

    const avatar = screen.getByTestId('user-avatar')
    expect(avatar).toHaveAttribute('src', 'https://example.com/avatar.png')
    expect(avatar).toHaveAttribute('alt', 'devuser')

    const link = screen.getByRole('link', { name: /#42 Fix critical bug/ })
    expect(link).toHaveAttribute('href', 'https://github.com/owasp/nest/pull/42')
    expect(screen.getByRole('link', { name: 'View on GitHub' })).toBeInTheDocument()
    expect(screen.getByText('Nest')).toBeInTheDocument()

    rerender(
      <PulseTimelineItem
        event={{
          ...baseEvent,
          githubUser: { ...baseEvent.githubUser!, avatarUrl: '' },
          githubRepository: { ...baseEvent.githubRepository!, key: '', name: 'owasp-nest' },
          occurredAt: new Date(Date.now() - 3600000).toISOString(),
        }}
      />
    )
    expect(screen.queryByTestId('user-avatar')).not.toBeInTheDocument()
    expect(screen.getByText('Owasp-nest')).toBeInTheDocument()
    expect(screen.getByText('1 hour ago')).toBeInTheDocument()

    rerender(
      <PulseTimelineItem
        event={{
          ...baseEvent,
          githubUser: null,
          githubRepository: { ...baseEvent.githubRepository!, key: '', name: '' },
          occurredAt: new Date(Date.now() - 5 * 3600000).toISOString(),
        }}
      />
    )
    expect(screen.getByText('OWASP Contributor')).toBeInTheDocument()
    expect(screen.getByText('Nest')).toBeInTheDocument()
    expect(screen.getByText('5 hours ago')).toBeInTheDocument()

    rerender(
      <PulseTimelineItem
        event={{
          ...baseEvent,
          number: null,
          occurredAt: new Date(Date.now() - 86400000).toISOString(),
        }}
      />
    )
    expect(screen.getByRole('link', { name: 'Fix critical bug' })).toBeInTheDocument()
    expect(screen.getByText('yesterday')).toBeInTheDocument()

    rerender(
      <PulseTimelineItem
        event={{
          ...baseEvent,
          title: '',
          occurredAt: new Date(Date.now() - 5 * 86400000).toISOString(),
        }}
      />
    )
    expect(screen.getByRole('link', { name: /Activity Title/ })).toBeInTheDocument()
    expect(screen.getByText('5 days ago')).toBeInTheDocument()

    rerender(
      <PulseTimelineItem
        event={{
          ...baseEvent,
          url: '',
          occurredAt: new Date('2024-01-15T12:00:00Z').toISOString(),
        }}
      />
    )
    expect(screen.getByText(/#42 Fix critical bug/)).toBeInTheDocument()
    expect(screen.getByText(/Jan 15/)).toBeInTheDocument()

    rerender(
      <PulseTimelineItem
        event={{ ...baseEvent, url: '', number: null, title: '', occurredAt: 'not-a-date' }}
      />
    )
    expect(screen.queryByRole('link', { name: 'View on GitHub' })).not.toBeInTheDocument()
    expect(screen.getByText('Activity Title')).toBeInTheDocument()
    expect(screen.getByText('not-a-date')).toBeInTheDocument()

    const oldDate = '2020-01-01T00:00:00.000Z'
    const spy = jest.spyOn(Date.prototype, 'toLocaleDateString').mockImplementationOnce(() => {
      throw new Error('Locale error')
    })
    rerender(<PulseTimelineItem event={{ ...baseEvent, occurredAt: oldDate }} />)
    expect(screen.getByText(oldDate)).toBeInTheDocument()
    spy.mockRestore()
  })
})
