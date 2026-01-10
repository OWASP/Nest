import { useQuery } from '@apollo/client/react'
import { addToast } from '@heroui/toast'
import { act, fireEvent, screen, waitFor, within } from '@testing-library/react'
import { mockProjectDetailsData } from '@unit/data/mockProjectDetailsData'
import { render } from 'wrappers/testUtil'
import ProjectDetailsPage from 'app/projects/[projectKey]/page'

jest.mock('@apollo/client/react', () => ({
  ...jest.requireActual('@apollo/client/react'),
  useQuery: jest.fn(),
}))

jest.mock('@heroui/toast', () => ({
  addToast: jest.fn(),
}))

jest.mock('react-apexcharts', () => {
  return {
    __esModule: true,
    default: () => {
      return <div data-testid="mock-apexcharts">Mock ApexChart</div>
    },
  }
})

const mockRouter = {
  push: jest.fn(),
}

jest.mock('next/navigation', () => ({
  ...jest.requireActual('next/navigation'),
  useRouter: jest.fn(() => mockRouter),
  useParams: () => ({ projectKey: 'test-project' }),
}))

jest.mock('utils/env.client', () => ({
  IS_PROJECT_HEALTH_ENABLED: true,
}))

const mockError = {
  error: new Error('GraphQL error'),
}

describe('ProjectDetailsPage', () => {
  beforeEach(() => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: mockProjectDetailsData,
      loading: false,
      error: null,
    })
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  test('renders loading state', async () => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: null,
      error: null,
      loading: true,
    })

    render(<ProjectDetailsPage />)

    const loadingSpinner = screen.getAllByAltText('Loading indicator')
    await waitFor(() => {
      expect(loadingSpinner.length).toBeGreaterThan(0)
    })
  })

  test('renders project details when data is available', async () => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
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
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: null,
      error: mockError,
      loading: false,
    })

    render(<ProjectDetailsPage />)

    await waitFor(() => screen.getByText('Error loading project'))
    expect(screen.getByText('Error loading project')).toBeInTheDocument()
    expect(addToast).toHaveBeenCalledWith({
      description: 'An unexpected server error occurred.',
      title: 'Server Error',
      timeout: 5000,
      shouldShowTimeoutProgress: true,
      color: 'danger',
      variant: 'solid',
    })
  })

  test('toggles contributors list when show more/less is clicked', async () => {
    render(<ProjectDetailsPage />)
    await waitFor(() => {
      expect(screen.getByText('Contributor 12')).toBeInTheDocument()
      expect(screen.queryByText('Contributor 13')).not.toBeInTheDocument()
    })

    const showMoreButton = screen.getByRole('button', { name: /Show more/i })
    fireEvent.click(showMoreButton)

    await waitFor(() => {
      expect(screen.getByText('Contributor 13')).toBeInTheDocument()
      expect(screen.getByText('Contributor 14')).toBeInTheDocument()
      expect(screen.getByText('Contributor 15')).toBeInTheDocument()
    })

    const showLessButton = screen.getByRole('button', { name: /Show less/i })
    fireEvent.click(showLessButton)

    await waitFor(() => {
      expect(screen.queryByText('Contributor 13')).not.toBeInTheDocument()
    })
  })

  test('navigates to user page when contributor is clicked', async () => {
    render(<ProjectDetailsPage />)
    await waitFor(() => {
      expect(screen.getByText('Contributor 1')).toBeInTheDocument()
    })

    const contributorLink = screen.getByText('Contributor 1').closest('a')
    expect(contributorLink).toHaveAttribute('href', '/members/contributor1')
  })

  test('Recent issues are rendered correctly', async () => {
    render(<ProjectDetailsPage />)

    await waitFor(() => {
      const issues = mockProjectDetailsData.project.recentIssues

      for (const issue of issues) {
        expect(screen.getByText(issue.title)).toBeInTheDocument()
        expect(screen.getByText(issue.repositoryName)).toBeInTheDocument()
      }
    })
  })

  test('Displays health metrics section', async () => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: mockProjectDetailsData,
      error: null,
    })
    render(<ProjectDetailsPage />)
    await waitFor(() => {
      expect(screen.getByText(/Issues Trend/)).toBeInTheDocument()
      expect(screen.getByText(/Pull Requests Trend/)).toBeInTheDocument()
      expect(screen.getByText(/Stars Trend/)).toBeInTheDocument()
      expect(screen.getByText(/Forks Trend/)).toBeInTheDocument()
      expect(screen.getByText(/Days Since Last Commit and Release/)).toBeInTheDocument()
    })
  })

  test('Handles case when no data is available', async () => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: { project: null },
      error: null,
      loading: false,
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
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
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
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
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

  test('renders pull requests section correctly', async () => {
    render(<ProjectDetailsPage />)

    await waitFor(() => {
      expect(screen.getByText('Test Pull Request 1')).toBeInTheDocument()
      expect(screen.getByText('Test Pull Request 2')).toBeInTheDocument()
    })
  })

  test('renders milestones section correctly', async () => {
    render(<ProjectDetailsPage />)
    await waitFor(() => {
      const recentMilestones = mockProjectDetailsData.project.recentMilestones

      for (const milestone of recentMilestones) {
        expect(screen.getByText(milestone.title)).toBeInTheDocument()
        expect(screen.getByText(milestone.repositoryName)).toBeInTheDocument()
        expect(screen.getByText(`${milestone.openIssuesCount} open`)).toBeInTheDocument()
        expect(screen.getByText(`${milestone.closedIssuesCount} closed`)).toBeInTheDocument()
      }
    })
  })
  test('renders project stats correctly', async () => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: mockProjectDetailsData,
      error: null,
    })

    render(<ProjectDetailsPage />)

    await waitFor(() => {
      expect(screen.getByText('2.2K Stars')).toBeInTheDocument()
      expect(screen.getByText('10 Forks')).toBeInTheDocument()
      expect(screen.getByText('1.2K Contributors')).toBeInTheDocument()
      expect(screen.getByText('3 Repositories')).toBeInTheDocument()
      expect(screen.getByText('10 Issues')).toBeInTheDocument()
    })
  })
  test('renders project sponsor block correctly', async () => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: mockProjectDetailsData,
      error: null,
    })

    render(<ProjectDetailsPage />)

    await waitFor(() => {
      expect(screen.getByText('Want to become a sponsor?')).toBeInTheDocument()
      expect(screen.getByText(`Sponsor ${mockProjectDetailsData.project.name}`)).toBeInTheDocument()
    })
  })

  test('renders leaders block from entityLeaders', async () => {
    render(<ProjectDetailsPage />)
    await waitFor(() => {
      expect(screen.getByText('Leaders')).toBeInTheDocument()
      expect(screen.getByText('Alice')).toBeInTheDocument()
      expect(screen.getByText('Project Leader')).toBeInTheDocument()
    })
  })
})
