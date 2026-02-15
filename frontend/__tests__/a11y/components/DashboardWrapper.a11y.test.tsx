import { render } from '@testing-library/react'
import { axe } from 'jest-axe'
import { useTheme } from 'next-themes'
import DashboardWrapper from 'components/DashboardWrapper'

jest.mock('hooks/useDjangoSession', () => ({
  useDjangoSession: jest.fn(() => ({
    isSyncing: false,
    session: { user: { isOwaspStaff: true } },
  })),
}))

describe.each([
  { theme: 'light', name: 'light' },
  { theme: 'dark', name: 'dark' },
])('DashboardWrapper a11y ($name theme)', ({ theme }) => {
  beforeEach(() => {
    ;(useTheme as jest.Mock).mockReturnValue({ theme, setTheme: jest.fn() })
  })
  it('should have no accessibility violations', async () => {
    const { container } = render(
      <DashboardWrapper>
        <div>Dashboard Content</div>
      </DashboardWrapper>
    )

    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })
})
