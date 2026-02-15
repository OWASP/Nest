import { render } from '@testing-library/react'
import { axe } from 'jest-axe'
import { useTheme } from 'next-themes'
import { Milestone } from 'types/milestone'
import { User } from 'types/user'
import Milestones from 'components/Milestones'

jest.mock('next/navigation', () => ({
  ...jest.requireActual('next/navigation'),
  useRouter: jest.fn(),
}))

const createMockUser = (): User => ({
  login: 'testuser',
  name: 'Test User',
  avatarUrl: 'https://github.com/testuser.png',
  url: 'https://github.com/testuser',
  key: 'testuser',
  followersCount: 10,
  followingCount: 5,
  publicRepositoriesCount: 20,
  contributionsCount: 50,
  createdAt: 1640995200000,
  updatedAt: 1640995200000,
})

const createMockMilestone = (overrides: Partial<Milestone> = {}): Milestone => ({
  author: createMockUser(),
  body: 'Test milestone description',
  closedIssuesCount: 5,
  createdAt: '2023-01-01T00:00:00Z',
  openIssuesCount: 3,
  organizationName: 'test-org',
  progress: 75,
  repositoryName: 'test-repo',
  state: 'open',
  title: 'Test Milestone',
  url: 'https://github.com/test-org/test-repo/milestone/1',
  ...overrides,
})

describe.each([
  { theme: 'light', name: 'light' },
  { theme: 'dark', name: 'dark' },
])('Milestones a11y ($name theme)', ({ theme }) => {
  beforeEach(() => {
    ;(useTheme as jest.Mock).mockReturnValue({ theme, setTheme: jest.fn() })
  })
  it('should not have any accessibility violations', async () => {
    const { container } = render(<Milestones data={[createMockMilestone()]} />)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })
})
