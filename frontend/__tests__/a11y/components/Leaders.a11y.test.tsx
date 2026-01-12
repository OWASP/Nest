import { mockProjectDetailsData } from '@mockData/mockProjectDetailsData'
import { render } from '@testing-library/react'
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
