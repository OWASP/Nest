import { render } from '@testing-library/react'
import { axe, toHaveNoViolations } from 'jest-axe'
import SecondaryCard from 'components/SecondaryCard'

expect.extend(toHaveNoViolations)

describe('SecondaryCard a11y', () => {
  it('should not have any accessibility violations', async () => {
    const { container } = render(<SecondaryCard />)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })
})
