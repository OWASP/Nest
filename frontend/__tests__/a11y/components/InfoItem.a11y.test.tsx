import { render } from '@testing-library/react'
import { axe, toHaveNoViolations } from 'jest-axe'
import { FaUser } from 'react-icons/fa6'
import InfoItem from 'components/InfoItem'

expect.extend(toHaveNoViolations)

describe('InfoItem a11y', () => {
  it('should not have any accessibility violations', async () => {
    const { container } = render(<InfoItem icon={FaUser} unit="user" value={1000} />)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })
})
