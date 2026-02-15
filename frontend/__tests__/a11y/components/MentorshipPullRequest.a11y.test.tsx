import { render } from '@testing-library/react'
import { axe } from 'jest-axe'
import { useTheme } from 'next-themes'
import type { PullRequest } from 'types/pullRequest'
import MentorshipPullRequest from 'components/MentorshipPullRequest'

const mockPR: PullRequest = {
  title: 'Fix accessibility issues',
  url: 'https://github.com/test/repo/pull/1',
  createdAt: '2025-01-15',
  state: 'open',
  author: {
    login: 'testuser',
    name: 'Test User',
    avatarUrl: 'https://example.com/avatar.png',
    key: 'testuser',
    contributionsCount: 10,
    createdAt: 0,
    followersCount: 5,
    followingCount: 3,
    publicRepositoriesCount: 8,
    url: 'https://github.com/testuser',
  },
}

describe.each([
  { theme: 'light', name: 'light' },
  { theme: 'dark', name: 'dark' },
])('MentorshipPullRequest a11y ($name theme)', ({ theme }) => {
  beforeEach(() => {
    ;(useTheme as jest.Mock).mockReturnValue({ theme, setTheme: jest.fn() })
  })
  it('should have no accessibility violations', async () => {
    const { container } = render(
      <main>
        <MentorshipPullRequest pr={mockPR} />
      </main>
    )

    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })
})
