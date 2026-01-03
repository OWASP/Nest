import { render } from '@testing-library/react'
import { axe, toHaveNoViolations } from 'jest-axe'
import { FaStar } from 'react-icons/fa6'
import InfoBlock from 'components/InfoBlock'

expect.extend(toHaveNoViolations)

const baseProps = {
  icon: FaStar,
  value: 1500,
  unit: 'contributor',
  pluralizedName: 'contributors',
  precision: 2,
  label: 'Team Members',
  className: 'custom-class',
}

describe('InfoBlock a11y', () => {
  it('should not have any accessibility violations', async () => {
    const { container } = render(<InfoBlock {...baseProps} />)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })
})
