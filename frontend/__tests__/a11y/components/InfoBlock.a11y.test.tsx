import { render } from '@testing-library/react'
import { axe } from 'jest-axe'
import { FaStar } from 'react-icons/fa6'
import InfoBlock from 'components/InfoBlock'

const baseProps = {
  icon: FaStar,
  value: 1500,
  unit: 'contributor',
  pluralizedName: 'contributors',
  precision: 2,
  className: 'custom-class',
}

describe('InfoBlock a11y', () => {
  it('should not have any accessibility violations', async () => {
    const { container } = render(<InfoBlock {...baseProps} />)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })

  it('should not have any accessibility violations when label is provided', async () => {
    const { container } = render(<InfoBlock {...baseProps} label="test-label" />)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })
})
