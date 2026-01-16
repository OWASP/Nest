import { render } from '@testing-library/react'
import { axe, toHaveNoViolations } from 'jest-axe'
import ToggleableList from 'components/ToggleableList'

expect.extend(toHaveNoViolations)

describe('ToggleableList Accessibility', () => {
  it('should not have any accessibility violations', async () => {
    const mockItems = Array.from({ length: 15 }, (_, i) => `Item ${i + 1}`)
    const { container } = render(<ToggleableList items={mockItems} label="test-label" />)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })
})
