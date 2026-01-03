import { render } from '@testing-library/react'
import { axe, toHaveNoViolations } from 'jest-axe'
import LoadingSpinner from 'components/LoadingSpinner'

expect.extend(toHaveNoViolations)

describe('LoadingSpinner a11y', () => {
  it('should not have any accessibility violations when no prop is provided', async () => {
    const { container } = render(<LoadingSpinner />)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })

  it('should not have any accessibility violations when imageUrl prop is provided', async () => {
    const { container } = render(<LoadingSpinner imageUrl="/img/spinner_white.png" />)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })
})
