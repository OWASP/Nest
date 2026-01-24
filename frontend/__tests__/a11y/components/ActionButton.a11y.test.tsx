import { render } from '@testing-library/react'
import { axe } from 'jest-axe'
import ActionButton from 'components/ActionButton'

describe('ActionButton Accessibility', () => {
  it('should not have any accessibility violations when no url is provided', async () => {
    const { container } = render(<ActionButton>Sample Text</ActionButton>)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })

  it('should not have any accessibility violations when url is provided', async () => {
    const { container } = render(<ActionButton url="https://example.com">Visit Site</ActionButton>)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })

  it('should not have any accessibility violations when tooltipLabel is provided', async () => {
    const { baseElement } = render(
      <ActionButton tooltipLabel="Test Label">Test Button</ActionButton>
    )
    const results = await axe(baseElement)

    expect(results).toHaveNoViolations()
  })
})
