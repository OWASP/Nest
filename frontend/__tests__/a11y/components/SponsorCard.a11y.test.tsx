import { render } from '@testing-library/react'
import { axe, toHaveNoViolations } from 'jest-axe'
import SponsorCard from 'components/SponsorCard'

expect.extend(toHaveNoViolations)

const defaultProps = {
  target: 'test-target',
  title: 'Test Title',
  type: 'project',
}

describe('SponsorCard Accessibility', () => {
  it('should not have any accessibility violations', async () => {
    const { container } = render(<SponsorCard {...defaultProps} />)
    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })
})
