import { render, screen } from '@testing-library/react'
import { axe } from 'jest-axe'
import { useTheme } from 'next-themes'
import ModeToggle from 'components/ModeToggle'

describe.each([
  { theme: 'light', name: 'light' },
  { theme: 'dark', name: 'dark' },
])('ModeToggle a11y ($name theme)', ({ theme }) => {
  beforeEach(() => {
    ;(useTheme as jest.Mock).mockReturnValue({ theme, setTheme: jest.fn() })
  })
  it('should not have any accessibility violations', async () => {
    const { baseElement } = render(<ModeToggle />)

    await screen.findByRole('button', {
      name: theme === 'light' ? /Enable dark mode/i : /Enable light mode/i,
    })

    const results = await axe(baseElement)

    expect(results).toHaveNoViolations()
  })
})
