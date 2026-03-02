import { render } from '@testing-library/react'
import { axe } from 'jest-axe'
import { useTheme } from 'next-themes'
import RecentIssues from 'components/RecentIssues'

const baseIssue = {
  author: {
    avatarUrl: 'https://example.com/avatar.png',
    login: 'user1',
    name: 'User One',
    contributionsCount: 10,
    createdAt: 1234567890,
    followersCount: 5,
    followingCount: 2,
    key: 'user1',
    publicRepositoriesCount: 3,
    url: 'https://github.com/user1',
  },
  createdAt: 1710000000,
  hint: 'Hint',
  labels: ['bug'],
  organizationName: 'org',
  projectName: 'proj',
  projectUrl: 'https://github.com/org/proj',
  summary: 'Summary',
  title: 'Issue Title',
  updatedAt: 1710000100,
  url: 'https://github.com/org/proj/issues/1',
  objectID: 'id1',
  repositoryName: 'repo',
}

describe.each([
  { theme: 'light', name: 'light' },
  { theme: 'dark', name: 'dark' },
])('RecentIssues a11y ($name theme)', ({ theme }) => {
  beforeEach(() => {
    ;(useTheme as jest.Mock).mockReturnValue({ theme, setTheme: jest.fn() })
    document.documentElement.classList.toggle('dark', theme === 'dark')
  })
  it('should not have any accessibility violations', async () => {
    const { container } = render(<RecentIssues data={[baseIssue]} />)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })
})
