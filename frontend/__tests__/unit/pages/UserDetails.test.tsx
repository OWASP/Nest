import { useQuery } from '@apollo/client'
import { screen, waitFor } from '@testing-library/react'
import { mockUserDetailsData } from '@unit/data/mockUserDetails'
import { useNavigate } from 'react-router-dom'
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

jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useParams: () => ({ userKey: 'test-user' }),
  useNavigate: jest.fn(),
}))

const mockError = {
  error: new Error('GraphQL error'),
}

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
    expect(screen.getByText(`Test @User`)).toBeInTheDocument()
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

      const followingCount = screen.getByText('5 Following')
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

      const userBio = screen.getByText('Test @User')
      expect(userBio).toBeInTheDocument()
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
})
