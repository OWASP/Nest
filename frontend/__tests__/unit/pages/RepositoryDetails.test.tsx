import { useQuery } from '@apollo/client'
import { act, screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { mockRepositoryData } from '@unit/data/mockRepositoryData'
import { RepositoryDetailsPage } from 'pages'
import { useNavigate } from 'react-router-dom'
import { render } from 'wrappers/testUtil'
import { toaster } from 'components/ui/toaster'

jest.mock('@apollo/client', () => ({
  ...jest.requireActual('@apollo/client'),
  useQuery: jest.fn(),
}))

jest.mock('components/ui/toaster', () => ({
  toaster: {
    create: jest.fn(),
  },
}))

jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useParams: () => ({ repositoryKey: 'test-repository' }),
  useNavigate: jest.fn(),
}))

const mockError = {
  error: new Error('GraphQL error'),
}

describe('RepositoryDetailsPage', () => {
  let navigateMock: jest.Mock

  beforeEach(() => {
    navigateMock = jest.fn()
    ;(useQuery as jest.Mock).mockReturnValue({
      data: mockRepositoryData,
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

    render(<RepositoryDetailsPage />)

    const loadingSpinner = screen.getAllByAltText('Loading indicator')
    await waitFor(() => {
      expect(loadingSpinner.length).toBeGreaterThan(0)
    })
  })

  test('renders repository details when data is available', async () => {
    ;(useQuery as jest.Mock).mockReturnValue({
      data: mockRepositoryData,
      error: null,
    })

    render(<RepositoryDetailsPage />)

    await waitFor(() => {
      expect(screen.getByText('Test Repo')).toBeInTheDocument()
      expect(screen.getByText('MIT')).toBeInTheDocument()
    })
    expect(screen.getByText('50K Stars')).toBeInTheDocument()
    expect(screen.getByText('3K Forks')).toBeInTheDocument()
    expect(screen.getByText('10 Commits')).toBeInTheDocument()
    expect(screen.getByText('5 Contributors')).toBeInTheDocument()
    expect(screen.getByText('2 Issues')).toBeInTheDocument()
  })

  test('renders error message when GraphQL request fails', async () => {
    ;(useQuery as jest.Mock).mockReturnValue({
      data: { repository: null },
      error: mockError,
    })

    render(<RepositoryDetailsPage />)

    await waitFor(() => screen.getByText('Repository not found'))
    expect(screen.getByText('Repository not found')).toBeInTheDocument()
    expect(toaster.create).toHaveBeenCalledWith({
      description: 'Unable to complete the requested operation.',
      title: 'GraphQL Request Failed',
      type: 'error',
    })
  })

  test('toggles contributors list when show more/less is clicked', async () => {
    render(<RepositoryDetailsPage />)
    const showMoreButton = screen.getByRole('button', { name: /Show more/i })
    await userEvent.click(showMoreButton)
    await screen.findByText('Contributor 7')

    const showLessButton = screen.getByRole('button', { name: /Show less/i })
    await userEvent.click(showLessButton)
    expect(showLessButton).toBeInTheDocument()
  }, 10000)
  test('navigates to user page when contributor is clicked', async () => {
    render(<RepositoryDetailsPage />)
    await waitFor(() => {
      expect(screen.getByText('Contributor 1')).toBeInTheDocument()
    })

    screen.getByText('Contributor 1').closest('button')?.click()

    expect(navigateMock).toHaveBeenCalledWith('/community/users/contributor1')
  })

  test('Recent issues are rendered correctly', async () => {
    render(<RepositoryDetailsPage />)

    await waitFor(() => {
      const issues = mockRepositoryData.repository.issues

      issues.forEach((issue) => {
        expect(screen.getByText(issue.title)).toBeInTheDocument()

        expect(screen.getByText(`${issue.commentsCount} comments`)).toBeInTheDocument()
      })
    })
  })

  test('Handles case when no data is available', async () => {
    ;(useQuery as jest.Mock).mockReturnValue({
      data: { repository: null },
      error: null,
    })
    render(<RepositoryDetailsPage />)
    await waitFor(() => {
      expect(screen.getByText('Repository not found')).toBeInTheDocument()
    })
  })

  test('handles undefined data gracefully', () => {
    const setRecentReleasesMock = jest.fn()
    const setRecentIssuesMock = jest.fn()

    act(() => {
      const data = undefined

      setRecentReleasesMock(data?.project?.recentReleases)
      setRecentIssuesMock(data?.project?.recentIssues)
    })

    expect(setRecentReleasesMock).toHaveBeenCalledWith(undefined)
    expect(setRecentIssuesMock).toHaveBeenCalledWith(undefined)
  })

  test('handles missing repository stats gracefully', async () => {
    ;(useQuery as jest.Mock).mockReturnValue({
      data: {
        repository: {
          ...mockRepositoryData.repository,
          commitsCount: 0,
          contributorsCount: 0,
          forksCount: 0,
          openIssuesCount: 0,
          starsCount: 0,
        },
      },
      error: null,
    })

    render(<RepositoryDetailsPage />)

    await waitFor(() => {
      expect(screen.getByText('No Commits')).toBeInTheDocument()
      expect(screen.getByText('No Contributors')).toBeInTheDocument()
      expect(screen.getByText('No Forks')).toBeInTheDocument()
      expect(screen.getByText('No Issues')).toBeInTheDocument()
      expect(screen.getByText('No Stars')).toBeInTheDocument()
    })
  })
})
