import { useQuery } from '@apollo/client/react'
import { render } from '@testing-library/react'
import { useIssueMutations } from 'hooks/useIssueMutations'
import { axe } from 'jest-axe'
import { useTheme } from 'next-themes'
import ModuleIssueDetailsPage from 'app/my/mentorship/programs/[programKey]/modules/[moduleKey]/issues/[issueId]/page'

jest.mock('@apollo/client/react', () => ({
  useQuery: jest.fn(),
}))

jest.mock('next/navigation', () => ({
  useParams: jest.fn(() => ({
    programKey: 'prog1',
    moduleKey: 'mod1',
    issueId: '123',
  })),
  useRouter: jest.fn(() => ({
    push: jest.fn(),
    replace: jest.fn(),
  })),
}))

jest.mock('hooks/useIssueMutations')

const mockIssueData = {
  getModule: {
    issueByNumber: {
      id: '1',
      title: 'Test Issue Title',
      body: 'This is the issue body.',
      number: 123,
      state: 'open',
      isMerged: false,
      organizationName: 'org',
      repositoryName: 'repo',
      url: 'https://github.com/issue/123',
      assignees: [
        {
          id: 'assignee1',
          login: 'user1',
          name: 'User One',
          avatarUrl: 'https://example.com/avatar1.png',
        },
      ],
      labels: ['bug', 'critical'],
      pullRequests: [
        {
          id: 'pr1',
          title: 'Fix for test issue',
          url: 'https://github.com/pr/1',
          state: 'open',
          mergedAt: null,
          createdAt: new Date().toISOString(),
          author: {
            login: 'dev1',
            avatarUrl: 'https://example.com/dev-avatar1.png',
          },
        },
      ],
    },
    taskAssignedAt: new Date().toISOString(),
    taskDeadline: null,
    interestedUsers: [
      {
        id: 'user2',
        login: 'user2',
        avatarUrl: 'https://example.com/avatar2.png',
      },
    ],
  },
}

describe.each([
  { theme: 'light', name: 'light' },
  { theme: 'dark', name: 'dark' },
])('ModuleIssueDetailsPage Accessibility ($name theme)', ({ theme }) => {
  beforeEach(() => {
    ;(useTheme as jest.Mock).mockReturnValue({ theme, setTheme: jest.fn() })
  })
  const mockUseQuery = useQuery as unknown as jest.Mock
  beforeEach(() => {
    ;(useIssueMutations as jest.Mock).mockReturnValue({
      assignIssue: jest.fn(),
      unassignIssue: jest.fn(),
      setTaskDeadlineMutation: jest.fn(),
      clearTaskDeadlineMutation: jest.fn(),
      assigning: false,
      unassigning: false,
      settingDeadline: false,
      clearingDeadline: false,
      isEditingDeadline: false,
      setIsEditingDeadline: jest.fn(),
      deadlineInput: '',
      setDeadlineInput: jest.fn(),
    })
  })

  it('should have no accessibility violations', async () => {
    mockUseQuery.mockReturnValue({
      loading: false,
      data: mockIssueData,
    })

    const { container } = render(<ModuleIssueDetailsPage />)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })

  it('should have no accessibility violations when loading', async () => {
    mockUseQuery.mockReturnValue({
      data: null,
      loading: true,
      error: null,
    })

    const { container } = render(<ModuleIssueDetailsPage />)
    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })

  it('should have no accessibility violations when error occurs', async () => {
    mockUseQuery.mockReturnValue({
      data: null,
      loading: false,
      error: new Error('test error'),
    })

    const { container } = render(<ModuleIssueDetailsPage />)
    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })

  it('should have no accessibility violations when no data exists', async () => {
    mockUseQuery.mockReturnValue({
      data: null,
      loading: false,
      error: null,
    })

    const { container } = render(<ModuleIssueDetailsPage />)
    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })
})
