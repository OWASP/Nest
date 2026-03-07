import { useMutation, useQuery, useApolloClient } from '@apollo/client/react'
import { addToast } from '@heroui/toast'
import { screen, waitFor, act } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { useRouter, useParams } from 'next/navigation'
import { useSession } from 'next-auth/react'
import { render } from 'wrappers/testUtil'
import EditModulePage from 'app/my/mentorship/programs/[programKey]/modules/[moduleKey]/edit/page'
import { ExperienceLevelEnum } from 'types/__generated__/graphql'

// Mocks
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

jest.mock('@heroui/toast', () => ({
  addToast: jest.fn(),
}))

describe('EditModulePage', () => {
  const mockPush = jest.fn()
  const mockReplace = jest.fn()
  const mockUpdateModule = jest.fn()

  beforeEach(() => {
    ;(useRouter as jest.Mock).mockReturnValue({ push: mockPush, replace: mockReplace })
    ;(useParams as jest.Mock).mockReturnValue({
      programKey: 'test-program',
      moduleKey: 'test-module',
    })
    ;(useApolloClient as jest.Mock).mockReturnValue({
      query: jest.fn().mockResolvedValue({
        data: {
          searchProjects: [{ id: '123', name: 'Awesome Project' }],
        },
      }),
    })
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  it('renders and submits form for editing module', async () => {
    ;(useSession as jest.Mock).mockReturnValue({
      data: { user: { login: 'admin-user' } },
      status: 'authenticated',
    })
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      loading: false,
      data: {
        getProgram: {
          admins: [{ login: 'admin-user' }],
        },
        getModule: {
          name: 'Existing Module',
          description: 'Old description',
          experienceLevel: ExperienceLevelEnum.Intermediate,
          startedAt: '2025-07-01',
          endedAt: '2025-07-31',
          domains: ['AI'],
          tags: ['graphql'],
          projectName: 'Awesome Project',
          projectId: '123',
          mentors: [{ login: 'mentor1' }],
        },
      },
    })
    ;(useMutation as unknown as jest.Mock).mockReturnValue([
      mockUpdateModule.mockResolvedValue({}),
      { loading: false },
    ])

    render(<EditModulePage />)

    // Ensure the form loads
    expect(await screen.findByDisplayValue('Existing Module')).toBeInTheDocument()

    // Modify values
    const user = userEvent.setup()

    await user.clear(screen.getByLabelText('Name'))
    await user.type(screen.getByLabelText('Name'), 'Updated Name')

    await user.clear(screen.getByLabelText(/Description/i))
    await user.type(screen.getByLabelText(/Description/i), 'Updated description')

    await user.clear(screen.getByLabelText(/Domains/i))
    await user.type(screen.getByLabelText(/Domains/i), 'AI, ML')

    await user.clear(screen.getByLabelText(/Tags/i))
    await user.type(screen.getByLabelText(/Tags/i), 'graphql, react')

    await user.click(screen.getByRole('button', { name: /Save/i }))

    await waitFor(() => {
      expect(mockUpdateModule).toHaveBeenCalled()
      expect(mockPush).toHaveBeenCalledWith(
        '/my/mentorship/programs/test-program/modules/test-module'
      )
    })
  }, 30000)

  it('shows access denied and redirects if user is not an admin', async () => {
    jest.useFakeTimers()
    try {
      ;(useSession as jest.Mock).mockReturnValue({
        data: { user: { login: 'non-admin-user' } },
        status: 'authenticated',
      })
      ;(useQuery as unknown as jest.Mock).mockReturnValue({
        loading: false,
        data: {
          getProgram: {
            admins: [{ login: 'admin-user' }], // User is not in this list
          },
          getModule: {
            name: 'Existing Module',
          },
        },
      })

      render(<EditModulePage />)

      await waitFor(() => {
        expect(addToast).toHaveBeenCalledWith({
          title: 'Access Denied',
          description: 'Only program admins can edit modules.',
          color: 'danger',
          variant: 'solid',
          timeout: 4000,
        })
      })

      // Advance timers to trigger the redirect
      act(() => {
        jest.advanceTimersByTime(1500)
      })

      await waitFor(() => {
        expect(mockReplace).toHaveBeenCalledWith('/my/mentorship/programs/test-program')
      })
    } finally {
      jest.runOnlyPendingTimers()
      jest.useRealTimers()
    }
  })

  it('shows loading spinner initially', () => {
    ;(useSession as jest.Mock).mockReturnValue({
      data: null,
      status: 'loading',
    })
    ;(useQuery as unknown as jest.Mock).mockReturnValue({ loading: true })

    render(<EditModulePage />)

    expect(screen.getAllByAltText('Loading indicator').length).toBeGreaterThan(0)
  })

  it('shows loading spinner when query returns an error', async () => {
    ;(useSession as jest.Mock).mockReturnValue({
      data: { user: { login: 'admin-user' } },
      status: 'authenticated',
    })
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      loading: false,
      error: new Error('GraphQL error'),
      data: null,
    })
    ;(useMutation as unknown as jest.Mock).mockReturnValue([jest.fn(), { loading: false }])

    await act(async () => {
      render(<EditModulePage />)
    })

    // When denied but formData is null, component shows spinner
    expect(screen.getAllByAltText('Loading indicator').length).toBeGreaterThan(0)
  })

  it('shows loading spinner when user is unauthenticated', async () => {
    ;(useSession as jest.Mock).mockReturnValue({
      data: null,
      status: 'unauthenticated',
    })
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      loading: false,
      data: {
        getProgram: { admins: [{ login: 'admin-user' }] },
        getModule: { name: 'Module' },
      },
    })
    ;(useMutation as unknown as jest.Mock).mockReturnValue([jest.fn(), { loading: false }])

    await act(async () => {
      render(<EditModulePage />)
    })

    // When denied but formData is null, component shows spinner
    expect(screen.getAllByAltText('Loading indicator').length).toBeGreaterThan(0)
  })

  it('handles form submission error gracefully', async () => {
    ;(useSession as jest.Mock).mockReturnValue({
      data: { user: { login: 'admin-user' } },
      status: 'authenticated',
    })
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      loading: false,
      data: {
        getProgram: {
          admins: [{ login: 'admin-user' }],
        },
        getModule: {
          name: 'Existing Module',
          description: 'Old description',
          experienceLevel: ExperienceLevelEnum.Intermediate,
          startedAt: '2025-07-01',
          endedAt: '2025-07-31',
          domains: ['AI'],
          tags: ['graphql'],
          projectName: 'Awesome Project',
          projectId: '123',
          mentors: [{ login: 'mentor1' }],
          labels: [],
        },
      },
    })
    ;(useMutation as unknown as jest.Mock).mockReturnValue([
      mockUpdateModule.mockRejectedValue(new Error('Mutation failed')),
      { loading: false },
    ])

    render(<EditModulePage />)

    // Form successfully loads
    expect(await screen.findByDisplayValue('Existing Module')).toBeInTheDocument()

    const user = userEvent.setup()

    await user.click(screen.getByRole('button', { name: /Save/i }))

    await waitFor(() => {
      expect(mockUpdateModule).toHaveBeenCalled()
    })
  })

  it('renders form with module having missing optional fields', async () => {
    ;(useSession as jest.Mock).mockReturnValue({
      data: { user: { login: 'admin-user' } },
      status: 'authenticated',
    })
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      loading: false,
      data: {
        getProgram: {
          admins: [{ login: 'admin-user' }],
          startedAt: '2025-01-01',
          endedAt: '2025-12-31',
        },
        getModule: {
          name: 'Minimal Module',
          description: '',
          experienceLevel: ExperienceLevelEnum.Beginner,
          startedAt: null,
          endedAt: null,
          domains: [],
          tags: [],
          projectName: null,
          projectId: null,
          mentors: [],
          labels: [],
        },
      },
    })
    ;(useMutation as unknown as jest.Mock).mockReturnValue([
      mockUpdateModule.mockResolvedValue({ data: { updateModule: { key: 'new-key' } } }),
      { loading: false },
    ])

    render(<EditModulePage />)

    expect(await screen.findByDisplayValue('Minimal Module')).toBeInTheDocument()
    // Verify form renders with empty/fallback values for missing optional fields
    expect(screen.getByLabelText('Name')).toHaveValue('Minimal Module')
  })

  it('renders form without program dates', async () => {
    ;(useSession as jest.Mock).mockReturnValue({
      data: { user: { login: 'admin-user' } },
      status: 'authenticated',
    })
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      loading: false,
      data: {
        getProgram: {
          admins: [{ login: 'admin-user' }],
          startedAt: null,
          endedAt: null,
        },
        getModule: {
          name: 'Test Module',
          description: 'Test description',
          experienceLevel: ExperienceLevelEnum.Advanced,
          startedAt: '',
          endedAt: '',
          domains: [],
          tags: [],
          projectName: '',
          projectId: '',
          mentors: [],
          labels: [],
        },
      },
    })
    ;(useMutation as unknown as jest.Mock).mockReturnValue([jest.fn(), { loading: false }])

    render(<EditModulePage />)

    expect(await screen.findByDisplayValue('Test Module')).toBeInTheDocument()
  })
})
