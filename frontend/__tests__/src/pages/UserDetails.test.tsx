import { act, screen, waitFor } from '@testing-library/react'
import { render } from 'wrappers/testUtil'
import UserDetailsPage from 'pages/UserDetails'
import '@testing-library/jest-dom'

// Mock the Algolia-related modules
jest.mock('utils/helpers/algoliaClient', () => ({
  createAlgoliaClient: jest.fn(),
}))

jest.mock('api/fetchAlgoliaData', () => ({
  fetchAlgoliaData: jest.fn(),
  removeIdxPrefix: (obj: unknown) => obj,
}))

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
  created_at: 1723002473,
}

describe('UserDetailsPage', () => {
  const { fetchAlgoliaData } = require('api/fetchAlgoliaData')

  beforeEach(() => {
    fetchAlgoliaData.mockReset()
  })

  test('renders loading spinner initially', async () => {
    fetchAlgoliaData.mockImplementation(() => new Promise(() => {}))
    await act(async () => {
      render(<UserDetailsPage />, { route: '/user/testuser' })
    })
    const loadingSpinner = screen.getAllByAltText('Loading indicator')
    await waitFor(() => {
      expect(loadingSpinner.length).toBeGreaterThan(0)
    })
  })

  test('renders user details after fetching data', async () => {
    fetchAlgoliaData.mockResolvedValue({ hits: [mockUser] })

    await act(async () => {
      render(<UserDetailsPage />, { route: '/user/testuser' })
    })

    // Wait for the loading state to finish
    await waitFor(() => {
      expect(screen.queryByAltText('Loading indicator')).not.toBeInTheDocument()
    })

    // Check for presence of user data
    expect(screen.getByText(mockUser.name)).toBeInTheDocument()
    expect(screen.getByText(`@${mockUser.login}`)).toBeInTheDocument()
    expect(screen.getByText(mockUser.bio)).toBeInTheDocument()
    expect(screen.getByText(mockUser.company)).toBeInTheDocument()
    expect(screen.getByText(mockUser.location)).toBeInTheDocument()
    expect(screen.getByText(`Joined August 7, 2024`)).toBeInTheDocument()
  })

  test('renders "User not found" message when user does not exist', async () => {
    fetchAlgoliaData.mockResolvedValue({ hits: [] })

    await act(async () => {
      render(<UserDetailsPage />, { route: '/user/testuser' })
    })

    await waitFor(() => {
      expect(screen.getByText('User not found')).toBeInTheDocument()
    })
  })

  test('logs error to logger when fetchUserData fails', async () => {
    const { fetchAlgoliaData } = require('api/fetchAlgoliaData')
    const logger = require('utils/logger')
    logger.error.mockClear()

    fetchAlgoliaData.mockRejectedValueOnce(new Error('Test fetch error'))

    await act(async () => {
      render(<UserDetailsPage />, { route: '/user/testuser' })
    })

    await waitFor(() => {
      expect(logger.error).toHaveBeenCalledWith(expect.any(Error))
    })
  })
})
