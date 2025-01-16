import { screen, waitFor } from '@testing-library/react'
import { fetchAlgoliaData } from 'api/fetchAlgoliaData'
import { render } from 'wrappers/testUtil'
import ProjectDetailsPage from 'pages/ProjectDetails'

jest.mock('api/fetchAlgoliaData')

jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useParams: () => ({
    projectKey: 'test-project',
  }),
}))

const mockProjectData = {
  idx_name: 'Test Project',
  idx_description: 'This is a test project description',
  idx_type: 'Tool',
  idx_level: 'Flagship',
  idx_organizations: 'OWASP',
  idx_leaders: ['Leader 1', 'Leader 2'],
  idx_updated_at: 1625097600,
  idx_url: 'https://example.com',
  idx_contributors_count: 50,
  idx_forks_count: 20,
  idx_stars_count: 100,
  idx_issues_count: 10,
  idx_repositories_count: 2,
  idx_summary: 'This is a summary of the test project.',
  idx_languages: Array.from({ length: 15 }, (_, i) => `Language ${i + 1}`),
  idx_topics: Array.from({ length: 15 }, (_, i) => `Topic ${i + 1}`),
  idx_top_contributors: Array.from({ length: 15 }, (_, i) => ({
    name: `Contributor ${i + 1}`,
    login: `contributor${i + 1}`,
    avatar_url: `https://example.com/avatar${i + 1}.jpg`,
    contributions_count: 30 - i,
  })),
  idx_issues: [
    {
      title: 'Issue 1',
      author: { name: 'Author 1', avatar_url: 'https://example.com/author1.jpg' },
      created_at: 1625097600,
      comments_count: 5,
    },
  ],
  idx_releases: [
    {
      name: 'Release 1.0',
      author: { name: 'Author 1', avatar_url: 'https://example.com/author1.jpg' },
      published_at: 1625097600,
      tag_name: 'v1.0',
    },
  ],
}

describe('ProjectDetailsPage Component', () => {
  beforeEach(() => {
    ;(fetchAlgoliaData as jest.Mock).mockImplementation(() =>
      Promise.resolve({
        hits: [mockProjectData],
      })
    )
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  test('topics visibility check', async () => {
    render(<ProjectDetailsPage />)
    await waitFor(() => {
      expect(screen.getByText('Topic 1')).toBeInTheDocument()
    })
    expect(screen.queryByText('Topic 11')).not.toBeInTheDocument()
  })

  test('contributors visibility check', async () => {
    render(<ProjectDetailsPage />)
    await waitFor(() => {
      expect(screen.getByText('Contributor 1')).toBeInTheDocument()
    })
    expect(screen.queryByText('Contributor 6')).not.toBeInTheDocument()
  })

  test('handles contributors with missing names gracefully', async () => {
    const projectDataWithIncompleteContributors = {
      ...mockProjectData,
      idx_top_contributors: [
        {
          login: 'user1',
          avatar_url: 'https://example.com/avatar1.jpg',
          contributions_count: 30,
        },
      ],
    }

    ;(fetchAlgoliaData as jest.Mock).mockImplementation(() =>
      Promise.resolve({
        hits: [projectDataWithIncompleteContributors],
      })
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
