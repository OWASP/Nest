import { render } from '@testing-library/react'
import { axe, toHaveNoViolations } from 'jest-axe'
import SearchPageLayout from 'components/SearchPageLayout'

expect.extend(toHaveNoViolations)

describe('SearchPageLayout Accessibility', () => {
  it('should not have any accessibility violations', async () => {
    const { container } = render(
      <SearchPageLayout
        isLoaded={true}
        totalPages={1}
        currentPage={1}
        searchQuery=""
        onSearch={() => {}}
        onPageChange={() => {}}
        searchPlaceholder="Search..."
        empty="No results"
        indexName="chapters"
      >
        <div>Mock Content</div>
      </SearchPageLayout>
    )

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })
})
