import { render } from '@testing-library/react'
import { axe, toHaveNoViolations } from 'jest-axe'
import MetricsScoreCircle from 'components/MetricsScoreCircle'

expect.extend(toHaveNoViolations)

describe('MetricsScoreCircle a11y', () => {
  it('should not have any accessibility violations', async () => {
    const { container } = render(<MetricsScoreCircle score={20} />)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })
})
