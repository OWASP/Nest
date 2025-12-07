import { useMutation } from '@apollo/client/react'
import { addToast } from '@heroui/toast'
import { fireEvent, screen, waitFor } from '@testing-library/react'
import { useRouter as mockUseRouter } from 'next/navigation'
import { useSession as mockUseSession } from 'next-auth/react'
import { render } from 'wrappers/testUtil'
import CreateProgramPage from 'app/my/mentorship/programs/create/page'

jest.mock('@apollo/client/react', () => ({
  ...jest.requireActual('@apollo/client/react'),
  useMutation: jest.fn(),
}))

jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
}))

jest.mock('next-auth/react', () => {
  const actual = jest.requireActual('next-auth/react')
  return {
    ...actual,
    useSession: jest.fn(),
  }
})

jest.mock('@heroui/toast', () => ({
  addToast: jest.fn(),
}))

const mockRouterPush = jest.fn()
const mockCreateProgram = jest.fn()

describe('CreateProgramPage (comprehensive tests)', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    ;(mockUseRouter as jest.Mock).mockReturnValue({ push: mockRouterPush })
    ;(useMutation as unknown as jest.Mock).mockReturnValue([mockCreateProgram, { loading: false }])
  })

  test('redirects if unauthenticated', async () => {
    ;(mockUseSession as jest.Mock).mockReturnValue({
      data: null,
      status: 'unauthenticated',
      loading: false,
    })

    render(<CreateProgramPage />)

    await waitFor(() => {
      expect(mockRouterPush).toHaveBeenCalledWith('/')
    })
  })

  test('shows nothing when session is loading', () => {
    ;(mockUseSession as jest.Mock).mockReturnValue({
      data: null,
      status: 'loading',
      loading: true,
    })

    render(<CreateProgramPage />)

    expect(screen.queryByLabelText('Name *')).not.toBeInTheDocument()
  })

  test('redirects with toast if not a project leader', async () => {
    ;(mockUseSession as jest.Mock).mockReturnValue({
      data: {
        user: {
          name: 'Test User',
          email: 'test@example.com',
          login: 'testuser',
          isLeader: false,
        },
        expires: '2099-01-01T00:00:00.000Z',
      },
      status: 'authenticated',
      loading: false,
    })

    render(<CreateProgramPage />)

    await waitFor(() => {
      expect(addToast).toHaveBeenCalledWith(expect.objectContaining({ title: 'Access Denied' }))
      expect(mockRouterPush).toHaveBeenCalledWith('/')
    })
  })

  test('renders form when user is project leader', async () => {
    ;(mockUseSession as jest.Mock).mockReturnValue({
      data: {
        user: {
          name: 'Test User',
          email: 'test@example.com',
          login: 'testuser',
          isLeader: true,
        },
        expires: '2099-01-01T00:00:00.000Z',
      },
      status: 'authenticated',
      loading: false,
    })

    render(<CreateProgramPage />)

    expect(await screen.findByLabelText('Name *')).toBeInTheDocument()
  })

  test('submits form and redirects on success', async () => {
    ;(mockUseSession as jest.Mock).mockReturnValue({
      data: {
        user: {
          name: 'Test User',
          email: 'test@example.com',
          login: 'testuser',
          isLeader: true,
        },
        expires: '2099-01-01T00:00:00.000Z',
      },
      status: 'authenticated',
      loading: false,
    })

    mockCreateProgram.mockResolvedValue({
      data: { createProgram: { key: 'program_1' } },
    })

    render(<CreateProgramPage />)

    fireEvent.change(screen.getByLabelText('Name *'), {
      target: { value: 'Test Program' },
    })
    fireEvent.change(screen.getByLabelText('Description *'), {
      target: { value: 'A description' },
    })
    fireEvent.change(screen.getByLabelText('Start Date *'), {
      target: { value: '2025-01-01' },
    })
    fireEvent.change(screen.getByLabelText('End Date *'), {
      target: { value: '2025-12-31' },
    })
    fireEvent.change(screen.getByLabelText('Tags'), {
      target: { value: 'tag1, tag2' },
    })
    fireEvent.change(screen.getByLabelText('Domains'), {
      target: { value: 'domain1, domain2' },
    })

    fireEvent.submit(screen.getByText('Save').closest('form')!)

    await waitFor(() => {
      expect(mockCreateProgram).toHaveBeenCalledWith({
        variables: {
          input: {
            name: 'Test Program',
            description: 'A description',
            menteesLimit: 5,
            startedAt: '2025-01-01',
            endedAt: '2025-12-31',
            tags: ['tag1', 'tag2'],
            domains: ['domain1', 'domain2'],
          },
        },
      })

      expect(mockRouterPush).toHaveBeenCalledWith('/my/mentorship')
    })
  })

  test('shows error toast if createProgram mutation fails', async () => {
    ;(mockUseSession as jest.Mock).mockReturnValue({
      data: {
        user: {
          name: 'Test User',
          email: 'test@example.com',
          login: 'testuser',
          isLeader: true,
        },
        expires: '2099-01-01T00:00:00.000Z',
      },
      status: 'authenticated',
      loading: false,
    })

    mockCreateProgram.mockRejectedValue(new Error('Server error'))

    render(<CreateProgramPage />)

    fireEvent.change(screen.getByLabelText('Name *'), {
      target: { value: 'Test Program' },
    })
    fireEvent.change(screen.getByLabelText('Description *'), {
      target: { value: 'A description' },
    })
    fireEvent.change(screen.getByLabelText('Start Date *'), {
      target: { value: '2025-01-01' },
    })
    fireEvent.change(screen.getByLabelText('End Date *'), {
      target: { value: '2025-12-31' },
    })

    fireEvent.submit(screen.getByText('Save').closest('form')!)

    await waitFor(() => {
      expect(addToast).toHaveBeenCalledWith(
        expect.objectContaining({ title: 'GraphQL Request Failed' })
      )
    })
  })
})
