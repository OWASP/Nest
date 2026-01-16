import { render } from '@testing-library/react'
import { axe, toHaveNoViolations } from 'jest-axe'
import MultiSearchBar from 'components/MultiSearch'

expect.extend(toHaveNoViolations)

const defaultProps = {
  isLoaded: true,
  placeholder: 'Search...',
  indexes: ['chapters', 'users', 'projects'],
  initialValue: 'test-value',
  eventData: [],
}

describe('MultiSearch a11y', () => {
  it('should not have any accessibility violations', async () => {
    const { container } = render(<MultiSearchBar {...defaultProps} />)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })
})
