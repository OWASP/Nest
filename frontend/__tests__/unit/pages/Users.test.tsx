import { fireEvent, screen, waitFor } from '@testing-library/react'
import { mockUserData } from '@unit/data/mockUserData'
import { useRouter } from 'next/navigation'
import { render } from 'wrappers/testUtil'
import UsersPage from 'app/members/page'
import { fetchAlgoliaData } from 'server/fetchAlgoliaData'

const mockRouter = {
  push: jest.fn(),
}

jest.mock('next/navigation', () => ({
  ...jest.requireActual('next/navigation'),
  useRouter: jest.fn(() => mockRouter),
  useParams: () => ({ userKey: 'test-user' }),
  useSearchParams: () => new URLSearchParams(),
}))

jest.mock('server/fetchAlgoliaData', () => ({
  fetchAlgoliaData: jest.fn(),
}))

jest.mock('components/Pagination', () =>
  jest.fn(({ currentPage, onPageChange }) => (
    <div>
      <button onClick={() => onPageChange(currentPage + 1)}>Next Page</button>
    </div>
  ))
)

describe('UsersPage Component', () => {
  let mockRouter: { push: jest.Mock }

  beforeEach(() => {
    ;(fetchAlgoliaData as jest.Mock).mockResolvedValue({
      hits: mockUserData.users,
      totalPages: 2,
    })
    mockRouter = { push: jest.fn() }
    ;(useRouter as jest.Mock).mockReturnValue(mockRouter)
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  test('renders skeleton initially', async () => {
    render(<UsersPage />)
    await waitFor(() => {
      const skeletonLoaders = screen.getAllByRole('status')
      expect(skeletonLoaders.length).toBeGreaterThan(0)
    })
  })

  test('renders SearchBar, user cards, and pagination after data is loaded', async () => {
    window.scrollTo = jest.fn()
    render(<UsersPage />)

    // Check loading state
    const skeletonLoaders = screen.getAllByRole('status')
    await waitFor(() => {
      expect(skeletonLoaders.length).toBeGreaterThan(0)
      expect(screen.queryByText('Next Page')).not.toBeInTheDocument()
    })

    // Check loaded state
    await waitFor(() => {
      expect(screen.getByPlaceholderText('Search for members...')).toBeInTheDocument()
      expect(screen.getByText('John Doe')).toBeInTheDocument()
      expect(screen.getByText('Next Page')).toBeInTheDocument()
    })

    expect(screen.queryByTestId('status')).not.toBeInTheDocument()
  })

  test('renders user cards correctly', async () => {
    render(<UsersPage />)

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument()
      expect(screen.getByText('OWASP')).toBeInTheDocument()
      expect(screen.getByText('Jane Smith')).toBeInTheDocument()
      expect(screen.getByText('Security Co')).toBeInTheDocument()
    })

    const viewButtons = screen.getAllByText('View Details')
    expect(viewButtons).toHaveLength(2)
  })

  test('displays "No Users found" when there are no users', async () => {
    ;(fetchAlgoliaData as jest.Mock).mockResolvedValue({
      hits: [],
      totalPages: 0,
    })

    render(<UsersPage />)

    await waitFor(() => {
      expect(screen.getByText('No Users found')).toBeInTheDocument()
    })
  })

  test('handles page change correctly', async () => {
    window.scrollTo = jest.fn()

    render(<UsersPage />)

    await waitFor(() => {
      const nextPageButton = screen.getByText('Next Page')
      fireEvent.click(nextPageButton)
    })

    expect(window.scrollTo).toHaveBeenCalledWith({
      top: 0,
      behavior: 'auto',
    })
  })

  test('navigates to user details on View Details button click', async () => {
    render(<UsersPage />)

    await waitFor(() => {
      const viewDetailsButtons = screen.getAllByText('View Details')
      expect(viewDetailsButtons[0]).toBeInTheDocument()
      fireEvent.click(viewDetailsButtons[0])
    })

    expect(mockRouter.push).toHaveBeenCalledWith('/members/user_1')
  })

  test('renders fallback username if user name is missing', async () => {
    ;(fetchAlgoliaData as jest.Mock).mockResolvedValue({
      hits: [
        {
          key: 'user_3',
          login: 'fallback_login',
          avatarUrl: 'https://example.com/avatar.jpg',
          company: 'Some Company',
        },
      ],
      totalPages: 1,
    })

    render(<UsersPage />)

    await waitFor(() => {
      expect(screen.getByText('@fallback_login')).toBeInTheDocument()
    })
  })
})
