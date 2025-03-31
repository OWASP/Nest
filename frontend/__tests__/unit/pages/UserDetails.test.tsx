import { useQuery } from '@apollo/client'
import { screen, waitFor } from '@testing-library/react'
import { mockUserDetailsData } from '@unit/data/mockUserDetails'
import { useNavigate } from 'react-router-dom'
import { drawContributions, fetchHeatmapData } from 'utils/helpers/githubHeatmap'
import { render } from 'wrappers/testUtil'
import { toaster } from 'components/ui/toaster'
import UserDetailsPage from 'pages/UserDetails'
import '@testing-library/jest-dom'

jest.mock('@apollo/client', () => ({
  ...jest.requireActual('@apollo/client'),
  useQuery: jest.fn(),
}))

jest.mock('components/ui/toaster', () => ({
  toaster: {
    create: jest.fn(),
  },
}))

jest.mock('@fortawesome/react-fontawesome', () => ({
  FontAwesomeIcon: () => <span data-testid="mock-icon" />,
}))

jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useParams: () => ({ userKey: 'test-user' }),
  useNavigate: jest.fn(),
}))

const mockError = {
  error: new Error('GraphQL error'),
}

jest.mock('utils/helpers/githubHeatmap', () => ({
  fetchHeatmapData: jest.fn(),
  drawContributions: jest.fn(() => {}),
}))

describe('UserDetailsPage', () => {
  let navigateMock: jest.Mock

  beforeEach(() => {
    navigateMock = jest.fn()
    ;(useQuery as jest.Mock).mockReturnValue({
      data: mockUserDetailsData,
      loading: false,
      error: null,
    })
    ;(useNavigate as jest.Mock).mockImplementation(() => navigateMock)
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
      data: mockUserDetailsData,
      error: null,
      loading: false,
    })

    // Wait for the loading state to finish
    render(<UserDetailsPage />)

    await waitFor(() => {
      expect(screen.queryByAltText('Loading indicator')).not.toBeInTheDocument()
    })

    expect(screen.getByText('Test User')).toBeInTheDocument()
    expect(screen.getByText('Statistics')).toBeInTheDocument()
    expect(screen.getByText('Contribution Heatmap')).toBeInTheDocument()
    expect(screen.getByText('Test Company')).toBeInTheDocument()
    expect(screen.getByText('Test Location')).toBeInTheDocument()
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

      const issueComments = screen.getByText('5 comments')
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

  test('renders user summary section correctly', async () => {
    ;(useQuery as jest.Mock).mockReturnValue({
      data: mockUserDetailsData,
      error: null,
    })

    render(<UserDetailsPage />)

    await waitFor(() => {
      const userName = screen.getByText('Test User')
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
      data: { repository: null },
      error: mockError,
    })

    render(<UserDetailsPage />)

    await waitFor(() => screen.getByText('User not found'))
    expect(toaster.create).toHaveBeenCalledWith({
      description: 'Unable to complete the requested operation.',
      title: 'GraphQL Request Failed',
      type: 'error',
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
      expect(screen.getByText('Test User')).toBeInTheDocument()
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
      ...mockUserDetailsData,
      user: { ...mockUserDetailsData.user, issues: [] },
    }
    ;(useQuery as jest.Mock).mockReturnValue({
      data: noIssuesData,
      loading: false,
      error: null,
    })

    render(<UserDetailsPage />)
    await waitFor(() => {
      expect(screen.getByText('Recent Issues')).toBeInTheDocument()
      expect(screen.queryByText('Test Issue')).not.toBeInTheDocument()
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

  test('renders statistics with zero values correctly', async () => {
    const zeroStatsData = {
      ...mockUserDetailsData,
      user: {
        ...mockUserDetailsData.user,
        followersCount: 0,
        followingCount: 0,
        publicRepositoriesCount: 0,
        issuesCount: 0,
        releasesCount: 0,
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
      expect(screen.getByText('No Issues')).toBeInTheDocument()
      expect(screen.getByText('No Releases')).toBeInTheDocument()
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
      expect(screen.getAllByText('Not provided').length).toBe(3) // Email, Company, Location
    })
  })
})
