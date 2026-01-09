import { render } from '@testing-library/react'
import { axe, toHaveNoViolations } from 'jest-axe'
import Badges from 'components/Badges'

const defaultProps = {
  name: 'Test Badge',
  cssClass: 'medal',
}

expect.extend(toHaveNoViolations)

describe('Badges Accessibility', () => {
  it('should not have any accessibility violations when tooltip is enabled', async () => {
    const { baseElement } = render(<Badges {...defaultProps} />)

    const results = await axe(baseElement)

    expect(results).toHaveNoViolations()
  })

  it('should not have any accessibility violations when tooltip is disabled', async () => {
    const { baseElement } = render(<Badges {...defaultProps} showTooltip={false} />)

    const results = await axe(baseElement)

    expect(results).toHaveNoViolations()
  })
})
