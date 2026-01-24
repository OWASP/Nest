import { render } from '@testing-library/react'
import { axe } from 'jest-axe'
import ScrollToTop from 'components/ScrollToTop'

describe('ScrollToTop a11y', () => {
  it('should not have any accessibility violations', async () => {
    const { container } = render(<ScrollToTop />)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })
})
