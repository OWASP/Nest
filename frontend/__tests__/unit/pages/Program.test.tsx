import { useQuery } from '@apollo/client'
import { addToast } from '@heroui/toast'
import { screen, fireEvent, waitFor } from '@testing-library/react'
import { useUserRoles } from 'hooks/useUserRoles'
import { useSession } from 'next-auth/react'
import { render } from 'wrappers/testUtil'
import ProgramsSearchPage from 'app/mentorship/programs/page'

jest.mock('hooks/useUserRoles')
jest.mock('@apollo/client')
jest.mock('@heroui/toast', () => ({ addToast: jest.fn() }))

const mockRouter = {
  push: jest.fn(),
  replace: jest.fn(),
}

jest.mock('next/navigation', () => ({
  useRouter: () => mockRouter,
  useParams: () => ({ userKey: 'test-user' }),
  useSearchParams: () => new URLSearchParams('q=&page=1'),
}))

jest.mock('next-auth/react', () => ({
  useSession: jest.fn(),
}))

jest.mock('wrappers/FontAwesomeIconWrapper', () => ({
  __esModule: true,
  default: () => <span data-testid="mock-icon" />,
}))

jest.mock('@/components/MarkdownWrapper', () => {
  return ({ content, className }: { content: string; className?: string }) => (
    <div
      className={`md-wrapper ${className || ''}`}
      dangerouslySetInnerHTML={{ __html: content }}
    />
  )
})

describe('ProgramsSearchPage', () => {
  const mockProgramsData = {
    allPrograms: {
      totalPages: 1,
      currentPage: 1,
      programs: [
        {
          id: '1',
          name: 'Test Program',
          description: 'Test description',
          startedAt: '2025-01-01',
          endedAt: '2025-12-31',
          key: 'test-program',
        },
      ],
    },
  }

  beforeEach(() => {
    jest.clearAllMocks()
    ;(useSession as jest.Mock).mockReturnValue({
      data: { user: { login: 'mockuser' } },
      status: 'authenticated',
    })
    ;(useUserRoles as jest.Mock).mockReturnValue({
      roles: ['mentor'],
      isLoadingRoles: false,
    })
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  it('renders programs list correctly', async () => {
    ;(useQuery as jest.Mock).mockReturnValue({
      data: mockProgramsData,
      loading: false,
      error: undefined,
    })

    render(<ProgramsSearchPage />)

    expect(await screen.findByText('Test Program')).toBeInTheDocument()
    expect(screen.getByText('Test description')).toBeInTheDocument()
    expect(screen.getByText('View Details')).toBeInTheDocument()
  })

  it('shows toast error if query fails', async () => {
    ;(useQuery as jest.Mock).mockReturnValue({
      data: undefined,
      loading: false,
      error: new Error('Query failed'),
    })

    render(<ProgramsSearchPage />)

    await waitFor(() => {
      expect(addToast).toHaveBeenCalledWith(
        expect.objectContaining({
          title: 'GraphQL Error',
          description: 'Unable to fetch programs',
        })
      )
    })
  })

  it('clicking "My Programs" sets mentor filter', async () => {
    ;(useQuery as jest.Mock).mockReturnValue({
      data: {
        allPrograms: {
          totalPages: 1,
          currentPage: 1,
          programs: [],
        },
      },
      loading: false,
      error: undefined,
    })

    render(<ProgramsSearchPage />)

    const button = await screen.findByText('My Programs')
    fireEvent.click(button)

    await waitFor(() => {
      expect(screen.getByText('All Programs')).toBeInTheDocument()
    })
  })

  it('navigates to program detail on button click', async () => {
    ;(useQuery as jest.Mock).mockReturnValue({
      data: mockProgramsData,
      loading: false,
      error: undefined,
    })

    render(<ProgramsSearchPage />)

    fireEvent.click(await screen.findByText('View Details'))

    await waitFor(() => {
      expect(mockRouter.push).toHaveBeenCalledWith('/mentorship/programs/test-program')
    })
  })
})
