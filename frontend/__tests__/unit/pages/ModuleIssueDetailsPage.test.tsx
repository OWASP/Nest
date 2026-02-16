import { useQuery } from '@apollo/client/react'
import { render, screen, fireEvent, waitFor, within, act } from '@testing-library/react'
import { useIssueMutations } from 'hooks/useIssueMutations'
import { useParams } from 'next/navigation'
import ModuleIssueDetailsPage from 'app/my/mentorship/programs/[programKey]/modules/[moduleKey]/issues/[issueId]/page'

// Mock dependencies
jest.mock('@apollo/client/react', () => ({
  ...jest.requireActual('@apollo/client/react'),
  useQuery: jest.fn(),
}))

jest.mock('next/navigation', () => ({
  useParams: jest.fn(),
  useRouter: jest.fn(() => ({
    push: jest.fn(),
    replace: jest.fn(),
  })),
}))

jest.mock('components/MarkdownWrapper', () => {
  return jest.fn(({ content }: { content: string }) => (
    <div data-testid="markdown-content">{content}</div>
  ))
})

jest.mock('hooks/useIssueMutations')

const mockUseQuery = useQuery as unknown as jest.Mock
const mockUseParams = useParams as jest.Mock
const mockUseIssueMutations = useIssueMutations as unknown as jest.Mock

const mockAssignIssue = jest.fn()
const mockUnassignIssue = jest.fn()
const mockSetTaskDeadline = jest.fn()
const mockClearTaskDeadline = jest.fn()

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

