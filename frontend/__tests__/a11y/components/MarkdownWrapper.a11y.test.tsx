import { render } from '@testing-library/react'
import { axe } from 'jest-axe'
import { useTheme } from 'next-themes'
import MarkdownWrapper from 'components/MarkdownWrapper'

jest.mock('markdown-it', () => {
  return jest.fn().mockImplementation(() => ({
    render: (content: string) => {
      // Very simple mock: replace **bold**
      return content.replaceAll(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    },
    use: jest.fn().mockReturnThis(),
  }))
})

describe.each([
  { theme: 'light', name: 'light' },
  { theme: 'dark', name: 'dark' },
])('MarkdownWrapper a11y ($name theme)', ({ theme }) => {
  beforeEach(() => {
    ;(useTheme as jest.Mock).mockReturnValue({ theme, setTheme: jest.fn() })
    document.documentElement.classList.toggle('dark', theme === 'dark')
  })
  it('should not have any accessibility violations', async () => {
    const { container } = render(<MarkdownWrapper content="test" className="custom-class" />)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })
})
