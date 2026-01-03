import { render } from '@testing-library/react'
import { axe, toHaveNoViolations } from 'jest-axe'
import { CSSProperties, ReactNode } from 'react'
import { Release } from 'types/release'
import RecentReleases from 'components/RecentReleases'

expect.extend(toHaveNoViolations)

const mockRouterPush = jest.fn()
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: mockRouterPush,
  }),
}))

jest.mock('next/link', () => ({
  __esModule: true,
  default: ({
    children,
    href,
    ...props
  }: {
    children: ReactNode
    href: string
    [key: string]: unknown
  }) => (
    <a href={href} {...props}>
      {children}
    </a>
  ),
}))

jest.mock('next/image', () => ({
  __esModule: true,
  default: ({
    src,
    alt,
    fill,
    objectFit,
    ...props
  }: {
    src: string
    alt: string
    fill?: boolean
    objectFit?: 'fill' | 'contain' | 'cover' | 'none' | 'scale-down'
    [key: string]: unknown
  }) => (
    // eslint-disable-next-line @next/next/no-img-element
    <img
      src={src}
      alt={alt}
      style={fill && { objectFit: objectFit as CSSProperties['objectFit'] }}
      {...props}
    />
  ),
}))

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

describe('RecentReleases a11y', () => {
  it('should not have any accessibility violations', async () => {
    const { container } = render(<RecentReleases data={mockReleases} />)
    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })
})
