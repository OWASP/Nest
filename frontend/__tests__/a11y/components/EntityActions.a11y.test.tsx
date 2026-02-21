import { fireEvent, render, screen } from '@testing-library/react'
import { axe } from 'jest-axe'
import { useTheme } from 'next-themes'
import EntityActions from 'components/EntityActions'

describe.each([
  { theme: 'light', name: 'light' },
  { theme: 'dark', name: 'dark' },
])('EntityActions a11y ($name theme)', ({ theme }) => {
  beforeEach(() => {
    ;(useTheme as jest.Mock).mockReturnValue({ theme, setTheme: jest.fn() })
    document.documentElement.classList.toggle('dark', theme === 'dark')
  })
  it('should not have any accessibility violations', async () => {
    const setStatus = jest.fn()

    const { container } = render(
      <EntityActions
        type="program"
        programKey="test-program"
        moduleKey="test-module"
        setStatus={setStatus}
      />
    )

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })

  it('should not have any accessibility violations when dropDown is open', async () => {
    const setStatus = jest.fn()

    const { container } = render(
      <EntityActions
        type="program"
        programKey="test-program"
        moduleKey="test-module"
        setStatus={setStatus}
      />
    )

    const toggleButton = screen.getByRole('button', { name: /Program actions menu/ })
    fireEvent.click(toggleButton)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })
})
