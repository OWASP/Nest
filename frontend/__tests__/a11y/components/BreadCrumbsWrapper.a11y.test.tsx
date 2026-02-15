import { render } from '@testing-library/react'
import { useBreadcrumbs } from 'hooks/useBreadcrumbs'
import { axe } from 'jest-axe'
import { usePathname } from 'next/navigation'
import { useTheme } from 'next-themes'
import BreadCrumbsWrapper from 'components/BreadCrumbsWrapper'

jest.mock('next/navigation', () => ({
  usePathname: jest.fn(),
}))

jest.mock('hooks/useBreadcrumbs', () => ({
  useBreadcrumbs: jest.fn(),
}))

describe.each([
  { theme: 'light', name: 'light' },
  { theme: 'dark', name: 'dark' },
])('BreadcrumbsWrapper a11y ($name theme)', ({ theme }) => {
  beforeEach(() => {
    ;(useTheme as jest.Mock).mockReturnValue({ theme, setTheme: jest.fn() })
  })
  beforeAll(() => {
    ;(usePathname as jest.Mock).mockReturnValue('/projects/test-project')
    ;(useBreadcrumbs as jest.Mock).mockReturnValue([
      { title: 'Home', path: '/' },
      { title: 'Projects', path: '/projects' },
      { title: 'Test Project', path: '/projects/test-project' },
    ])
  })

  it('should not have any accessibility violations', async () => {
    const { container } = render(<BreadCrumbsWrapper />)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })
})
