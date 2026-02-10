import { useQuery, useApolloClient, useMutation } from '@apollo/client/react'
import { addToast } from '@heroui/toast'
import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import { useParams, useRouter } from 'next/navigation'
import { useSession } from 'next-auth/react'
import EditProgramPage from 'app/my/mentorship/programs/[programKey]/edit/page'
import { ProgramStatusEnum } from 'types/__generated__/graphql'

jest.mock('next-auth/react', () => ({
  useSession: jest.fn(),
}))
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
  useParams: jest.fn(),
}))

const mockUpdateProgram = jest.fn()

jest.mock('@apollo/client/react', () => {
  const actual = jest.requireActual('@apollo/client/react')
  return {
    ...actual,
    useMutation: jest.fn(),
    useQuery: jest.fn(),
    useApolloClient: jest.fn(),
  }
})
jest.mock('@heroui/toast', () => ({
  addToast: jest.fn(),
}))

describe('EditProgramPage', () => {
  const mockPush = jest.fn()
  const mockReplace = jest.fn()
  const mockQuery = jest.fn().mockResolvedValue({
    data: {
      myPrograms: {
        programs: [],
      },
    },
  })

  beforeEach(() => {
    ;(useRouter as jest.Mock).mockReturnValue({ push: mockPush, replace: mockReplace })
    ;(useParams as jest.Mock).mockReturnValue({ programKey: 'program_1' })
    ;(useApolloClient as jest.Mock).mockReturnValue({
      query: mockQuery,
    })
    ;(useMutation as unknown as jest.Mock).mockReturnValue([mockUpdateProgram, { loading: false }])
    jest.clearAllMocks()
  })

  test('shows loading spinner while checking access', () => {
    ;(useSession as jest.Mock).mockReturnValue({ status: 'loading' })
    ;(useQuery as unknown as jest.Mock).mockReturnValue({ loading: true })

    render(<EditProgramPage />)

    expect(screen.getAllByAltText('Loading indicator')).toHaveLength(2)
  })

  test('denies access for non-admins and redirects', async () => {
    ;(useSession as jest.Mock).mockReturnValue({
      data: { user: { login: 'nonadmin' } },
      status: 'authenticated',
    })
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      loading: false,
      data: {
        getProgram: {
          admins: [{ login: 'admin1' }],
        },
      },
    })

    render(<EditProgramPage />)

    await waitFor(async () => {
      expect(await screen.findByText('Access Denied')).toBeInTheDocument()
    })
  })

  test('renders form for valid admin', async () => {
    ;(useSession as jest.Mock).mockReturnValue({
      data: { user: { login: 'admin1' } },
      status: 'authenticated',
    })
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      loading: false,
      data: {
        getProgram: {
          name: 'Test',
          description: 'Test description',
          menteesLimit: 10,
          startedAt: '2025-01-01',
          endedAt: '2025-12-31',
          tags: ['react', 'js'],
          domains: ['web'],
          admins: [{ login: 'admin1' }],
          status: ProgramStatusEnum.Draft,
        },
      },
    })

    render(<EditProgramPage />)

    expect(await screen.findByLabelText('Name')).toBeInTheDocument()
    expect(screen.getByDisplayValue('Test')).toBeInTheDocument()
  })

  test('denies access when session user has no login property', async () => {
    ;(useSession as jest.Mock).mockReturnValue({
      data: { user: { name: 'User Without Login' } },
      status: 'authenticated',
    })
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      loading: false,
      data: {
        getProgram: {
          admins: [{ login: 'admin1' }],
        },
      },
    })

    render(<EditProgramPage />)

    await waitFor(async () => {
      expect(await screen.findByText('Access Denied')).toBeInTheDocument()
    })
  })

  test('denies access when program data is not found', async () => {
    ;(useSession as jest.Mock).mockReturnValue({
      data: { user: { login: 'admin1' } },
      status: 'authenticated',
    })
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      loading: false,
      data: null,
    })

    render(<EditProgramPage />)

    await waitFor(async () => {
      expect(await screen.findByText('Access Denied')).toBeInTheDocument()
    })
  })

  test('submits form successfully and navigates', async () => {
    ;(useSession as jest.Mock).mockReturnValue({
      data: { user: { login: 'admin1' } },
      status: 'authenticated',
    })
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      loading: false,
      data: {
        getProgram: {
          name: 'Test',
          description: 'Test description',
          menteesLimit: 10,
          startedAt: '2025-01-01',
          endedAt: '2025-12-31',
          tags: ['react', 'js'],
          domains: ['web'],
          admins: [{ login: 'admin1' }],
          status: ProgramStatusEnum.Draft,
        },
      },
    })
    mockUpdateProgram.mockResolvedValue({
      data: { updateProgram: { key: 'program_1' } },
    })

    render(<EditProgramPage />)

    await waitFor(async () => {
      expect(await screen.findByLabelText('Name')).toBeInTheDocument()
    })

    const submitButton = screen.getByRole('button', { name: /save/i })
    fireEvent.click(submitButton)

    await waitFor(() => {
      expect(mockUpdateProgram).toHaveBeenCalled()
      expect(addToast).toHaveBeenCalledWith(
        expect.objectContaining({
          title: 'Program Updated',
          color: 'success',
        })
      )
      expect(mockPush).toHaveBeenCalledWith('/my/mentorship/programs/program_1')
    })
  })

  test('handles form submission error', async () => {
    ;(useSession as jest.Mock).mockReturnValue({
      data: { user: { login: 'admin1' } },
      status: 'authenticated',
    })
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      loading: false,
      data: {
        getProgram: {
          name: 'Test',
          description: 'Test description',
          menteesLimit: 10,
          startedAt: '2025-01-01',
          endedAt: '2025-12-31',
          tags: ['react', 'js'],
          domains: ['web'],
          admins: [{ login: 'admin1' }],
          status: ProgramStatusEnum.Draft,
        },
      },
    })
    mockUpdateProgram.mockRejectedValue(new Error('Update failed'))

    render(<EditProgramPage />)

    await waitFor(async () => {
      expect(await screen.findByLabelText('Name')).toBeInTheDocument()
    })

    const submitButton = screen.getByRole('button', { name: /save/i })
    fireEvent.click(submitButton)

    await waitFor(() => {
      expect(addToast).toHaveBeenCalledWith(
        expect.objectContaining({
          title: 'Update Failed',
          color: 'danger',
        })
      )
    })
  })

  test('uses default program key when mutation returns no key', async () => {
    ;(useSession as jest.Mock).mockReturnValue({
      data: { user: { login: 'admin1' } },
      status: 'authenticated',
    })
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      loading: false,
      data: {
        getProgram: {
          name: 'Test',
          description: 'Test description',
          menteesLimit: 10,
          startedAt: '2025-01-01',
          endedAt: '2025-12-31',
          tags: ['react', 'js'],
          domains: ['web'],
          admins: [{ login: 'admin1' }],
          status: ProgramStatusEnum.Draft,
        },
      },
    })
    mockUpdateProgram.mockResolvedValue({
      data: { updateProgram: null },
    })

    render(<EditProgramPage />)

    await waitFor(async () => {
      expect(await screen.findByLabelText('Name')).toBeInTheDocument()
    })

    const submitButton = screen.getByRole('button', { name: /save/i })
    fireEvent.click(submitButton)

    await waitFor(() => {
      expect(mockPush).toHaveBeenCalledWith('/my/mentorship/programs/program_1')
    })
  })

  test('handles graphql query error', async () => {
    ;(useSession as jest.Mock).mockReturnValue({
      data: { user: { login: 'admin1' } },
      status: 'authenticated',
    })
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      loading: false,
      data: {
        getProgram: {
          name: 'Test',
          admins: [{ login: 'admin1' }],
          status: ProgramStatusEnum.Draft,
        },
      },
      error: new Error('GraphQL error'),
    })

    render(<EditProgramPage />)

    await waitFor(async () => {
      expect(await screen.findByLabelText('Name')).toBeInTheDocument()
    })
  })

  test('handles program with null/empty fields and multiple admins', async () => {
    ;(useSession as jest.Mock).mockReturnValue({
      data: { user: { login: 'admin1' } },
      status: 'authenticated',
    })
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      loading: false,
      data: {
        getProgram: {
          name: 'Test',
          description: null,
          menteesLimit: null,
          startedAt: '2025-01-01',
          endedAt: '2025-12-31',
          tags: null,
          domains: null,
          admins: [{ login: 'admin1' }, { login: 'admin2' }],
          status: null,
        },
      },
    })

    render(<EditProgramPage />)

    await waitFor(async () => {
      expect(await screen.findByLabelText('Name')).toBeInTheDocument()
    })
  })

  test('redirects after timeout when access is denied', async () => {
    jest.useFakeTimers()
    ;(useSession as jest.Mock).mockReturnValue({
      data: { user: { login: 'nonadmin' } },
      status: 'authenticated',
    })
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      loading: false,
      data: {
        getProgram: {
          admins: [{ login: 'admin1' }],
        },
      },
    })

    render(<EditProgramPage />)

    await waitFor(async () => {
      expect(await screen.findByText('Access Denied')).toBeInTheDocument()
    })

    jest.advanceTimersByTime(1500)

    await waitFor(() => {
      expect(mockReplace).toHaveBeenCalledWith('/my/mentorship/programs')
    })

    jest.useRealTimers()
  })
})
