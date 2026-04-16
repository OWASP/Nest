import { render } from '@testing-library/react'
import { axe } from 'jest-axe'
import { useTheme } from 'next-themes'
import ToggleableList from 'components/ToggleableList'

describe.each([
  { theme: 'light', name: 'light' },
  { theme: 'dark', name: 'dark' },
])('ToggleableList Accessibility ($name theme)', ({ theme }) => {
  beforeEach(() => {
    ;(useTheme as jest.Mock).mockReturnValue({ theme, setTheme: jest.fn() })
    document.documentElement.classList.toggle('dark', theme === 'dark')
  })
  it('should not have any accessibility violations', async () => {
    const mockItems = Array.from({ length: 15 }, (_, i) => `Item ${i + 1}`)
    const { container } = render(<ToggleableList items={mockItems} label="test-label" />)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })
})
