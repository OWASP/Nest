import { render } from '@testing-library/react'
import { axe } from 'jest-axe'
import { useTheme } from 'next-themes'
import { FaHome } from 'react-icons/fa'
import { FaUser } from 'react-icons/fa6'
import { NavButtonProps } from 'types/button'
import NavButton from 'components/NavButton'

jest.mock('next/link', () => ({ children, href }) => <a href={href}>{children}</a>)

const defaultProps: NavButtonProps & { defaultIcon: typeof FaHome; hoverIcon: typeof FaUser } = {
  href: '/test-path',
  defaultIcon: FaHome,
  hoverIcon: FaUser,
  text: 'Test Button',
}

describe.each([
  { theme: 'light', name: 'light' },
  { theme: 'dark', name: 'dark' },
])('NavButton a11y ($name theme)', ({ theme }) => {
  beforeEach(() => {
    ;(useTheme as jest.Mock).mockReturnValue({ theme, setTheme: jest.fn() })
  })
  it('should not have any accessibility violations', async () => {
    const { container } = render(<NavButton {...defaultProps} />)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })
})
