import { render } from '@testing-library/react'
import { axe } from 'jest-axe'
import { useTheme } from 'next-themes'
import { FaHeartPulse } from 'react-icons/fa6'
import ProjectTypeDashboardCard from 'components/ProjectTypeDashboardCard'

const baseProps = {
  type: 'healthy' as const,
  count: 42,
  icon: FaHeartPulse,
}

describe.each([
  { theme: 'light', name: 'light' },
  { theme: 'dark', name: 'dark' },
])('ProjectTypeDashboardCard a11y ($name theme)', ({ theme }) => {
  beforeEach(() => {
    ;(useTheme as jest.Mock).mockReturnValue({ theme, setTheme: jest.fn() })
    document.documentElement.classList.toggle('dark', theme === 'dark')
  })
  it('should not have any accessibility violations', async () => {
    const { container } = render(<ProjectTypeDashboardCard {...baseProps} />)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })
})
