import { useQuery } from '@apollo/client'
import { screen, waitFor } from '@testing-library/react'
import { mockAlgoliaData, mockGraphQLData } from '@unit/data/mockHomeData'
import { fetchAlgoliaData } from 'api/fetchAlgoliaData'
import { toast } from 'hooks/useToast'
import { Home } from 'pages'
import { render } from 'wrappers/testUtil'

jest.mock('hooks/useToast', () => ({
  toast: jest.fn(),
}))

jest.mock('@apollo/client', () => ({
  ...jest.requireActual('@apollo/client'),
  useQuery: jest.fn(),
}))

jest.mock('api/fetchAlgoliaData', () => ({
  fetchAlgoliaData: jest.fn(),
}))

describe('Home', () => {
  beforeEach(() => {
    ;(useQuery as jest.Mock).mockReturnValue({
      data: mockGraphQLData,
      loading: false,
      error: null,
    })
    ;(fetchAlgoliaData as jest.Mock).mockResolvedValue(mockAlgoliaData)
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  test('renders loading state', async () => {
    ;(useQuery as jest.Mock).mockReturnValue({
      data: null,
      loading: true,
      error: null,
    })

    render(<Home />)

    await waitFor(() => {
      const loadingSpinners = screen.getAllByAltText('Loading indicator')
      expect(loadingSpinners.length).toBeGreaterThan(0)
    })
  })

  test('renders data when GraphQL and Algolia data are available', async () => {
    render(<Home />)

    await waitFor(() => {
      expect(screen.getByText('Welcome to OWASP Nest')).toBeInTheDocument()
      expect(screen.getByText('OWASP GameSec Framework')).toBeInTheDocument()
      expect(screen.getByText('Documentation')).toBeInTheDocument()
    })
  })

  test('renders error message when GraphQL request fails', async () => {
    ;(useQuery as jest.Mock).mockReturnValue({
      data: null,
      error: { message: 'GraphQL error' },
    })

    render(<Home />)

    await waitFor(() => {
      expect(toast).toHaveBeenCalledWith({
        description: 'Unable to complete the requested operation.',
        title: 'GraphQL Request Failed',
        variant: 'destructive',
      })
    })
  })

  test('renders Graphql data correctly', async () => {
    render(<Home />)

    await waitFor(() => {
      expect(screen.getByText('OWASP Sivagangai')).toBeInTheDocument()
      expect(screen.getByText('OWASP Foundation')).toBeInTheDocument()
    })
  })

  test('renders MultiSearchBar component', async () => {
    render(<Home />)

    await waitFor(() => {
      expect(screen.getByPlaceholderText('Search the OWASP community')).toBeInTheDocument()
    })
  })

  test('renders SecondaryCard components', async () => {
    render(<Home />)

    await waitFor(() => {
      expect(screen.getByText('New Chapters')).toBeInTheDocument()
      expect(screen.getByText('New Projects')).toBeInTheDocument()
    })
  })

  test('renders TopContributors component', async () => {
    render(<Home />)

    await waitFor(() => {
      expect(screen.getByText('Top Contributors')).toBeInTheDocument()
      expect(screen.getByText('OWASP Foundation')).toBeInTheDocument()
    })
  })

  test('renders ChapterMap component', async () => {
    render(<Home />)

    await waitFor(() => {
      expect(screen.getByText('OWASP Chapters Nearby')).toBeInTheDocument()
    })
  })

  test('renders ItemCardList components', async () => {
    render(<Home />)

    await waitFor(() => {
      expect(screen.getByText('Recent Issues')).toBeInTheDocument()
      expect(screen.getByText('Recent Releases')).toBeInTheDocument()
    })
  })

  test('renders AnimatedCounter components', async () => {
    render(<Home />)

    await waitFor(() => {
      expect(screen.getByText('Active Projects')).toBeInTheDocument()
      expect(screen.getByText('Contributors')).toBeInTheDocument()
      expect(screen.getByText('Local Chapters')).toBeInTheDocument()
      expect(screen.getByText('Countries')).toBeInTheDocument()
    })
  })

  test('handles missing data gracefully', async () => {
    ;(useQuery as jest.Mock).mockReturnValue({
      data: mockGraphQLData,
      error: null,
    })
    ;(fetchAlgoliaData as jest.Mock).mockResolvedValue({ hits: [] })

    render(<Home />)

    await waitFor(() => {
      expect(screen.getByText('Welcome to OWASP Nest')).toBeInTheDocument()
      expect(screen.getByText('OWASP GameSec Framework')).toBeInTheDocument()
      expect(screen.getByText('Documentation')).toBeInTheDocument()
    })
  })

  test('renders Upcoming Events section', async () => {
    render(<Home />)
    await waitFor(() => {
      expect(screen.getByText('Upcoming Events')).toBeInTheDocument()
      mockGraphQLData.upcomingEvents.forEach((event) => {
        expect(screen.getByText(event.name)).toBeInTheDocument()
        expect(screen.getByText('Feb 27 — 28, 2025')).toBeInTheDocument()
      })
    })
  })
})
