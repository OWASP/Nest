import { render } from '@testing-library/react'
import { axe } from 'jest-axe'
import { useTheme } from 'next-themes'
import { ReactNode } from 'react'
import ProjectsDashboardNavBar from 'components/ProjectsDashboardNavBar'

jest.mock('next/link', () => {
  return ({ children, href }: { children: ReactNode; href: string }) => {
    return <a href={href}>{children}</a>
  }
})

describe.each([
  { theme: 'light', name: 'light' },
  { theme: 'dark', name: 'dark' },
])('ProjectsDashboardNavBar a11y ($name theme)', ({ theme }) => {
  beforeEach(() => {
    ;(useTheme as jest.Mock).mockReturnValue({ theme, setTheme: jest.fn() })
  })
  it('should not have any accessibility violations', async () => {
    const { container } = render(<ProjectsDashboardNavBar />)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })
})
