import { act, screen, waitFor } from '@testing-library/react'
import { render } from 'wrappers/testUtil'
import UserDetailsPage from 'pages/UserDetails'
import { GET_USER_DATA } from 'api/queries/userQueries'
import '@testing-library/jest-dom'

// Mock the Apollo Client
const mockGraphQLData = {
  user: {
    login: 'testuser',
    name: 'Test User',
    avatarUrl: 'https://example.com/avatar.jpg',
    url: 'https://github.com/testuser',
    bio: 'This is a test user',
    company: 'Test Company',
    location: 'Test Location',
    email: 'testuser@example.com',
    followersCount: 10,
    followingCount: 5,
    publicRepositoriesCount: 3,
    createdAt: 1723002473,
    issues: [
      {
        number: 1,
        title: 'Test Issue',
        createdAt: 1723002473,
        commentsCount: 5,
        repository: {
          key: 'test-repo',
          ownerKey: 'testuser'
        }
      }
    ],
    releases: [
      {
        name: 'v1.0.0',
        tagName: '1.0.0',
        isPreRelease: false,
        publishedAt: 1723002473,
        repository: {
          key: 'test-repo',
          ownerKey: 'testuser'
        }
      }
    ]
  }
}

const mocks = [
  {
    request: {
      query: GET_USER_DATA,
      variables: { key: 'testuser' }
    },
    result: {
      data: mockGraphQLData
    }
  }
]

// Mock the heatmap utilities
jest.mock('utils/helpers/githubHeatmap', () => ({
  fetchHeatmapData: jest.fn().mockResolvedValue({
    contributions: true,
    years: [{ year: 2024, total: 365, range: { start: '2024-01-01', end: '2024-12-31' } }]
  }),
  drawContributions: jest.fn()
}))

jest.mock('utils/logger', () => ({
  error: jest.fn()
}))

describe('UserDetailsPage', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  test('renders loading spinner initially', async () => {
    render(<UserDetailsPage />, { 
      route: '/user/testuser',
      mocks,
      addTypename: false
    })

    expect(screen.getByAltText('Loading indicator')).toBeInTheDocument()
  })

  test('renders user details after fetching data', async () => {
    render(<UserDetailsPage />, {
      route: '/user/testuser',
      mocks,
      addTypename: false
    })

    // Wait for loading to finish
    await waitFor(() => {
      expect(screen.queryByAltText('Loading indicator')).not.toBeInTheDocument()
    })

    // Verify user details are displayed
    expect(screen.getByText(mockGraphQLData.user.name)).toBeInTheDocument()
    expect(screen.getByText(`@${mockGraphQLData.user.login}`)).toBeInTheDocument()
    expect(screen.getByText(mockGraphQLData.user.bio)).toBeInTheDocument()
    expect(screen.getByText(mockGraphQLData.user.company)).toBeInTheDocument()
    expect(screen.getByText(mockGraphQLData.user.location)).toBeInTheDocument()
    expect(screen.getByText('Joined August 7, 2024')).toBeInTheDocument()

    // Verify statistics
    expect(screen.getByText('10')).toBeInTheDocument() // followers
    expect(screen.getByText('5')).toBeInTheDocument() // following
    expect(screen.getByText('3')).toBeInTheDocument() // repositories

    // Verify issues and releases sections
    expect(screen.getByText('Recent Issues')).toBeInTheDocument()
    expect(screen.getByText('Test Issue')).toBeInTheDocument()
    expect(screen.getByText('Recent Releases')).toBeInTheDocument()
    expect(screen.getByText('v1.0.0')).toBeInTheDocument()
  })

  test('renders "User not found" message when user does not exist', async () => {
    const errorMocks = [
      {
        request: {
          query: GET_USER_DATA,
          variables: { key: 'testuser' }
        },
        result: {
          data: { user: null }
        }
      }
    ]

    render(<UserDetailsPage />, {
      route: '/user/testuser',
      mocks: errorMocks,
      addTypename: false
    })

    await waitFor(() => {
      expect(screen.getByText('User not found')).toBeInTheDocument()
      expect(screen.getByText("Sorry, the user you're looking for doesn't exist")).toBeInTheDocument()
    })
  })

  test('shows error toast when GraphQL request fails', async () => {
    const errorMocks = [
      {
        request: {
          query: GET_USER_DATA,
          variables: { key: 'testuser' }
        },
        error: new Error('GraphQL Error')
      }
    ]

    render(<UserDetailsPage />, {
      route: '/user/testuser',
      mocks: errorMocks,
      addTypename: false
    })

    await waitFor(() => {
      expect(screen.getByText('GraphQL Request Failed')).toBeInTheDocument()
      expect(screen.getByText('Unable to complete the requested operation.')).toBeInTheDocument()
    })
  })
})