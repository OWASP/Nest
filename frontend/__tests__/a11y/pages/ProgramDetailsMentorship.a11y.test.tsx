import { useQuery } from '@apollo/client/react'
import mockProgramDetailsData from '@mockData/mockProgramData'
import { render } from '@testing-library/react'
import { axe } from 'jest-axe'
import { useTheme } from 'next-themes'
import ProgramDetailsPage from 'app/my/mentorship/programs/[programKey]/page'

jest.mock('next/navigation', () => ({
  useParams: jest.fn(() => ({ programKey: 'test-program' })),
  useRouter: jest.fn(() => ({ replace: jest.fn() })),
  useSearchParams: jest.fn(() => new URLSearchParams()),
}))

jest.mock('@apollo/client/react', () => ({
  useQuery: jest.fn(),
  useMutation: jest.fn(() => [jest.fn()]),
}))

describe.each([
  { theme: 'light', name: 'light' },
  { theme: 'dark', name: 'dark' },
])('ProgramDetailsMentorship ($name theme)', ({ theme }) => {
  beforeEach(() => {
    ;(useTheme as jest.Mock).mockReturnValue({ theme, setTheme: jest.fn() })
    document.documentElement.classList.toggle('dark', theme === 'dark')
  })
  it('should have no accessibility violations', async () => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: mockProgramDetailsData,
      loading: false,
      error: null,
    })

    const { container } = render(<ProgramDetailsPage />)
    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })
})
