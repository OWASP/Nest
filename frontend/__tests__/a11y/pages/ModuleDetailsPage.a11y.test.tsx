import { useQuery } from '@apollo/client/react'
import { mockModuleData } from '@mockData/mockModuleData'
import { render } from '@testing-library/react'
import { axe } from 'jest-axe'
import { useTheme } from 'next-themes'
import ModuleDetailsPage from 'app/my/mentorship/programs/[programKey]/modules/[moduleKey]/page'

jest.mock('next/navigation', () => ({
  useParams: jest.fn(() => ({
    programKey: 'program-1',
    moduleKey: 'module-1',
  })),
  useRouter: jest.fn(),
}))

jest.mock('@apollo/client/react', () => ({
  useQuery: jest.fn(),
}))

describe.each([
  { theme: 'light', name: 'light' },
  { theme: 'dark', name: 'dark' },
])('ModuleDetailsPage Accessibility ($name theme)', ({ theme }) => {
  beforeEach(() => {
    ;(useTheme as jest.Mock).mockReturnValue({ theme, setTheme: jest.fn() })
    document.documentElement.classList.toggle('dark', theme === 'dark')
  })
  const mockUseQuery = useQuery as unknown as jest.Mock

  it('should have no accessibility violations', async () => {
    mockUseQuery.mockReturnValue({
      loading: false,
      data: {
        getModule: mockModuleData,
        getProgram: {
          admins: [{ login: 'admin1' }],
        },
      },
    })

    const { container } = render(<ModuleDetailsPage />)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })

  it('should have no accessibility violations when loading', async () => {
    mockUseQuery.mockReturnValue({
      data: null,
      loading: true,
      error: null,
    })

    const { container } = render(<ModuleDetailsPage />)
    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })

  it('should have no accessibility violations when error occurs', async () => {
    mockUseQuery.mockReturnValue({
      data: null,
      loading: false,
      error: new Error('test error'),
    })

    const { container } = render(<ModuleDetailsPage />)
    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })

  it('should have no accessibility violations when no data exists', async () => {
    mockUseQuery.mockReturnValue({
      data: null,
      loading: false,
      error: null,
    })

    const { container } = render(<ModuleDetailsPage />)
    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })
})
