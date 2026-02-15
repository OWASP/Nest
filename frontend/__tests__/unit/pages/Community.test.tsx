import { useQuery } from '@apollo/client/react'
import { addToast } from '@heroui/toast'
import { mockCommunityGraphQLData } from '@mockData/mockCommunityData'
import { screen, waitFor } from '@testing-library/react'
import { render } from 'wrappers/testUtil'
import CommunityPage from 'app/community/page'

jest.mock('@apollo/client/react', () => ({
  ...jest.requireActual('@apollo/client/react'),
  useQuery: jest.fn(),
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

describe('Community Page', () => {
  beforeEach(() => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: mockCommunityGraphQLData,
      loading: false,
      error: null,
    })
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

    render(<CommunityPage />)

    await waitFor(() => {
      const loadings = screen.getAllByAltText('Loading indicator')
      expect(loadings.length).toBeGreaterThan(0)
    })
  })

  test('renders error state', async () => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: null,
      loading: false,
      error: { message: 'Failed to fetch' },
    })

    render(<CommunityPage />)

    await waitFor(() => {
      expect(addToast).toHaveBeenCalledWith(
        expect.objectContaining({
          title: 'GraphQL Request Failed',
          color: 'danger',
        })
      )
    })
  })

  test('renders hero section correctly', async () => {
    render(<CommunityPage />)

    await waitFor(() => {
      expect(screen.getByText('OWASP Community')).toBeInTheDocument()
      expect(screen.getByText(/Connect, collaborate, and contribute/)).toBeInTheDocument()
      expect(screen.getByPlaceholderText('Search the OWASP community')).toBeInTheDocument()
    })
  })

  test('renders navigation cards', async () => {
    render(<CommunityPage />)

    await waitFor(() => {
      expect(screen.getByText('Chapters')).toBeInTheDocument()
      expect(screen.getByText('Members')).toBeInTheDocument()
      expect(screen.getByText('Organizations')).toBeInTheDocument()
      expect(screen.getAllByText('Snapshots').length).toBeGreaterThan(0)
    })
  })

  test('renders new chapters section', async () => {
    render(<CommunityPage />)

    await waitFor(() => {
      expect(screen.getByText('New Chapters')).toBeInTheDocument()
      expect(screen.getByText('OWASP Chapter 1')).toBeInTheDocument()
      expect(screen.getByText('OWASP Chapter 2')).toBeInTheDocument()
      expect(screen.getByText('Location 1')).toBeInTheDocument()
    })
  })

  test('renders recent organizations section', async () => {
    render(<CommunityPage />)

    await waitFor(() => {
      expect(screen.getByText('New Organizations')).toBeInTheDocument()
      expect(screen.getByText('Organization 1')).toBeInTheDocument()
    })
  })

  test('renders snapshots section', async () => {
    render(<CommunityPage />)

    await waitFor(() => {
      expect(screen.getAllByText('Snapshots').length).toBeGreaterThan(0)
      expect(screen.getByText('Snapshot 1')).toBeInTheDocument()
      expect(screen.getByText(/Jan 1, 2025 - Jan 31, 2025/)).toBeInTheDocument()
    })
  })

  test('renders top contributors section', async () => {
    render(<CommunityPage />)

    await waitFor(() => {
      expect(screen.getByText('Top Contributors')).toBeInTheDocument()
      expect(screen.getByText('User 1')).toBeInTheDocument()
      expect(screen.getByText('User 2')).toBeInTheDocument()
    })
  })

  test('renders stats section', async () => {
    render(<CommunityPage />)

    await waitFor(() => {
      expect(screen.getByText('Active Chapters')).toBeInTheDocument()
      expect(screen.getByText('150+')).toBeInTheDocument()
      expect(screen.getByText('Active Projects')).toBeInTheDocument()
      expect(screen.getByText('50+')).toBeInTheDocument()
      expect(screen.getByText('Countries')).toBeInTheDocument()
      expect(screen.getByText('100+')).toBeInTheDocument()
      expect(screen.getByText('Contributors')).toBeInTheDocument()
      expect(screen.getByText(/5k\+/i)).toBeInTheDocument()
    })
  })
})
