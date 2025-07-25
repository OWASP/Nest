import { MockedProvider } from '@apollo/client/testing'
import { render, screen, fireEvent } from '@testing-library/react'
import { useRouter } from 'next/navigation'
import { GET_LEADER_DATA } from 'server/queries/userQueries'
import LeadersListBlock from 'components/LeadersListBlock'

jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
}))

const mockLeaders = {
  leader1: 'Role 1',
  leader2: 'Role 2',
}

const mocks = [
  {
    request: {
      query: GET_LEADER_DATA,
      variables: { key: 'leader1' },
    },
    result: {
      data: {
        user: {
          login: 'leader1',
          avatarUrl: 'https://avatars.githubusercontent.com/u/1',
          company: 'Company 1',
          location: 'Location 1',
          name: 'Leader One',
        },
      },
    },
  },
  {
    request: {
      query: GET_LEADER_DATA,
      variables: { key: 'leader2' },
    },
    result: {
      data: {
        user: {
          login: 'leader2',
          avatarUrl: 'https://avatars.githubusercontent.com/u/2',
          company: 'Company 2',
          location: 'Location 2',
          name: 'Leader Two',
        },
      },
    },
  },
]

describe('LeadersListBlock', () => {
  const push = jest.fn()
  beforeEach(() => {
    ;(useRouter as jest.Mock).mockReturnValue({ push })
  })

  test('renders loading state initially', () => {
    render(
      <MockedProvider mocks={mocks} addTypename={false}>
        <LeadersListBlock leaders={mockLeaders} />
      </MockedProvider>
    )

    expect(screen.getByText('Loading leader1...')).toBeInTheDocument()
    expect(screen.getByText('Loading leader2...')).toBeInTheDocument()
  })

  test('renders user cards on successful data fetch', async () => {
    render(
      <MockedProvider mocks={mocks} addTypename={false}>
        <LeadersListBlock leaders={mockLeaders} />
      </MockedProvider>
    )

    expect(await screen.findByText('Leader One')).toBeInTheDocument()
    expect(await screen.findByText('Leader Two')).toBeInTheDocument()
  })

  test('navigates to the correct user profile on button click', async () => {
    render(
      <MockedProvider mocks={mocks} addTypename={false}>
        <LeadersListBlock leaders={mockLeaders} />
      </MockedProvider>
    )

    const viewProfileButton = await screen.findAllByText('View Profile')
    fireEvent.click(viewProfileButton[0])

    expect(push).toHaveBeenCalledWith('/members/leader1')
  })

  test('renders an error message if the query fails', async () => {
    const errorMocks = [
      {
        request: {
          query: GET_LEADER_DATA,
          variables: { key: 'leader1' },
        },
        error: new Error('An error occurred'),
      },
    ]

    render(
      <MockedProvider mocks={errorMocks} addTypename={false}>
        <LeadersListBlock leaders={{ leader1: 'Role 1' }} />
      </MockedProvider>
    )

    expect(await screen.findByText("Error loading leader1's data")).toBeInTheDocument()
  })
})
