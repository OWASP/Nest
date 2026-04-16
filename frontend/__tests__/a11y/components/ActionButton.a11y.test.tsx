import { render } from '@testing-library/react'
import { axe } from 'jest-axe'
import { useTheme } from 'next-themes'
import ActionButton from 'components/ActionButton'

describe.each([
  { theme: 'light', name: 'light' },
  { theme: 'dark', name: 'dark' },
])('ActionButton Accessibility ($name theme)', ({ theme }) => {
  beforeEach(() => {
    ;(useTheme as jest.Mock).mockReturnValue({ theme, setTheme: jest.fn() })
    document.documentElement.classList.toggle('dark', theme === 'dark')
  })
  it('should not have any accessibility violations when no url is provided', async () => {
    const { container } = render(<ActionButton>Sample Text</ActionButton>)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })

  it('should not have any accessibility violations when url is provided', async () => {
    const { container } = render(<ActionButton url="https://example.com">Visit Site</ActionButton>)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })

  it('should not have any accessibility violations when tooltipLabel is provided', async () => {
    const { baseElement } = render(
      <ActionButton tooltipLabel="Test Label">Test Button</ActionButton>
    )
    const results = await axe(baseElement)

    expect(results).toHaveNoViolations()
  })
})
