import { render } from '@testing-library/react'
import { axe } from 'jest-axe'
import MetricsScoreCircle from 'components/MetricsScoreCircle'

describe('MetricsScoreCircle a11y', () => {
  it('should not have any accessibility violations', async () => {
    const { container } = render(<MetricsScoreCircle score={20} />)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })

  it('should not have any accessibility violations when clickable', async () => {
    const { container } = render(<MetricsScoreCircle score={20} clickable />)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })
})
