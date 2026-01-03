import { render } from '@testing-library/react'
import { axe, toHaveNoViolations } from 'jest-axe'
import EntityActions from 'components/EntityActions'

expect.extend(toHaveNoViolations)

describe('EntityActions a11y', () => {
  it('should not have any accessibility violations', async () => {
    const setStatus = jest.fn()

    const { container } = render(
      <EntityActions
        type="program"
        programKey="test-program"
        moduleKey="test-module"
        setStatus={setStatus}
      />
    )

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })
})
