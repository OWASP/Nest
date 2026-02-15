import { render } from '@testing-library/react'
import { axe } from 'jest-axe'
import { useTheme } from 'next-themes'
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

describe.each([
  { theme: 'light', name: 'light' },
  { theme: 'dark', name: 'dark' },
])('Release a11y ($name theme)', ({ theme }) => {
  beforeEach(() => {
    ;(useTheme as jest.Mock).mockReturnValue({ theme, setTheme: jest.fn() })
  })
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
