import { render } from '@testing-library/react'
import { axe, toHaveNoViolations } from 'jest-axe'
import { FaUser } from 'react-icons/fa'
import DashboardCard from 'components/DashboardCard'

expect.extend(toHaveNoViolations)

const baseProps = {
  title: 'Test Card',
  icon: FaUser,
  className: undefined,
  stats: undefined,
}

describe('Dashboard a11y', () => {
  it('should not have any accessibility violations', async () => {
    const { container } = render(<DashboardCard {...baseProps} />)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })
})
