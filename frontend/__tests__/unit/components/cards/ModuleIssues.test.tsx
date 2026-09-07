import { useQuery } from '@apollo/client/react'
import { render, screen, fireEvent, waitFor, within } from '@testing-library/react'
import { useRouter, useSearchParams } from 'next/navigation'
import { useSession } from 'next-auth/react'
import { handleAppError } from 'app/global-error'
import ModuleIssues from 'components/cards/ModuleIssues'

// Mock dependencies
jest.mock('@apollo/client/react', () => ({
  ...jest.requireActual('@apollo/client/react'),
  useQuery: jest.fn(),
}))
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
  useSearchParams: jest.fn(),
}))
jest.mock('next-auth/react', () => ({
  useSession: jest.fn(),
}))

const mockUseQuery = useQuery as unknown as jest.Mock
const mockUseRouter = useRouter as jest.Mock
const mockUseSearchParams = useSearchParams as jest.Mock
const mockUseSession = useSession as jest.Mock
const mockPush = jest.fn()
const mockReplace = jest.fn()

const mockModuleData = {
  managementModule: {
    name: 'Test Module',
    issues: [
      {
        id: '1',
        objectID: '1',
        number: 101,
        title: 'First Issue Title',
        state: 'open',
        isMerged: false,
        labels: ['bug'],
        assignees: [
          {
            avatarUrl: 'http://example.com/avatar.png',
            login: 'user1',
            name: 'User One',
          },
        ],
      },
    ],
    issuesCount: 1,
    availableLabels: ['bug', 'feature-request', 'documentation'],
  },
}

jest.mock('app/global-error', () => ({
  handleAppError: jest.fn(),
  ErrorDisplay: ({ title }: { title: string }) => <div>{title}</div>,
}))

const mockHandleAppError = handleAppError as jest.Mock

