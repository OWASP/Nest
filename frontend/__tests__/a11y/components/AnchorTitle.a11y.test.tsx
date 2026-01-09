import { render } from '@testing-library/react'
import { axe, toHaveNoViolations } from 'jest-axe'
import AnchorTitle from 'components/AnchorTitle'

expect.extend(toHaveNoViolations)

describe('AnchorTitle Accessibility', () => {
  it('should not have any accessibility violations', async () => {
    const { container } = render(<AnchorTitle title="Test Title" />)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })
})
