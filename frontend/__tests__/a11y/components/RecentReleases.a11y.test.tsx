import { render } from '@testing-library/react'
import { axe } from 'jest-axe'
import { useTheme } from 'next-themes'
import type { Release as ReleaseType } from 'types/release'
import RecentReleases from 'components/RecentReleases'

const mockReleases: ReleaseType[] = [
  {
    id: '1',
    name: 'v1.0.0',
    tagName: 'v1.0.0',
    publishedAt: Date.now(),
    repositoryName: 'test-repo',
    organizationName: 'test-org',
    isPreRelease: false,
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
  },
]

describe.each([
  { theme: 'light', name: 'light' },
  { theme: 'dark', name: 'dark' },
])('RecentReleases a11y ($name theme)', ({ theme }) => {
  beforeEach(() => {
    ;(useTheme as jest.Mock).mockReturnValue({ theme, setTheme: jest.fn() })
  })
  it('should have no accessibility violations with releases', async () => {
    const { container } = render(
      <main>
        <RecentReleases data={mockReleases} />
      </main>
    )

    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })

  it('should have no accessibility violations with empty data', async () => {
    const { container } = render(
      <main>
        <RecentReleases data={[]} />
      </main>
    )

    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })
})
