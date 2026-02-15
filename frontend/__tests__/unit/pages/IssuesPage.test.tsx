import { useQuery } from '@apollo/client/react'
import { render, screen, fireEvent, waitFor, within } from '@testing-library/react'
import { useParams, useRouter, useSearchParams } from 'next/navigation'
import { handleAppError } from 'app/global-error'
import IssuesPage from 'app/my/mentorship/programs/[programKey]/modules/[moduleKey]/issues/page'

// Mock dependencies
jest.mock('@apollo/client/react', () => ({
  ...jest.requireActual('@apollo/client/react'),
  useQuery: jest.fn(),
}))
jest.mock('next/navigation', () => ({
  useParams: jest.fn(),
  useRouter: jest.fn(),
  useSearchParams: jest.fn(),
}))

const mockUseQuery = useQuery as unknown as jest.Mock
const mockUseParams = useParams as jest.Mock
const mockUseRouter = useRouter as jest.Mock
const mockUseSearchParams = useSearchParams as jest.Mock
const mockPush = jest.fn()
const mockReplace = jest.fn()

const mockModuleData = {
  getModule: {
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

describe('IssuesPage', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    mockUseParams.mockReturnValue({ programKey: 'prog1', moduleKey: 'mod1' })
    mockUseRouter.mockReturnValue({ push: mockPush, replace: mockReplace })
    mockUseSearchParams.mockReturnValue(new URLSearchParams())
  })

  it('renders a loading spinner while data is being fetched', () => {
    mockUseQuery.mockReturnValue({ data: undefined, loading: true, error: undefined })
    render(<IssuesPage />)
    expect(screen.getAllByAltText('Loading indicator').length).toBeGreaterThan(0)
  })

  it('calls handleAppError on query error', () => {
    const error = new Error('Test error')
    mockUseQuery.mockReturnValue({ data: undefined, loading: false, error })
    render(<IssuesPage />)
    expect(mockHandleAppError).toHaveBeenCalledWith(error)
  })

  it('renders a 404 error if the module is not found', () => {
    mockUseQuery.mockReturnValue({ data: { getModule: null }, loading: false, error: undefined })
    render(<IssuesPage />)
    expect(screen.getByText('Module Not Found')).toBeInTheDocument()
  })

  it('displays a "no issues found" message when there are no issues', () => {
    mockUseQuery.mockReturnValue({
      data: { getModule: { ...mockModuleData.getModule, issues: [], issuesCount: 0 } },
      loading: false,
      error: undefined,
    })
    render(<IssuesPage />)
    expect(screen.getAllByText('No issues found for the selected filter.')).toHaveLength(1)
  })

  it('renders the list of issues successfully', () => {
    mockUseQuery.mockReturnValue({ data: mockModuleData, loading: false, error: undefined })
    render(<IssuesPage />)
    expect(screen.getByText('Test Module Issues')).toBeInTheDocument()
    expect(screen.getAllByText('First Issue Title')[0]).toBeInTheDocument()
    expect(screen.getAllByText('Open')[0]).toBeInTheDocument()
    expect(screen.getAllByText('bug')[0]).toBeInTheDocument()
    expect(screen.getAllByText('user1')[0]).toBeInTheDocument()
  })

  it('navigates to the correct issue details page on click', () => {
    mockUseQuery.mockReturnValue({ data: mockModuleData, loading: false, error: undefined })
    render(<IssuesPage />)
    const issueTitleButton = screen.getAllByRole('button', { name: /First Issue Title/i })[0]
    fireEvent.click(issueTitleButton)
    expect(mockPush).toHaveBeenCalledWith('/my/mentorship/programs/prog1/modules/mod1/issues/101')
  })

  it('filters issues based on the selected label', async () => {
    mockUseQuery.mockReturnValue({ data: mockModuleData, loading: false, error: undefined })
    render(<IssuesPage />)

    const selectTrigger = screen.getByRole('button', { name: /Label/i })
    fireEvent.click(selectTrigger)

    const listbox = await screen.findByRole('listbox')
    const optionToSelect = within(listbox).getByText('bug')
    fireEvent.click(optionToSelect)

    await waitFor(() => {
      expect(mockReplace).toHaveBeenCalledWith('?label=bug')
    })
  })

  it('resets to page 1 when a new label is selected', async () => {
    mockUseQuery.mockReturnValue({ data: mockModuleData, loading: false, error: undefined })
    render(<IssuesPage />)

    const selectTrigger = screen.getByRole('button', { name: /Label/i })
    fireEvent.click(selectTrigger)

    const listbox = await screen.findByRole('listbox')
    const optionToSelect = within(listbox).getByText('documentation')
    fireEvent.click(optionToSelect)

    await waitFor(() => {
      expect(mockReplace).toHaveBeenCalledWith('?label=documentation')
    })
  })

  it('clears the filter when "All" is selected', async () => {
    mockUseQuery.mockReturnValue({ data: mockModuleData, loading: false, error: undefined })
    mockUseSearchParams.mockReturnValue(new URLSearchParams('?label=bug'))
    render(<IssuesPage />)

    const selectTrigger = screen.getByRole('button', { name: /Label/i })
    fireEvent.click(selectTrigger)

    const listbox = await screen.findByRole('listbox')
    const optionToSelect = within(listbox).getByText('All')
    fireEvent.click(optionToSelect)

    await waitFor(() => {
      expect(mockReplace).toHaveBeenCalledWith('?')
    })
  })

  it('handles pagination correctly', async () => {
    const twentyFiveIssues = {
      getModule: {
        ...mockModuleData.getModule,
        issues: Array.from({ length: 25 }, (_, i) => ({
          ...mockModuleData.getModule.issues[0],
          id: `${i + 1}`,
          objectID: `${i + 1}`,
          number: 100 + i,
          title: `Issue ${i + 1}`,
        })),
        issuesCount: 25,
      },
    }
    mockUseQuery.mockReturnValue({ data: twentyFiveIssues, loading: false, error: undefined })
    render(<IssuesPage />)

    const pageTwoButton = screen.getByRole('button', { name: /go to page 2/i })
    fireEvent.click(pageTwoButton)

    await waitFor(() => {
      expect(mockUseQuery).toHaveBeenLastCalledWith(
        expect.anything(),
        expect.objectContaining({
          variables: expect.objectContaining({
            offset: 20,
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
        ...mockModuleData.getModule.issues[0],
        state,
        isMerged,
      }
      mockUseQuery.mockReturnValue({
        data: {
          getModule: { ...mockModuleData.getModule, issues: [issue] },
        },
        loading: false,
        error: undefined,
      })
      render(<IssuesPage />)
      const desktopTable = screen.getByRole('table')
      expect(within(desktopTable).getByText(expectedText)).toBeInTheDocument()
    })
  })

  it('renders remaining labels count if there are more than 5 labels', () => {
    const manyLabelsIssue = {
      ...mockModuleData.getModule.issues[0],
      labels: ['bug', 'feature', 'docs', 'help', 'question', 'wontfix'],
    }
    mockUseQuery.mockReturnValue({
      data: {
        getModule: { ...mockModuleData.getModule, issues: [manyLabelsIssue] },
      },
      loading: false,
      error: undefined,
    })
    render(<IssuesPage />)
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
      ...mockModuleData.getModule.issues[0],
      assignees: multipleAssignees,
    }
    mockUseQuery.mockReturnValue({
      data: {
        getModule: {
          ...mockModuleData.getModule,
          issues: [multipleAssigneesIssue],
        },
      },
      loading: false,
      error: undefined,
    })
    render(<IssuesPage />)
    const plusOneElements = screen.getAllByText(/\+1/)
    expect(plusOneElements.length).toBeGreaterThan(0)
  })

  it('extracts labels from issues when availableLabels is empty', async () => {
    const dataWithoutAvailableLabels = {
      getModule: {
        ...mockModuleData.getModule,
        availableLabels: [],
        issues: [
          {
            ...mockModuleData.getModule.issues[0],
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
    render(<IssuesPage />)

    // Open the label dropdown to verify extracted labels are present
    const selectTrigger = screen.getByRole('button', { name: /Label/i })
    fireEvent.click(selectTrigger)

    const listbox = await screen.findByRole('listbox')
    expect(within(listbox).getByText('extracted-label-1')).toBeInTheDocument()
    expect(within(listbox).getByText('extracted-label-2')).toBeInTheDocument()
  })

  it('extracts labels from issues when availableLabels is null', async () => {
    const dataWithNullAvailableLabels = {
      getModule: {
        ...mockModuleData.getModule,
        availableLabels: null,
        issues: [
          {
            ...mockModuleData.getModule.issues[0],
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
    render(<IssuesPage />)

    const selectTrigger = screen.getByRole('button', { name: /Label/i })
    fireEvent.click(selectTrigger)

    const listbox = await screen.findByRole('listbox')
    expect(within(listbox).getByText('label-from-issue')).toBeInTheDocument()
  })

  it('handles issues with null labels and assignees', () => {
    const issueWithNullFields = {
      ...mockModuleData.getModule.issues[0],
      labels: null,
      assignees: null,
    }
    mockUseQuery.mockReturnValue({
      data: {
        getModule: {
          ...mockModuleData.getModule,
          issues: [issueWithNullFields],
        },
      },
      loading: false,
      error: undefined,
    })
    render(<IssuesPage />)
    expect(screen.getByText('Test Module Issues')).toBeInTheDocument()
    expect(screen.getAllByText('First Issue Title')[0]).toBeInTheDocument()
  })
  it('extracts labels from issues and handles null labels when availableLabels is empty', async () => {
    mockUseQuery.mockReturnValue({
      loading: false,
      data: {
        getModule: {
          ...mockModuleData.getModule,
          availableLabels: [], // Force extraction from issues
          issues: [
            {
              ...mockModuleData.getModule.issues[0],
              id: '1',
              labels: ['extracted-label'],
            },
            {
              ...mockModuleData.getModule.issues[0],
              id: '2',
              labels: null, // Test null labels handling
            },
          ],
        },
      },
    })

    render(<IssuesPage />)

    // Open the label filter dropdown
    const selectTrigger = screen.getByRole('button', { name: /Label/i })
    fireEvent.click(selectTrigger)

    // Verify that the label from the issue is present in the listbox
    const listbox = await screen.findByRole('listbox')
    expect(within(listbox).getByText('extracted-label')).toBeInTheDocument()
  })
})
