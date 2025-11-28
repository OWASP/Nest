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
        indexName="unknown-index"
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

    // Should show the mock content
    expect(screen.getByText('Mock Content')).toBeInTheDocument()

    // Should NOT show the loading spinner
    const images = screen.queryAllByRole('img')
    expect(images.length).toBe(0)
  })

  it('renders empty message when totalPages is 0 and loaded', () => {
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

  it('renders sortChildren when totalPages = 1 and isLoaded is true', () => {
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
        sortChildren={<div>Sort Options</div>}
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

  // -------- Edge Case Tests --------
  it('renders safely with minimal required props and no optional children', () => {
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
        indexName="test"
      />
    )

    expect(screen.getByPlaceholderText('Search...')).toBeInTheDocument()
    expect(screen.getByText('No results')).toBeInTheDocument()
  })
  it('renders safely when currentPage is greater than totalPages', () => {
    render(
      <SearchPageLayout
        isLoaded={true}
        totalPages={2}
        currentPage={5} // currentPage > totalPages
        searchQuery=""
        onSearch={() => {}}
        onPageChange={() => {}}
        searchPlaceholder="Search..."
        empty="No results"
        indexName="test"
      >
        <div>Edge case content</div>
      </SearchPageLayout>
    )

    expect(screen.getByPlaceholderText('Search...')).toBeInTheDocument()
    expect(screen.getByText('Edge case content')).toBeInTheDocument()
  })
  it('renders safely when onSearch and onPageChange are undefined', () => {
    render(
      // @ts-expect-error Testing with missing handlers intentionally
      <SearchPageLayout
        isLoaded={true}
        totalPages={0}
        currentPage={1}
        searchQuery=""
        // onSearch and onPageChange are intentionally omitted
        searchPlaceholder="Search..."
        empty="No results"
        indexName="test"
      />
    )

    expect(screen.getByPlaceholderText('Search...')).toBeInTheDocument()
    expect(screen.getByText('No results')).toBeInTheDocument()
  })

  it('renders safely when currentPage is negative', () => {
    const handlePageChange = jest.fn()

    render(
      <SearchPageLayout
        isLoaded={true}
        totalPages={3}
        currentPage={-2}
        onSearch={() => {}}
        onPageChange={handlePageChange}
        searchQuery=""
        searchPlaceholder="Search..."
        empty="No results"
        indexName="test"
      />
    )

    expect(screen.getByText('1')).toBeInTheDocument()
    expect(screen.queryByText('-2')).not.toBeInTheDocument()
  })

  it('renders safely when currentPage is NaN', () => {
    const handlePageChange = jest.fn()

    render(
      <SearchPageLayout
        isLoaded={true}
        totalPages={3}
        currentPage={Number.NaN}
        onSearch={() => {}}
        onPageChange={handlePageChange}
        searchQuery=""
        searchPlaceholder="Search..."
        empty="No results"
        indexName="test"
      />
    )

    expect(screen.getByText('1')).toBeInTheDocument()
  })

  it('renders safely when totalPages is a float', () => {
    const handlePageChange = jest.fn()

    render(
      <SearchPageLayout
        isLoaded={true}
        totalPages={2.8} // Float value
        currentPage={1}
        onSearch={() => {}}
        onPageChange={handlePageChange}
        searchQuery=""
        searchPlaceholder="Search..."
        empty="No results"
        indexName="test"
      >
        <div>Test Content</div>
      </SearchPageLayout>
    )

    // Math.floor(2.8) => 2
    expect(screen.getByText('1')).toBeInTheDocument()
    expect(screen.getByText('2')).toBeInTheDocument()
    expect(screen.queryByText('3')).not.toBeInTheDocument()
  })

  it('renders safely when totalPages is Infinity', () => {
    const handlePageChange = jest.fn()

    render(
      <SearchPageLayout
        isLoaded={true}
        totalPages={Infinity}
        currentPage={1}
        onSearch={() => {}}
        onPageChange={handlePageChange}
        searchQuery=""
        searchPlaceholder="Search..."
        empty="No results"
        indexName="test"
      >
        <div>Test Content</div>
      </SearchPageLayout>
    )

    // Should render first few page buttons (e.g., 1, 2, 3) only
    expect(screen.getByText('1')).toBeInTheDocument()
    expect(screen.getByText('2')).toBeInTheDocument()
    expect(screen.getByText('3')).toBeInTheDocument()

    // Check that it's not crashing on infinity
    expect(screen.getByText('Test Content')).toBeInTheDocument()
  })

  it('renders safely when totalPages is negative', () => {
    render(
      <SearchPageLayout
        isLoaded={true}
        totalPages={-5}
        currentPage={1}
        onSearch={() => {}}
        onPageChange={() => {}}
        searchQuery=""
        searchPlaceholder="Search..."
        empty="No results"
        indexName="test"
      >
        Test Content
      </SearchPageLayout>
    )

    // Expect the main content to still render
    expect(screen.getByText('Test Content')).toBeInTheDocument()

    // Expect pagination not to render
    expect(screen.queryByText('Prev')).not.toBeInTheDocument()
    expect(screen.queryByText('Next')).not.toBeInTheDocument()
  })

  it('renders safely when totalPages is NaN', () => {
    render(
      <SearchPageLayout
        isLoaded={true}
        totalPages={Number.NaN}
        currentPage={1}
        onSearch={() => {}}
        onPageChange={() => {}}
        searchQuery=""
        searchPlaceholder="Search..."
        empty="No results"
        indexName="test"
      >
        Test Content
      </SearchPageLayout>
    )

    // Should render content safely
    expect(screen.getByText('Test Content')).toBeInTheDocument()

    // Pagination should not appear for NaN pages
    expect(screen.queryByText('Prev')).not.toBeInTheDocument()
    expect(screen.queryByText('Next')).not.toBeInTheDocument()
  })

  it('renders root layout with expected structure and classNames', () => {
    const { container } = render(
      <SearchPageLayout
        isLoaded={true}
        totalPages={1}
        currentPage={1}
        onSearch={() => {}}
        onPageChange={() => {}}
        searchQuery=""
        searchPlaceholder="Search..."
        empty="No results"
        indexName="test"
        sortChildren={<div>Sort Options</div>}
      >
        <div>Child Content</div>
      </SearchPageLayout>
    )

    // Check the outermost layout container has expected classNames
    const rootDiv = container.querySelector('div.flex.min-h-screen')
    expect(rootDiv).toBeInTheDocument()

    // Check both children and sortChildren are rendered
    expect(screen.getByText('Child Content')).toBeInTheDocument()
    expect(screen.getByText('Sort Options')).toBeInTheDocument()
  })

  it('renders top-level layout structure and nested content', () => {
    render(
      <SearchPageLayout
        isLoaded={true}
        totalPages={1}
        currentPage={1}
        onSearch={() => {}}
        onPageChange={() => {}}
        searchQuery=""
        searchPlaceholder="Search..."
        empty="No results"
        indexName="test"
      >
        <div>Test child content</div>
      </SearchPageLayout>
    )

    // Assert a text element (child) appears inside the layout
    expect(screen.getByText('Test child content')).toBeInTheDocument()

    // Assert there's at least one div with expected role in layout
    const divs = screen.getAllByRole('generic') // 'div' usually maps to role='generic'
    expect(divs.length).toBeGreaterThan(0)
  })
})
