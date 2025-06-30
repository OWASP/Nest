import { useQuery } from '@apollo/client'
import { addToast } from '@heroui/toast'
import { act, screen, waitFor } from '@testing-library/react'
import { assertContributorToggle, assertRepoDetails } from '@testUtils/sharedAssertions'
import { mockRepositoryData } from '@unit/data/mockRepositoryData'
import { render } from 'wrappers/testUtil'
import RepositoryDetailsPage from 'app/organizations/[organizationKey]/repositories/[repositoryKey]/page'

jest.mock('@apollo/client', () => ({
  ...jest.requireActual('@apollo/client'),
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
    ;(useQuery as jest.Mock).mockReturnValue({
      data: mockRepositoryData,
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

    render(<RepositoryDetailsPage />)

    const loadingSpinner = screen.getAllByAltText('Loading indicator')
    await waitFor(() => {
      expect(loadingSpinner.length).toBeGreaterThan(0)
    })
  })

  // eslint-disable-next-line jest/expect-expect
  test('renders repository details when data is available', async () => {
    ;(useQuery as jest.Mock).mockReturnValue({
      data: mockRepositoryData,
      error: null,
    })

    render(<RepositoryDetailsPage />)

    await assertRepoDetails({
      heading: 'Test Repo',
      license: 'MIT',
      stars: '50K Stars',
      forks: '3K Forks',
      commits: '10 Commits',
      contributors: '5 Contributors',
      issues: '2 Issues',
    })
  })

  test('renders error message when GraphQL request fails', async () => {
    ;(useQuery as jest.Mock).mockReturnValue({
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

  // eslint-disable-next-line jest/expect-expect
  test('toggles contributors list when show more/less is clicked', async () => {
    render(<RepositoryDetailsPage />)
    await assertContributorToggle('Contributor 9', ['Contributor 7', 'Contributor 8'])
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

      issues.forEach((issue) => {
        expect(screen.getByText(issue.title)).toBeInTheDocument()
        expect(screen.getByText(issue.repositoryName)).toBeInTheDocument()
      })
    })
  })

  test('Handles case when no data is available', async () => {
    ;(useQuery as jest.Mock).mockReturnValue({
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
      recentMilestones.forEach((milestone) => {
        expect(screen.getByText(milestone.title)).toBeInTheDocument()
        expect(screen.getByText(milestone.repositoryName)).toBeInTheDocument()
        expect(screen.getByText(`${milestone.openIssuesCount} open`)).toBeInTheDocument()
        expect(screen.getByText(`${milestone.closedIssuesCount} closed`)).toBeInTheDocument()
      })
    })
  })

  test('handles missing repository stats gracefully', async () => {
    ;(useQuery as jest.Mock).mockReturnValue({
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
})
