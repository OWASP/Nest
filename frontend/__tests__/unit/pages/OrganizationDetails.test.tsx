import { useQuery } from '@apollo/client/react'
import { addToast } from '@heroui/toast'
import { screen, waitFor } from '@testing-library/react'
import { mockOrganizationDetailsData } from '@unit/data/mockOrganizationData'
import { render } from 'wrappers/testUtil'
import OrganizationDetailsPage from 'app/organizations/[organizationKey]/page'
import { formatDate } from 'utils/dateFormatter'
import '@testing-library/jest-dom'

jest.mock('@apollo/client/react', () => ({
  ...jest.requireActual('@apollo/client/react'),
  useQuery: jest.fn(),
}))

const mockRouter = {
  push: jest.fn(),
}

jest.mock('@heroui/toast', () => ({
  addToast: jest.fn(),
}))

jest.mock('next/navigation', () => ({
  ...jest.requireActual('next/navigation'),
  useRouter: jest.fn(() => mockRouter),
  useParams: () => ({ repositoryKey: 'test-org' }),
  usePathname: jest.fn(() => '/organizations/test-org'),
}))

const mockError = {
  error: new Error('GraphQL error'),
}

describe('OrganizationDetailsPage', () => {
  beforeEach(() => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: mockOrganizationDetailsData,
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
      error: null,
    })

    render(<OrganizationDetailsPage />)

    const loadingSpinner = screen.getAllByAltText('Loading indicator')
    await waitFor(() => {
      expect(loadingSpinner.length).toBeGreaterThan(0)
    })
  })

  test('renders organization details when data is available', async () => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: mockOrganizationDetailsData,
      error: null,
    })

    render(<OrganizationDetailsPage />)

    await waitFor(() => {
      expect(screen.getByRole('heading', { name: 'Test Organization' })).toBeInTheDocument()
    })

    expect(screen.getByText('@test-org')).toBeInTheDocument()
    expect(screen.getByText('San Francisco, CA')).toBeInTheDocument()
    expect(screen.getByText('1000')).toBeInTheDocument()
    expect(
      screen.getByText(formatDate(mockOrganizationDetailsData.organization.createdAt))
    ).toBeInTheDocument()
  })

  test('renders organization stats correctly', async () => {
    render(<OrganizationDetailsPage />)

    await waitFor(() => {
      expect(screen.getByText('5K Stars')).toBeInTheDocument()
      expect(screen.getByText('1.2K Forks')).toBeInTheDocument()
      expect(screen.getByText('150 Contributors')).toBeInTheDocument()
      expect(screen.getByText('300 Issues')).toBeInTheDocument()
      expect(screen.getByText('25 Repositories')).toBeInTheDocument()
    })
  })

  test('renders issues section correctly', async () => {
    render(<OrganizationDetailsPage />)

    await waitFor(() => {
      expect(screen.getByText('Test Issue 1')).toBeInTheDocument()
      expect(screen.getByText('Test Issue 2')).toBeInTheDocument()
    })
  })

  test('renders releases section correctly', async () => {
    render(<OrganizationDetailsPage />)

    await waitFor(() => {
      expect(screen.getByText('Release v1.0.0')).toBeInTheDocument()
      expect(screen.getByText('Release v2.0.0')).toBeInTheDocument()
    })
  })

  test('renders milestones section correctly', async () => {
    render(<OrganizationDetailsPage />)
    await waitFor(() => {
      const recentMilestones = mockOrganizationDetailsData.recentMilestones

      for (const milestone of recentMilestones) {
        expect(screen.getByText(milestone.title)).toBeInTheDocument()
        expect(screen.getByText(milestone.repositoryName)).toBeInTheDocument()
        expect(screen.getByText(`${milestone.openIssuesCount} open`)).toBeInTheDocument()
        expect(screen.getByText(`${milestone.closedIssuesCount} closed`)).toBeInTheDocument()
      }
    })
  })

  test('handles no recent releases gracefully', async () => {
    const noReleasesData = {
      ...mockOrganizationDetailsData,
      recentReleases: [],
    }
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: noReleasesData,
      loading: false,
      error: null,
    })
    render(<OrganizationDetailsPage />)
    await waitFor(() => {
      expect(screen.getByText('Recent Releases')).toBeInTheDocument()
      expect(screen.queryByText('Test v1.0.0')).not.toBeInTheDocument()
    })
  })

  test('renders no milestones correctly', async () => {
    const noMilestones = {
      ...mockOrganizationDetailsData,
      recentMilestones: [],
    }

    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: noMilestones,
      loading: false,
      error: null,
    })

    render(<OrganizationDetailsPage />)
    await waitFor(() => {
      expect(screen.getByText('Recent Milestones')).toBeInTheDocument()
      expect(screen.queryByText('v2.0.0 Release')).not.toBeInTheDocument()
    })
  })

  test('renders pull requests section correctly', async () => {
    render(<OrganizationDetailsPage />)

    await waitFor(() => {
      expect(screen.getByText('Test Pull Request 1')).toBeInTheDocument()
      expect(screen.getByText('Test Pull Request 2')).toBeInTheDocument()
    })
  })

  test('renders top contributors section correctly', async () => {
    render(<OrganizationDetailsPage />)

    await waitFor(() => {
      expect(screen.getByText('User One')).toBeInTheDocument()
      expect(screen.getByText('User Two')).toBeInTheDocument()
      expect(screen.getByText('User Three')).toBeInTheDocument()
    })
  })

  test('displays error message when there is a GraphQL error', async () => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: undefined,
      error: mockError,
    })

    render(<OrganizationDetailsPage />)

    await waitFor(() => {
      expect(screen.getByText('Organization not found')).toBeInTheDocument()
      expect(addToast).toHaveBeenCalledWith({
        description: 'An unexpected server error occurred.',
        title: 'Server Error',
        timeout: 5000,
        shouldShowTimeoutProgress: true,
        color: 'danger',
        variant: 'solid',
      })
    })
  })
  test('does not render sponsor block', async () => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: mockOrganizationDetailsData,
      error: null,
    })
    render(<OrganizationDetailsPage />)
    await waitFor(() => {
      expect(screen.queryByText('Want to become a sponsor?')).toBeNull()
    })
  })
})
