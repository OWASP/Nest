import { render } from '@testing-library/react'
import { axe } from 'jest-axe'
import { useTheme } from 'next-themes'
import { TruncatedText } from 'components/TruncatedText'

describe.each([
  { theme: 'light', name: 'light' },
  { theme: 'dark', name: 'dark' },
])('TruncatedText Accessibility ($name theme)', ({ theme }) => {
  beforeEach(() => {
    ;(useTheme as jest.Mock).mockReturnValue({ theme, setTheme: jest.fn() })
    document.documentElement.classList.toggle('dark', theme === 'dark')
  })
  it('should not have any accessibility violations', async () => {
    const longText = 'This is a long text that should be truncated'
    const { container } = render(<TruncatedText text={longText} />)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })
})
