import { useQuery } from '@apollo/client'
import { fireEvent, screen, waitFor } from '@testing-library/react'
import { mockAlgoliaData, mockGraphQLData } from '@unit/data/mockHomeData'
import { fetchAlgoliaData } from 'api/fetchAlgoliaData'
import { Home } from 'pages'
import { render } from 'wrappers/testUtil'
import { toaster } from 'components/ui/toaster'

jest.mock('@apollo/client', () => ({
  ...jest.requireActual('@apollo/client'),
  useQuery: jest.fn(),
}))

jest.mock('components/ui/toaster', () => ({
  toaster: {
    create: jest.fn(),
  },
}))

jest.mock('api/fetchAlgoliaData', () => ({
  fetchAlgoliaData: jest.fn(),
}))

jest.mock('components/Modal', () => {
  const ModalMock = jest.fn(({ isOpen, onClose, title, summary, button, description }) => {
    if (!isOpen) return null
    return (
      <div role="dialog">
        <h2>{title}</h2>
        <p>{summary}</p>
        <p>{description}</p>
        <button onClick={onClose} aria-label="Close modal">
          Close
        </button>
        <a href={button.url}>{button.label}</a>
      </div>
    )
  })
  return ModalMock
})

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
      expect(screen.getByText('Tool')).toBeInTheDocument()
    })
  })

  test('renders error message when GraphQL request fails', async () => {
    ;(useQuery as jest.Mock).mockReturnValue({
      data: null,
      error: { message: 'GraphQL error' },
    })

    render(<Home />)

    await waitFor(() => {
      expect(toaster.create).toHaveBeenCalledWith({
        description: 'Unable to complete the requested operation.',
        title: 'GraphQL Request Failed',
        type: 'error',
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
      expect(screen.getByText('OWASP Chapters Worldwide')).toBeInTheDocument()
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
      expect(screen.getByText('Tool')).toBeInTheDocument()
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

  test('renders Recent Pull Requests section', async () => {
    render(<Home />)

    await waitFor(() => {
      expect(screen.getByText('Recent Pull Requests')).toBeInTheDocument()
      mockGraphQLData.recentPullRequests.forEach((pullRequest) => {
        expect(screen.getByText(pullRequest.title)).toBeInTheDocument()
        expect(
          screen.getByText(pullRequest.author.name || pullRequest.author.login)
        ).toBeInTheDocument()
      })
    })
  })

  test('renders when no recent releases', async () => {
    ;(useQuery as jest.Mock).mockReturnValue({
      data: {
        ...mockGraphQLData,
        recentReleases: [],
      },
      error: null,
    })
    render(<Home />)
    await waitFor(() => {
      expect(screen.getByText('No recent releases.')).toBeInTheDocument()
    })
  })

  test('renders event details including date range and location', async () => {
    render(<Home />)

    await waitFor(() => {
      expect(screen.getByText('Upcoming Events')).toBeInTheDocument()
      expect(screen.getByText('Event 1')).toBeInTheDocument()
      expect(screen.getByText('Feb 27 — 28, 2025')).toBeInTheDocument()
      expect(screen.getByText('Location 1')).toBeInTheDocument()
    })
  })

  test('opens and closes modal for Upcoming Events and triggers onClose', async () => {
    render(<Home />)

    await waitFor(() => {
      expect(screen.getByText('Upcoming Events')).toBeInTheDocument()
      expect(screen.getByText('Event 1')).toBeInTheDocument()
    })

    const eventButton = screen.getByText('Event 1')
    fireEvent.click(eventButton)

    await waitFor(() => {
      expect(screen.getByText('Event Summary')).toBeInTheDocument()
    })
  })

  test('displays modal content correctly after clicking Event 1', async () => {
    render(<Home />)

    await waitFor(() => {
      expect(screen.getByText('Upcoming Events')).toBeInTheDocument()
      expect(screen.getByText('Event 1')).toBeInTheDocument()
    })

    const eventButton = screen.getByText('Event 1')
    fireEvent.click(eventButton)

    await waitFor(() => {
      expect(screen.getByText('Event Summary')).toBeInTheDocument()
      expect(screen.getByText('View Event')).toBeInTheDocument()
      expect(screen.getByText('The event summary has been generated by AI')).toBeInTheDocument()
    })
  })

  test('closes modal when close button is clicked', async () => {
    render(<Home />)

    await waitFor(() => {
      expect(screen.getByText('Upcoming Events')).toBeInTheDocument()
      expect(screen.getByText('Event 1')).toBeInTheDocument()
    })

    const eventButton = screen.getByText('Event 1')
    fireEvent.click(eventButton)

    await waitFor(() => {
      expect(screen.getByRole('dialog')).toBeInTheDocument()
    })

    const closeButton = screen.getByLabelText('Close modal')
    fireEvent.click(closeButton)

    await waitFor(() => {
      expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
    })
  })
})
