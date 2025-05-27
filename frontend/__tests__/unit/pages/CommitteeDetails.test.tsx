import { useQuery } from '@apollo/client'
import { screen, waitFor } from '@testing-library/react'
import { mockCommitteeDetailsData } from '@unit/data/mockCommitteeDetailsData'
import { render } from 'wrappers/testUtil'
import CommitteeDetailsPage from 'app/committees/[committeeKey]/page'

jest.mock('@apollo/client', () => ({
  ...jest.requireActual('@apollo/client'),
  useQuery: jest.fn(),
}))

jest.mock('@fortawesome/react-fontawesome', () => ({
  FontAwesomeIcon: () => <span data-testid="mock-icon" />,
}))

const mockRouter = {
  push: jest.fn(),
}

jest.mock('next/navigation', () => ({
  ...jest.requireActual('next/navigation'),
  useRouter: jest.fn(() => mockRouter),
  useParams: () => ({ committeeKey: 'test-committee' }),
}))

describe('CommitteeDetailsPage Component', () => {
  beforeEach(() => {
    ;(useQuery as jest.Mock).mockReturnValue({
      data: mockCommitteeDetailsData,
      error: null,
    })
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  test('renders loading spinner initially', async () => {
    ;(useQuery as jest.Mock).mockReturnValue({
      data: null,
      loading: true,
      error: null,
    })
    render(<CommitteeDetailsPage />)
    const loadingSpinner = screen.getAllByAltText('Loading indicator')
    await waitFor(() => {
      expect(loadingSpinner.length).toBeGreaterThan(0)
    })
  })

  test('renders committee data correctly', async () => {
    render(<CommitteeDetailsPage />)
    await waitFor(() => {
      expect(screen.getByText('Test Committee')).toBeInTheDocument()
    })
    expect(screen.getByText('This is a test committee summary.')).toBeInTheDocument()
    expect(screen.getByText('Leader 1')).toBeInTheDocument()
    expect(screen.getByText('Leader 2')).toBeInTheDocument()
    expect(screen.getByText('https://owasp.org/test-committee')).toBeInTheDocument()
  })

  test('displays "Committee not found" when there is no committee', async () => {
    ;(useQuery as jest.Mock).mockReturnValue({
      data: null,
      error: { message: 'Committee not found' },
    })
    render(<CommitteeDetailsPage />)
    await waitFor(() => {
      expect(screen.getByText('Committee not found')).toBeInTheDocument()
    })
  })

  test('renders committee URL as clickable link', async () => {
    render(<CommitteeDetailsPage />)
    await waitFor(() => {
      const link = screen.getByText('https://owasp.org/test-committee')
      expect(link.tagName).toBe('A')
      expect(link).toHaveAttribute('href', 'https://owasp.org/test-committee')
    })
  })

  test('handles contributors with missing names gracefully', async () => {
    const committeeDataWithIncompleteContributors = {
      committee: mockCommitteeDetailsData.committee,
      topContributors: [
        {
          avatarUrl: 'https://example.com/avatar1.jpg',
          contributionsCount: 30,
          login: 'Contributor 1',
          name: '',
          __typename: 'UserNode',
        },
      ],
    }
    ;(useQuery as jest.Mock).mockReturnValue({
      data: committeeDataWithIncompleteContributors,
      error: null,
    })
    render(<CommitteeDetailsPage />)

    await waitFor(() => {
      expect(screen.getByText('Contributor 1')).toBeInTheDocument()
    })
  })

  test('renders top contributors correctly', async () => {
    render(<CommitteeDetailsPage />)
    await waitFor(() => {
      expect(screen.getByText('Contributor 1')).toBeInTheDocument()
      expect(screen.getByText('Contributor 2')).toBeInTheDocument()
    })
  })

  test('renders error message when GraphQL request fails', async () => {
    ;(useQuery as jest.Mock).mockReturnValue({
      loading: false,
      data: null,
      error: { message: 'GraphQL error' },
    })
    render(<CommitteeDetailsPage />)

    await waitFor(() => {
      expect(screen.getByText('Committee not found')).toBeInTheDocument()
    })
  })
})
