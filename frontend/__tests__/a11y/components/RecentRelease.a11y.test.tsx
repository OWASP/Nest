import { render } from '@testing-library/react'
import { axe } from 'jest-axe'
import { useTheme } from 'next-themes'
import { Release } from 'types/release'
import RecentReleases from 'components/RecentReleases'

const mockReleases: Release[] = [
  {
    name: 'v1.0 The First Release',
    publishedAt: Date.now(),
    repositoryName: 'our-awesome-project',
    organizationName: 'our-org',
    tagName: 'v1.0',
    isPreRelease: false,
    author: {
      login: 'testuser',
      name: 'Test User',
      avatarUrl: 'https://example.com/avatar.png',
      key: 'testuser',
      contributionsCount: 0,
      createdAt: 0,
      followersCount: 0,
      followingCount: 0,
      publicRepositoriesCount: 0,
      url: 'https://example.com/user/testuser',
    },
  },
  {
    name: 'v2.0 The Second Release',
    publishedAt: Date.now(),
    repositoryName: 'another-cool-project',
    organizationName: 'our-org',
    tagName: 'v2.0',
    isPreRelease: false,
    author: {
      login: 'jane-doe',
      name: 'Jane Doe',
      avatarUrl: 'https://example.com/avatar2.png',
      key: 'jane-doe',
      contributionsCount: 0,
      createdAt: 0,
      followersCount: 0,
      followingCount: 0,
      publicRepositoriesCount: 0,
      url: 'https://example.com/user/jane-doe',
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
  it('should not have any accessibility violations', async () => {
    const { container } = render(<RecentReleases data={mockReleases} />)
    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })
})
