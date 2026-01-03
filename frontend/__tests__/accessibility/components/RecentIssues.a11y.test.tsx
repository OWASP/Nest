import { render } from '@testing-library/react'
import { axe, toHaveNoViolations } from 'jest-axe'
import { CSSProperties, ReactNode } from 'react'
import RecentIssues from 'components/RecentIssues'

expect.extend(toHaveNoViolations)

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

describe('RecentIssues a11y', () => {
  it('should not have any accessibility violations', async () => {
    const { container } = render(<RecentIssues data={[baseIssue]} />)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })
})
