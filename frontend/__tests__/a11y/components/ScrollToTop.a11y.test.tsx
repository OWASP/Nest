import { render } from '@testing-library/react'
import { axe, toHaveNoViolations } from 'jest-axe'
import ScrollToTop from 'components/ScrollToTop'

expect.extend(toHaveNoViolations)

describe('ScrollToTop a11y', () => {
  it('should not have any accessibility violations', async () => {
    const { container } = render(<ScrollToTop />)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })
})
