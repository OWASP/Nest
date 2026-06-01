import { render } from '@testing-library/react'
import { axe } from 'jest-axe'
import { Release } from 'types/release'
import RecentReleases from 'components/RecentReleases'

const publishedAtIso = new Date(Date.now()).toISOString()

const mockReleases: Release[] = [
  {
    id: 'release-a11y-1',
    name: 'v1.0 The First Release',
    publishedAt: publishedAtIso,
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
      createdAt: '1970-01-01T00:00:00.000Z',
      followersCount: 0,
      followingCount: 0,
      publicRepositoriesCount: 0,
      url: 'https://example.com/user/testuser',
    },
  },
  {
    id: 'release-a11y-2',
    name: 'v2.0 The Second Release',
    publishedAt: publishedAtIso,
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
      createdAt: '1970-01-01T00:00:00.000Z',
      followersCount: 0,
      followingCount: 0,
      publicRepositoriesCount: 0,
      url: 'https://example.com/user/jane-doe',
    },
  },
]

describe('RecentReleases a11y', () => {
  it('should not have any accessibility violations', async () => {
    const { container } = render(<RecentReleases data={mockReleases} />)
    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })
})
