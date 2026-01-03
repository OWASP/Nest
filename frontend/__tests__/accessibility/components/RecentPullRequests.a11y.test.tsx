import { render } from '@testing-library/react'
import { axe, toHaveNoViolations } from 'jest-axe'
import { CSSProperties, ReactNode } from 'react'
import RecentPullRequests from 'components/RecentPullRequests'

expect.extend(toHaveNoViolations)

jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
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

const mockUser = {
  avatarUrl: 'https://example.com/avatar.png',
  bio: 'Test bio',
  company: 'Test Company',
  contributionsCount: 42,
  createdAt: 1577836800000,
  email: 'test@example.com',
  followersCount: 10,
  followingCount: 5,
  key: 'user-key',
  location: 'Test City',
  login: 'testuser',
  name: 'Test User',
  publicRepositoriesCount: 3,
  url: 'https://github.com/testuser',
}

const minimalData = [
  {
    id: 'mock-pull-request',
    author: mockUser,
    createdAt: '2024-06-01T12:00:00Z',
    organizationName: 'test-org',
    repositoryName: 'test-repo',
    title: 'Test Pull Request',
    url: 'https://github.com/test-org/test-repo/pull/1',
    state: 'open',
    mergedAt: '2024-06-02T12:00:00Z',
  },
]

describe('RecentPullRequests a11y', () => {
  it('should not have any accessibility violations', async () => {
    const { container } = render(<RecentPullRequests data={minimalData} />)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })
})
