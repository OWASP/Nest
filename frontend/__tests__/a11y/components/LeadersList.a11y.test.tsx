import { render } from '@testing-library/react'
import { axe, toHaveNoViolations } from 'jest-axe'
import { ReactNode } from 'react'
import LeadersList from 'components/LeadersList'

expect.extend(toHaveNoViolations)

jest.mock('next/link', () => {
  return function MockLink({
    children,
    href,
    'aria-label': ariaLabel,
    className,
    title,
  }: {
    children: ReactNode
    href: string
    'aria-label'?: string
    className?: string
    title?: string
  }) {
    return (
      <a
        href={href}
        aria-label={ariaLabel}
        className={className}
        title={title}
        data-testid="leader-link"
      >
        {children}
      </a>
    )
  }
})

describe('LeadersList a11y', () => {
  it('should not have any accessibility violations', async () => {
    const { container } = render(<LeadersList leaders={'John Doe, Jane Smith, Bob Johnson'} />)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })
})
