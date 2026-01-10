import { render } from '@testing-library/react'
import { axe, toHaveNoViolations } from 'jest-axe'
import { ReactNode } from 'react'
import ProjectsDashboardNavBar from 'components/ProjectsDashboardNavBar'

expect.extend(toHaveNoViolations)

jest.mock('next/link', () => {
  return ({ children, href }: { children: ReactNode; href: string }) => {
    return <a href={href}>{children}</a>
  }
})

describe('ProjectsDashboardNavBar a11y', () => {
  it('should not have any accessibility violations', async () => {
    const { container } = render(<ProjectsDashboardNavBar />)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })
})
