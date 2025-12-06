import { useMutation, useQuery, useApolloClient } from '@apollo/client/react'
import { addToast } from '@heroui/toast'
import { screen, fireEvent, waitFor, act } from '@testing-library/react'
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

  // Helper function to fill all required form fields
  const fillRequiredFields = () => {
    fireEvent.change(screen.getByLabelText('Name *'), { target: { value: 'Test Module' } })
    fireEvent.change(screen.getByLabelText(/Description/i), {
      target: { value: 'A test description' },
    })
    fireEvent.change(screen.getByLabelText(/Start Date/i), { target: { value: '2025-01-01' } })
    fireEvent.change(screen.getByLabelText(/End Date/i), { target: { value: '2025-01-02' } })
    fireEvent.change(screen.getByLabelText(/Project Name/i), { target: { value: 'Test' } })
  }

  // Helper to handle the asynchronous project selection and form submission
  const selectProjectAndSubmit = async () => {
    // Wait for the debounced search to trigger and for the suggestion to appear
    const suggestionButton = await screen.findByRole('button', { name: /Awesome Project/i })
    fireEvent.click(suggestionButton)

    // Submit the form
    fireEvent.click(screen.getByRole('button', { name: /Create Module/i }))
  }

  beforeEach(() => {
    // Reset mocks before each test to ensure isolation
    jest.clearAllMocks()
    ;(useRouter as jest.Mock).mockReturnValue({ push: mockPush, replace: mockReplace })
    ;(useParams as jest.Mock).mockReturnValue({ programKey: 'test-program' })
    ;(useApolloClient as jest.Mock).mockReturnValue({
      query: jest.fn().mockResolvedValue({
        data: { searchProjects: [{ id: '123', name: 'Awesome Project' }] },
      }),
    })
  })

  it('submits the form and updates cache correctly on success', async () => {
    ;(useSession as jest.Mock).mockReturnValue({
      data: { user: { login: 'admin-user' } },
      status: 'authenticated',
    })
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: { getProgram: { admins: [{ login: 'admin-user' }] } },
      loading: false,
    })
    const mockCache = {
      readQuery: jest.fn().mockReturnValue({ getProgram: {}, getProgramModules: [] }),
      writeQuery: jest.fn(),
    }
    const createModuleFn = jest.fn(async (options) => {
      options.update(mockCache, { data: { createModule: { id: 'new-module' } } })
      return { data: { createModule: { id: 'new-module' } } }
    })
    ;(useMutation as unknown as jest.Mock).mockReturnValue([createModuleFn, { loading: false }])

    render(<CreateModulePage />)
    fillRequiredFields()
    await selectProjectAndSubmit()

    await waitFor(() => {
      expect(mockCache.writeQuery).toHaveBeenCalled()
      expect(mockPush).toHaveBeenCalledWith('/my/mentorship/programs/test-program')
    })
  })

  it('redirects non-admin users', async () => {
    jest.useFakeTimers()
    ;(useSession as jest.Mock).mockReturnValue({
      data: { user: { login: 'not-an-admin' } },
      status: 'authenticated',
    })
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: { getProgram: { admins: [{ login: 'admin-user' }] } },
      loading: false,
    })

    render(<CreateModulePage />)

    await waitFor(() => {
      expect(addToast).toHaveBeenCalledWith(expect.objectContaining({ title: 'Access Denied' }))
    })

    // Advance timers by 1.5 seconds to trigger the redirect
    act(() => {
      jest.advanceTimersByTime(1500)
    })

    await waitFor(() => {
      expect(mockReplace).toHaveBeenCalledWith('/my/mentorship')
    })
    jest.useRealTimers()
  })

  it('handles submission failure correctly', async () => {
    ;(useSession as jest.Mock).mockReturnValue({
      data: { user: { login: 'admin-user' } },
      status: 'authenticated',
    })
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: { getProgram: { admins: [{ login: 'admin-user' }] } },
      loading: false,
    })
    const submissionError = new Error('Submission failed')
    const createModuleFn = jest.fn().mockRejectedValue(submissionError)
    ;(useMutation as unknown as jest.Mock).mockReturnValue([createModuleFn, { loading: false }])

    render(<CreateModulePage />)
    fillRequiredFields()
    await selectProjectAndSubmit()

    await waitFor(() => {
      expect(addToast).toHaveBeenCalledWith(
        expect.objectContaining({ description: submissionError.message })
      )
    })
  })

  it('handles cache updates when cache is empty or mutation data is missing', async () => {
    ;(useSession as jest.Mock).mockReturnValue({
      data: { user: { login: 'admin-user' } },
      status: 'authenticated',
    })
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: { getProgram: { admins: [{ login: 'admin-user' }] } },
      loading: false,
    })
    const mockCache = { readQuery: jest.fn(), writeQuery: jest.fn() }
    const createModuleFn = jest.fn()
    ;(useMutation as unknown as jest.Mock).mockReturnValue([createModuleFn, { loading: false }])

    const { rerender } = render(<CreateModulePage />)

    fillRequiredFields()
    mockCache.readQuery.mockReturnValue(null)
    createModuleFn.mockImplementation(async (options) => {
      options.update(mockCache, { data: { createModule: { id: 'new-module' } } })
      return {}
    })

    await selectProjectAndSubmit()
    await waitFor(() => {
      expect(mockCache.writeQuery).not.toHaveBeenCalled()
      expect(mockPush).toHaveBeenCalledTimes(1)
    })

    rerender(<CreateModulePage />)
    fillRequiredFields()
    mockCache.writeQuery.mockClear()
    mockPush.mockClear()

    mockCache.readQuery.mockReturnValue({ getProgram: {}, getProgramModules: [] })
    createModuleFn.mockImplementation(async (options) => {
      options.update(mockCache, { data: { createModule: null } })
      return {}
    })

    await selectProjectAndSubmit()
    await waitFor(() => {
      expect(mockCache.writeQuery).not.toHaveBeenCalled()
      expect(mockPush).toHaveBeenCalledTimes(1)
    })
  })
})