describe('ModuleIssues', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    mockUseRouter.mockReturnValue({ push: mockPush, replace: mockReplace })
    mockUseSearchParams.mockReturnValue(new URLSearchParams())
    mockUseSession.mockReturnValue({
      data: {
        user: {
          login: 'testuser',
          email: 'test@example.com',
        },
      },
      status: 'authenticated',
    })
    mockUseQuery.mockReturnValue({ data: mockModuleData, loading: false, error: undefined })
  })

  it('shows a loading message in the table while data is being fetched', () => {
    mockUseQuery.mockReturnValue({ data: undefined, loading: true, error: undefined })
    render(<ModuleIssues programKey="prog1" moduleKey="mod1" />)
    expect(screen.getByText('Loading issues...')).toBeInTheDocument()
  })

  it('calls handleAppError on query error', () => {
    const error = new Error('Test error')
    mockUseQuery.mockReturnValue({ data: undefined, loading: false, error })
    render(<ModuleIssues programKey="prog1" moduleKey="mod1" />)
    expect(mockHandleAppError).toHaveBeenCalledWith(error)
  })

  it('renders an empty table when the module has no issues data', () => {
    mockUseQuery.mockReturnValue({
      data: { managementModule: null },
      loading: false,
      error: undefined,
    })
    render(<ModuleIssues programKey="prog1" moduleKey="mod1" />)
    expect(screen.getByText('No issues found for the selected filter.')).toBeInTheDocument()
  })

  it('displays a "no issues found" message when there are no issues', () => {
    mockUseQuery.mockReturnValue({
      data: {
        managementModule: { ...mockModuleData.managementModule, issues: [], issuesCount: 0 },
      },
      loading: false,
      error: undefined,
    })
    render(<ModuleIssues programKey="prog1" moduleKey="mod1" />)
    expect(screen.getAllByText('No issues found for the selected filter.')).toHaveLength(1)
  })

  it('renders the list of issues successfully', () => {
    mockUseQuery.mockReturnValue({ data: mockModuleData, loading: false, error: undefined })
    render(<ModuleIssues programKey="prog1" moduleKey="mod1" />)
    expect(screen.getByText('Issues')).toBeInTheDocument()
    expect(screen.getAllByText('First Issue Title')[0]).toBeInTheDocument()
    expect(screen.getAllByText('Open')[0]).toBeInTheDocument()
    expect(screen.getAllByText('bug')[0]).toBeInTheDocument()
    expect(screen.getAllByText('user1')[0]).toBeInTheDocument()
  })

  it('navigates to the correct issue details page on click', () => {
    mockUseQuery.mockReturnValue({ data: mockModuleData, loading: false, error: undefined })
    render(<ModuleIssues programKey="prog1" moduleKey="mod1" />)
    const issueTitleButton = screen.getAllByRole('button', { name: /First Issue Title/i })[0]
    fireEvent.click(issueTitleButton)
    expect(mockPush).toHaveBeenCalledWith('/my/mentorship/programs/prog1/modules/mod1/issues/101')
  })

  it('filters issues based on the selected label', async () => {
    mockUseQuery.mockReturnValue({ data: mockModuleData, loading: false, error: undefined })
    render(<ModuleIssues programKey="prog1" moduleKey="mod1" />)

    const selectTrigger = screen.getByRole('button', { name: /Label/i })
    fireEvent.click(selectTrigger)

    const listbox = await screen.findByRole('listbox')
    const optionToSelect = within(listbox).getByText('bug')
    fireEvent.click(optionToSelect)

    await waitFor(() => {
      expect(mockReplace).toHaveBeenCalledWith('?label=bug', { scroll: false })
    })
  })

  it('resets to page 1 when a new label is selected', async () => {
    mockUseQuery.mockReturnValue({ data: mockModuleData, loading: false, error: undefined })
    render(<ModuleIssues programKey="prog1" moduleKey="mod1" />)

    const selectTrigger = screen.getByRole('button', { name: /Label/i })
    fireEvent.click(selectTrigger)

    const listbox = await screen.findByRole('listbox')
    const optionToSelect = within(listbox).getByText('documentation')
    fireEvent.click(optionToSelect)

    await waitFor(() => {
      expect(mockReplace).toHaveBeenCalledWith('?label=documentation', { scroll: false })
    })
  })

  it('clears the filter when "All" is selected', async () => {
    mockUseQuery.mockReturnValue({ data: mockModuleData, loading: false, error: undefined })
    mockUseSearchParams.mockReturnValue(new URLSearchParams('?label=bug'))
    render(<ModuleIssues programKey="prog1" moduleKey="mod1" />)

    const selectTrigger = screen.getByRole('button', { name: /Label/i })
    fireEvent.click(selectTrigger)

    const listbox = await screen.findByRole('listbox')
    const optionToSelect = within(listbox).getByText('All')
    fireEvent.click(optionToSelect)

    await waitFor(() => {
      expect(mockReplace).toHaveBeenCalledWith(globalThis.location.pathname, {
        scroll: false,
      })
    })
  })

  it('handles pagination correctly', async () => {
    const twentyFiveIssues = {
      managementModule: {
        ...mockModuleData.managementModule,
        issues: Array.from({ length: 25 }, (_, i) => ({
          ...mockModuleData.managementModule.issues[0],
          id: `${i + 1}`,
          objectID: `${i + 1}`,
          number: 100 + i,
          title: `Issue ${i + 1}`,
        })),
        issuesCount: 25,
      },
    }
    mockUseQuery.mockReturnValue({ data: twentyFiveIssues, loading: false, error: undefined })
    render(<ModuleIssues programKey="prog1" moduleKey="mod1" />)

    const pageTwoButton = screen.getByRole('button', { name: /go to page 2/i })
    fireEvent.click(pageTwoButton)

    await waitFor(() => {
      expect(mockUseQuery).toHaveBeenLastCalledWith(
        expect.anything(),
        expect.objectContaining({
          variables: expect.objectContaining({
            offset: 10,
          }),
        })
      )
    })
  })

  describe.each([
    { state: 'closed', isMerged: true, expectedText: 'Closed' },
    { state: 'closed', isMerged: false, expectedText: 'Closed' },
  ])('issue states', ({ state, isMerged, expectedText }) => {
    it(`renders ${expectedText} issues correctly`, () => {
      const issue = {
        ...mockModuleData.managementModule.issues[0],
        state,
        isMerged,
      }
      mockUseQuery.mockReturnValue({
        data: {
          managementModule: { ...mockModuleData.managementModule, issues: [issue] },
        },
        loading: false,
        error: undefined,
      })
      render(<ModuleIssues programKey="prog1" moduleKey="mod1" />)
      const desktopTable = screen.getByRole('table')
      expect(within(desktopTable).getByText(expectedText)).toBeInTheDocument()
    })
  })

  it('renders remaining labels count if there are more than 5 labels', () => {
    const manyLabelsIssue = {
      ...mockModuleData.managementModule.issues[0],
      labels: ['bug', 'feature', 'docs', 'help', 'question', 'wontfix'],
    }
    mockUseQuery.mockReturnValue({
      data: {
        managementModule: { ...mockModuleData.managementModule, issues: [manyLabelsIssue] },
      },
      loading: false,
      error: undefined,
    })
    render(<ModuleIssues programKey="prog1" moduleKey="mod1" />)
    expect(screen.getByText('+1 more')).toBeInTheDocument()
  })

  it('renders multiple assignees correctly', () => {
    const multipleAssignees = [
      {
        avatarUrl: 'http://example.com/avatar.png',
        login: 'user1',
        name: 'User One',
      },
      {
        avatarUrl: 'http://example.com/avatar2.png',
        login: 'user2',
        name: 'User Two',
      },
    ]
    const multipleAssigneesIssue = {
      ...mockModuleData.managementModule.issues[0],
      assignees: multipleAssignees,
    }
    mockUseQuery.mockReturnValue({
      data: {
        managementModule: {
          ...mockModuleData.managementModule,
          issues: [multipleAssigneesIssue],
        },
      },
      loading: false,
      error: undefined,
    })
    render(<ModuleIssues programKey="prog1" moduleKey="mod1" />)
    const plusOneElements = screen.getAllByText(/\+1/)
    expect(plusOneElements.length).toBeGreaterThan(0)
  })

  it('extracts labels from issues when availableLabels is empty', async () => {
    const dataWithoutAvailableLabels = {
      managementModule: {
        ...mockModuleData.managementModule,
        availableLabels: [],
        issues: [
          {
            ...mockModuleData.managementModule.issues[0],
            labels: ['extracted-label-1', 'extracted-label-2'],
          },
        ],
      },
    }
    mockUseQuery.mockReturnValue({
      data: dataWithoutAvailableLabels,
      loading: false,
      error: undefined,
    })
    render(<ModuleIssues programKey="prog1" moduleKey="mod1" />)

    // Open the label dropdown to verify extracted labels are present
    const selectTrigger = screen.getByRole('button', { name: /Label/i })
    fireEvent.click(selectTrigger)

    const listbox = await screen.findByRole('listbox')
    expect(within(listbox).getByText('extracted-label-1')).toBeInTheDocument()
    expect(within(listbox).getByText('extracted-label-2')).toBeInTheDocument()
  })

  it('extracts labels from issues when availableLabels is null', async () => {
    const dataWithNullAvailableLabels = {
      managementModule: {
        ...mockModuleData.managementModule,
        availableLabels: null,
        issues: [
          {
            ...mockModuleData.managementModule.issues[0],
            labels: ['label-from-issue'],
          },
        ],
      },
    }
    mockUseQuery.mockReturnValue({
      data: dataWithNullAvailableLabels,
      loading: false,
      error: undefined,
    })
    render(<ModuleIssues programKey="prog1" moduleKey="mod1" />)

    const selectTrigger = screen.getByRole('button', { name: /Label/i })
    fireEvent.click(selectTrigger)

    const listbox = await screen.findByRole('listbox')
    expect(within(listbox).getByText('label-from-issue')).toBeInTheDocument()
  })

  it('handles issues with null labels and assignees', () => {
    const issueWithNullFields = {
      ...mockModuleData.managementModule.issues[0],
      labels: null,
      assignees: null,
    }
    mockUseQuery.mockReturnValue({
      data: {
        managementModule: {
          ...mockModuleData.managementModule,
          issues: [issueWithNullFields],
        },
      },
      loading: false,
      error: undefined,
    })
    render(<ModuleIssues programKey="prog1" moduleKey="mod1" />)
    expect(screen.getByText('Issues')).toBeInTheDocument()
    expect(screen.getAllByText('First Issue Title')[0]).toBeInTheDocument()
  })
  it('extracts labels from issues and handles null labels when availableLabels is empty', async () => {
    mockUseQuery.mockReturnValue({
      loading: false,
      data: {
        managementModule: {
          ...mockModuleData.managementModule,
          availableLabels: [], // Force extraction from issues
          issues: [
            {
              ...mockModuleData.managementModule.issues[0],
              id: '1',
              labels: ['extracted-label'],
            },
            {
              ...mockModuleData.managementModule.issues[0],
              id: '2',
              labels: null, // Test null labels handling
            },
          ],
        },
      },
    })

    render(<ModuleIssues programKey="prog1" moduleKey="mod1" />)

    const selectTrigger = screen.getByRole('button', { name: /Label/i })
    fireEvent.click(selectTrigger)

    const listbox = await screen.findByRole('listbox')
    expect(within(listbox).getByText('extracted-label')).toBeInTheDocument()
  })

  describe('deadline filtering', () => {
    it('filters issues by deadline category "overdue"', async () => {
      const now = new Date()
      const yesterday = new Date(now.getTime() - 24 * 60 * 60 * 1000)
      const tomorrow = new Date(now.getTime() + 24 * 60 * 60 * 1000)

      mockUseQuery.mockReturnValue({
        data: {
          managementModule: {
            ...mockModuleData.managementModule,
            issues: [
              {
                ...mockModuleData.managementModule.issues[0],
                id: '1',
                number: 101,
                taskDeadline: yesterday.toISOString(),
              },
              {
                ...mockModuleData.managementModule.issues[0],
                id: '2',
                number: 102,
                taskDeadline: tomorrow.toISOString(),
              },
            ],
            issuesCount: 2,
          },
        },
        loading: false,
        error: undefined,
      })
      render(<ModuleIssues programKey="prog1" moduleKey="mod1" />)

      const deadlineSelectTrigger = screen.getByRole('button', { name: /Deadline/i })
      fireEvent.click(deadlineSelectTrigger)

      const listbox = await screen.findByRole('listbox')
      const overdueOption = within(listbox).getByText('Overdue')
      fireEvent.click(overdueOption)

      await waitFor(() => {
        expect(mockReplace).toHaveBeenCalledWith('?deadline=overdue', { scroll: false })
      })
    })

    it('filters issues by deadline category "due-soon"', async () => {
      const now = new Date()
      const threeDaysLater = new Date(now.getTime() + 3 * 24 * 60 * 60 * 1000)
      const twentyDaysLater = new Date(now.getTime() + 20 * 24 * 60 * 60 * 1000)

      mockUseQuery.mockReturnValue({
        data: {
          managementModule: {
            ...mockModuleData.managementModule,
            issues: [
              {
                ...mockModuleData.managementModule.issues[0],
                id: '1',
                number: 101,
                taskDeadline: threeDaysLater.toISOString(),
              },
              {
                ...mockModuleData.managementModule.issues[0],
                id: '2',
                number: 102,
                taskDeadline: twentyDaysLater.toISOString(),
              },
            ],
            issuesCount: 2,
          },
        },
        loading: false,
        error: undefined,
      })
      render(<ModuleIssues programKey="prog1" moduleKey="mod1" />)

      const deadlineSelectTrigger = screen.getByRole('button', { name: /Deadline/i })
      fireEvent.click(deadlineSelectTrigger)

      const listbox = await screen.findByRole('listbox')
      const dueSoonOption = within(listbox).getByText('Due Soon')
      fireEvent.click(dueSoonOption)

      await waitFor(() => {
        expect(mockReplace).toHaveBeenCalledWith('?deadline=due-soon', { scroll: false })
      })
    })

    it('filters issues by deadline category "upcoming"', async () => {
      const now = new Date()
      const thirtyDaysLater = new Date(now.getTime() + 30 * 24 * 60 * 60 * 1000)

      mockUseQuery.mockReturnValue({
        data: {
          managementModule: {
            ...mockModuleData.managementModule,
            issues: [
              {
                ...mockModuleData.managementModule.issues[0],
                id: '1',
                number: 101,
                taskDeadline: thirtyDaysLater.toISOString(),
              },
            ],
            issuesCount: 1,
          },
        },
        loading: false,
        error: undefined,
      })
      render(<ModuleIssues programKey="prog1" moduleKey="mod1" />)

      const deadlineSelectTrigger = screen.getByRole('button', { name: /Deadline/i })
      fireEvent.click(deadlineSelectTrigger)

      const listbox = await screen.findByRole('listbox')
      const upcomingOption = within(listbox).getByText('Upcoming')
      fireEvent.click(upcomingOption)

      await waitFor(() => {
        expect(mockReplace).toHaveBeenCalledWith('?deadline=upcoming', { scroll: false })
      })
    })

    it('filters issues by "no-deadline" category', async () => {
      mockUseQuery.mockReturnValue({
        data: {
          managementModule: {
            ...mockModuleData.managementModule,
            issues: [
              {
                ...mockModuleData.managementModule.issues[0],
                id: '1',
                number: 101,
                taskDeadline: null,
              },
              {
                ...mockModuleData.managementModule.issues[0],
                id: '2',
                number: 102,
                taskDeadline: undefined,
              },
            ],
            issuesCount: 2,
          },
        },
        loading: false,
        error: undefined,
      })
      render(<ModuleIssues programKey="prog1" moduleKey="mod1" />)

      const deadlineSelectTrigger = screen.getByRole('button', { name: /Deadline/i })
      fireEvent.click(deadlineSelectTrigger)

      const listbox = await screen.findByRole('listbox')
      const noDeadlineOption = within(listbox).getByText('No Deadline')
      fireEvent.click(noDeadlineOption)

      await waitFor(() => {
        expect(mockReplace).toHaveBeenCalledWith('?deadline=no-deadline', { scroll: false })
      })
    })

    it('clears deadline filter when "All" is selected', async () => {
      mockUseSearchParams.mockReturnValue(new URLSearchParams('?deadline=overdue'))
      mockUseQuery.mockReturnValue({
        data: mockModuleData,
        loading: false,
        error: undefined,
      })
      render(<ModuleIssues programKey="prog1" moduleKey="mod1" />)

      const deadlineSelectTrigger = screen.getByRole('button', { name: /Deadline/i })
      fireEvent.click(deadlineSelectTrigger)

      const listbox = await screen.findByRole('listbox')
      const allOption = within(listbox).getByText('All')
      fireEvent.click(allOption)

      await waitFor(() => {
        expect(mockReplace).toHaveBeenCalledWith(globalThis.location.pathname, {
          scroll: false,
        })
      })
    })

    it('handles client-side pagination when deadline filter is active', async () => {
      const now = new Date()
      const yesterday = new Date(now.getTime() - 24 * 60 * 60 * 1000)
      const twentyFiveOverdueIssues = Array.from({ length: 25 }, (_, i) => ({
        ...mockModuleData.managementModule.issues[0],
        id: `${i + 1}`,
        objectID: `${i + 1}`,
        number: 100 + i,
        title: `Overdue Issue ${i + 1}`,
        taskDeadline: yesterday.toISOString(),
      }))

      mockUseQuery.mockReturnValue({
        data: {
          managementModule: {
            ...mockModuleData.managementModule,
            issues: twentyFiveOverdueIssues,
            issuesCount: 25,
          },
        },
        loading: false,
        error: undefined,
      })
      mockUseSearchParams.mockReturnValue(new URLSearchParams('?deadline=overdue'))

      render(<ModuleIssues programKey="prog1" moduleKey="mod1" />)

      await waitFor(() => {
        expect(screen.getAllByText(/Overdue Issue/)).toHaveLength(10)
      })

      mockUseQuery.mockReturnValue({
        data: {
          managementModule: {
            ...mockModuleData.managementModule,
            issues: twentyFiveOverdueIssues,
            issuesCount: 25,
          },
        },
        loading: false,
        error: undefined,
      })

      const pageTwoButton = screen.getByRole('button', { name: /go to page 2/i })
      fireEvent.click(pageTwoButton)

      await waitFor(() => {
        const rows = screen.queryAllByText(/Overdue Issue/)
        expect(rows.length).toBeGreaterThan(0)
      })
    })

    it('fetches all issues when deadline filter is active for client-side filtering', () => {
      const now = new Date()
      const yesterday = new Date(now.getTime() - 24 * 60 * 60 * 1000)

      mockUseQuery.mockReturnValue({
        data: {
          managementModule: {
            ...mockModuleData.managementModule,
            issues: [
              {
                ...mockModuleData.managementModule.issues[0],
                id: '1',
                taskDeadline: yesterday.toISOString(),
              },
            ],
            issuesCount: 1,
          },
        },
        loading: false,
        error: undefined,
      })
      mockUseSearchParams.mockReturnValue(new URLSearchParams('?deadline=overdue'))

      render(<ModuleIssues programKey="prog1" moduleKey="mod1" />)

      expect(mockUseQuery).toHaveBeenCalledWith(
        expect.anything(),
        expect.objectContaining({
          variables: expect.objectContaining({
            limit: 1000, // MAX_ISSUES_FOR_DEADLINE_FILTER
            offset: 0,
          }),
        })
      )
    })

    it('preserves label and handles deadline filter together', async () => {
      const now = new Date()
      const yesterday = new Date(now.getTime() - 24 * 60 * 60 * 1000)

      mockUseSearchParams.mockReturnValue(new URLSearchParams('?label=bug&deadline=overdue'))
      mockUseQuery.mockReturnValue({
        data: {
          managementModule: {
            ...mockModuleData.managementModule,
            issues: [
              {
                ...mockModuleData.managementModule.issues[0],
                labels: ['bug'],
                taskDeadline: yesterday.toISOString(),
              },
            ],
          },
        },
        loading: false,
        error: undefined,
      })

      render(<ModuleIssues programKey="prog1" moduleKey="mod1" />)

      const deadlineSelectTrigger = screen.getByRole('button', { name: /Deadline/i })
      fireEvent.click(deadlineSelectTrigger)

      const listbox = await screen.findByRole('listbox')
      const allOption = within(listbox).getByText('All')
      fireEvent.click(allOption)

      await waitFor(() => {
        expect(mockReplace).toHaveBeenCalledWith('?label=bug', { scroll: false })
      })
    })
  })

  describe('error handling', () => {
    it('handles errors from useQuery and triggers handleAppError', () => {
      const error = new Error('GraphQL error')
      mockUseQuery.mockReturnValue({
        data: undefined,
        loading: false,
        error,
      })

      render(<ModuleIssues programKey="prog1" moduleKey="mod1" />)

      expect(mockHandleAppError).toHaveBeenCalledWith(error)
    })

    it('renders nothing when the issues query returns a FORBIDDEN GraphQL error', () => {
      const error = {
        graphQLErrors: [{ message: 'Forbidden', extensions: { code: 'FORBIDDEN' } }],
      }
      mockUseQuery.mockReturnValue({ data: undefined, loading: false, error })

      render(<ModuleIssues programKey="prog1" moduleKey="mod1" />)

      expect(screen.queryByText('Issues')).not.toBeInTheDocument()
      expect(screen.queryByRole('table')).not.toBeInTheDocument()
      expect(mockHandleAppError).not.toHaveBeenCalled()
    })

    it('does not call handleAppError when there is no error', () => {
      mockUseQuery.mockReturnValue({
        data: mockModuleData,
        loading: false,
        error: undefined,
      })

      render(<ModuleIssues programKey="prog1" moduleKey="mod1" />)

      expect(mockHandleAppError).not.toHaveBeenCalled()
    })

    it('calls handleAppError when error changes from undefined to an error', () => {
      mockUseQuery.mockReturnValue({
        data: undefined,
        loading: false,
        error: undefined,
      })

      const { rerender } = render(<ModuleIssues programKey="prog1" moduleKey="mod1" />)
      expect(mockHandleAppError).not.toHaveBeenCalled()

      const newError = new Error('Network error')
      mockUseQuery.mockReturnValue({
        data: undefined,
        loading: false,
        error: newError,
      })

      rerender(<ModuleIssues programKey="prog1" moduleKey="mod1" />)
      expect(mockHandleAppError).toHaveBeenCalledWith(newError)
    })
  })

  describe('Authorization', () => {
    it('hides the section when the query is forbidden', () => {
      mockUseQuery.mockImplementation(() => ({
        data: undefined,
        loading: false,
        error: {
          graphQLErrors: [{ message: 'Forbidden', extensions: { code: 'FORBIDDEN' } }],
        },
      }))

      render(<ModuleIssues programKey="prog1" moduleKey="mod1" />)

      expect(screen.queryByText('Issues')).not.toBeInTheDocument()
      expect(screen.queryByRole('table')).not.toBeInTheDocument()
    })

    it('grants access for authenticated user who is a program admin', () => {
      mockUseSession.mockReturnValue({
        data: {
          user: {
            login: 'admin-user',
            email: 'admin@example.com',
          },
        },
        status: 'authenticated',
      })

      mockUseQuery.mockReturnValue({ data: mockModuleData, loading: false, error: undefined })

      render(<ModuleIssues programKey="prog1" moduleKey="mod1" />)

      expect(screen.getByText('Issues')).toBeInTheDocument()
    })

    it('grants access for authenticated user who is a module mentor', () => {
      mockUseSession.mockReturnValue({
        data: {
          user: {
            login: 'mentor-user',
            email: 'mentor@example.com',
          },
        },
        status: 'authenticated',
      })

      mockUseQuery.mockReturnValue({ data: mockModuleData, loading: false, error: undefined })

      render(<ModuleIssues programKey="prog1" moduleKey="mod1" />)

      expect(screen.getByText('Issues')).toBeInTheDocument()
    })
  })
})

