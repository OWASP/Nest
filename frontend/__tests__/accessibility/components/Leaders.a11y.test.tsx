import { render } from '@testing-library/react'
import { mockProjectDetailsData } from '@unit/data/mockProjectDetailsData'
import { axe, toHaveNoViolations } from 'jest-axe'
import Leaders from 'components/Leaders'

expect.extend(toHaveNoViolations)

describe('Leaders a11y', () => {
  it('should not have any accessibility violations', async () => {
    const { container } = render(<Leaders users={mockProjectDetailsData.project.entityLeaders} />)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })
})
