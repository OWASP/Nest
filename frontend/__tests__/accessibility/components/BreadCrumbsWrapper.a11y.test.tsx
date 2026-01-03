import { render } from '@testing-library/react'
import { useBreadcrumbs } from 'hooks/useBreadcrumbs'
import { axe, toHaveNoViolations } from 'jest-axe'
import { usePathname } from 'next/navigation'
import BreadCrumbsWrapper from 'components/BreadCrumbsWrapper'

expect.extend(toHaveNoViolations)

jest.mock('next/navigation', () => ({
  usePathname: jest.fn(),
}))

jest.mock('hooks/useBreadcrumbs', () => ({
  useBreadcrumbs: jest.fn(),
}))

describe('BreadcrumbsWrapper a11y', () => {
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
