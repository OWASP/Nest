import { useQuery } from '@apollo/client'
import { addToast } from '@heroui/toast'
import { screen, waitFor } from '@testing-library/react'
import { mockUserDetailsData } from '@unit/data/mockUserDetails'
import { render } from 'wrappers/testUtil'
import '@testing-library/jest-dom'
import UserDetailsPage from 'app/members/[memberKey]/page'
import { drawContributions, fetchHeatmapData } from 'utils/helpers/githubHeatmap'

// Mock Apollo Client
jest.mock('@apollo/client', () => ({
  ...jest.requireActual('@apollo/client'),
  useQuery: jest.fn(),
}))

// Mock FontAwesome
jest.mock('@fortawesome/react-fontawesome', () => ({
  FontAwesomeIcon: () => <span data-testid="mock-icon" />,
}))

const mockRouter = {
  push: jest.fn(),
}

const mockError = {
  error: new Error('GraphQL error'),
}

jest.mock('next/navigation', () => ({
  ...jest.requireActual('next/navigation'),
  useRouter: jest.fn(() => mockRouter),
  useParams: () => ({ userKey: 'test-user' }),
}))

// Mock GitHub heatmap utilities
jest.mock('utils/helpers/githubHeatmap', () => ({
  fetchHeatmapData: jest.fn(),
  drawContributions: jest.fn(() => {}),
}))

jest.mock('@heroui/toast', () => ({
  addToast: jest.fn(),
}))

