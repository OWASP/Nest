import { render, waitFor } from '@testing-library/react'
import { axe } from 'jest-axe'
import { useTheme } from 'next-themes'
import FontLoaderWrapper from 'components/FontLoaderWrapper'

const originalFonts = document.fonts

describe.each([
  { theme: 'light', name: 'light' },
  { theme: 'dark', name: 'dark' },
])('FontLoaderWrapper a11y ($name theme)', ({ theme }) => {
  beforeEach(() => {
    ;(useTheme as jest.Mock).mockReturnValue({ theme, setTheme: jest.fn() })
    document.documentElement.classList.toggle('dark', theme === 'dark')
    Object.defineProperty(document, 'fonts', {
      value: { ready: Promise.resolve() },
      configurable: true,
    })
  })

  afterEach(() => {
    Object.defineProperty(document, 'fonts', {
      value: originalFonts,
      configurable: true,
    })
  })

  it('should have no accessibility violations', async () => {
    const { container } = render(
      <FontLoaderWrapper>
        <div>Content</div>
      </FontLoaderWrapper>
    )

    await waitFor(() => {
      expect(container.textContent).toContain('Content')
    })

    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })
})
