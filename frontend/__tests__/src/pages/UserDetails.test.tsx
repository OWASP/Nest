import { act, render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import UserDetailsPage from 'pages/UserDetails'
import '@testing-library/jest-dom'

jest.mock('utils/logger', () => ({
  error: jest.fn(),
}))

const mockUser = {
  login: 'testuser',
  name: 'Test User',
  avatar_url: 'https://example.com/avatar.jpg',
  url: 'https://github.com/testuser',
  bio: 'This is a test user',
  company: 'Test Company',
  location: 'Test Location',
  twitter_username: 'testuser',
  email: 'testuser@example.com',
  followers_count: 10,
  following_count: 5,
  public_repositories_count: 3,
  created_at: '2020-01-01T00:00:00Z',
}

describe('UserDetailsPage', () => {
  beforeEach(() => {
    global.fetch = jest.fn(() =>
      Promise.resolve({
        json: () => Promise.resolve(mockUser),
      })
    ) as jest.Mock
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  test('renders loading spinner initially', async () => {
    render(<UserDetailsPage />)
    const loadingSpinner = screen.getAllByAltText('Loading indicator')
    await waitFor(() => {
      expect(loadingSpinner.length).toBeGreaterThan(0)
    })
  })

  test('renders user details after fetching data', async () => {
    await act(async () => {
      render(
        <MemoryRouter initialEntries={['/user/testuser']}>
          <Routes>
            <Route path="/user/:login" element={<UserDetailsPage />} />
          </Routes>
        </MemoryRouter>
      )
    })

    await waitFor(() => expect(screen.getByText('Test User')).toBeInTheDocument())
    expect(screen.getByText('@testuser')).toBeInTheDocument()
    expect(screen.getByText('This is a test user')).toBeInTheDocument()
    expect(screen.getByText('Test Company')).toBeInTheDocument()
    expect(screen.getByText('Test Location')).toBeInTheDocument()
    expect(screen.getByText('testuser')).toBeInTheDocument()
    expect(screen.getByText('testuser@example.com')).toBeInTheDocument()
    expect(screen.getByText('Followers')).toBeInTheDocument()
    expect(screen.getByText('Following')).toBeInTheDocument()
    expect(screen.getByText('Repositories')).toBeInTheDocument()
    expect(screen.getByText('Joined January 1, 2020')).toBeInTheDocument()
  })

  test('renders error message when user does not exist', async () => {
    global.fetch = jest.fn(() =>
      Promise.resolve({
        json: () => Promise.resolve(null),
      })
    ) as jest.Mock

    render(
      <MemoryRouter initialEntries={['/user/nonexistentuser']}>
        <Routes>
          <Route path="/user/:login" element={<UserDetailsPage />} />
        </Routes>
      </MemoryRouter>
    )

    await waitFor(() => expect(screen.getByText('User does not exist')).toBeInTheDocument())
  })
})
