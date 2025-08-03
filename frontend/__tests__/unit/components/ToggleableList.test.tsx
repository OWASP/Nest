import { IconDefinition } from '@fortawesome/fontawesome-svg-core'
import { faUser } from '@fortawesome/free-solid-svg-icons'
import { render, screen, fireEvent } from '@testing-library/react'
import ToggleableList from 'components/ToggleableList'


// Mock next/router
const mockPush = jest.fn();
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: mockPush,
  }),
}))

// Mock ShowMoreButton as default export
jest.mock('components/ShowMoreButton', () => ({
  __esModule: true,
  default: ({ onToggle }: { onToggle: () => void }) => (
    <button data-testid="show-more-button" onClick={onToggle}>
      Show More
    </button>
  ),
}))

// Mock FontAwesomeIcon with role and className
jest.mock('@fortawesome/react-fontawesome', () => ({
  __esModule: true,
  FontAwesomeIcon: ({ icon, className }: { icon: IconDefinition; className: string }) => (
    <span role="img" data-testid="font-awesome-icon" className={className}>
      {icon.iconName}
    </span>
  ),
}))

describe('ToggleableList', () => {
  const mockItems = Array.from({ length: 15 }, (_, i) => `Item ${i + 1}`)

  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('renders with limited props initially', () => {
    render(<ToggleableList items={mockItems} label="test-label" />)

    // First 10 items should be visible
    mockItems.slice(0, 10).forEach(item => {
      expect(screen.getByText(item)).toBeInTheDocument()
    })

    // Remaining items should be hidden
    mockItems.slice(10).forEach(item => {
      expect(screen.queryByText(item)).not.toBeInTheDocument()
    })
  })

  it('renders with an icon', () => {
    render(<ToggleableList items={mockItems} label="test-label" icon={faUser} />)

    const iconElement = screen.getByTestId('font-awesome-icon')
    expect(iconElement).toBeInTheDocument()
    expect(iconElement).toHaveClass('mr-2', 'h-5', 'w-5')
  })

  it('respects custom limit prop', () => {
    render(<ToggleableList items={mockItems} label="test-label" limit={3} />)

    expect(screen.getByText('Item 1')).toBeInTheDocument()
    expect(screen.getByText('Item 2')).toBeInTheDocument()
    expect(screen.getByText('Item 3')).toBeInTheDocument()
    expect(screen.queryByText('Item 4')).not.toBeInTheDocument()
  })

  it('does not show Show More button when item count is less than the limit', () => {
    const limitedItems = mockItems.slice(0, 5)
    render(<ToggleableList items={limitedItems} label="test-label" />)

    expect(screen.queryByTestId('show-more-button')).not.toBeInTheDocument()
  })

  it('shows Show More button when items exceed limit', () => {
    render(<ToggleableList items={mockItems} label="test-label" limit={5} />)

    expect(screen.getByTestId('show-more-button')).toBeInTheDocument()
  })

  it('expands to show all items when ShowMoreButton is clicked', () => {
    render(<ToggleableList items={mockItems} label="Expandable Items" limit={5} />)

    // Initially hidden items
    expect(screen.queryByText('Item 6')).not.toBeInTheDocument()
    expect(screen.queryByText('Item 15')).not.toBeInTheDocument()

    // Click Show More
    fireEvent.click(screen.getByTestId('show-more-button'))

    // All items should now be visible
    expect(screen.getByText('Item 6')).toBeInTheDocument()
    expect(screen.getByText('Item 15')).toBeInTheDocument()
  })

  it('collapses back to limited view when ShowMoreButton is clicked again', () => {
    render(<ToggleableList items={mockItems} label="Collapsible Items" limit={5} />)

    // Expand
    fireEvent.click(screen.getByTestId('show-more-button'))
    expect(screen.getByText('Item 10')).toBeInTheDocument()

    // Collapse
    fireEvent.click(screen.getByTestId('show-more-button'))
    expect(screen.queryByText('Item 6')).not.toBeInTheDocument()
    expect(screen.getByText('Item 5')).toBeInTheDocument()
  })

  it('navigates on item button click', () => {
    render(<ToggleableList items={['React', 'Next.js', 'FastAPI']} label="Tags" limit={2} />)
    const button = screen.getByText('React')
    fireEvent.click(button)
    expect(mockPush).toHaveBeenCalledWith('/projects?q=React')
  })

  it('handles empty items array', () => {
    render(<ToggleableList items={[]} label="Empty List" />)

    expect(screen.getByText('Empty List')).toBeInTheDocument()
    expect(screen.queryByTestId('show-more-button')).not.toBeInTheDocument()
  })

  it('handles single item', () => {
    render(<ToggleableList items={['Single Item']} label="Single" />)

    expect(screen.getByText('Single Item')).toBeInTheDocument()
    expect(screen.queryByTestId('show-more-button')).not.toBeInTheDocument()
  })

  it('handles items exactly equal to limit', () => {
    const exactItems = Array.from({ length: 5 }, (_, i) => `Item ${i + 1}`)
    render(<ToggleableList items={exactItems} label="Exact Items" limit={5} />)

    expect(screen.getByText('Item 5')).toBeInTheDocument()
    expect(screen.queryByTestId('show-more-button')).not.toBeInTheDocument()
  })

  it('handles limit of 0', () => {
    render(<ToggleableList items={mockItems} label="test-label" limit={0} />)
    // Should show ShowMoreButton since limit is exceeded
    expect(screen.getByTestId('show-more-button')).toBeInTheDocument()
    expect(screen.queryByText('item')).not.toBeInTheDocument()
  })
})
