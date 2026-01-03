import { render } from '@testing-library/react'
import { axe, toHaveNoViolations } from 'jest-axe'
import BreadCrumbsWrapper from 'components/BreadCrumbsWrapper'

expect.extend(toHaveNoViolations)

describe('BreadcrumbsWrapper a11y', () => {
  it('should not have any accessibility violations', async () => {
    const { container } = render(<BreadCrumbsWrapper />)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })
})
