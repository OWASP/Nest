import { render } from '@testing-library/react'
import { axe } from 'jest-axe'
import { useTheme } from 'next-themes'
import { FaStar } from 'react-icons/fa6'
import InfoBlock from 'components/InfoBlock'

const baseProps = {
  icon: FaStar,
  value: 1500,
  unit: 'contributor',
  pluralizedName: 'contributors',
  precision: 2,
  className: 'custom-class',
}

describe.each([
  { theme: 'light', name: 'light' },
  { theme: 'dark', name: 'dark' },
])('InfoBlock a11y ($name theme)', ({ theme }) => {
  beforeEach(() => {
    ;(useTheme as jest.Mock).mockReturnValue({ theme, setTheme: jest.fn() })
    document.documentElement.classList.toggle('dark', theme === 'dark')
  })
  it('should not have any accessibility violations', async () => {
    const { container } = render(<InfoBlock {...baseProps} />)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })

  it('should not have any accessibility violations when label is provided', async () => {
    const { container } = render(<InfoBlock {...baseProps} label="test-label" />)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })
})
