import { useApolloClient, useQuery } from '@apollo/client/react'
import { axe } from 'jest-axe'
import { useTheme } from 'next-themes'
import { render } from 'wrappers/testUtil'
import CreateModulePage from 'app/my/mentorship/programs/[programKey]/modules/create/page'

jest.mock('next/navigation', () => ({
  useParams: jest.fn(() => ({ programKey: 'test-program' })),
  useRouter: jest.fn(),
}))

jest.mock('@apollo/client/react', () => ({
  useMutation: jest.fn(() => [jest.fn(), { loading: false }]),
  useQuery: jest.fn(),
  useApolloClient: jest.fn(),
}))

describe.each([
  { theme: 'light', name: 'light' },
  { theme: 'dark', name: 'dark' },
])('CreateModulePage Accessibility ($name theme)', ({ theme }) => {
  beforeEach(() => {
    ;(useTheme as jest.Mock).mockReturnValue({ theme, setTheme: jest.fn() })
    document.documentElement.classList.toggle('dark', theme === 'dark')
  })
  beforeEach(() => {
    ;(useApolloClient as jest.Mock).mockReturnValue({
      query: jest.fn().mockReturnValue({
        data: {
          searchProjects: [{ id: '123', name: 'Awesome Project' }],
        },
      }),
    })
  })

  afterAll(() => {
    jest.clearAllMocks()
  })

  it('should have no accessibility violations', async () => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: {
        getProgram: {
          admins: [{ login: 'admin-user' }],
        },
      },
      loading: false,
    })

    const { container } = render(<CreateModulePage />)

    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })
})
