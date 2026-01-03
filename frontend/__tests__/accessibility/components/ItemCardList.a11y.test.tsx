import { render } from '@testing-library/react'
import { axe, toHaveNoViolations } from 'jest-axe'
import { ReactNode } from 'react'
import { Issue } from 'types/issue'
import ItemCardList from 'components/ItemCardList'

expect.extend(toHaveNoViolations)

jest.mock('next/link', () => ({
  __esModule: true,
  default: ({
    children,
    href,
    target,
    className,
  }: {
    children: ReactNode
    href: string
    target?: string
    className?: string
  }) => (
    <a href={href} target={target} className={className} data-testid="link">
      {children}
    </a>
  ),
}))

jest.mock('next/image', () => ({
  __esModule: true,
  default: ({
    src,
    alt,
    width,
    height,
    className,
  }: {
    src: string
    alt: string
    width: number
    height: number
    className?: string
  }) => (
    // eslint-disable-next-line @next/next/no-img-element
    <img
      src={src}
      alt={alt}
      width={width}
      height={height}
      className={className}
      data-testid="avatar-image"
    />
  ),
}))

const mockUser = {
  avatarUrl: 'https://github.com/author1.png',
  contributionsCount: 50,
  createdAt: 1640995200000,
  followersCount: 100,
  followingCount: 50,
  key: 'author1',
  login: 'author1',
  name: 'Author One',
  publicRepositoriesCount: 25,
  url: 'https://github.com/author1',
}

const mockIssue: Issue = {
  author: mockUser,
  createdAt: 1640995200000,
  hint: 'Good first issue',
  labels: ['bug', 'help-wanted'],
  number: '123',
  organizationName: 'test-org',
  projectName: 'Test Project',
  projectUrl: 'https://github.com/test-org/test-project',
  summary: 'This is a test issue summary',
  title: 'Test Issue Title',
  updatedAt: 1641081600000,
  url: 'https://github.com/test-org/test-project/issues/123',
  objectID: 'issue-123',
}

const defaultProps = {
  title: 'Test Title',
  data: [mockIssue],
  renderDetails: jest.fn((item) => (
    <div data-testid="render-details">
      <span>Created: {item.createdAt}</span>
      <span>Org: {item.organizationName}</span>
    </div>
  )),
}

describe('ItemCardList a11y', () => {
  it('should not have any accessibility violations', async () => {
    const { container } = render(<ItemCardList {...defaultProps} />)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })
})
