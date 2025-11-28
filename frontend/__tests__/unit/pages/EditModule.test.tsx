import { useMutation, useQuery, useApolloClient } from '@apollo/client/react'
import { screen, fireEvent, waitFor, act } from '@testing-library/react'
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

describe('EditModulePage', () => {
  const mockPush = jest.fn()
  const mockReplace = jest.fn()
  const mockUpdateModule = jest.fn()

  beforeEach(() => {
    jest.useFakeTimers()
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
    jest.runOnlyPendingTimers()
    jest.useRealTimers()
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
    fireEvent.change(screen.getByLabelText('Name *'), {
      target: { value: 'Updated Name' },
    })
    fireEvent.change(screen.getByLabelText(/Description/i), {
      target: { value: 'Updated description' },
    })
    fireEvent.change(screen.getByLabelText(/Domains/i), {
      target: { value: 'AI, ML' },
    })
    fireEvent.change(screen.getByLabelText(/Tags/i), {
      target: { value: 'graphql, react' },
    })
    fireEvent.change(screen.getByLabelText(/Project Name/i), {
      target: { value: 'Awesome Project' },
    })

    await act(async () => {
      jest.runAllTimers()
    })

    fireEvent.click(screen.getByRole('button', { name: /Save/i }))

    await waitFor(() => {
      expect(mockUpdateModule).toHaveBeenCalled()
      expect(mockPush).toHaveBeenCalledWith('/my/mentorship/programs/test-program')
    })
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
})
