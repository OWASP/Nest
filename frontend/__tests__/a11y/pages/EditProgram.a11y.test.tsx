import { useMutation, useQuery } from '@apollo/client/react'
import mockProgramDetailsData from '@mockData/mockProgramData'
import { render } from '@testing-library/react'
import { axe } from 'jest-axe'
import { useSession } from 'next-auth/react'
import EditProgramPage from 'app/my/mentorship/programs/[programKey]/edit/page'

jest.mock('next/navigation', () => ({
  useParams: jest.fn(() => ({ programKey: 'test-program', moduleKey: 'test-module' })),
  useRouter: jest.fn(() => ({ push: jest.fn() })),
}))

jest.mock('@apollo/client/react', () => ({
  useMutation: jest.fn(),
  useQuery: jest.fn(),
  useApolloClient: jest.fn(),
}))

jest.mock('next-auth/react', () => ({
  useSession: jest.fn(),
}))

describe('EditProgramPage Accessibility', () => {
  beforeEach(() => {
    ;(useMutation as unknown as jest.Mock).mockReturnValue([jest.fn(), { loading: false }])
  })

  afterAll(() => {
    jest.clearAllMocks()
  })

  it('should have no accessibility violations', async () => {
    ;(useSession as jest.Mock).mockReturnValue({
      data: { user: { login: 'admin-user' } },
      status: 'authenticated',
    })
    ;(useMutation as unknown as jest.Mock).mockReturnValue([jest.fn(), { loading: false }])
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: {
        getProgram: mockProgramDetailsData.getProgram,
      },
      loading: false,
    })

    const { container } = render(<EditProgramPage />)

    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })

  it('should have no accessibility violations when loading', async () => {
    ;(useSession as jest.Mock).mockReturnValue({
      data: null,
      status: 'loading',
    })

    const { container } = render(<EditProgramPage />)

    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })
})
