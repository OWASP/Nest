import { render } from '@testing-library/react'
import { axe, toHaveNoViolations } from 'jest-axe'
import { TruncatedText } from 'components/TruncatedText'

expect.extend(toHaveNoViolations)

describe('TruncatedText Accessibility', () => {
  it('should not have any accessibility violations', async () => {
    const longText = 'This is a long text that should be truncated'
    const { container } = render(<TruncatedText text={longText} />)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })
})
