import { fireEvent, screen, waitFor } from '@testing-library/react'
import { fetchAlgoliaData } from 'helpers/api'
import { render } from 'helpers/wrappers/test-util'
import { useNavigate } from 'react-router-dom'
import UsersPage from 'pages/Users'
import { mockUserData } from '@tests/data/mockUserData'

jest.mock('helpers/api', () => ({
  fetchAlgoliaData: jest.fn(),
}))

jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: jest.fn(),
}))

jest.mock('components/Pagination', () =>
  jest.fn(({ currentPage, onPageChange }) => (
    <div>
      <button onClick={() => onPageChange(currentPage + 1)}>Next Page</button>
    </div>
  ))
)

jest.mock('helpers/wrappers/FontAwesomeIconWrapper', () => ({
  __esModule: true,
  default: () => <span data-testid="mock-icon" />,
}))

describe('UsersPage Component', () => {
  beforeEach(() => {
    ;(fetchAlgoliaData as jest.Mock).mockResolvedValue({
      hits: mockUserData.users,
      totalPages: 2,
    })
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  test('renders loading spinner initially', async () => {
    render(<UsersPage />)
    const loadingSpinner = screen.getAllByAltText('Loading indicator')
    await waitFor(() => {
      expect(loadingSpinner.length).toBeGreaterThan(0)
    })
  })

  test('renders SearchBar, user cards, and pagination after data is loaded', async () => {
    window.scrollTo = jest.fn()
    render(<UsersPage />)

    // Check loading state
    const loadingSpinner = screen.getAllByAltText('Loading indicator')
    await waitFor(() => {
      expect(loadingSpinner.length).toBeGreaterThan(0)
      expect(screen.queryByText('Next Page')).not.toBeInTheDocument()
    })

    // Check loaded state
    await waitFor(() => {
      expect(screen.getByPlaceholderText('Search for OWASP users...')).toBeInTheDocument()
      expect(screen.getByText('John Doe')).toBeInTheDocument()
      expect(screen.getByText('Next Page')).toBeInTheDocument()
    })

    expect(screen.queryByAltText('Loading indicator')).not.toBeInTheDocument()
  })

  test('renders user cards correctly', async () => {
    render(<UsersPage />)

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument()
      expect(screen.getByText('OWASP')).toBeInTheDocument()
      expect(screen.getByText('Jane Smith')).toBeInTheDocument()
      expect(screen.getByText('Security Co')).toBeInTheDocument()
    })

    const viewButtons = screen.getAllByText('View Profile')
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
    const navigateMock = jest.fn()
    ;(useNavigate as jest.Mock).mockReturnValue(navigateMock)

    render(<UsersPage />)

    await waitFor(() => {
      const viewDetailsButtons = screen.getAllByText('View Profile')
      expect(viewDetailsButtons[0]).toBeInTheDocument()
      fireEvent.click(viewDetailsButtons[0])
    })

    expect(navigateMock).toHaveBeenCalledWith('/community/users/user_1')
  })
})
