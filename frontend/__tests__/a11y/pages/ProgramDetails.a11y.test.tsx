import { useQuery } from '@apollo/client/react'
import mockProgramDetailsData from '@mockData/mockProgramData'
import { waitFor, screen } from '@testing-library/react'
import { axe } from 'jest-axe'
import { useTheme } from 'next-themes'
import { render } from 'wrappers/testUtil'
import ProgramDetailsPage from 'app/mentorship/programs/[programKey]/page'

jest.mock('@apollo/client/react', () => ({
  useQuery: jest.fn(),
}))

jest.mock('next/navigation', () => ({
  useRouter: () => ({ replace: jest.fn() }),
  useParams: () => ({ programKey: 'test-program' }),
  useSearchParams: () => new URLSearchParams(),
}))

describe.each([
  { theme: 'light', name: 'light' },
  { theme: 'dark', name: 'dark' },
])('ProgramDetailsPage Accessibility ($name theme)', ({ theme }) => {
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

    await waitFor(() => {
      expect(screen.getByText('Test Program')).toBeInTheDocument()
    })

    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })
})
