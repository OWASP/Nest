import { render } from '@testing-library/react'
import { axe } from 'jest-axe'
import { useTheme } from 'next-themes'
import { ReactNode } from 'react'
import LeadersList from 'components/LeadersList'

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

describe.each([
  { theme: 'light', name: 'light' },
  { theme: 'dark', name: 'dark' },
])('LeadersList a11y ($name theme)', ({ theme }) => {
  beforeEach(() => {
    ;(useTheme as jest.Mock).mockReturnValue({ theme, setTheme: jest.fn() })
  })
  it('should not have any accessibility violations', async () => {
    const { container } = render(<LeadersList leaders={'John Doe, Jane Smith, Bob Johnson'} />)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })
})
