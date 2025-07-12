import { useMutation } from '@apollo/client'
import { screen } from '@testing-library/react'
import { useUserRoles } from 'hooks/useUserRoles'
import { useSession } from 'next-auth/react'
import { render } from 'wrappers/testUtil'
import RoleApplicationPage from 'app/mentorship/page'

jest.mock('next-auth/react', () => ({
  ...jest.requireActual('next-auth/react'),
  useSession: jest.fn(),
}))

jest.mock('hooks/useUserRoles', () => ({
  useUserRoles: jest.fn(),
}))
jest.mock('@heroui/toast', () => ({
  addToast: jest.fn(),
}))

jest.mock('@apollo/client', () => {
  const actual = jest.requireActual('@apollo/client')
  return {
    ...actual,
    useMutation: jest.fn(),
    gql: actual.gql,
  }
})

const useSessionMock = useSession as jest.Mock
const useUserRolesMock = useUserRoles as jest.Mock
const useMutationMock = useMutation as jest.Mock

describe('RoleApplicationPage', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    useMutationMock.mockReturnValue([jest.fn(), { loading: false }])
  })

  it('renders loading spinner when session is loading', () => {
    useSessionMock.mockReturnValue({ status: 'loading' })
    useUserRolesMock.mockReturnValue({ roles: [], isLoadingRoles: false })
    useMutationMock.mockReturnValue([jest.fn(), { loading: false }])

    render(<RoleApplicationPage />)

    expect(screen.getByRole('status')).toBeInTheDocument()
  })

  it('shows message when unauthenticated', () => {
    useSessionMock.mockReturnValue({ status: 'unauthenticated' })
    useUserRolesMock.mockReturnValue({ roles: [], isLoadingRoles: false })
    useMutationMock.mockReturnValue([jest.fn(), { loading: false }]) // ✅ fix

    render(<RoleApplicationPage />)

    expect(screen.getByText(/You must be logged in to apply for a role./i)).toBeInTheDocument()
  })

  it('shows spinner while roles are loading', () => {
    useSessionMock.mockReturnValue({ status: 'authenticated' })
    useUserRolesMock.mockReturnValue({ roles: [], isLoadingRoles: true })
    useMutationMock.mockReturnValue([jest.fn(), { loading: false }]) // ✅ fix

    render(<RoleApplicationPage />)

    expect(screen.getAllByAltText('Loading indicator').length).toBeGreaterThan(0)
  })

  it('shows apply buttons when user is not a mentor/contributor', () => {
    useSessionMock.mockReturnValue({ status: 'authenticated' })
    useUserRolesMock.mockReturnValue({ roles: [], isLoadingRoles: false })
    useMutationMock.mockReturnValue([jest.fn(), { loading: false }])

    render(<RoleApplicationPage />)

    expect(screen.getByRole('button', { name: 'Apply as Contributor' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Apply as Mentor' })).toBeInTheDocument()
  })

  it('disables apply button when loading', () => {
    useSessionMock.mockReturnValue({ status: 'authenticated' })
    useUserRolesMock.mockReturnValue({ roles: [], isLoadingRoles: false })
    useMutationMock.mockReturnValue([jest.fn(), { loading: true }])

    render(<RoleApplicationPage />)
    const buttons = screen.getAllByRole('button')
    buttons.forEach((btn) => {
      expect(btn).toBeDisabled()
    })
  })
})
