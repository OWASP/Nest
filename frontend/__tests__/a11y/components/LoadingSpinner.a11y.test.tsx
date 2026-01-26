import { render } from '@testing-library/react'
import { axe } from 'jest-axe'
import LoadingSpinner from 'components/LoadingSpinner'

describe('LoadingSpinner a11y', () => {
  it('should not have any accessibility violations', async () => {
    const { container } = render(<LoadingSpinner />)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })
})
