import { screen, fireEvent, waitFor } from '@testing-library/react'
import { fetchAlgoliaData } from 'api/fetchAlgoliaData'
import { render } from 'wrappers/testUtil'
import ProjectDetailsPage from 'pages/ProjectDetails'
import { mockProjectDetailsData } from '@tests/data/mockProjectDetailsData'
import '@testing-library/jest-dom' // Ensure you have this for matchers like .toBeInTheDocument()

jest.mock('api/fetchAlgoliaData')
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useParams: () => ({
    projectKey: 'test-project',
  }),
}))

describe('ProjectDetailsPage Component', () => {
  beforeEach(() => {
    (fetchAlgoliaData as jest.Mock).mockImplementation(() =>
      Promise.resolve({
        hits: [mockProjectDetailsData],
      }),
    )
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  test('topics visibility check', async () => {
    render(<ProjectDetailsPage />)
    await waitFor(() => {
      // First topic: visible
      expect(screen.getByText('Topic 1')).toBeInTheDocument()
    })
    // 11th topic: not visible by default
    expect(screen.queryByText('Topic 11')).not.toBeInTheDocument()
  })

  test('contributors visibility check', async () => {
    render(<ProjectDetailsPage />)
    await waitFor(() => {
      // First contributor: visible
      expect(screen.getByText('Contributor 1')).toBeInTheDocument()
    })
    // 6th contributor: not visible by default
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
      }),
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

  // Below are additional tests to cover toggling “Show more/Show less” for languages, topics, and contributors.

  test('toggles “Show more/Show less” for languages', async () => {
    // Render with default data (already has 15 languages).
    render(<ProjectDetailsPage />)

    // By default, only 10 languages should be shown
    await waitFor(() => {
      for (let i = 1; i <= 10; i++) {
        expect(screen.getByText(`Language ${i}`)).toBeInTheDocument()
      }
    })
    // 11th language should not be visible initially
    expect(screen.queryByText('Language 11')).not.toBeInTheDocument()

    // Click “Show more” for languages
    fireEvent.click(screen.getByTestId('show-more-languages')) // Make sure your component has data-testid="show-more-languages"

    // Now the remaining languages (11–15) should appear
    await waitFor(() => {
      for (let i = 11; i <= 15; i++) {
        expect(screen.getByText(`Language ${i}`)).toBeInTheDocument()
      }
    })

    // Click again to “Show less”
    fireEvent.click(screen.getByTestId('show-more-languages'))
    // 11th+ languages should be hidden again
    await waitFor(() => {
      expect(screen.queryByText('Language 11')).not.toBeInTheDocument()
    })
  })

  test('toggles “Show more/Show less” for topics', async () => {
    render(<ProjectDetailsPage />)

    // By default, only 10 topics should be shown
    await waitFor(() => {
      for (let i = 1; i <= 10; i++) {
        expect(screen.getByText(`Topic ${i}`)).toBeInTheDocument()
      }
    })
    // 11th topic should not be visible initially
    expect(screen.queryByText('Topic 11')).not.toBeInTheDocument()

    // Click “Show more” for topics
    fireEvent.click(screen.getByTestId('show-more-topics')) // data-testid="show-more-topics"

    // Now we should see topics 11–15
    await waitFor(() => {
      for (let i = 11; i <= 15; i++) {
        expect(screen.getByText(`Topic ${i}`)).toBeInTheDocument()
      }
    })

    // Click to “Show less”
    fireEvent.click(screen.getByTestId('show-more-topics'))
    await waitFor(() => {
      expect(screen.queryByText('Topic 11')).not.toBeInTheDocument()
    })
  })

  test('toggles “Show more/Show less” for contributors', async () => {
    render(<ProjectDetailsPage />)

    // By default, only 5 contributors should be shown
    await waitFor(() => {
      for (let i = 1; i <= 5; i++) {
        expect(screen.getByText(`Contributor ${i}`)).toBeInTheDocument()
      }
    })
    // Contributor 6 not visible initially
    expect(screen.queryByText('Contributor 6')).not.toBeInTheDocument()

    // Click “Show more” for contributors
    fireEvent.click(screen.getByTestId('show-more-contributors')) // data-testid="show-more-contributors"

    // Now contributors 6–15 should appear
    await waitFor(() => {
      for (let i = 6; i <= 15; i++) {
        expect(screen.getByText(`Contributor ${i}`)).toBeInTheDocument()
      }
    })

    // Click “Show less”
    fireEvent.click(screen.getByTestId('show-more-contributors'))
    expect(screen.queryByText('Contributor 6')).not.toBeInTheDocument()
  })
  test('renders recent issues if project.issues is not empty', async () => {
    // Modify mock data so issues is non-empty
    (fetchAlgoliaData as jest.Mock).mockResolvedValueOnce({
      hits: [
        {
          ...mockProjectDetailsData,
          issues: [
            {
              title: 'Issue 1',
              author: { name: 'Author 1', avatar_url: 'https://example.com/author1.jpg' },
              created_at: 1625097600,
              comments_count: 5,
            },
          ],
        },
      ],
    })
  
    render(<ProjectDetailsPage />)
  
    // Confirm the "Issue 1" text appears in the DOM
    await waitFor(() => {
      expect(screen.getByText('Issue 1')).toBeInTheDocument()
    })
  })
  
  test('renders "No recent issues." when issues array is empty', async () => {
    (fetchAlgoliaData as jest.Mock).mockResolvedValueOnce({
      hits: [
        {
          ...mockProjectDetailsData,
          issues: [],
        },
      ],
    })
  
    render(<ProjectDetailsPage />)
  
    await waitFor(() => {
      expect(screen.getByText('No recent issues.')).toBeInTheDocument()
    })
  })
  
  test('renders recent releases if project.releases is not empty', async () => {
    // Modify mock data so releases is non-empty
    (fetchAlgoliaData as jest.Mock).mockResolvedValueOnce({
      hits: [
        {
          ...mockProjectDetailsData,
          releases: [
            {
              name: 'Release 1.0',
              author: { name: 'Author 1', avatar_url: 'https://example.com/author1.jpg' },
              published_at: 1625097600,
              tag_name: 'v1.0',
            },
          ],
        },
      ],
    })
  
    render(<ProjectDetailsPage />)
  
    // Confirm the "Release 1.0" text appears in the DOM
    await waitFor(() => {
      expect(screen.getByText('Release 1.0')).toBeInTheDocument()
    })
  })
  
  test('renders "No recent releases." when releases array is empty', async () => {
    (fetchAlgoliaData as jest.Mock).mockResolvedValueOnce({
      hits: [
        {
          ...mockProjectDetailsData,
          releases: [],
        },
      ],
    })
  
    render(<ProjectDetailsPage />)
  
    await waitFor(() => {
      expect(screen.getByText('No recent releases.')).toBeInTheDocument()
    })
  })
})