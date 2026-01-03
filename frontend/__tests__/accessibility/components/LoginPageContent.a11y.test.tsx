import { render } from '@testing-library/react'
import { axe, toHaveNoViolations } from 'jest-axe'
import LoginPageContent from 'components/LoginPageContent'

expect.extend(toHaveNoViolations)

describe('LoginPage a11y', () => {
  it('should not have any accessibility violations', async () => {
    const { container } = render(<LoginPageContent isGitHubAuthEnabled={true} />)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })
})
