import { useQuery } from '@apollo/client/react'
import { addToast } from '@heroui/toast'
import { mockAlgoliaData, mockGraphQLData } from '@mockData/mockHomeData'
import { fireEvent, screen, waitFor } from '@testing-library/react'
import millify from 'millify'
import { useRouter } from 'next/navigation'
import { render } from 'wrappers/testUtil'
import Home from 'app/page'
import { fetchAlgoliaData } from 'server/fetchAlgoliaData'

jest.mock('@apollo/client/react', () => ({
  ...jest.requireActual('@apollo/client/react'),
  useQuery: jest.fn(),
}))

jest.mock('server/fetchAlgoliaData', () => ({
  fetchAlgoliaData: jest.fn(),
}))

jest.mock('@heroui/toast', () => ({
  addToast: jest.fn(),
}))

const mockRouter = {
  push: jest.fn(),
}

jest.mock('next/navigation', () => ({
  ...jest.requireActual('next/navigation'),
  useRouter: jest.fn(() => mockRouter),
}))

jest.mock('@/components/MarkdownWrapper', () => {
  return ({ content, className }: { content: string; className?: string }) => (
    <div
      className={`md-wrapper ${className || ''}`}
      dangerouslySetInnerHTML={{ __html: content }}
    />
  )
})

jest.mock('components/Modal', () => {
  const ModalMock = jest.fn(({ isOpen, onClose, title, summary, button, description }) => {
    if (!isOpen) return null
    return (
      <dialog open>
        <h2>{title}</h2>
        <p>{summary}</p>
        <p>{description}</p>
        <button onClick={onClose} aria-label="Close modal">
          Close
        </button>
        <a href={button.url}>{button.label}</a>
      </dialog>
    )
  })
  return ModalMock
})

describe('Home', () => {
  let mockRouter: { push: jest.Mock }

  beforeEach(() => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: mockGraphQLData,
      loading: false,
      error: null,
    })
    ;(fetchAlgoliaData as jest.Mock).mockResolvedValue(mockAlgoliaData)
    mockRouter = { push: jest.fn() }
    ;(useRouter as jest.Mock).mockReturnValue(mockRouter)
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  test('renders loading state', async () => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
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
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: null,
      error: { message: 'GraphQL error' },
    })

    render(<Home />)

    await waitFor(() => {
      expect(addToast).toHaveBeenCalledWith({
        description: 'Unable to complete the requested operation.',
        title: 'GraphQL Request Failed',
        timeout: 3000,
        shouldShowTimeoutProgress: true,
        color: 'danger',
        variant: 'solid',
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
      expect(screen.getByText('Chapters Worldwide')).toBeInTheDocument()
    })
  })

  test('renders ItemCardList components', async () => {
    render(<Home />)

    await waitFor(() => {
      expect(screen.getByText('Recent Issues')).toBeInTheDocument()
      expect(screen.getByText('Recent Releases')).toBeInTheDocument()
    })
  })

  test('handles missing data gracefully', async () => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
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
      for (const event of mockGraphQLData.upcomingEvents) {
        expect(screen.getByText(event.name)).toBeInTheDocument()
        expect(screen.getByText('Feb 27 — 28, 2025')).toBeInTheDocument()
      }
    })
  })

  test('renders Recent Pull Requests section', async () => {
    render(<Home />)

    await waitFor(() => {
      expect(screen.getByText('Recent Pull Requests')).toBeInTheDocument()

      for (const pullRequest of mockGraphQLData.recentPullRequests) {
        expect(screen.getByText(pullRequest.title)).toBeInTheDocument()
        expect(screen.getByText(pullRequest.repositoryName)).toBeInTheDocument()
      }
    })
  })

  test('renders milestones section correctly', async () => {
    render(<Home />)
    await waitFor(() => {
      const recentMilestones = mockGraphQLData.recentMilestones

      for (const milestone of recentMilestones) {
        expect(screen.getByText(milestone.title)).toBeInTheDocument()
        expect(screen.getByText(milestone.repositoryName)).toBeInTheDocument()
        expect(screen.getByText(`${milestone.openIssuesCount} open`)).toBeInTheDocument()
        expect(screen.getByText(`${milestone.closedIssuesCount} closed`)).toBeInTheDocument()
      }
    })
  })
  test('renders when no recent releases', async () => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
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

  test('renders stats correctly', async () => {
    render(<Home />)

    const headers = [
      'Active Projects',
      'Local Chapters',
      'Contributors',
      'Countries',
      'Slack Community',
    ]
    const stats = mockGraphQLData.statsOverview

    const statTexts = [
      millify(stats.activeProjectsStats) + '+',
      millify(stats.activeChaptersStats) + '+',
      millify(stats.contributorsStats) + '+',
      millify(stats.countriesStats) + '+',
      millify(stats.slackWorkspaceStats) + '+',
    ]

    await waitFor(
      () => {
        for (const stat of statTexts) {
          expect(screen.getByText(stat)).toBeInTheDocument()
        }
        for (const header of headers) {
          expect(screen.getByText(header)).toBeInTheDocument()
        }
      },
      { timeout: 3000 }
    )
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
