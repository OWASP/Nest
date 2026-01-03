import { render } from '@testing-library/react'
import { axe, toHaveNoViolations } from 'jest-axe'
import { Icon } from 'types/icon'
import DisplayIcon from 'components/DisplayIcon'

expect.extend(toHaveNoViolations)

const mockIcons: Icon = {
  starsCount: 1250,
  forksCount: 350,
  contributorsCount: 25,
  contributionCount: 25,
  issuesCount: 42,
  license: 'MIT',
}

describe('DisplayIcon a11y', () => {
  it('should not have any accessibility violations', async () => {
    const { container } = render(<DisplayIcon item="starsCount" icons={mockIcons} />)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })
})
