import { render } from '@testing-library/react'
import { axe } from 'jest-axe'
import { useTheme } from 'next-themes'
import Pagination from 'components/Pagination'

const props = {
  currentPage: 6,
  totalPages: 10,
  isLoaded: true,
  onPageChange: jest.fn(),
}

describe.each([
  { theme: 'light', name: 'light' },
  { theme: 'dark', name: 'dark' },
])('Pagination a11y ($name theme)', ({ theme }) => {
  beforeEach(() => {
    ;(useTheme as jest.Mock).mockReturnValue({ theme, setTheme: jest.fn() })
    document.documentElement.classList.toggle('dark', theme === 'dark')
  })
  it('should not have any accessibility violations', async () => {
    const { container } = render(<Pagination {...props} />)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })
})