describe('Mentee view', () => {
  beforeEach(() => {
    mockUseRouter.mockReturnValue({ push: mockPush, replace: mockReplace })
    mockUseSearchParams.mockReturnValue(new URLSearchParams())
    mockUseSession.mockReturnValue({
      data: { user: { login: 'mentee1', isLeader: false, isMentor: false } },
      status: 'authenticated',
    })
  })

  it('clears URL-driven filters a mentee cannot see or reset', async () => {
    mockUseSearchParams.mockReturnValue(new URLSearchParams('?label=bug&deadline=overdue'))
    mockUseQuery.mockReturnValue({
      data: {
        managementModule: {
          name: 'Test Module',
          userRole: 'mentee',
          issuesCount: 0,
          availableLabels: [],
          issues: [],
        },
      },
      loading: false,
      error: undefined,
    })
    render(<ModuleIssues programKey="prog1" moduleKey="mod1" />)
    await waitFor(() => {
      expect(mockReplace).toHaveBeenCalled()
    })
    const target = mockReplace.mock.calls.at(-1)?.[0]
    expect(target).not.toContain('label')
    expect(target).not.toContain('deadline')
  })

  it('shows loading spinner when mentee issues are loading', () => {
    mockUseQuery.mockReturnValue({ data: undefined, loading: true, error: undefined })
    render(<ModuleIssues programKey="prog1" moduleKey="mod1" />)
    expect(screen.getByText('Loading issues...')).toBeInTheDocument()
  })

  it('renders mentee issues list when data is available', async () => {
    mockUseQuery.mockImplementation(() => ({
      data: {
        managementModule: {
          name: 'Test Module',
          userRole: 'mentee',
          issuesCount: 1,
          availableLabels: [],
          issues: [
            {
              id: '1',
              number: 1,
              title: 'Mentee Issue One',
              state: 'open',
              isMerged: false,
              labels: [],
              assignees: [],
              taskDeadline: null,
            },
          ],
        },
      },
      loading: false,
      error: undefined,
    }))
    render(<ModuleIssues programKey="prog1" moduleKey="mod1" />)
    await waitFor(() => {
      expect(screen.getByText('Mentee Issue One')).toBeInTheDocument()
    })
    // Mentees don't get the management filter controls.
    expect(screen.queryByRole('button', { name: /Label/i })).not.toBeInTheDocument()
  })

  it('reports the error when the query fails', async () => {
    mockUseQuery.mockImplementation(() => ({
      data: undefined,
      loading: false,
      error: new Error('Failed'),
    }))
    render(<ModuleIssues programKey="prog1" moduleKey="mod1" />)
    await waitFor(() => {
      expect(mockHandleAppError).toHaveBeenCalled()
    })
  })
})
