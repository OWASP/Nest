import { useQuery } from '@apollo/client'
import { screen, waitFor } from '@testing-library/react'
import { toast } from 'hooks/useToast'
import { useNavigate } from 'react-router-dom'
import { render } from 'wrappers/testUtil'
import UserDetailsPage from 'pages/UserDetails'
import '@testing-library/jest-dom'
import { mockUserDetailsData } from '@tests/data/mockUserDetailsData'

jest.mock('hooks/useToast', () => ({
  toast: jest.fn(),
}))

jest.mock('@apollo/client', () => ({
  ...jest.requireActual('@apollo/client'),
  useQuery: jest.fn(),
}))

jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useParams: () => ({ userKey: 'test-user' }),
  useNavigate: jest.fn(),
}))

const mockError = {
  error: new Error('GraphQL error'),
}

describe('UserDetailsPage', () => {
  let navigateMock: jest.Mock

  beforeEach(() => {
    navigateMock = jest.fn()
    ;(useQuery as jest.Mock).mockReturnValue({
      data: mockUserDetailsData,
      loading: false,
      error: null,
    })
    ;(useNavigate as jest.Mock).mockImplementation(() => navigateMock)
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  test('renders loading state', async () => {
    ;(useQuery as jest.Mock).mockReturnValue({
      data: null,
      error: null,
    })

    render(<UserDetailsPage />)
    const loadingSpinner = screen.getAllByAltText('Loading indicator')
    await waitFor(() => {
      expect(loadingSpinner.length).toBeGreaterThan(0)
    })
  })

  test('renders user details', async () => {
    ;(useQuery as jest.Mock).mockReturnValue({
      data: mockUserDetailsData,
      error: null,
      loading: false,
    })

    // Wait for the loading state to finish
    render(<UserDetailsPage />)

    await waitFor(() => {
      expect(screen.queryByAltText('Loading indicator')).not.toBeInTheDocument()
    })

    expect(screen.getByText('Test User')).toBeInTheDocument()
    expect(screen.getByText(`@testuser`)).toBeInTheDocument()
    expect(screen.getByText('This is a test user')).toBeInTheDocument()
    expect(screen.getByText('Test Company')).toBeInTheDocument()
    expect(screen.getByText('Test Location')).toBeInTheDocument()
    expect(screen.getByText(`Joined December 15, 2023`)).toBeInTheDocument()
  })

  test('displays GitHub profile link correctly', async () => {
    ;(useQuery as jest.Mock).mockReturnValue({
      data: mockUserDetailsData,
      error: null,
    })

    render(<UserDetailsPage />)

    await waitFor(() => {
      const githubProfileLink = screen.getByText('Visit GitHub Profile')
      expect(githubProfileLink).toBeInTheDocument()
      expect(githubProfileLink.closest('a')).toHaveAttribute('href', 'https://github.com/testuser')
    })
  })

  test('displays contact information elements', async () => {
    ;(useQuery as jest.Mock).mockReturnValue({
      data: mockUserDetailsData,
      error: null,
    })

    render(<UserDetailsPage />)

    await waitFor(() => {
      const emailElement = screen.getByText('testuser@example.com')
      expect(emailElement).toBeInTheDocument()

      const companyElement = screen.getByText('Test Company')
      expect(companyElement).toBeInTheDocument()

      const locationElement = screen.getByText('Test Location')
      expect(locationElement).toBeInTheDocument()
    })
  })

  test('renders error message when GraphQL request fails', async () => {
    ;(useQuery as jest.Mock).mockReturnValue({
      data: { repository: null },
      error: mockError,
    })

    render(<UserDetailsPage />)

    await waitFor(() => screen.getByText('User not found'))
    expect(toast).toHaveBeenCalledWith({
      description: 'Unable to complete the requested operation.',
      title: 'GraphQL Request Failed',
      variant: 'destructive',
    })
  })
})
