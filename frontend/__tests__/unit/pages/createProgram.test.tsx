import { useMutation } from '@apollo/client'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { useUserRoles } from 'hooks/useUserRoles'
import { useRouter } from 'next/navigation'
import { useSession } from 'next-auth/react'
import CreateProgramPage from 'app/mentorship/programs/create/page'

jest.mock('next-auth/react', () => ({
  ...jest.requireActual('next-auth/react'),
  useSession: jest.fn(),
}))

jest.mock('hooks/useUserRoles', () => ({
  useUserRoles: jest.fn(),
}))

jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
}))

jest.mock('@apollo/client', () => {
  const actual = jest.requireActual('@apollo/client')
  return {
    ...actual,
    useMutation: jest.fn(),
    gql: actual.gql,
  }
})

jest.mock('@heroui/toast', () => ({ addToast: jest.fn() }))
jest.mock('components/LoadingSpinner', () => () => <div>Loading...</div>)
jest.mock('components/programCard', () => (props: any) => (
  <form onSubmit={props.onSubmit}>
    <button type="submit">Submit</button>
  </form>
))

describe('CreateProgramPage', () => {
  const mockPush = jest.fn()

  beforeEach(() => {
    jest.clearAllMocks()
    ;(useRouter as jest.Mock).mockReturnValue({ push: mockPush })
    // ✅ Ensure this always returns a valid tuple
    ;(useMutation as jest.Mock).mockReturnValue([jest.fn(), { loading: false }])
  })

  it('renders loading spinner while session or roles are loading', () => {
    ;(useSession as jest.Mock).mockReturnValue({ status: 'loading' })
    ;(useUserRoles as jest.Mock).mockReturnValue({ roles: [], isLoadingRoles: true })

    render(<CreateProgramPage />)
    expect(screen.getByText('Loading...')).toBeInTheDocument()
  })

  it('redirects to /mentorship/programs if user is not a mentor', () => {
    ;(useSession as jest.Mock).mockReturnValue({ status: 'authenticated', data: {} })
    ;(useUserRoles as jest.Mock).mockReturnValue({ roles: [], isLoadingRoles: false })

    render(<CreateProgramPage />)
    expect(mockPush).toHaveBeenCalledWith('/mentorship/programs')
  })

  it('submits form and redirects on success', async () => {
    const mockCreateProgram = jest.fn().mockResolvedValue({})
    ;(useMutation as jest.Mock).mockReturnValue([mockCreateProgram, { loading: false }])
    ;(useSession as jest.Mock).mockReturnValue({ status: 'authenticated', data: {} })
    ;(useUserRoles as jest.Mock).mockReturnValue({
      roles: ['mentor'],
      isLoadingRoles: false,
    })

    render(<CreateProgramPage />)
    fireEvent.click(screen.getByText('Submit'))

    await waitFor(() => {
      expect(mockCreateProgram).toHaveBeenCalled()
      expect(mockPush).toHaveBeenCalledWith('/mentorship/programs')
    })
  })
})
