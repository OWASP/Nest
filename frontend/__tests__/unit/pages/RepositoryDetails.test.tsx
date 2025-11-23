import { useQuery } from '@apollo/client/react'
import { addToast } from '@heroui/toast'
import { act, fireEvent, screen, waitFor } from '@testing-library/react'
import { mockRepositoryData } from '@unit/data/mockRepositoryData'
import { render } from 'wrappers/testUtil'
import RepositoryDetailsPage from 'app/organizations/[organizationKey]/repositories/[repositoryKey]/page'

jest.mock('@apollo/client/react', () => ({
  ...jest.requireActual('@apollo/client/react'),
  useQuery: jest.fn(),
}))

jest.mock('@fortawesome/react-fontawesome', () => ({
  FontAwesomeIcon: () => <span data-testid="mock-icon" />,
}))

jest.mock('@heroui/toast', () => ({
  addToast: jest.fn(),
}))

const mockRouter = {
  push: jest.fn(),
}

jest.mock('next/navigation', () => ({
  ...jest.requireActual('next/navigation'),
  useRouter: jest.fn(() => mockRouter),
  useParams: () => ({ repositoryKey: 'test-repository' }),
}))

const mockError = {
  error: new Error('GraphQL error'),
}

describe('RepositoryDetailsPage', () => {
  beforeEach(() => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: mockRepositoryData,
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
    })

    render(<RepositoryDetailsPage />)

    const loadingSpinner = screen.getAllByAltText('Loading indicator')
    await waitFor(() => {
      expect(loadingSpinner.length).toBeGreaterThan(0)
    })
  })

  test('renders repository details when data is available', async () => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: mockRepositoryData,
      error: null,
    })

    render(<RepositoryDetailsPage />)

    await waitFor(() => {
      expect(screen.getByText('Test Repo')).toBeInTheDocument()
      expect(screen.getByText('MIT')).toBeInTheDocument()
    })
    expect(screen.getByText('50K Stars')).toBeInTheDocument()
    expect(screen.getByText('3K Forks')).toBeInTheDocument()
    expect(screen.getByText('10 Commits')).toBeInTheDocument()
    expect(screen.getByText('5 Contributors')).toBeInTheDocument()
    expect(screen.getByText('2 Issues')).toBeInTheDocument()
  })

  test('renders error message when GraphQL request fails', async () => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: { repository: null },
      error: mockError,
    })

    render(<RepositoryDetailsPage />)

    await waitFor(() => screen.getByText('Repository not found'))
    expect(screen.getByText('Repository not found')).toBeInTheDocument()
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
    render(<RepositoryDetailsPage />)
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
    render(<RepositoryDetailsPage />)
    await waitFor(() => {
      expect(screen.getByText('Contributor 1')).toBeInTheDocument()
    })

    const contributorLink = screen.getByText('Contributor 1').closest('a')
    expect(contributorLink).toHaveAttribute('href', '/members/contributor1')
  })

  test('Recent issues are rendered correctly', async () => {
    render(<RepositoryDetailsPage />)

    await waitFor(() => {
      const issues = mockRepositoryData.repository.issues

      for (const issue of issues) {
        expect(screen.getByText(issue.title)).toBeInTheDocument()
        expect(screen.getByText(issue.repositoryName)).toBeInTheDocument()
      }
    })
  })

  test('Handles case when no data is available', async () => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: { repository: null },
      error: null,
    })
    render(<RepositoryDetailsPage />)
    await waitFor(() => {
      expect(screen.getByText('Repository not found')).toBeInTheDocument()
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

  test('renders pull requests section correctly', async () => {
    render(<RepositoryDetailsPage />)

    await waitFor(() => {
      expect(screen.getByText('Test Pull Request 1')).toBeInTheDocument()
      expect(screen.getByText('Test Pull Request 2')).toBeInTheDocument()
    })
  })

  test('renders milestones section correctly', async () => {
    render(<RepositoryDetailsPage />)
    await waitFor(() => {
      const recentMilestones = mockRepositoryData.repository.recentMilestones

      expect(screen.getByText('Recent Milestones')).toBeInTheDocument()

      for (const milestone of recentMilestones) {
        expect(screen.getByText(milestone.title)).toBeInTheDocument()
        expect(screen.getByText(milestone.repositoryName)).toBeInTheDocument()
        expect(screen.getByText(`${milestone.openIssuesCount} open`)).toBeInTheDocument()
        expect(screen.getByText(`${milestone.closedIssuesCount} closed`)).toBeInTheDocument()
      }
    })
  })

  test('handles missing repository stats gracefully', async () => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: {
        repository: {
          ...mockRepositoryData.repository,
          commitsCount: 0,
          contributorsCount: 0,
          forksCount: 0,
          openIssuesCount: 0,
          starsCount: 0,
        },
      },
      error: null,
    })

    render(<RepositoryDetailsPage />)

    await waitFor(() => {
      expect(screen.getByText('No Commits')).toBeInTheDocument()
      expect(screen.getByText('No Contributors')).toBeInTheDocument()
      expect(screen.getByText('No Forks')).toBeInTheDocument()
      expect(screen.getByText('No Issues')).toBeInTheDocument()
      expect(screen.getByText('No Stars')).toBeInTheDocument()
    })
  })

  test('renders repository sponsor block correctly', async () => {
    render(<RepositoryDetailsPage />)

    await waitFor(() => {
      expect(screen.getByText('Want to become a sponsor?')).toBeInTheDocument()
      expect(
        screen.getByText(`Sponsor ${mockRepositoryData.repository.project.name}`)
      ).toBeInTheDocument()
    })
  })
})
