import { render } from '@testing-library/react'
import { axe, toHaveNoViolations } from 'jest-axe'
import { FaHeartPulse } from 'react-icons/fa6'
import ProjectTypeDashboardCard from 'components/ProjectTypeDashboardCard'

expect.extend(toHaveNoViolations)

const baseProps = {
  type: 'healthy' as const,
  count: 42,
  icon: FaHeartPulse,
}

describe('ProjectTypeDashboardCard a11y', () => {
  it('should not have any accessibility violations', async () => {
    const { container } = render(<ProjectTypeDashboardCard {...baseProps} />)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })
})
