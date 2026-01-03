import { render } from '@testing-library/react'
import { axe, toHaveNoViolations } from 'jest-axe'
import { TruncatedText } from 'components/TruncatedText'

expect.extend(toHaveNoViolations)

describe('TruncatedText Accessibility', () => {
  it('should not have any accessibility violations', async () => {
    const { container } = render(<TruncatedText />)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })
})
