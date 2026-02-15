import { fireEvent, render, screen } from '@testing-library/react'
import { axe } from 'jest-axe'
import { useTheme } from 'next-themes'
import Footer from 'components/Footer'

describe.each([
  { theme: 'light', name: 'light' },
  { theme: 'dark', name: 'dark' },
])('Footer a11y ($name theme)', ({ theme }) => {
  beforeEach(() => {
    ;(useTheme as jest.Mock).mockReturnValue({ theme, setTheme: jest.fn() })
  })
  it('should not have any accessibility violations', async () => {
    const { container } = render(<Footer />)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })

  it('should not have any accessibility violations when section is opened', async () => {
    const { container } = render(<Footer />)

    const button = screen.getByRole('button', { name: /Resources/ })
    fireEvent.click(button)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })
})
