import { render } from '@testing-library/react'
import { axe } from 'jest-axe'
import { useTheme } from 'next-themes'
import SearchPageLayout from 'components/SearchPageLayout'

const baseProps = {
  currentPage: 1,
  searchQuery: '',
  onSearch: () => {},
  onPageChange: () => {},
  searchPlaceholder: 'Search...',
  empty: 'No results',
  indexName: 'chapters',
}

describe.each([
  { theme: 'light', name: 'light' },
  { theme: 'dark', name: 'dark' },
])('SearchPageLayout Accessibility ($name theme)', ({ theme }) => {
  beforeEach(() => {
    ;(useTheme as jest.Mock).mockReturnValue({ theme, setTheme: jest.fn() })
    document.documentElement.classList.toggle('dark', theme === 'dark')
  })
  describe('should not have any accessibility violations when isLoaded is true', () => {
    it('has more than one total pages', async () => {
      const { container } = render(
        <SearchPageLayout {...baseProps} totalPages={2} isLoaded={true}>
          <div>Mock Content</div>
        </SearchPageLayout>
      )

      const results = await axe(container)

      expect(results).toHaveNoViolations()
    })

    it('has 0 total page', async () => {
      const { container } = render(
        <SearchPageLayout {...baseProps} totalPages={0} isLoaded={true}>
          <div>Mock Content</div>
        </SearchPageLayout>
      )

      const results = await axe(container)

      expect(results).toHaveNoViolations()
    })
  })

  describe('should not have any accessibility violations when isLoaded is false', () => {
    it('has more than one total pages', async () => {
      const { container } = render(
        <SearchPageLayout isLoaded={false} {...baseProps} totalPages={2} />
      )
      const results = await axe(container)

      expect(results).toHaveNoViolations()
    })

    it('has 0 total page', async () => {
      const { container } = render(
        <SearchPageLayout isLoaded={false} {...baseProps} totalPages={0} />
      )
      const results = await axe(container)

      expect(results).toHaveNoViolations()
    })
  })
})
