import { render } from '@testing-library/react'
import { axe } from 'jest-axe'
import { useTheme } from 'next-themes'
import Header from 'components/Header'

jest.mock('hooks/useDjangoSession', () => ({
  useDjangoSession: jest.fn(() => ({
    session: null,
    isSyncing: false,
    status: 'unauthenticated',
  })),
}))

jest.mock('hooks/useLogout', () => ({
  useLogout: jest.fn(() => ({
    logout: jest.fn(),
    isLoggingOut: false,
  })),
}))

describe.each([
  { theme: 'light', name: 'light' },
  { theme: 'dark', name: 'dark' },
])('Header a11y ($name theme)', ({ theme }) => {
  beforeEach(() => {
    ;(useTheme as jest.Mock).mockReturnValue({ theme, setTheme: jest.fn() })
    document.documentElement.classList.toggle('dark', theme === 'dark')
    jest.spyOn(console, 'error').mockImplementation((...args) => {
      if (typeof args[0] === 'string' && args[0].includes('non-boolean attribute')) return
      throw new Error(`Console error: ${args.join(' ')}`)
    })
  })

  afterEach(() => {
    jest.restoreAllMocks()
  })

  it('should have no accessibility violations', async () => {
    const { container } = render(
      <main>
        <Header isGitHubAuthEnabled={false} />
      </main>
    )

    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })
})
