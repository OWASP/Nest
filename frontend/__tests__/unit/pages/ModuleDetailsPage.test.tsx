import { useQuery } from '@apollo/client/react'
import { screen, waitFor } from '@testing-library/react'
import { mockModuleData } from '@unit/data/mockModuleData'
import { useParams } from 'next/navigation'
import { render } from 'wrappers/testUtil'
import { handleAppError } from 'app/global-error'
import ModuleDetailsPage from 'app/my/mentorship/programs/[programKey]/modules/[moduleKey]/page'

jest.mock('next/navigation', () => ({
  useParams: jest.fn(),
}))

jest.mock('@apollo/client/react', () => ({
  ...jest.requireActual('@apollo/client/react'),
  useQuery: jest.fn(),
}))

jest.mock('app/global-error', () => ({
  handleAppError: jest.fn(),
  ErrorDisplay: ({ title }) => <div>{title}</div>,
}))

jest.mock('components/LoadingSpinner', () => () => <div>LoadingSpinner</div>)

jest.mock('components/CardDetailsPage', () => (props) => (
  <div data-testid="details-card">
    <div>{props.title}</div>
    <div>{props.summary}</div>
  </div>
))

describe('ModuleDetailsPage', () => {
  const mockUseParams = useParams as jest.Mock
  const mockUseQuery = useQuery as unknown as jest.Mock

  const admins = [{ login: 'admin1' }]

  beforeEach(() => {
    mockUseParams.mockReturnValue({
      programKey: 'program-1',
      moduleKey: 'module-1',
    })
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  it('shows loading spinner initially', () => {
    mockUseQuery.mockReturnValue({ loading: true })

    const { container } = render(<ModuleDetailsPage />)
    expect(container.innerHTML).toContain('LoadingSpinner')
  })

  it('calls error handler on GraphQL error', async () => {
    const error = new Error('Query failed')
    mockUseQuery.mockReturnValue({ error, loading: false })

    render(<ModuleDetailsPage />)

    await waitFor(() => {
      expect(handleAppError).toHaveBeenCalledWith(error)
    })
  })

  it('renders module details when data is present', async () => {
    mockUseQuery.mockReturnValue({
      loading: false,
      data: {
        getModule: mockModuleData,
        getProgram: {
          admins,
        },
      },
    })

    render(<ModuleDetailsPage />)

    expect(await screen.findByTestId('details-card')).toHaveTextContent('Intro to Web')
    expect(screen.getByTestId('details-card')).toHaveTextContent('A beginner friendly module.')
  })
})
