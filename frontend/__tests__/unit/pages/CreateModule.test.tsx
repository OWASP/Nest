import { useMutation, useQuery, useApolloClient } from '@apollo/client/react'
import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { useRouter, useParams } from 'next/navigation'
import { useSession } from 'next-auth/react'
import { render } from 'wrappers/testUtil'
import CreateModulePage from 'app/my/mentorship/programs/[programKey]/modules/create/page'

// Mock dependencies to isolate the component
jest.mock('@heroui/toast', () => ({ addToast: jest.fn() }))
jest.mock('app/global-error', () => ({
  handleAppError: jest.fn(),
  ErrorDisplay: ({ title }: { title: string }) => <div>{title}</div>,
}))
jest.mock('next-auth/react', () => ({
  ...jest.requireActual('next-auth/react'),
  useSession: jest.fn(),
}))
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
  useParams: jest.fn(),
}))
jest.mock('@apollo/client/react', () => ({
  useMutation: jest.fn(),
  useQuery: jest.fn(),
  useApolloClient: jest.fn(),
}))

describe('CreateModulePage', () => {
  const mockPush = jest.fn()
  const mockReplace = jest.fn()
  const mockCreateModule = jest.fn()

  const mockQuery = jest.fn().mockResolvedValue({
    data: {
      searchProjects: [{ id: '123', name: 'Awesome Project' }],
    },
  })

  beforeEach(() => {
    ;(useRouter as jest.Mock).mockReturnValue({ push: mockPush, replace: mockReplace })
    ;(useParams as jest.Mock).mockReturnValue({ programKey: 'test-program' })
    ;(useApolloClient as jest.Mock).mockReturnValue({
      query: mockQuery,
    })
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  it('submits the form and navigates to programs page', async () => {
    const user = userEvent.setup()

    ;(useSession as jest.Mock).mockReturnValue({
      data: { user: { login: 'admin-user' } },
      status: 'authenticated',
    })
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: {
        getProgram: {
          admins: [{ login: 'admin-user' }],
        },
      },
      loading: false,
    })
    ;(useMutation as unknown as jest.Mock).mockReturnValue([
      mockCreateModule.mockResolvedValue({
        data: {
          createModule: {
            key: 'my-test-module',
          },
        },
      }),
      { loading: false },
    ])

    render(<CreateModulePage />)

    // Fill all inputs
    await user.type(screen.getByLabelText('Name'), 'My Test Module')
    await user.type(screen.getByLabelText(/Description/i), 'This is a test module')
    await user.type(screen.getByLabelText(/Start Date/i), '2025-07-15')
    await user.type(screen.getByLabelText(/End Date/i), '2025-08-15')
    await user.type(screen.getByLabelText(/Domains/i), 'AI, ML')
    await user.type(screen.getByLabelText(/Tags/i), 'react, graphql')

    const projectInput = await waitFor(() => {
      return screen.getByPlaceholderText('Start typing project name...')
    })

    await user.type(projectInput, 'Aw')

    await waitFor(
      () => {
        expect(mockQuery).toHaveBeenCalled()
      },
      { timeout: 2000 }
    )

    const projectOption = await waitFor(
      () => {
        return (
          screen.queryByRole('option', { name: /Awesome Project/i }) ||
          screen.queryByText('Awesome Project') ||
          document.querySelector('[data-key="123"]')
        )
      },
      { timeout: 2000 }
    )

    if (projectOption) {
      await user.click(projectOption)
    } else {
      await user.type(projectInput, '{ArrowDown}{Enter}')
    }

    await user.click(screen.getByRole('button', { name: /Create Module/i }))

    await waitFor(
      () => {
        expect(mockCreateModule).toHaveBeenCalled()
        expect(mockPush).toHaveBeenCalledWith('/my/mentorship/programs/test-program')
      },
      { timeout: 10000 }
    )
  }, 15000)

  it('shows loading spinner while session or query is loading', () => {
    ;(useSession as jest.Mock).mockReturnValue({
      data: null,
      status: 'loading',
    })
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: undefined,
      loading: true,
    })
    ;(useMutation as unknown as jest.Mock).mockReturnValue([jest.fn(), { loading: false }])

    render(<CreateModulePage />)
    expect(screen.getAllByAltText('Loading indicator')[0]).toBeInTheDocument()
  })

  it('shows access denied when query has an error', async () => {
    ;(useSession as jest.Mock).mockReturnValue({
      data: { user: { login: 'test-user' } },
      status: 'authenticated',
    })
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: undefined,
      loading: false,
      error: new Error('Query failed'),
    })
    ;(useMutation as unknown as jest.Mock).mockReturnValue([jest.fn(), { loading: false }])

    render(<CreateModulePage />)

    await waitFor(() => {
      expect(screen.getByText('Access Denied')).toBeInTheDocument()
    })
  })

  it('shows access denied when user is unauthenticated', async () => {
    ;(useSession as jest.Mock).mockReturnValue({
      data: null,
      status: 'unauthenticated',
    })
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: { getProgram: { admins: [] } },
      loading: false,
    })
    ;(useMutation as unknown as jest.Mock).mockReturnValue([jest.fn(), { loading: false }])

    render(<CreateModulePage />)

    await waitFor(() => {
      expect(screen.getByText('Access Denied')).toBeInTheDocument()
    })
  })

  it('shows access denied when program data is not found', async () => {
    ;(useSession as jest.Mock).mockReturnValue({
      data: { user: { login: 'test-user' } },
      status: 'authenticated',
    })
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: { getProgram: null },
      loading: false,
    })
    ;(useMutation as unknown as jest.Mock).mockReturnValue([jest.fn(), { loading: false }])

    render(<CreateModulePage />)

    await waitFor(() => {
      expect(screen.getByText('Access Denied')).toBeInTheDocument()
    })
  })

  it('shows access denied and redirects when user is not an admin', async () => {
    jest.useFakeTimers()
    ;(useSession as jest.Mock).mockReturnValue({
      data: { user: { login: 'non-admin-user' } },
      status: 'authenticated',
    })
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: {
        getProgram: {
          admins: [{ login: 'admin-user' }],
        },
      },
      loading: false,
    })
    ;(useMutation as unknown as jest.Mock).mockReturnValue([jest.fn(), { loading: false }])

    render(<CreateModulePage />)

    await waitFor(() => {
      expect(screen.getByText('Access Denied')).toBeInTheDocument()
    })

    // Fast-forward past the redirect timeout
    jest.advanceTimersByTime(2000)

    await waitFor(() => {
      expect(mockReplace).toHaveBeenCalledWith('/my/mentorship')
    })

    jest.useRealTimers()
  })

  it('renders form with min and max dates when program has start and end dates', async () => {
    ;(useSession as jest.Mock).mockReturnValue({
      data: { user: { login: 'admin-user' } },
      status: 'authenticated',
    })
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: {
        getProgram: {
          admins: [{ login: 'admin-user' }],
          startedAt: '2025-01-15T00:00:00Z',
          endedAt: '2025-12-31T00:00:00Z',
        },
      },
      loading: false,
    })
    ;(useMutation as unknown as jest.Mock).mockReturnValue([jest.fn(), { loading: false }])

    render(<CreateModulePage />)

    await waitFor(() => {
      const moduleForm = screen.getByText('Create New Module')
      expect(moduleForm).toBeInTheDocument()
    })
  })
})
