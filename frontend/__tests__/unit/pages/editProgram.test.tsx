import { useQuery, useMutation } from '@apollo/client'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { useRouter, useParams } from 'next/navigation'
import { useSession } from 'next-auth/react'
import EditProgramPage from 'app/mentorship/programs/[programKey]/edit/page'


jest.mock('next-auth/react', () => ({
  ...jest.requireActual('next-auth/react'),
  useSession: jest.fn(),
}))

jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
  useParams: jest.fn(),
}))

jest.mock('@apollo/client', () => {
  const actual = jest.requireActual('@apollo/client')
  return {
    ...actual,
    useQuery: jest.fn(),
    useMutation: jest.fn(),
    gql: actual.gql,
  }
})

jest.mock('@heroui/toast', () => ({ addToast: jest.fn() }))
jest.mock('app/global-error', () => ({
  ErrorDisplay: () => <div>Access Denied</div>,
  handleAppError: jest.fn(),
}))
jest.mock('components/LoadingSpinner', () => () => <div>Loading...</div>)
jest.mock('components/programCard', () => (props: any) => (
  <form onSubmit={props.onSubmit}>
    <button type="submit">{props.submitText}</button>
  </form>
))

describe('EditProgramPage', () => {
  const mockPush = jest.fn()
  const mockReplace = jest.fn()

  beforeEach(() => {
    jest.clearAllMocks()
    ;(useParams as jest.Mock).mockReturnValue({ programKey: 'test-program' })
    ;(useRouter as jest.Mock).mockReturnValue({ push: mockPush, replace: mockReplace })
    ;(useMutation as jest.Mock).mockReturnValue([jest.fn(), { loading: false }])
  })

  it('renders loading spinner when session or query is loading', () => {
    ;(useSession as jest.Mock).mockReturnValue({ status: 'loading' })
    ;(useQuery as jest.Mock).mockReturnValue({ loading: true })
    render(<EditProgramPage />)
    expect(screen.getByText('Loading...')).toBeInTheDocument()
  })

  it('denies access if user is not admin', async () => {
    ;(useSession as jest.Mock).mockReturnValue({
      status: 'authenticated',
      data: { user: { login: 'nonadmin' } },
    })
    ;(useQuery as jest.Mock).mockReturnValue({
      loading: false,
      data: {
        program: {
          admins: [{ login: 'adminuser' }],
        },
      },
    })

    render(<EditProgramPage />)

    await waitFor(() => {
      expect(screen.getByText('Access Denied')).toBeInTheDocument()
    })
  })

  it('submits form and redirects on success', async () => {
    const mockUpdate = jest.fn().mockResolvedValue({})
    ;(useMutation as jest.Mock).mockReturnValue([mockUpdate, { loading: false }])
    ;(useSession as jest.Mock).mockReturnValue({
      status: 'authenticated',
      data: { user: { login: 'adminuser' } },
    })
    ;(useQuery as jest.Mock).mockReturnValue({
      loading: false,
      data: {
        program: {
          name: 'Test Program',
          description: 'A test program',
          menteesLimit: 5,
          startedAt: '2025-07-01',
          endedAt: '2025-07-31',
          experienceLevels: ['BEGINNER'],
          tags: ['tag1'],
          domains: ['domain1'],
          admins: [{ login: 'adminuser' }],
          status: 'DRAFT',
        },
      },
    })

    render(<EditProgramPage />)
    fireEvent.click(screen.getByText('Save Changes'))

    await waitFor(() => {
      expect(mockUpdate).toHaveBeenCalled()
      expect(mockPush).toHaveBeenCalledWith('/mentorship/programs')
    })
  })
})
