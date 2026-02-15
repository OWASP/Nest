import { render } from '@testing-library/react'
import { axe } from 'jest-axe'
import { useTheme } from 'next-themes'
import SponsorCard from 'components/SponsorCard'

const defaultProps = {
  target: 'test-target',
  title: 'Test Title',
  type: 'project',
}

describe.each([
  { theme: 'light', name: 'light' },
  { theme: 'dark', name: 'dark' },
])('SponsorCard Accessibility ($name theme)', ({ theme }) => {
  beforeEach(() => {
    ;(useTheme as jest.Mock).mockReturnValue({ theme, setTheme: jest.fn() })
  })
  it('should not have any accessibility violations', async () => {
    const { container } = render(<SponsorCard {...defaultProps} />)
    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })
})
