import { render } from '@testing-library/react'
import { axe, toHaveNoViolations } from 'jest-axe'
import PageLayout from 'components/PageLayout'

expect.extend(toHaveNoViolations)

describe('PageLayout a11y', () => {
  it('should not have any accessibility violations', async () => {
    const { container } = render(
      <PageLayout title="OWASP ZAP" path="/projects/zap">
        <div>Child Content</div>
      </PageLayout>
    )

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })
})