describe('UserDetailsPage', () => {
  beforeEach(() => {
    ;(useQuery as jest.Mock).mockReturnValue({
      data: mockUserDetailsData,
      loading: false,
      error: null,
    })
    ;(fetchHeatmapData as jest.Mock).mockResolvedValue({
      contributions: { years: [{ year: '2023' }] },
    })
    ;(drawContributions as jest.Mock).mockImplementation(() => {})
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  test('renders loading state', async () => {
    ;(useQuery as jest.Mock).mockReturnValue({
      data: null,
      error: null,
    })

    render(<UserDetailsPage />)
    const loadingSpinner = screen.getAllByAltText('Loading indicator')
    await waitFor(() => {
      expect(loadingSpinner.length).toBeGreaterThan(0)
    })
  })

  test('renders user details', async () => {
    ;(useQuery as jest.Mock).mockReturnValue({
      data: {
        ...mockUserDetailsData,
        user: { ...mockUserDetailsData.user, recentIssues: {} },
      },
      error: null,
      loading: false,
    })

    render(<UserDetailsPage />)

    await waitFor(() => {
      expect(screen.queryByAltText('Loading indicator')).not.toBeInTheDocument()
    })

    const title = screen.getByRole('heading', { name: 'Test User' })
    expect(title).toBeInTheDocument()
    expect(screen.getByText('Statistics')).toBeInTheDocument()
    expect(screen.getByText('Contribution Heatmap')).toBeInTheDocument()
    expect(screen.getByText('Test Company')).toBeInTheDocument()
    expect(screen.getByText('Test Location')).toBeInTheDocument()
    expect(screen.getByText('10 Followers')).toBeInTheDocument()
    expect(screen.getByText('5 Followings')).toBeInTheDocument()
    expect(screen.getByText('3 Repositories')).toBeInTheDocument()
    expect(screen.getByText('100 Contributions')).toBeInTheDocument()
  })

  test('renders recent issues correctly', async () => {
    ;(useQuery as jest.Mock).mockReturnValue({
      data: mockUserDetailsData,
      error: null,
      loading: false,
    })

    render(<UserDetailsPage />)

    await waitFor(() => {
      const recentIssuesTitle = screen.getByText('Recent Issues')
      expect(recentIssuesTitle).toBeInTheDocument()

      const issueTitle = screen.getByText('Test Issue')
      expect(issueTitle).toBeInTheDocument()

      const issueComments = screen.getByText('Test Repo')
      expect(issueComments).toBeInTheDocument()
    })
  })

  test('renders recent pull requests correctly', async () => {
    ;(useQuery as jest.Mock).mockReturnValue({
      data: mockUserDetailsData,
      error: null,
      loading: false,
    })

    render(<UserDetailsPage />)

    await waitFor(() => {
      const pullRequestsTitle = screen.getByText('Recent Pull Requests')
      expect(pullRequestsTitle).toBeInTheDocument()

      const pullRequestTitle = screen.getByText('Test Pull Request')
      expect(pullRequestTitle).toBeInTheDocument()
    })
  })

  test('renders recent releases correctly', async () => {
    ;(useQuery as jest.Mock).mockReturnValue({
      data: mockUserDetailsData,
      error: null,
      loading: false,
    })
    render(<UserDetailsPage />)
    await waitFor(() => {
      const releasesTitle = screen.getByText('Recent Releases')
      expect(releasesTitle).toBeInTheDocument()
      const releases = mockUserDetailsData.recentReleases
      releases.forEach((release) => {
        expect(screen.getByText(release.name)).toBeInTheDocument()
        expect(screen.getByText(release.repositoryName)).toBeInTheDocument()
      })
    })
  })

  test('renders recent milestones correctly', async () => {
    ;(useQuery as jest.Mock).mockReturnValue({
      data: mockUserDetailsData,
      error: null,
      loading: false,
    })

    render(<UserDetailsPage />)

    await waitFor(() => {
      const milestonesTitle = screen.getByText('Recent Milestones')
      expect(milestonesTitle).toBeInTheDocument()
      const milestones = mockUserDetailsData.recentMilestones
      milestones.forEach((milestone) => {
        expect(screen.getByText(milestone.title)).toBeInTheDocument()
        expect(screen.getByText(milestone.repositoryName)).toBeInTheDocument()
        expect(screen.getByText(`${milestone.openIssuesCount} open`)).toBeInTheDocument()
        expect(screen.getByText(`${milestone.closedIssuesCount} closed`)).toBeInTheDocument()
      })
    })
  })

  test('renders repositories section correctly', async () => {
    ;(useQuery as jest.Mock).mockReturnValue({
      data: mockUserDetailsData,
      error: null,
      loading: false,
    })

    render(<UserDetailsPage />)

    await waitFor(() => {
      const repositoriesTitle = screen.getByText('Repositories')
      expect(repositoriesTitle).toBeInTheDocument()

      const repositoryName = screen.getByText('Test Repo')
      expect(repositoryName).toBeInTheDocument()

      const starsCount = screen.getByText('10')
      expect(starsCount).toBeInTheDocument()

      const forksCount = screen.getByText('5')
      expect(forksCount).toBeInTheDocument()
    })
  })

  test('renders statistics section correctly', async () => {
    ;(useQuery as jest.Mock).mockReturnValue({
      data: mockUserDetailsData,
      error: null,
      loading: false,
    })

    render(<UserDetailsPage />)

    await waitFor(() => {
      const statisticsTitle = screen.getByText('Statistics')
      expect(statisticsTitle).toBeInTheDocument()

      const followersCount = screen.getByText('10 Followers')
      expect(followersCount).toBeInTheDocument()

      const followingCount = screen.getByText('5 Followings')
      expect(followingCount).toBeInTheDocument()

      const repositoriesCount = screen.getByText('3 Repositories')
      expect(repositoriesCount).toBeInTheDocument()

      const contributionsCount = screen.getByText('100 Contributions')
      expect(contributionsCount).toBeInTheDocument()
    })
  })

  test('renders contribution heatmap correctly', async () => {
    ;(useQuery as jest.Mock).mockReturnValue({
      data: mockUserDetailsData,
      error: null,
    })

    render(<UserDetailsPage />)

    await waitFor(() => {
      const heatmapTitle = screen.getByText('Contribution Heatmap')
      expect(heatmapTitle).toBeInTheDocument()
    })
  })

  test('handles contribution heatmap loading error correctly', async () => {
    ;(useQuery as jest.Mock).mockReturnValue({
      data: mockUserDetailsData,
      error: null,
    })
    ;(fetchHeatmapData as jest.Mock).mockResolvedValue(null)

    render(<UserDetailsPage />)

    await waitFor(() => {
      const heatmapTitle = screen.queryByText('Contribution Heatmap')
      expect(heatmapTitle).not.toBeInTheDocument()
    })
  })

  test('renders user summary section correctly', async () => {
    ;(useQuery as jest.Mock).mockReturnValue({
      data: mockUserDetailsData,
      error: null,
    })

    render(<UserDetailsPage />)

    await waitFor(() => {
      const userName = screen.getByRole('heading', { name: 'Test User' })
      expect(userName).toBeInTheDocument()
    })
  })

  test('displays contact information elements', async () => {
    ;(useQuery as jest.Mock).mockReturnValue({
      data: mockUserDetailsData,
      error: null,
    })

    render(<UserDetailsPage />)

    await waitFor(() => {
      const emailElement = screen.getByText('testuser@example.com')
      expect(emailElement).toBeInTheDocument()

      const companyElement = screen.getByText('Test Company')
      expect(companyElement).toBeInTheDocument()

      const locationElement = screen.getByText('Test Location')
      expect(locationElement).toBeInTheDocument()
    })
  })

  test('renders error message when GraphQL request fails', async () => {
    ;(useQuery as jest.Mock).mockReturnValue({
      data: null,
      error: mockError,
    })

    render(<UserDetailsPage />)

    await waitFor(() => {
      expect(screen.getByText('User not found')).toBeInTheDocument()
    })

    expect(addToast).toHaveBeenCalledWith({
      description: 'An unexpected server error occurred.',
      title: 'Server Error',
      timeout: 5000,
      shouldShowTimeoutProgress: true,
      color: 'danger',
      variant: 'solid',
    })
  })

  test('renders user summary with no bio', async () => {
    const noBioData = {
      ...mockUserDetailsData,
      user: { ...mockUserDetailsData.user, bio: '' },
    }
    ;(useQuery as jest.Mock).mockReturnValue({
      data: noBioData,
      loading: false,
      error: null,
    })

    render(<UserDetailsPage />)
    await waitFor(() => {
      const userName = screen.getByRole('heading', { name: 'Test User' })
      expect(userName).toBeInTheDocument()
      expect(screen.queryByText('Test @User')).not.toBeInTheDocument()
    })
  })

  test('renders bio with multiple GitHub mentions correctly', async () => {
    const multiMentionData = {
      ...mockUserDetailsData,
      user: { ...mockUserDetailsData.user, bio: 'Test @User1 and @User2!' },
    }
    ;(useQuery as jest.Mock).mockReturnValue({
      data: multiMentionData,
      loading: false,
      error: null,
    })

    render(<UserDetailsPage />)
    await waitFor(() => {
      const user1Link = screen.getByText('@User1')
      const user2Link = screen.getByText('@User2')
      expect(user1Link).toHaveAttribute('href', 'https://github.com/User1')
      expect(user2Link).toHaveAttribute('href', 'https://github.com/User2')
    })
  })

  test('handles no recent issues gracefully', async () => {
    const noIssuesData = {
      user: { ...mockUserDetailsData.user, recentIssues: {} },
    }
    ;(useQuery as jest.Mock).mockReturnValue({
      data: noIssuesData,
      loading: false,
      error: null,
    })

    render(<UserDetailsPage />)
    await waitFor(() => {
      expect(screen.getByText('Recent Issues')).toBeInTheDocument()
      expect(screen.getByText('No recent releases.')).toBeInTheDocument()
    })
  })

  test('handles no recent pull requests gracefully', async () => {
    const noPullsData = {
      ...mockUserDetailsData,
      recentPullRequests: [],
    }
    ;(useQuery as jest.Mock).mockReturnValue({
      data: noPullsData,
      loading: false,
      error: null,
    })

    render(<UserDetailsPage />)
    await waitFor(() => {
      expect(screen.getByText('Recent Pull Requests')).toBeInTheDocument()
      expect(screen.queryByText('Test Pull Request')).not.toBeInTheDocument()
    })
  })

  test('handles no recent releases gracefully', async () => {
    const noReleasesData = {
      ...mockUserDetailsData,
      recentReleases: [],
    }
    ;(useQuery as jest.Mock).mockReturnValue({
      data: noReleasesData,
      loading: false,
      error: null,
    })
    render(<UserDetailsPage />)
    await waitFor(() => {
      expect(screen.getByText('Recent Releases')).toBeInTheDocument()
      expect(screen.queryByText('Test v1.0.0')).not.toBeInTheDocument()
    })
  })

  test('handles no recent milestones gracefully', async () => {
    const noMilestonesData = {
      ...mockUserDetailsData,
      recentMilestones: [],
    }
    ;(useQuery as jest.Mock).mockReturnValue({
      data: noMilestonesData,
      loading: false,
      error: null,
    })
    render(<UserDetailsPage />)
    await waitFor(() => {
      expect(screen.getByText('Recent Milestones')).toBeInTheDocument()
      expect(screen.queryByText('v2.0.0 Release')).not.toBeInTheDocument()
    })
  })

  test('renders statistics with zero values correctly', async () => {
    const zeroStatsData = {
      ...mockUserDetailsData,
      user: {
        ...mockUserDetailsData.user,
        contributionsCount: 0,
        followersCount: 0,
        followingCount: 0,
        publicRepositoriesCount: 0,
      },
    }
    ;(useQuery as jest.Mock).mockReturnValue({
      data: zeroStatsData,
      loading: false,
      error: null,
    })

    render(<UserDetailsPage />)
    await waitFor(() => {
      expect(screen.getByText('No Followers')).toBeInTheDocument()
      expect(screen.getByText('No Followings')).toBeInTheDocument()
      expect(screen.getByText('No Repositories')).toBeInTheDocument()
      expect(screen.getByText('No Contributions')).toBeInTheDocument()
    })
  })

  test('renders user details with missing optional fields', async () => {
    const minimalData = {
      ...mockUserDetailsData,
      user: {
        ...mockUserDetailsData.user,
        email: '',
        company: '',
        location: '',
      },
    }
    ;(useQuery as jest.Mock).mockReturnValue({
      data: minimalData,
      loading: false,
      error: null,
    })

    render(<UserDetailsPage />)
    await waitFor(() => {
      expect(screen.getAllByText('N/A').length).toBe(3)
    })
  })
})
