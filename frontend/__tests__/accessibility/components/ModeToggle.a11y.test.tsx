import { render } from '@testing-library/react'
import { axe, toHaveNoViolations } from 'jest-axe'
import ModeToggle from 'components/ModeToggle'

expect.extend(toHaveNoViolations)

describe('ModeToggle a11y', () => {
  it('should not have any accessibility violations', async () => {
    const { container } = render(<ModeToggle />)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })
})
