import { render } from '@testing-library/react'
import { axe } from 'jest-axe'
import { useTheme } from 'next-themes'
import { Icon } from 'types/icon'
import DisplayIcon from 'components/DisplayIcon'

const mockIcons: Icon = {
  starsCount: 1250,
  forksCount: 350,
  contributorsCount: 25,
  contributionCount: 25,
  issuesCount: 42,
  license: 'MIT',
}

describe.each([
  { theme: 'light', name: 'light' },
  { theme: 'dark', name: 'dark' },
])('DisplayIcon a11y ($name theme)', ({ theme }) => {
  beforeEach(() => {
    ;(useTheme as jest.Mock).mockReturnValue({ theme, setTheme: jest.fn() })
  })
  it('should not have any accessibility violations', async () => {
    const { container } = render(<DisplayIcon item="starsCount" icons={mockIcons} />)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })
})
