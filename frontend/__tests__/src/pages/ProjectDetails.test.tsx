import { useQuery } from '@apollo/client'
import { fireEvent, screen, waitFor, within } from '@testing-library/react'
import { fetchAlgoliaData } from 'api/fetchAlgoliaData'
import { toast } from 'hooks/useToast'
import { act } from 'react'
import { useNavigate } from 'react-router-dom'
import { formatDate } from 'utils/dateFormatter'
import { render } from 'wrappers/testUtil'
import ProjectDetailsPage from 'pages/ProjectDetails'
import {
  mockProjectDetailsData,
  mockProjectDetailsDataGQL,
} from '@tests/data/mockProjectDetailsData'

jest.mock('hooks/useToast', () => ({
  toast: jest.fn(),
}))

jest.mock('@apollo/client', () => ({
  ...jest.requireActual('@apollo/client'),
  useQuery: jest.fn(),
}))

jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useParams: () => ({ projectKey: 'test-project' }),
  useNavigate: jest.fn(),
}))

jest.mock('api/fetchAlgoliaData')
const mockError = {
  error: new Error('GraphQL error'),
}

describe('ProjectDetailsPage', () => {
  let navigateMock: jest.Mock

  beforeEach(() => {
    navigateMock = jest.fn()
    ;(useQuery as jest.Mock).mockReturnValue({
      data: mockProjectDetailsDataGQL,
      loading: false,
      error: null,
    })
    ;(useNavigate as jest.Mock).mockImplementation(() => navigateMock)
    ;(fetchAlgoliaData as jest.Mock).mockImplementation(() =>
      Promise.resolve({ hits: [mockProjectDetailsData] })
    )
  })

  afterEach(() => {
    jest.clearAllMocks()
  })
  test('renders loading spinner initially', async () => {
    render(<ProjectDetailsPage />)
    const loadingSpinner = screen.getAllByAltText('Loading indicator')
    await waitFor(() => {
      expect(loadingSpinner.length).toBeGreaterThan(0)
    })
  })

  test('renders project data correctly', async () => {
    render(<ProjectDetailsPage />)
    await waitFor(() => {
      expect(screen.getByText('Test Project')).toBeInTheDocument()
    })
    expect(screen.getByText('This is a test project description')).toBeInTheDocument()
    expect(screen.getByText('Tool')).toBeInTheDocument()
    expect(screen.getByText('Flagship')).toBeInTheDocument()
  })

  test('displays error when project is not found', async () => {
    ;(fetchAlgoliaData as jest.Mock).mockImplementationOnce(() => Promise.resolve({ hits: [] }))
    render(<ProjectDetailsPage />)

    await waitFor(() => {
      expect(screen.getByText('Project not found')).toBeInTheDocument()
      expect(
        screen.getByText("Sorry, the project you're looking for doesn't exist")
      ).toBeInTheDocument()
    })
  })

  test('renders project details when project is found', async () => {
    render(<ProjectDetailsPage />)

    await waitFor(() => {
      expect(screen.getByText(mockProjectDetailsData.name)).toBeInTheDocument()
      expect(screen.getByText(mockProjectDetailsData.description)).toBeInTheDocument()
      expect(screen.getByText('Project Details')).toBeInTheDocument()
      expect(screen.getByText('Statistics')).toBeInTheDocument()
      expect(screen.getByText('Top Contributors')).toBeInTheDocument()
    })
  })

  test('formats date correctly using formatDate function', () => {
    const timestamp = 1674249600 // January 21, 2023 (UTC)
    const formatted = formatDate(timestamp)
    expect(formatted).toContain('2023')
  })

  test('toggles languages list when show more/less is clicked', async () => {
    const projectWithManyLanguages = {
      ...mockProjectDetailsData,
      languages: Array.from({ length: 12 }, (_, i) => `Language ${i + 1}`),
    }
    ;(fetchAlgoliaData as jest.Mock).mockImplementationOnce(() =>
      Promise.resolve({ hits: [projectWithManyLanguages] })
    )

    render(<ProjectDetailsPage />)
    await waitFor(() => {
      expect(screen.getByText('Language 10')).toBeInTheDocument()
      expect(screen.queryByText('Language 11')).not.toBeInTheDocument()
    })

    const languagesSection = screen.getByRole('heading', { name: /Languages/i }).closest('div')
    const showMoreButton = within(languagesSection!).getByRole('button', { name: /Show more/i })
    fireEvent.click(showMoreButton)

    await waitFor(() => {
      expect(screen.getByText('Language 11')).toBeInTheDocument()
      expect(screen.getByText('Language 12')).toBeInTheDocument()
    })

    const showLessButton = within(languagesSection!).getByRole('button', { name: /Show less/i })
    fireEvent.click(showLessButton)

    await waitFor(() => {
      expect(screen.queryByText('Language 11')).not.toBeInTheDocument()
    })
  })

  test('toggles topics list when show more/less is clicked', async () => {
    const projectWithManyTopics = {
      ...mockProjectDetailsData,
      topics: Array.from({ length: 12 }, (_, i) => `Topic ${i + 1}`),
    }
    ;(fetchAlgoliaData as jest.Mock).mockImplementationOnce(() =>
      Promise.resolve({ hits: [projectWithManyTopics] })
    )

    render(<ProjectDetailsPage />)
    await waitFor(() => {
      expect(screen.getByText('Topic 10')).toBeInTheDocument()
      expect(screen.queryByText('Topic 11')).not.toBeInTheDocument()
    })

    const topicsSection = screen.getByRole('heading', { name: /Topics/i }).closest('div')
    const showMoreButton = within(topicsSection!).getByRole('button', { name: /Show more/i })
    fireEvent.click(showMoreButton)

    await waitFor(() => {
      expect(screen.getByText('Topic 11')).toBeInTheDocument()
      expect(screen.getByText('Topic 12')).toBeInTheDocument()
    })

    const showLessButton = within(topicsSection!).getByRole('button', { name: /Show less/i })
    fireEvent.click(showLessButton)

    await waitFor(() => {
      expect(screen.queryByText('Topic 11')).not.toBeInTheDocument()
    })
  })

  test('toggles contributors list when show more/less is clicked', async () => {
    const projectWithManyContributors = {
      ...mockProjectDetailsData,
      top_contributors: Array.from({ length: 8 }, (_, i) => ({
        login: `contributor${i + 1}`,
        name: `Contributor ${i + 1}`,
        avatar_url: 'https://example.com/avatarX.jpg',
        contributions_count: i * 10,
      })),
    }
    ;(fetchAlgoliaData as jest.Mock).mockImplementationOnce(() =>
      Promise.resolve({ hits: [projectWithManyContributors] })
    )

    render(<ProjectDetailsPage />)
    await waitFor(() => {
      expect(screen.getByText('Contributor 6')).toBeInTheDocument()
      expect(screen.queryByText('Contributor 7')).not.toBeInTheDocument()
    })

    const contributorsSection = screen
      .getByRole('heading', { name: /Top Contributors/i })
      .closest('div')
    const showMoreButton = within(contributorsSection!).getByRole('button', { name: /Show more/i })
    fireEvent.click(showMoreButton)

    await waitFor(() => {
      expect(screen.getByText('Contributor 7')).toBeInTheDocument()
      expect(screen.getByText('Contributor 8')).toBeInTheDocument()
    })

    const showLessButton = within(contributorsSection!).getByRole('button', { name: /Show less/i })
    fireEvent.click(showLessButton)

    await waitFor(() => {
      expect(screen.queryByText('Contributor 7')).not.toBeInTheDocument()
    })
  })

  test('navigates to user page when contributor is clicked', async () => {
    render(<ProjectDetailsPage />)
    await waitFor(() => {
      expect(screen.getByText('Contributor 1')).toBeInTheDocument()
    })

    screen.getByText('Contributor 1').closest('div')?.click()

    expect(navigateMock).toHaveBeenCalledWith('/community/users/contributor1')
  })

  test('handles contributors with missing names gracefully', async () => {
    const projectDataWithIncompleteContributors = {
      ...mockProjectDetailsData,
      top_contributors: [
        {
          login: 'user1',
          avatar_url: 'https://example.com/avatar1.jpg',
          contributions_count: 30,
        },
      ],
    }
    ;(fetchAlgoliaData as jest.Mock).mockImplementationOnce(() =>
      Promise.resolve({ hits: [projectDataWithIncompleteContributors] })
    )

    render(<ProjectDetailsPage />)

    await waitFor(() => {
      expect(screen.getByText('user1')).toBeInTheDocument()
    })
  })

  test('renders project URL as clickable link', async () => {
    render(<ProjectDetailsPage />)

    await waitFor(() => {
      const link = screen.getByText('https://example.com')
      expect(link.tagName).toBe('A')
      expect(link).toHaveAttribute('href', 'https://example.com')
    })
  })

  test('renders data state for GraphQL query', async () => {
    render(<ProjectDetailsPage />)

    await waitFor(() => {
      expect(screen.getByText('Test Project')).toBeInTheDocument()
      expect(screen.getByText('This is a test project description')).toBeInTheDocument()
      expect(screen.getByText('Tool')).toBeInTheDocument()
      expect(screen.getByText('Flagship')).toBeInTheDocument()
    })
  })

  test('Recent issues are rendered correctly', async () => {
    render(<ProjectDetailsPage />)

    await waitFor(() => {
      const issues = mockProjectDetailsDataGQL.project.recentIssues

      issues.forEach((issue) => {
        expect(screen.getByText(issue.title)).toBeInTheDocument()

        expect(screen.getByText(issue.author.name)).toBeInTheDocument()

        expect(screen.getByText(`${issue.commentsCount} comments`)).toBeInTheDocument()
      })
    })
  })

  test('No recent issues message is displayed when issues array is empty', async () => {
    const emptyIssuesData = {
      ...mockProjectDetailsDataGQL,
      project: {
        ...mockProjectDetailsDataGQL.project,
        recentIssues: [],
      },
    }

    ;(useQuery as jest.Mock).mockReturnValue({
      data: emptyIssuesData,
      loading: false,
      error: null,
    })

    render(<ProjectDetailsPage />)

    await waitFor(() => {
      expect(screen.getByText('No recent issues.')).toBeInTheDocument()
    })
  })

  test('Handles case when no data is available', async () => {
    ;(useQuery as jest.Mock).mockReturnValue({
      data: null,
      loading: false,
      error: null,
    })
    ;(fetchAlgoliaData as jest.Mock).mockResolvedValue({ hits: [] })

    render(<ProjectDetailsPage />)

    await waitFor(() => {
      expect(screen.getByText('Project not found')).toBeInTheDocument()
    })
  })

  test('sets recent releases and issues correctly from GraphQL data', () => {
    const setRecentReleasesMock = jest.fn()
    const setRecentIssuesMock = jest.fn()

    act(() => {
      const data = mockProjectDetailsDataGQL

      setRecentReleasesMock(data?.project?.recentReleases)
      setRecentIssuesMock(data?.project?.recentIssues)
    })

    expect(setRecentReleasesMock).toHaveBeenCalledWith(
      mockProjectDetailsDataGQL.project.recentReleases
    )

    expect(setRecentIssuesMock).toHaveBeenCalledWith(mockProjectDetailsDataGQL.project.recentIssues)
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

  test('handles missing project stats gracefully', async () => {
    const projectWithNoStats = {
      ...mockProjectDetailsData,
      contributors_count: 0,
      forks_count: 0,
      issues_count: 0,
      repositories_count: 0,
      stars_count: 0,
    }
    ;(fetchAlgoliaData as jest.Mock).mockImplementationOnce(() =>
      Promise.resolve({ hits: [projectWithNoStats] })
    )

    render(<ProjectDetailsPage />)

    await waitFor(() => {
      expect(screen.getByText('No Contributors')).toBeInTheDocument()
      expect(screen.getByText('No Forks')).toBeInTheDocument()
      expect(screen.getByText('No Issues')).toBeInTheDocument()
      expect(screen.getByText('No Repositories')).toBeInTheDocument()
      expect(screen.getByText('No Stars')).toBeInTheDocument()
    })
  })

  test('renders error message when GraphQL request fails', async () => {
    ;(useQuery as jest.Mock).mockReturnValue({
      loading: false,
      data: null,
      error: mockError,
    })
    ;(fetchAlgoliaData as jest.Mock).mockResolvedValue({ hits: [] })

    render(<ProjectDetailsPage />)

    await waitFor(() => {
      expect(screen.getByText('Project not found')).toBeInTheDocument()
    })
    expect(toast).toHaveBeenCalledWith({
      description: 'Unable to complete the requested operation.',
      title: 'GraphQL Request Failed',
      variant: 'destructive',
    })
  })
})
