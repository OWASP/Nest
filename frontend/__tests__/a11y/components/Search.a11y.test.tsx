import { render } from '@testing-library/react'
import { axe } from 'jest-axe'
import { useTheme } from 'next-themes'
import SearchBar from 'components/Search'

const mockOnSearch = jest.fn()
const defaultProps = {
  isLoaded: false,
  onSearch: mockOnSearch,
  placeholder: 'Search projects...',
}

describe.each([
  { theme: 'light', name: 'light' },
  { theme: 'dark', name: 'dark' },
])('SearchBar a11y ($name theme)', ({ theme }) => {
  beforeEach(() => {
    ;(useTheme as jest.Mock).mockReturnValue({ theme, setTheme: jest.fn() })
    document.documentElement.classList.toggle('dark', theme === 'dark')
  })
  describe('when not loaded', () => {
    it('should not have any accessibility violations', async () => {
      const { container } = render(<SearchBar {...defaultProps} />)

      const results = await axe(container)

      expect(results).toHaveNoViolations()
    })
  })

  describe('when loaded', () => {
    it('should not have any accessibility violations when searchQuery is empty', async () => {
      const { container } = render(<SearchBar {...defaultProps} isLoaded={true} />)

      const results = await axe(container)

      expect(results).toHaveNoViolations()
    })
    it('should not have any accessibility violations when searchQuery has value', async () => {
      const { container } = render(
        <SearchBar {...defaultProps} isLoaded={true} initialValue="test search" />
      )

      const results = await axe(container)

      expect(results).toHaveNoViolations()
    })
  })
})
