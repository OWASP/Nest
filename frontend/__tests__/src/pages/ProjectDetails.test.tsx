import { within } from '@testing-library/dom'
import { screen, waitFor, fireEvent } from '@testing-library/react'
import { fetchAlgoliaData } from 'api/fetchAlgoliaData'
import { useNavigate } from 'react-router-dom'
import { render } from 'wrappers/testUtil'
import ProjectDetailsPage, { formatDate } from 'pages/ProjectDetails'
import { mockProjectDetailsData } from '@tests/data/mockProjectDetailsData'
jest.mock('api/fetchAlgoliaData')

jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useParams: () => ({ projectKey: 'test-project' }),
  useNavigate: jest.fn(),
}))

describe('ProjectDetailsPage', () => {
  let navigateMock: jest.Mock

  beforeEach(() => {
    navigateMock = jest.fn()
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
    expect(screen.getByText('OWASP')).toBeInTheDocument()
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
      expect(screen.getByText('Recent Issues')).toBeInTheDocument()
      expect(screen.getByText('Recent Releases')).toBeInTheDocument()
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

  test('displays "No recent issues" when there are no issues', async () => {
    const projectNoIssues = {
      ...mockProjectDetailsData,
      issues: [],
    }
    ;(fetchAlgoliaData as jest.Mock).mockImplementationOnce(() =>
      Promise.resolve({ hits: [projectNoIssues] })
    )

    render(<ProjectDetailsPage />)
    await waitFor(() => {
      expect(screen.getByText('No recent issues.')).toBeInTheDocument()
    })
  })

  test('displays "No recent releases" when there are no releases', async () => {
    const projectNoReleases = {
      ...mockProjectDetailsData,
      releases: [],
    }
    ;(fetchAlgoliaData as jest.Mock).mockImplementationOnce(() =>
      Promise.resolve({ hits: [projectNoReleases] })
    )

    render(<ProjectDetailsPage />)
    await waitFor(() => {
      expect(screen.getByText('No recent releases.')).toBeInTheDocument()
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
})
