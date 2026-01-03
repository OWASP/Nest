import { render } from '@testing-library/react'
import { axe, toHaveNoViolations } from 'jest-axe'
import StatusBadge from 'components/StatusBadge'

expect.extend(toHaveNoViolations)

describe('StatusBadge Accessibility', () => {
  it('should not have any accessibility violations', async () => {
    const { container } = render(<StatusBadge status="archived" />)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })
})
