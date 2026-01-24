import { Breadcrumbs } from '@heroui/react'
import { render } from '@testing-library/react'
import { axe } from 'jest-axe'

describe('Breadcrumbs a11y', () => {
  it('should not have any accessibility violations', async () => {
    const { container } = render(<Breadcrumbs />)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })
})
