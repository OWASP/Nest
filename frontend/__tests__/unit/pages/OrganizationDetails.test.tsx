import { useQuery } from '@apollo/client'
import { addToast } from '@heroui/toast'
import { screen, waitFor } from '@testing-library/react'
import { mockOrganizationDetailsData } from '@unit/data/mockOrganizationData'
import { formatDate } from 'utils/dateFormatter'
import { render } from 'wrappers/testUtil'
import OrganizationDetailsPage from 'app/organizations/[organizationKey]/page'
import '@testing-library/jest-dom'

jest.mock('@apollo/client', () => ({
  ...jest.requireActual('@apollo/client'),
  useQuery: jest.fn(),
}))

const mockRouter = {
  push: jest.fn(),
}

jest.mock('@heroui/toast', () => ({
  addToast: jest.fn(),
}))

jest.mock('@fortawesome/react-fontawesome', () => ({
  FontAwesomeIcon: () => <span data-testid="mock-icon" />,
}))

jest.mock('next/navigation', () => ({
  ...jest.requireActual('next/navigation'),
  useRouter: jest.fn(() => mockRouter),
  useParams: () => ({ repositoryKey: 'test-org' }),
}))

const mockError = {
  error: new Error('GraphQL error'),
}

describe('OrganizationDetailsPage', () => {
  beforeEach(() => {
    ;(useQuery as jest.Mock).mockReturnValue({
      data: mockOrganizationDetailsData,
      loading: false,
      error: null,
    })
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  test('renders loading state', async () => {
    ;(useQuery as jest.Mock).mockReturnValue({
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
    ;(useQuery as jest.Mock).mockReturnValue({
      data: mockOrganizationDetailsData,
      error: null,
    })

    render(<OrganizationDetailsPage />)

    await waitFor(() => {
      expect(screen.getByText('Test Organization')).toBeInTheDocument()
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
    ;(useQuery as jest.Mock).mockReturnValue({
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
})
