import { render } from '@testing-library/react'
import { axe } from 'jest-axe'
import type { Release as ReleaseType } from 'types/release'
import Release from 'components/Release'

const release: ReleaseType = {
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
}

describe('Release a11y', () => {
  it('should not have any accessibility violations', async () => {
    const { baseElement } = render(
      <main>
        <Release release={release} />
      </main>
    )

    const results = await axe(baseElement)

    expect(results).toHaveNoViolations()
  })
})
