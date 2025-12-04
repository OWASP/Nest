import { useQuery } from '@apollo/client/react'
import { render, screen, waitFor } from '@testing-library/react'
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
jest.mock('@apollo/client/react', () => {
  const actual = jest.requireActual('@apollo/client/react')
  return {
    ...actual,
    useMutation: jest.fn(() => [jest.fn(), { loading: false }]),
    useQuery: jest.fn(),
  }
})
jest.mock('@heroui/toast', () => ({
  addToast: jest.fn(),
}))

describe('EditProgramPage', () => {
  const mockPush = jest.fn()
  const mockReplace = jest.fn()

  beforeEach(() => {
    ;(useRouter as jest.Mock).mockReturnValue({ push: mockPush, replace: mockReplace })
    ;(useParams as jest.Mock).mockReturnValue({ programKey: 'program_1' })
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

    expect(await screen.findByLabelText('Name *')).toBeInTheDocument()
    expect(screen.getByDisplayValue('Test')).toBeInTheDocument()
  })
})
