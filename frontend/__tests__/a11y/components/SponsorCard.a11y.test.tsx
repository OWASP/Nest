import { render } from '@testing-library/react'
import { axe, toHaveNoViolations } from 'jest-axe'
import { ReactNode } from 'react'
import SponsorCard from 'components/SponsorCard'

expect.extend(toHaveNoViolations)

jest.mock('next/link', () => ({
  __esModule: true,
  default: ({
    href,
    children,
    ...props
  }: {
    href: string
    children: ReactNode
    [key: string]: unknown
  }) => (
    <a href={href} {...props}>
      {children}
    </a>
  ),
}))

const defaultProps = {
  target: 'test-target',
  title: 'Test Title',
  type: 'project',
}

describe('SponsorCard Accessibility', () => {
  it('should not have any accessibility violations', async () => {
    const { container } = render(<SponsorCard {...defaultProps} />)
    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })
})
