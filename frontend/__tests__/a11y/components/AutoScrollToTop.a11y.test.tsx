import { render } from '@testing-library/react'
import { axe } from 'jest-axe'
import { useTheme } from 'next-themes'
import AutoScrollToTop from 'components/AutoScrollToTop'

jest.mock('next/navigation', () => ({
  usePathname: () => '/test-path',
}))

beforeAll(() => {
  window.scrollTo = jest.fn()
})

afterAll(() => {
  jest.clearAllMocks()
})

describe.each([
  { theme: 'light', name: 'light' },
  { theme: 'dark', name: 'dark' },
])('AutoScrollToTop Accessibility ($name theme)', ({ theme }) => {
  beforeEach(() => {
    ;(useTheme as jest.Mock).mockReturnValue({ theme, setTheme: jest.fn() })
    document.documentElement.classList.toggle('dark', theme === 'dark')
  })
  it('should not have any accessibility violations', async () => {
    const { container } = render(<AutoScrollToTop />)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })
})
