import { screen, waitFor } from '@testing-library/react'
import { fetchAlgoliaData } from 'api/fetchAlgoliaData'
import { render } from 'wrappers/testUtil'
import ProjectDetailsPage from 'pages/ProjectDetails'
import { mockProjectDetailsData } from '@tests/data/mockProjectDetailsData'
jest.mock('api/fetchAlgoliaData')

jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useParams: () => ({
    projectKey: 'test-project',
  }),
}))

describe('ProjectDetailsPage Component', () => {
  beforeEach(() => {
    ;(fetchAlgoliaData as jest.Mock).mockImplementation(() =>
      Promise.resolve({
        hits: [mockProjectDetailsData],
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
      ...mockProjectDetailsData,
      top_contributors: [
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
