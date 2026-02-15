import { render } from '@testing-library/react'
import { axe } from 'jest-axe'
import { useTheme } from 'next-themes'
import { ReactNode } from 'react'
import { Issue } from 'types/issue'
import ItemCardList from 'components/ItemCardList'

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

describe.each([
  { theme: 'light', name: 'light' },
  { theme: 'dark', name: 'dark' },
])('ItemCardList a11y ($name theme)', ({ theme }) => {
  beforeEach(() => {
    ;(useTheme as jest.Mock).mockReturnValue({ theme, setTheme: jest.fn() })
  })
  it('should not have any accessibility violations', async () => {
    const { baseElement } = render(
      <main>
        <ItemCardList {...defaultProps} />
      </main>
    )

    const results = await axe(baseElement)

    expect(results).toHaveNoViolations()
  })
})
