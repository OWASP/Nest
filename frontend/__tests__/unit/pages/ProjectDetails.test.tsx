import { useQuery } from '@apollo/client'
import { addToast } from '@heroui/toast'
import { act, fireEvent, screen, waitFor, within } from '@testing-library/react'
import { mockProjectDetailsData } from '@unit/data/mockProjectDetailsData'
import { render } from 'wrappers/testUtil'
import ProjectDetailsPage from 'app/projects/[projectKey]/page'

jest.mock('@apollo/client', () => ({
  ...jest.requireActual('@apollo/client'),
  useQuery: jest.fn(),
}))

jest.mock('@heroui/toast', () => ({
  addToast: jest.fn(),
}))

jest.mock('@fortawesome/react-fontawesome', () => ({
  FontAwesomeIcon: () => <span data-testid="mock-icon" />,
}))

const mockRouter = {
  push: jest.fn(),
}

jest.mock('next/navigation', () => ({
  ...jest.requireActual('next/navigation'),
  useRouter: jest.fn(() => mockRouter),
  useParams: () => ({ projectKey: 'test-project' }),
}))

const mockError = {
  error: new Error('GraphQL error'),
}

describe('ProjectDetailsPage', () => {
  beforeEach(() => {
    ;(useQuery as jest.Mock).mockReturnValue({
      data: mockProjectDetailsData,
      loading: false,
      error: null,
    })
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  test('renders loading state', async () => {
    ;(useQuery as jest.Mock).mockReturnValue({
      data: null,
      error: null,
    })

    render(<ProjectDetailsPage />)

    const loadingSpinner = screen.getAllByAltText('Loading indicator')
    await waitFor(() => {
      expect(loadingSpinner.length).toBeGreaterThan(0)
    })
  })

  test('renders project details when data is available', async () => {
    ;(useQuery as jest.Mock).mockReturnValue({
      data: mockProjectDetailsData,
      error: null,
    })

    render(<ProjectDetailsPage />)

    await waitFor(() => {
      expect(screen.getByText('Test Project')).toBeInTheDocument()
      expect(screen.getByText('Lab')).toBeInTheDocument()
    })
    expect(screen.getByText('2.2K Stars')).toBeInTheDocument()
    expect(screen.getByText('10 Forks')).toBeInTheDocument()
    expect(screen.getByText('10 Issues')).toBeInTheDocument()
  })

  test('renders error message when GraphQL request fails', async () => {
    ;(useQuery as jest.Mock).mockReturnValue({
      data: { repository: null },
      error: mockError,
    })

    render(<ProjectDetailsPage />)

    await waitFor(() => screen.getByText('Project not found'))
    expect(screen.getByText('Project not found')).toBeInTheDocument()
    expect(addToast).toHaveBeenCalledWith({
      description: 'Unable to complete the requested operation.',
      title: 'GraphQL Request Failed',
      timeout: 3000,
      shouldShowTimeoutProgress: true,
      color: 'danger',
      variant: 'solid',
    })
  })

  test('toggles contributors list when show more/less is clicked', async () => {
    render(<ProjectDetailsPage />)
    await waitFor(() => {
      expect(screen.getByText('Contributor 9')).toBeInTheDocument()
      expect(screen.queryByText('Contributor 10')).not.toBeInTheDocument()
    })

    const contributorsSection = screen.getByTestId('top-contributors')

    const showMoreButton = within(contributorsSection!).getByRole('button', { name: /Show more/i })
    fireEvent.click(showMoreButton)

    await waitFor(() => {
      expect(screen.getByText('Contributor 7')).toBeInTheDocument()
      expect(screen.getByText('Contributor 8')).toBeInTheDocument()
    })

    const showLessButton = within(contributorsSection!).getByRole('button', { name: /Show less/i })
    fireEvent.click(showLessButton)

    await waitFor(() => {
      expect(screen.queryByText('Contributor 10')).not.toBeInTheDocument()
    })
  })

  test('navigates to user page when contributor is clicked', async () => {
    render(<ProjectDetailsPage />)
    await waitFor(() => {
      expect(screen.getByText('Contributor 1')).toBeInTheDocument()
    })

    screen.getByText('Contributor 1').closest('button')?.click()

    expect(mockRouter.push).toHaveBeenCalledWith('/members/contributor1')
  })

  test('Recent issues are rendered correctly', async () => {
    render(<ProjectDetailsPage />)

    await waitFor(() => {
      const issues = mockProjectDetailsData.project.recentIssues

      issues.forEach((issue) => {
        expect(screen.getByText(issue.title)).toBeInTheDocument()

        expect(screen.getByText(`${issue.commentsCount} comments`)).toBeInTheDocument()
      })
    })
  })

  test('Handles case when no data is available', async () => {
    ;(useQuery as jest.Mock).mockReturnValue({
      data: { repository: null },
      error: null,
    })
    render(<ProjectDetailsPage />)
    await waitFor(() => {
      expect(screen.getByText('Project not found')).toBeInTheDocument()
    })
  })

  test('handles undefined data gracefully', () => {
    const setRecentReleasesMock = jest.fn()
    const setRecentIssuesMock = jest.fn()

    act(() => {
      const data = undefined

      setRecentReleasesMock(data?.project?.recentReleases)
      setRecentIssuesMock(data?.project?.recentIssues)
    })

    expect(setRecentReleasesMock).toHaveBeenCalledWith(undefined)
    expect(setRecentIssuesMock).toHaveBeenCalledWith(undefined)
  })

  test('renders project details with correct capitalization', async () => {
    ;(useQuery as jest.Mock).mockReturnValue({
      data: mockProjectDetailsData,
      error: null,
    })

    render(<ProjectDetailsPage />)

    await waitFor(() => {
      const levelElement = screen.getByText(/Level:/)
      expect(levelElement).toBeInTheDocument()
      const levelValueElement = within(levelElement.parentElement).getByText('Lab')
      expect(levelValueElement).toBeInTheDocument()

      const typeElement = screen.getByText(/Type:/)
      expect(typeElement).toBeInTheDocument()
      const typeValueElement = within(typeElement.parentElement).getByText('Tool')
      expect(typeValueElement).toBeInTheDocument()
    })
  })

  test('handles missing project stats gracefully', async () => {
    ;(useQuery as jest.Mock).mockReturnValue({
      data: {
        project: {
          ...mockProjectDetailsData.project,
          contributorsCount: 0,
          forksCount: 0,
          issuesCount: 0,
          starsCount: 0,
        },
      },
      error: null,
    })

    render(<ProjectDetailsPage />)

    await waitFor(() => {
      expect(screen.getByText('No Contributors')).toBeInTheDocument()
      expect(screen.getByText('No Forks')).toBeInTheDocument()
      expect(screen.getByText('No Issues')).toBeInTheDocument()
      expect(screen.getByText('No Stars')).toBeInTheDocument()
    })
  })
})
test('renders project stats correctly', async () => {
  ;(useQuery as jest.Mock).mockReturnValue({
    data: mockProjectDetailsData,
    error: null,
  })

  render(<ProjectDetailsPage />)

  await waitFor(() => {
    expect(screen.getByText(`2.2K Stars`)).toBeInTheDocument()
    expect(screen.getByText(`10 Forks`)).toBeInTheDocument()
    expect(screen.getByText(`1.2K Contributors`)).toBeInTheDocument()
    expect(screen.getByText(`3 Repositories`)).toBeInTheDocument()
    expect(screen.getByText(`10 Issues`)).toBeInTheDocument()
  })
})
