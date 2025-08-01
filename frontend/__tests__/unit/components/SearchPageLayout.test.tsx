import { render, screen } from '@testing-library/react'
import SearchPageLayout from 'components/SearchPageLayout'

describe('<SearchPageLayout />', () => {
  it('renders SearchBar and loading spinner when not loaded', () => {
    render(
      <SearchPageLayout
        isLoaded={false}
        totalPages={0}
        currentPage={1}
        searchQuery=""
        onSearch={() => {}}
        onPageChange={() => {}}
        searchPlaceholder="Search..."
        empty="No results"
        indexName="unknown-index" // ✅ triggers the <LoadingSpinner> (default case)
      />
    )

    // Should render the <img> in LoadingSpinner
    expect(screen.getAllByRole('img').length).toBeGreaterThan(0)
  })

  it('renders children content and hides spinner when loaded', () => {
    render(
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

    // ✅ Should show the mock content
    expect(screen.getByText('Mock Content')).toBeInTheDocument()

    // ✅ Should NOT show the loading spinner
    const images = screen.queryAllByRole('img')
    expect(images.length).toBe(0)
  })

  it('renders empty message when totalPages is 0 and loaded', ()=>{
       render(
      <SearchPageLayout
        isLoaded={true}
        totalPages={0}
        currentPage={1}
        searchQuery=""
        onSearch={() => {}}
        onPageChange={() => {}}
        searchPlaceholder="Search..."
        empty="Nothing here"
        indexName="any-index"
      >
        <div>Child Content</div>
      </SearchPageLayout>
    )
    expect(screen.getByText('Nothing here')).toBeInTheDocument()
  })

  it('renders pagination when totalPages > 1 and isLoaded is true', () => {
    render(
    <SearchPageLayout
      isLoaded={true}
      totalPages={5}
      currentPage={1}
      searchQuery=""
      onSearch={() => {}}
      onPageChange={() => {}}
      searchPlaceholder="Search..."
      empty="No results"
      indexName="any-index"
    >
      <div>Some content</div>
    </SearchPageLayout>
  )
  expect(screen.getByText('Next')).toBeInTheDocument()
  expect(screen.getByText('Prev')).toBeInTheDocument()
  
  })
 
  it('renders sortChildren when totalPages > 0 and isLoaded is true', () => {
  render(
    <SearchPageLayout
      isLoaded={true}
      totalPages={3}
      currentPage={1}
      searchQuery=""
      onSearch={() => {}}
      onPageChange={() => {}}
      searchPlaceholder="Search..."
      empty="No results"
      indexName="any-index"
      sortChildren={<div>Sort Options</div>}
    >
      <div>Some content</div>
    </SearchPageLayout>
  )

  expect(screen.getByText('Sort Options')).toBeInTheDocument()
})
  it('does not render pagination when totalPages = 1', () => {
  render(
    <SearchPageLayout
      isLoaded={true}
      totalPages={1}
      currentPage={1}
      searchQuery=""
      onSearch={() => {}}
      onPageChange={() => {}}
      searchPlaceholder="Search..."
      empty="No results"
      indexName="any-index"
    >
      <div>Some content</div>
    </SearchPageLayout>
  )

  expect(screen.queryByText('Prev')).not.toBeInTheDocument()
  expect(screen.queryByText('Next')).not.toBeInTheDocument()
})
  it('renders sortChildren when totalPages > 0 and isLoaded is true', () => {
  render(
    <SearchPageLayout
      isLoaded={true}
      totalPages={1} // ✅ greater than 0
      currentPage={1}
      searchQuery=""
      onSearch={() => {}}
      onPageChange={() => {}}
      searchPlaceholder="Search..."
      empty="No results"
      indexName="any-index"
      sortChildren={<div>Sort Options</div>} // ✅ pass this
    >
      <div>Some content</div>
    </SearchPageLayout>
  )

  expect(screen.getByText('Sort Options')).toBeInTheDocument()
})
  it('renders without crashing when no children or sortChildren and totalPages is 0', () => {
  render(
    <SearchPageLayout
      isLoaded={true}
      totalPages={0}
      currentPage={1}
      searchQuery=""
      onSearch={() => {}}
      onPageChange={() => {}}
      searchPlaceholder="Search..."
      empty="No results"
      indexName="any-index"
    />
  )

  // Should still show the empty message
  expect(screen.getByText('No results')).toBeInTheDocument()
})

  
})
