import { render } from '@testing-library/react'
import { axe } from 'jest-axe'
import { useTheme } from 'next-themes'
import Badges from 'components/Badges'

const defaultProps = {
  name: 'Test Badge',
  cssClass: 'medal',
}

describe.each([
  { theme: 'light', name: 'light' },
  { theme: 'dark', name: 'dark' },
])('Badges Accessibility ($name theme)', ({ theme }) => {
  beforeEach(() => {
    ;(useTheme as jest.Mock).mockReturnValue({ theme, setTheme: jest.fn() })
    document.documentElement.classList.toggle('dark', theme === 'dark')
  })
  it('should not have any accessibility violations when tooltip is enabled', async () => {
    const { baseElement } = render(<Badges {...defaultProps} />)

    const results = await axe(baseElement)

    expect(results).toHaveNoViolations()
  })

  it('should not have any accessibility violations when tooltip is disabled', async () => {
    const { baseElement } = render(<Badges {...defaultProps} showTooltip={false} />)

    const results = await axe(baseElement)

    expect(results).toHaveNoViolations()
  })
})
