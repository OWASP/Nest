import { render } from '@testing-library/react'
import { axe } from 'jest-axe'
import { useTheme } from 'next-themes'
import MultiSearchBar from 'components/MultiSearch'

const defaultProps = {
  isLoaded: true,
  placeholder: 'Search...',
  indexes: ['chapters', 'users', 'projects'],
  initialValue: 'test-value',
  eventData: [],
}

describe.each([
  { theme: 'light', name: 'light' },
  { theme: 'dark', name: 'dark' },
])('MultiSearch a11y ($name theme)', ({ theme }) => {
  beforeEach(() => {
    ;(useTheme as jest.Mock).mockReturnValue({ theme, setTheme: jest.fn() })
  })
  it('should not have any accessibility violations', async () => {
    const { container } = render(<MultiSearchBar {...defaultProps} />)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })
})
