import { render } from '@testing-library/react'
import { axe } from 'jest-axe'
import { useTheme } from 'next-themes'
import StatusBadge from 'components/StatusBadge'

describe.each([
  { theme: 'light', name: 'light' },
  { theme: 'dark', name: 'dark' },
])('StatusBadge Accessibility ($name theme)', ({ theme }) => {
  beforeEach(() => {
    ;(useTheme as jest.Mock).mockReturnValue({ theme, setTheme: jest.fn() })
  })
  it('should not have any accessibility violations when status is archived', async () => {
    const { container } = render(<StatusBadge status="archived" />)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })

  it('should not have any accessibility violations when status is inactive', async () => {
    const { container } = render(<StatusBadge status="inactive" />)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })
})
