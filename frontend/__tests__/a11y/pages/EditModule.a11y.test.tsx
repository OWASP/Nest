import { useQuery } from '@apollo/client/react'
import { mockModuleData } from '@mockData/mockModuleData'
import mockProgramDetailsData from '@mockData/mockProgramData'
import { axe } from 'jest-axe'
import { useTheme } from 'next-themes'
import { render } from 'wrappers/testUtil'
import EditModulePage from 'app/my/mentorship/programs/[programKey]/modules/[moduleKey]/edit/page'

jest.mock('next/navigation', () => ({
  useParams: jest.fn(() => ({ programKey: 'test-program', moduleKey: 'test-module' })),
  useRouter: jest.fn(() => ({ push: jest.fn() })),
}))

jest.mock('@apollo/client/react', () => ({
  useMutation: jest.fn(() => [jest.fn(), { loading: false }]),
  useQuery: jest.fn(),
  useApolloClient: jest.fn(),
}))

describe.each([
  { theme: 'light', name: 'light' },
  { theme: 'dark', name: 'dark' },
])('EditModulePage Accessibility ($name theme)', ({ theme }) => {
  beforeEach(() => {
    ;(useTheme as jest.Mock).mockReturnValue({ theme, setTheme: jest.fn() })
  })
  it('should have no accessibility violations', async () => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: {
        getProgram: mockProgramDetailsData.getProgram,
        getModule: mockModuleData,
      },
      loading: false,
    })

    const { container } = render(<EditModulePage />)

    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })
})
