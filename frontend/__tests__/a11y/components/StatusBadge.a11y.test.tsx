import { render } from '@testing-library/react'
import { axe } from 'jest-axe'
import StatusBadge from 'components/StatusBadge'

describe('StatusBadge Accessibility', () => {
  it('should not have any accessibility violations when status is archived', async () => {
    const { container } = render(<StatusBadge status="archived" />)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })

  it('should not have any accessibility violations when status is inactive', async () => {
    const { container } = render(<StatusBadge status="inactive" />)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })
})
