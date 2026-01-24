import { render } from '@testing-library/react'
import { axe } from 'jest-axe'
import SponsorCard from 'components/SponsorCard'

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
