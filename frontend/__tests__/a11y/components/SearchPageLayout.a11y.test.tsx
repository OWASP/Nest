import { render } from '@testing-library/react'
import { axe } from 'jest-axe'
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

describe('SearchPageLayout Accessibility', () => {
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