describe('ModuleIssueDetailsPage', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    mockUseParams.mockReturnValue({
      programKey: 'prog1',
      moduleKey: 'mod1',
      issueId: '123',
    })
    mockUseIssueMutations.mockReturnValue({
      assignIssue: mockAssignIssue,
      unassignIssue: mockUnassignIssue,
      setTaskDeadlineMutation: mockSetTaskDeadline,
      clearTaskDeadlineMutation: mockClearTaskDeadline,
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

  it('renders a loading spinner while data is being fetched', () => {
    mockUseQuery.mockReturnValue({ data: undefined, loading: true, error: undefined })
    render(<ModuleIssueDetailsPage />)
    expect(screen.getAllByAltText('Loading indicator')[0]).toBeInTheDocument()
  })

  it('renders an error display on query error', () => {
    const error = new Error('Test error')
    mockUseQuery.mockReturnValue({ data: undefined, loading: false, error })
    render(<ModuleIssueDetailsPage />)
    expect(screen.getByText('Error Loading Issue')).toBeInTheDocument()
    expect(screen.getByText(error.message)).toBeInTheDocument()
  })

  it('renders a 404 error if the issue is not found', () => {
    mockUseQuery.mockReturnValue({
      data: { getModule: { issueByNumber: null } },
      loading: false,
      error: undefined,
    })
    render(<ModuleIssueDetailsPage />)
    expect(screen.getByText('Issue Not Found')).toBeInTheDocument()
  })

  it('renders the issue details successfully', () => {
    mockUseQuery.mockReturnValue({ data: mockIssueData, loading: false, error: undefined })
    render(<ModuleIssueDetailsPage />)
    expect(screen.getByText('Test Issue Title')).toBeInTheDocument()
    expect(screen.getByText('This is the issue body.')).toBeInTheDocument()
    expect(screen.getByText('org/repo • #123')).toBeInTheDocument()
    expect(screen.getAllByText('Open')[0]).toBeInTheDocument()
    expect(screen.getByText('bug')).toBeInTheDocument()
    expect(screen.getByText('user1')).toBeInTheDocument()
    expect(screen.getByText('Fix for test issue')).toBeInTheDocument()
    expect(screen.getByText('@user2')).toBeInTheDocument()
  })

  it('calls assignIssue when assigning an interested user', async () => {
    mockUseQuery.mockReturnValue({ data: mockIssueData, loading: false, error: undefined })
    render(<ModuleIssueDetailsPage />)
    const interestedUsersHeading = screen.getByRole('heading', { name: /Interested Users/i })
    const userGrid = interestedUsersHeading.nextElementSibling
    expect(userGrid).not.toBeNull()
    const assignButton = within(userGrid as HTMLElement).getByRole('button', { name: /Assign/i })
    fireEvent.click(assignButton)

    await waitFor(() => {
      expect(mockAssignIssue).toHaveBeenCalledWith({
        variables: {
          programKey: 'prog1',
          moduleKey: 'mod1',
          issueNumber: 123,
          userLogin: 'user2',
        },
      })
    })
  })

  it('calls unassignIssue when unassigning a user', async () => {
    mockUseQuery.mockReturnValue({ data: mockIssueData, loading: false, error: undefined })
    render(<ModuleIssueDetailsPage />)
    const unassignButton = screen.getByRole('button', { name: /Unassign @user1/i })
    fireEvent.click(unassignButton)

    await waitFor(() => {
      expect(mockUnassignIssue).toHaveBeenCalledWith({
        variables: {
          programKey: 'prog1',
          moduleKey: 'mod1',
          issueNumber: 123,
          userLogin: 'user1',
        },
      })
    })
  })

  it('shows "No linked pull requests" when there are none', () => {
    const noPrData = {
      getModule: {
        ...mockIssueData.getModule,
        issueByNumber: {
          ...mockIssueData.getModule.issueByNumber,
          pullRequests: [],
        },
      },
    }
    mockUseQuery.mockReturnValue({ data: noPrData, loading: false, error: undefined })
    render(<ModuleIssueDetailsPage />)
    expect(screen.getByText('No linked pull requests.')).toBeInTheDocument()
  })

  it('shows "No interested users yet" when there are none', () => {
    const noInterestedData = {
      getModule: {
        ...mockIssueData.getModule,
        interestedUsers: [],
      },
    }
    mockUseQuery.mockReturnValue({ data: noInterestedData, loading: false, error: undefined })
    render(<ModuleIssueDetailsPage />)
    expect(screen.getByText('No interested users yet.')).toBeInTheDocument()
  })

  describe('Task Timeline and Deadline', () => {
    it.each([
      { dayOffset: -1, expectedText: /\(overdue\)/, expectedColor: 'text-[#DA3633]' },
      { dayOffset: 2, expectedText: /\(2 days left\)/, expectedColor: 'text-[#F59E0B]' },
      {
        dayOffset: 10,
        expectedText: /\(10 days left\)/,
        expectedColor: 'text-gray-600 dark:text-gray-300',
      },
      {
        dayOffset: null,
        expectedText: /No deadline set/,
        expectedColor: 'text-gray-600 dark:text-gray-300',
      },
    ])(
      'renders deadline text for deadline with offset $dayOffset',
      ({ dayOffset, expectedText, expectedColor }) => {
        const today = new Date()
        let deadline = null
        if (dayOffset !== null) {
          const deadlineDate = new Date(today)
          deadlineDate.setDate(today.getDate() + dayOffset)
          deadline = deadlineDate.toISOString()
        }

        const dataWithDeadline = {
          ...mockIssueData,
          getModule: { ...mockIssueData.getModule, taskDeadline: deadline },
        }
        mockUseQuery.mockReturnValue({ data: dataWithDeadline, loading: false, error: undefined })
        render(<ModuleIssueDetailsPage />)
        const deadlineElement = screen.getByText(expectedText)
        expect(deadlineElement).toBeInTheDocument()
        expect(deadlineElement).toHaveClass(expectedColor)
      }
    )

    it('disables the deadline button when there are no assignees', () => {
      const noAssigneesData = {
        ...mockIssueData,
        getModule: {
          ...mockIssueData.getModule,
          issueByNumber: {
            ...mockIssueData.getModule.issueByNumber,
            assignees: [],
          },
        },
      }
      mockUseQuery.mockReturnValue({ data: noAssigneesData, loading: false, error: undefined })
      render(<ModuleIssueDetailsPage />)
      const deadlineButton = screen.getByRole('button', { name: /No deadline set/i })
      expect(deadlineButton).toBeDisabled()
    })

    it('switches to an input field when the deadline is clicked', async () => {
      const setIsEditingDeadline = jest.fn()
      const baseMocks = (useIssueMutations as jest.Mock)()
      mockUseIssueMutations.mockReturnValue({
        ...baseMocks,
        setIsEditingDeadline,
      })
      mockUseQuery.mockReturnValue({ data: mockIssueData, loading: false, error: undefined })
      render(<ModuleIssueDetailsPage />)
      const deadlineButton = screen.getByRole('button', { name: /No deadline set/i })
      fireEvent.click(deadlineButton)
      await waitFor(() => {
        expect(setIsEditingDeadline).toHaveBeenCalledWith(true)
      })
    })

    it('calls setTaskDeadlineMutation when a new date is selected', async () => {
      const setTaskDeadlineMutation = jest.fn()
      const baseMocks = (useIssueMutations as jest.Mock)()
      mockUseIssueMutations.mockReturnValue({
        ...baseMocks,
        isEditingDeadline: true, // Mock that we are in editing mode
        setTaskDeadlineMutation,
        deadlineInput: '', // Ensure input is controlled and can be found
      })
      mockUseQuery.mockReturnValue({ data: mockIssueData, loading: false, error: undefined })
      render(<ModuleIssueDetailsPage />)

      const dateInput = screen.getByDisplayValue('')
      fireEvent.change(dateInput, { target: { value: '2025-12-25' } })

      await waitFor(() => {
        expect(setTaskDeadlineMutation).toHaveBeenCalled()
      })
    })
    it('populates input with existing deadline when clicked', async () => {
      const setDeadlineInput = jest.fn()
      const setIsEditingDeadline = jest.fn()
      const baseMocks = (useIssueMutations as jest.Mock)()

      mockUseIssueMutations.mockReturnValue({
        ...baseMocks,
        setDeadlineInput,
        setIsEditingDeadline,
      })

      const pastDate = new Date('2020-01-01').toISOString()
      const dataWithDeadline = {
        ...mockIssueData,
        getModule: { ...mockIssueData.getModule, taskDeadline: pastDate },
      }

      mockUseQuery.mockReturnValue({ data: dataWithDeadline, loading: false, error: undefined })
      render(<ModuleIssueDetailsPage />)

      const deadlineButton = screen.getByRole('button', { name: /\(overdue\)/i })
      fireEvent.click(deadlineButton)

      await waitFor(() => {
        expect(setDeadlineInput).toHaveBeenCalledWith('2020-01-01')
        expect(setIsEditingDeadline).toHaveBeenCalledWith(true)
      })
    })
  })

  describe('issue states', () => {
    it.each([
      { state: 'closed', isMerged: true, expectedText: 'Closed' },
      { state: 'closed', isMerged: false, expectedText: 'Closed' },
      { state: 'open', isMerged: false, expectedText: 'Open' },
    ])('renders issue state as "$expectedText"', ({ state, isMerged, expectedText }) => {
      const issueWithState = {
        ...mockIssueData,
        getModule: {
          ...mockIssueData.getModule,
          issueByNumber: {
            ...mockIssueData.getModule.issueByNumber,
            state,
            isMerged,
          },
        },
      }
      mockUseQuery.mockReturnValue({ data: issueWithState, loading: false, error: undefined })
      render(<ModuleIssueDetailsPage />)
      expect(screen.getAllByText(expectedText)[0]).toBeInTheDocument()
    })
  })

  it('renders correctly with missing optional data', () => {
    const dataWithMissingFields = {
      getModule: {
        ...mockIssueData.getModule,
        taskAssignedAt: null,
        issueByNumber: {
          ...mockIssueData.getModule.issueByNumber,
          body: null,
          assignees: [{ id: 'a1', login: 'user1', name: null, avatarUrl: null }],
          pullRequests: [
            {
              id: 'pr1',
              title: 'PR',
              url: '',
              state: 'open',
              mergedAt: null,
              createdAt: new Date().toISOString(),
              author: null,
            },
          ],
        },
        interestedUsers: [{ id: 'u1', login: 'user2', avatarUrl: null }],
      },
    }
    mockUseQuery.mockReturnValue({ data: dataWithMissingFields, loading: false, error: undefined })
    render(<ModuleIssueDetailsPage />)
    expect(screen.getByText('No description.')).toBeInTheDocument()
    expect(screen.getByText('Not assigned')).toBeInTheDocument()
    expect(screen.getByText(/by Unknown/)).toBeInTheDocument()
    expect(screen.getByText('user1')).toBeInTheDocument()
    expect(screen.getByText('@user2')).toBeInTheDocument()
  })

  it('calls clearTaskDeadlineMutation when the date input is cleared', async () => {
    const clearTaskDeadlineMutation = jest.fn()
    const baseMocks = (useIssueMutations as jest.Mock)()
    mockUseIssueMutations.mockReturnValue({
      ...baseMocks,
      isEditingDeadline: true, // Mock that we are in editing mode
      clearTaskDeadlineMutation,
      deadlineInput: '2025-12-25', // Mock an existing value
    })
    mockUseQuery.mockReturnValue({ data: mockIssueData, loading: false, error: undefined })
    render(<ModuleIssueDetailsPage />)

    const dateInput = screen.getByDisplayValue('2025-12-25')
    fireEvent.change(dateInput, { target: { value: '' } })

    await waitFor(() => {
      expect(clearTaskDeadlineMutation).toHaveBeenCalledWith({
        variables: {
          programKey: 'prog1',
          moduleKey: 'mod1',
          issueNumber: 123,
        },
      })
    })
  })

  it('disables assign/unassign buttons when mutations are in progress', () => {
    const baseMocks = (useIssueMutations as jest.Mock)()
    mockUseIssueMutations.mockReturnValue({
      ...baseMocks,
      assigning: true,
      unassigning: true,
    })
    mockUseQuery.mockReturnValue({ data: mockIssueData, loading: false, error: undefined })
    render(<ModuleIssueDetailsPage />)

    const interestedUsersHeading = screen.getByRole('heading', { name: /Interested Users/i })
    const userGrid = interestedUsersHeading.nextElementSibling
    const assignButton = within(userGrid as HTMLElement).getByRole('button', { name: /Assign/i })
    expect(assignButton).toBeDisabled()

    const unassignButton = screen.getByRole('button', { name: /Unassign @user1/i })
    expect(unassignButton).toBeDisabled()
  })
  it('calls fetchMore when clicking Show More button', async () => {
    const fetchMoreMock = jest.fn().mockResolvedValue({
      data: {
        getModule: {
          issueByNumber: {
            pullRequests: [
              {
                id: 'pr-new',
                title: 'New PR',
                url: 'http://example.com',
                state: 'open',
                mergedAt: null,
                createdAt: new Date().toISOString(),
                author: { login: 'user-new', avatarUrl: '' },
              },
            ],
          },
        },
      },
    })

    mockUseQuery.mockReturnValue({
      data: {
        getModule: {
          issueByNumber: {
            ...mockIssueData.getModule.issueByNumber,
            pullRequests: Array.from({ length: 4 }, (_, i) => ({
              ...mockIssueData.getModule.issueByNumber.pullRequests[0],
              id: `pr-${i}`,
            })),
          },
        },
      },
      loading: false,
      error: undefined,
      fetchMore: fetchMoreMock,
    })

    render(<ModuleIssueDetailsPage />)

    const showMoreButton = screen.getByRole('button', { name: /Show more/i })
    expect(showMoreButton).toBeInTheDocument()

    await act(async () => {
      fireEvent.click(showMoreButton)
    })

    expect(fetchMoreMock).toHaveBeenCalledWith(
      expect.objectContaining({
        variables: expect.objectContaining({
          offset: 4,
          limit: 4,
        }),
      })
    )
  })

  it('renders "(today)" for deadline that is exactly today', () => {
    const today = new Date()
    const todayDeadline = new Date(
      Date.UTC(today.getUTCFullYear(), today.getUTCMonth(), today.getUTCDate())
    ).toISOString()

    const dataWithTodayDeadline = {
      ...mockIssueData,
      getModule: { ...mockIssueData.getModule, taskDeadline: todayDeadline },
    }
    mockUseQuery.mockReturnValue({ data: dataWithTodayDeadline, loading: false, error: undefined })
    render(<ModuleIssueDetailsPage />)
    expect(screen.getByText(/\(today\)/)).toBeInTheDocument()
  })

  it('shows "Loading issue…" title when issueId is not available', () => {
    mockUseParams.mockReturnValue({
      programKey: 'prog1',
      moduleKey: 'mod1',
      issueId: '',
    })
    mockUseQuery.mockReturnValue({ data: mockIssueData, loading: false, error: undefined })
    render(<ModuleIssueDetailsPage />)

    const interestedUsersHeading = screen.getByRole('heading', { name: /Interested Users/i })
    const userGrid = interestedUsersHeading.nextElementSibling
    const assignButton = within(userGrid as HTMLElement).getByRole('button', { name: /Assign/i })
    expect(assignButton).toHaveAttribute('title', 'Loading issue…')
  })

  it('shows ShowMoreButton when there are more than 4 pull requests', async () => {
    const manyPRsData = {
      ...mockIssueData,
      getModule: {
        ...mockIssueData.getModule,
        issueByNumber: {
          ...mockIssueData.getModule.issueByNumber,
          pullRequests: Array.from({ length: 6 }, (_, i) => ({
            id: `pr${i + 1}`,
            title: `Pull Request ${i + 1}`,
            url: `https://github.com/pr/${i + 1}`,
            state: 'open',
            mergedAt: null,
            createdAt: new Date().toISOString(),
            author: {
              login: `dev${i + 1}`,
              avatarUrl: `https://example.com/avatar${i + 1}.png`,
            },
          })),
        },
      },
    }
    mockUseQuery.mockReturnValue({
      data: manyPRsData,
      loading: false,
      error: undefined,
      fetchMore: jest.fn().mockResolvedValue({ data: manyPRsData }),
    })
    render(<ModuleIssueDetailsPage />)

    // Initially only 4 PRs should be visible
    expect(screen.getByText('Pull Request 1')).toBeInTheDocument()
    expect(screen.queryByText('Pull Request 5')).not.toBeInTheDocument()

    // Click ShowMoreButton to show all PRs
    const showMoreButton = screen.getByRole('button', { name: /show more/i })
    fireEvent.click(showMoreButton)

    await waitFor(() => {
      expect(screen.getByText('Pull Request 5')).toBeInTheDocument()
      expect(screen.getByText('Pull Request 6')).toBeInTheDocument()
    })
  })

  it('renders assignee name when login is not available', () => {
    const dataWithNameOnlyAssignee = {
      ...mockIssueData,
      getModule: {
        ...mockIssueData.getModule,
        issueByNumber: {
          ...mockIssueData.getModule.issueByNumber,
          assignees: [
            {
              id: 'assignee1',
              login: '',
              name: 'Fallback Name',
              avatarUrl: 'https://example.com/avatar1.png',
            },
          ],
        },
      },
    }
    mockUseQuery.mockReturnValue({
      data: dataWithNameOnlyAssignee,
      loading: false,
      error: undefined,
    })
    render(<ModuleIssueDetailsPage />)
    expect(screen.getByText('Fallback Name')).toBeInTheDocument()
  })

  it('renders placeholder avatar for assignee without avatarUrl', () => {
    const dataWithNoAvatarAssignee = {
      ...mockIssueData,
      getModule: {
        ...mockIssueData.getModule,
        issueByNumber: {
          ...mockIssueData.getModule.issueByNumber,
          assignees: [
            {
              id: 'assignee1',
              login: 'user1',
              name: 'User One',
              avatarUrl: null,
            },
          ],
        },
      },
    }
    mockUseQuery.mockReturnValue({
      data: dataWithNoAvatarAssignee,
      loading: false,
      error: undefined,
    })
    render(<ModuleIssueDetailsPage />)
    const placeholderDiv = document.querySelector('[aria-hidden="true"].rounded-full.bg-gray-400')
    expect(placeholderDiv).toBeInTheDocument()
  })

  it('handles null pullRequests array', () => {
    const dataWithNullPRs = {
      ...mockIssueData,
      getModule: {
        ...mockIssueData.getModule,
        issueByNumber: {
          ...mockIssueData.getModule.issueByNumber,
          pullRequests: null,
        },
      },
    }
    mockUseQuery.mockReturnValue({ data: dataWithNullPRs, loading: false, error: undefined })
    render(<ModuleIssueDetailsPage />)
    expect(screen.getByText('No linked pull requests.')).toBeInTheDocument()
  })

  it('renders placeholder avatar for interested user without avatarUrl', () => {
    const dataWithNoAvatarInterestedUser = {
      ...mockIssueData,
      getModule: {
        ...mockIssueData.getModule,
        interestedUsers: [
          {
            id: 'user2',
            login: 'user2',
            avatarUrl: null,
          },
        ],
      },
    }
    mockUseQuery.mockReturnValue({
      data: dataWithNoAvatarInterestedUser,
      loading: false,
      error: undefined,
    })
    render(<ModuleIssueDetailsPage />)
    const placeholderDivs = document.querySelectorAll(
      '[aria-hidden="true"].rounded-full.bg-gray-400'
    )
    expect(placeholderDivs.length).toBeGreaterThan(0)
  })

  it('handles null assignees, labels, and interestedUsers', () => {
    const dataWithNulls = {
      getModule: {
        ...mockIssueData.getModule,
        interestedUsers: null,
        issueByNumber: {
          ...mockIssueData.getModule.issueByNumber,
          assignees: null,
          labels: null,
        },
      },
    }
    mockUseQuery.mockReturnValue({ data: dataWithNulls, loading: false, error: undefined })
    render(<ModuleIssueDetailsPage />)

    expect(screen.getByText('Test Issue Title')).toBeInTheDocument()
  })

  it('does not trigger mutations when they are already in progress', () => {
    const assignIssue = jest.fn()
    const unassignIssue = jest.fn()
    const setTaskDeadlineMutation = jest.fn()
    const baseMocks = (useIssueMutations as jest.Mock)()

    mockUseIssueMutations.mockReturnValue({
      ...baseMocks,
      assignIssue,
      unassignIssue,
      setTaskDeadlineMutation,
      assigning: true,
      unassigning: true,
      settingDeadline: true,
      isEditingDeadline: true,
      deadlineInput: '2025-01-01',
      setDeadlineInput: jest.fn(),
    })

    mockUseQuery.mockReturnValue({ data: mockIssueData, loading: false, error: undefined })
    render(<ModuleIssueDetailsPage />)

    const interestedUsersHeading = screen.getByRole('heading', { name: /Interested Users/i })
    const userGrid = interestedUsersHeading.nextElementSibling
    const assignButton = within(userGrid as HTMLElement).getByRole('button', { name: /Assign/i })

    fireEvent.click(assignButton)
    expect(assignIssue).not.toHaveBeenCalled()

    const unassignButton = screen.getByRole('button', { name: /Unassign/i })
    fireEvent.click(unassignButton)
    expect(unassignIssue).not.toHaveBeenCalled()

    const dateInputEl = screen.getByDisplayValue('2025-01-01')
    fireEvent.change(dateInputEl, { target: { value: '2025-02-02' } })
    expect(setTaskDeadlineMutation).not.toHaveBeenCalled()
  })
})
