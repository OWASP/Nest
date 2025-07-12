import { useQuery, useMutation } from '@apollo/client'
import { screen, waitFor, fireEvent } from '@testing-library/react'
import { useParams } from 'next/navigation'
import { useSession } from 'next-auth/react'
import { render } from 'wrappers/testUtil'
import { handleAppError } from 'app/global-error'
import ProgramDetailsPage from 'app/mentorship/programs/[programKey]/page'

jest.mock('next/navigation', () => ({
  useParams: jest.fn(),
}))

jest.mock('next-auth/react', () => ({
  __esModule: true,
  useSession: jest.fn(),
}))

jest.mock('@apollo/client', () => ({
  ...jest.requireActual('@apollo/client'),
  useQuery: jest.fn(),
  useMutation: jest.fn(),
}))

jest.mock('@heroui/toast', () => ({ addToast: jest.fn() }))

jest.mock('app/global-error', () => ({
  handleAppError: jest.fn(),
  ErrorDisplay: ({ title }) => <div>{title}</div>,
}))

jest.mock('components/CardDetailsPage', () => (props) => (
  <div data-testid="details-card">
    <div>{props.title}</div>
    {props.isDraft && (
      <button onClick={props.setPublish} data-testid="publish-btn">
        Publish
      </button>
    )}
  </div>
))

describe('ProgramDetailsPage', () => {
  const mockUseQuery = useQuery as jest.Mock
  const mockUseMutation = useMutation as jest.Mock
  const mockUseSession = useSession as jest.Mock
  const mockUseParams = useParams as jest.Mock

  const program = {
    id: '1',
    key: 'prog-123',
    name: 'My Program',
    status: 'draft',
    startedAt: '2025-01-01',
    endedAt: '2025-12-31',
    menteesLimit: 10,
    experienceLevels: ['beginner'],
    tags: ['tag1'],
    domains: ['domain1'],
    description: 'desc',
    admins: [{ login: 'adminuser' }],
  }

  beforeEach(() => {
    mockUseParams.mockReturnValue({ programKey: 'prog-123' })
    mockUseSession.mockReturnValue({
      data: { user: { login: 'adminuser' } },
      status: 'authenticated',
    })

    // Provide a default mutation mock to avoid "undefined is not iterable"
    mockUseMutation.mockReturnValue([jest.fn(), {}])
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  it('shows loading spinner', async () => {
    mockUseQuery.mockReturnValue({ loading: true })

    render(<ProgramDetailsPage />)
    const loadingSpinner = screen.getAllByAltText('Loading indicator')
    await waitFor(() => {
      expect(loadingSpinner.length).toBeGreaterThan(0)
    }) // Replace with actual text if needed
  })

  it('shows not found error if no program returned', async () => {
    mockUseQuery.mockReturnValue({ loading: false, data: { program: null } })

    render(<ProgramDetailsPage />)
    expect(await screen.findByText('Program Not Found')).toBeInTheDocument()
  })

  it('renders program when data is present', async () => {
    mockUseQuery.mockReturnValue({ loading: false, data: { program, modulesByProgram: [] } })

    render(<ProgramDetailsPage />)
    expect(await screen.findByTestId('details-card')).toHaveTextContent('My Program')
  })

  it('shows publish button for admin when status is draft', async () => {
    mockUseQuery.mockReturnValue({ loading: false, data: { program, modulesByProgram: [] } })

    render(<ProgramDetailsPage />)
    expect(await screen.findByTestId('publish-btn')).toBeInTheDocument()
  })

  it('calls mutation on publish button click', async () => {
    const updateMock = jest.fn().mockResolvedValue({})
    mockUseMutation.mockReturnValue([updateMock, {}])
    mockUseQuery.mockReturnValue({ loading: false, data: { program, modulesByProgram: [] } })

    render(<ProgramDetailsPage />)

    const btn = await screen.findByTestId('publish-btn')
    fireEvent.click(btn)

    await waitFor(() => {
      expect(updateMock).toHaveBeenCalledWith({
        variables: {
          inputData: {
            key: 'prog-123',
            name: 'My Program',
            status: 'PUBLISHED',
          },
        },
        refetchQueries: expect.any(Array),
      })
    })
  })

  it('prevents publish if user is not admin', async () => {
    mockUseSession.mockReturnValue({
      data: { user: { login: 'notadmin' } },
      status: 'authenticated',
    })

    mockUseQuery.mockReturnValue({ loading: false, data: { program, modulesByProgram: [] } })

    render(<ProgramDetailsPage />)

    expect(screen.queryByTestId('publish-btn')).not.toBeInTheDocument()
  })

  it('calls error handler on GraphQL error', async () => {
    const error = new Error('Query failed')
    mockUseQuery.mockReturnValue({ error, loading: false })

    render(<ProgramDetailsPage />)

    await waitFor(() => {
      expect(handleAppError).toHaveBeenCalledWith(error)
    })
  })
})
