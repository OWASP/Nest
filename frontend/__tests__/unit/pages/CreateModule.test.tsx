import { useMutation, useQuery, useApolloClient } from '@apollo/client/react'
import { screen, fireEvent, waitFor, act } from '@testing-library/react'
import { useRouter, useParams } from 'next/navigation'
import { useSession } from 'next-auth/react'
import { render } from 'wrappers/testUtil'
import CreateModulePage from 'app/my/mentorship/programs/[programKey]/modules/create/page'

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

  beforeEach(() => {
    jest.useFakeTimers()
    ;(useRouter as jest.Mock).mockReturnValue({ push: mockPush, replace: mockReplace })
    ;(useParams as jest.Mock).mockReturnValue({ programKey: 'test-program' })
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

  it('submits the form and navigates to programs page', async () => {
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
      mockCreateModule.mockResolvedValue({}),
      { loading: false },
    ])

    render(<CreateModulePage />)

    // Fill all inputs
    fireEvent.change(screen.getByLabelText('Name *'), {
      target: { value: 'My Test Module' },
    })
    fireEvent.change(screen.getByLabelText(/Description/i), {
      target: { value: 'This is a test module' },
    })
    fireEvent.change(screen.getByLabelText(/Start Date/i), {
      target: { value: '2025-07-15' },
    })
    fireEvent.change(screen.getByLabelText(/End Date/i), {
      target: { value: '2025-08-15' },
    })
    fireEvent.change(screen.getByLabelText(/Domains/i), {
      target: { value: 'AI, ML' },
    })
    fireEvent.change(screen.getByLabelText(/Tags/i), {
      target: { value: 'react, graphql' },
    })

    // Simulate project typing and suggestion click
    fireEvent.change(screen.getByLabelText(/Project Name/i), {
      target: { value: 'Awesome Project' },
    })

    // Run debounce
    await act(async () => {
      jest.runAllTimers()
    })

    const suggestionButton = await screen.findByRole('button', {
      name: /Awesome Project/i,
    })

    fireEvent.click(suggestionButton)

    // Now the form should be valid → submit
    fireEvent.click(screen.getByRole('button', { name: /Create Module/i }))

    await waitFor(() => {
      expect(mockCreateModule).toHaveBeenCalled()
      expect(mockPush).toHaveBeenCalledWith('/my/mentorship/programs/test-program')
    })
  })
})
