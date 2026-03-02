import { render } from '@testing-library/react'
import { axe } from 'jest-axe'
import { useTheme } from 'next-themes'
import { FaUser } from 'react-icons/fa6'
import InfoItem from 'components/InfoItem'

describe.each([
  { theme: 'light', name: 'light' },
  { theme: 'dark', name: 'dark' },
])('InfoItem a11y ($name theme)', ({ theme }) => {
  beforeEach(() => {
    ;(useTheme as jest.Mock).mockReturnValue({ theme, setTheme: jest.fn() })
    document.documentElement.classList.toggle('dark', theme === 'dark')
  })
  it('should not have any accessibility violations', async () => {
    const { container } = render(<InfoItem icon={FaUser} unit="user" value={1000} />)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })
})
