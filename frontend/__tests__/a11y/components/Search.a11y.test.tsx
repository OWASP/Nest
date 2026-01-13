import { render } from '@testing-library/react'
import { axe, toHaveNoViolations } from 'jest-axe'
import SearchBar from 'components/Search'

expect.extend(toHaveNoViolations)

const mockOnSearch = jest.fn()
const defaultProps = {
  isLoaded: false,
  onSearch: mockOnSearch,
  placeholder: 'Search projects...',
}

describe('SearchBar a11y', () => {
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
