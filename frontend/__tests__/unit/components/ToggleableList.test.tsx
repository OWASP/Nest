import { render, screen, fireEvent } from '@testing-library/react'
import React from 'react'
import { FaUser } from 'react-icons/fa'
import ToggleableList from 'components/ToggleableList'

const mockPush = jest.fn()
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: mockPush,
  }),
}))

jest.mock('components/ShowMoreButton', () => ({
  __esModule: true,
  default: ({ onToggle }: { onToggle: () => void }) => (
    <button data-testid="show-more-button" onClick={onToggle}>
      Show More
    </button>
  ),
}))

jest.mock('wrappers/IconWrapper', () => ({
  IconWrapper: ({
    icon: Icon,
    className,
    ...props
  }: { icon: React.ComponentType<{ className?: string }> } & React.SVGProps<SVGSVGElement>) => (
    <Icon className={className} data-testid="react-icon" {...props} />
  ),
}))

describe('ToggleableList', () => {
  const mockItems = Array.from({ length: 15 }, (_, i) => `Item ${i + 1}`)

  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('renders with limited props initially', () => {
    render(<ToggleableList entityKey="test" items={mockItems} label="test-label" />)

    // First 10 items should be visible
    for (const item of mockItems.slice(0, 10)) {
      expect(screen.getByText(item)).toBeInTheDocument()
    }

    // Remaining items should be hidden
    for (const item of mockItems.slice(10)) {
      expect(screen.queryByText(item)).not.toBeInTheDocument()
    }
  })

  it('renders with an icon', () => {
    render(<ToggleableList entityKey="test" items={mockItems} label="test-label" icon={FaUser} />)

    const iconElement = screen.getByTestId('react-icon')
    expect(iconElement).toBeInTheDocument()
    expect(iconElement).toHaveClass('mr-2', 'h-5', 'w-5')
  })

  it('respects custom limit prop', () => {
    render(<ToggleableList entityKey="test" items={mockItems} label="test-label" limit={3} />)

    expect(screen.getByText('Item 1')).toBeInTheDocument()
    expect(screen.getByText('Item 2')).toBeInTheDocument()
    expect(screen.getByText('Item 3')).toBeInTheDocument()
    expect(screen.queryByText('Item 4')).not.toBeInTheDocument()
  })

  it('does not show Show More button when item count is less than the limit', () => {
    const limitedItems = mockItems.slice(0, 5)
    render(<ToggleableList entityKey="test" items={limitedItems} label="test-label" />)

    expect(screen.queryByTestId('show-more-button')).not.toBeInTheDocument()
  })

  it('shows Show More button when items exceed limit', () => {
    render(<ToggleableList entityKey="test" items={mockItems} label="test-label" limit={5} />)

    expect(screen.getByRole('button', { name: /show more/i })).toBeInTheDocument()
  })

  it('expands to show all items when ShowMoreButton is clicked', () => {
    render(<ToggleableList entityKey="test" items={mockItems} label="Expandable Items" limit={5} />)

    // Initially hidden items
    expect(screen.queryByText('Item 6')).not.toBeInTheDocument()
    expect(screen.queryByText('Item 15')).not.toBeInTheDocument()

    // Click Show More
    fireEvent.click(screen.getByRole('button', { name: /show more/i }))

    // All items should now be visible
    expect(screen.getByText('Item 6')).toBeInTheDocument()
    expect(screen.getByText('Item 15')).toBeInTheDocument()
  })

  it('collapses back to limited view when ShowMoreButton is clicked again', () => {
    render(
      <ToggleableList entityKey="test" items={mockItems} label="Collapsible Items" limit={5} />
    )

    // Expand
    fireEvent.click(screen.getByRole('button', { name: /show more/i }))
    expect(screen.getByText('Item 10')).toBeInTheDocument()

    // Collapse
    fireEvent.click(screen.getByRole('button', { name: /show more/i }))
    expect(screen.queryByText('Item 6')).not.toBeInTheDocument()
    expect(screen.getByText('Item 5')).toBeInTheDocument()
  })

  it('navigates on item button click', () => {
    render(
      <ToggleableList
        entityKey="test"
        items={['React', 'Next.js', 'FastAPI']}
        label="Tags"
        limit={2}
      />
    )
    const button = screen.getByText('React')
    fireEvent.click(button)
    expect(mockPush).toHaveBeenCalledWith('/projects?q=React')
  })

  it('handles empty items array', () => {
    render(<ToggleableList entityKey="test" items={[]} label="Empty List" />)

    expect(screen.getByText('Empty List')).toBeInTheDocument()
    expect(screen.queryByTestId('show-more-button')).not.toBeInTheDocument()
  })

  it('handles single item', () => {
    render(<ToggleableList entityKey="test" items={['Single Item']} label="Single" />)

    expect(screen.getByText('Single Item')).toBeInTheDocument()
    expect(screen.queryByTestId('show-more-button')).not.toBeInTheDocument()
  })

  it('handles items exactly equal to limit', () => {
    const exactItems = Array.from({ length: 5 }, (_, i) => `Item ${i + 1}`)
    render(<ToggleableList entityKey="test" items={exactItems} label="Exact Items" limit={5} />)

    expect(screen.getByText('Item 5')).toBeInTheDocument()
    expect(screen.queryByTestId('show-more-button')).not.toBeInTheDocument()
  })

  it('handles limit of 0', () => {
    render(<ToggleableList entityKey="test" items={mockItems} label="test-label" limit={0} />)
    // Should show ShowMoreButton since limit is exceeded
    expect(screen.getByRole('button', { name: /show more/i })).toBeInTheDocument()
    for (const item of mockItems) {
      expect(screen.queryByText(item)).not.toBeInTheDocument()
    }
  })

  it('properly encodes special character in item names', () => {
    const itemsWithSpecialChars = ['C++', 'C#', 'Node.js & Express']
    render(<ToggleableList entityKey="test" items={itemsWithSpecialChars} label="Special Items" />)
    const specialButton = screen.getByText('C++')
    fireEvent.click(specialButton)

    expect(mockPush).toHaveBeenCalledWith('/projects?q=C%2B%2B')
  })

  it('applies correct CSS classes to main container', () => {
    const { container } = render(
      <ToggleableList entityKey="test" items={mockItems} label="Styled List" />
    )
    const mainDiv = container.firstChild
    expect(mainDiv).toHaveClass('rounded-lg', 'bg-gray-100', 'p-6', 'shadow-md', 'dark:bg-gray-800')
  })

  it('applies correct CSS classes to header', () => {
    render(<ToggleableList entityKey="test" items={mockItems} label="Styled header" />)
    const header = screen.getByRole('heading', { level: 2 })
    expect(header).toHaveClass('mb-4', 'text-2xl', 'font-semibold')
  })

  it('applies correct CSS to button items (no underline, no transition, only hover background)', () => {
    const randomItems = ['React', 'Vue', 'Angular']
    render(<ToggleableList entityKey="test" items={randomItems} label="Styled Buttons" />)
    const button = screen.getByText('React')
    expect(button).toHaveClass(
      'rounded-lg',
      'border',
      'border-gray-400',
      'px-3',
      'py-1',
      'text-sm',
      'hover:bg-gray-200',
      'dark:border-gray-300',
      'dark:hover:bg-gray-700'
    )
    expect(button).not.toHaveClass(
      'hover:underline',
      'transition-all',
      'duration-200',
      'ease-in-out',
      'hover:scale-105'
    )
  })

  it('navigates when Enter key is pressed on item button', () => {
    render(
      <ToggleableList
        entityKey="test"
        items={['React', 'Next.js', 'FastAPI']}
        label="Tags"
        limit={2}
      />
    )
    const button = screen.getByText('Next.js')
    fireEvent.keyDown(button, { key: 'Enter' })
    expect(mockPush).toHaveBeenCalledWith('/projects?q=Next.js')
  })

  it('handles Enter key press on item button', () => {
    render(<ToggleableList entityKey="test" items={['React', 'Vue', 'Angular']} label="Tags" />)
    const button = screen.getByText('React')
    fireEvent.keyDown(button, { key: 'Enter' })
    expect(mockPush).toHaveBeenCalledWith('/projects?q=React')
  })

  it('navigates when Space key is pressed on item button', () => {
    render(
      <ToggleableList
        entityKey="test"
        items={['React', 'Next.js', 'FastAPI']}
        label="Tags"
        limit={2}
      />
    )
    const button = screen.getByText('Next.js')
    fireEvent.keyDown(button, { key: ' ' })
    expect(mockPush).toHaveBeenCalledWith('/projects?q=Next.js')
  })

  it('does not navigate when other keys are pressed on item button', () => {
    render(
      <ToggleableList
        entityKey="test"
        items={['React', 'Next.js', 'FastAPI']}
        label="Tags"
        limit={2}
      />
    )
    const button = screen.getByText('React')
    fireEvent.keyDown(button, { key: 'Tab' })
    expect(mockPush).not.toHaveBeenCalled()
  })

  it('does not navigate when clicking disabled item button', () => {
    render(
      <ToggleableList
        entityKey="test"
        items={['React', 'Next.js', 'FastAPI']}
        label="Tags"
        limit={2}
        isDisabled={true}
      />
    )
    const button = screen.getByText('React')
    fireEvent.click(button)
    expect(mockPush).not.toHaveBeenCalled()
  })

  it('handles Space key press on item button', () => {
    render(<ToggleableList entityKey="test" items={['React', 'Vue', 'Angular']} label="Tags" />)
    const button = screen.getByText('Vue')
    fireEvent.keyDown(button, { key: ' ' })
    expect(mockPush).toHaveBeenCalledWith('/projects?q=Vue')
  })

  it('prevents default behavior on keyboard event', () => {
    render(<ToggleableList entityKey="test" items={['React']} label="Tags" />)
    const button = screen.getByText('React')
    fireEvent.keyDown(button, { key: 'Enter' })
    expect(mockPush).toHaveBeenCalled()
  })

  it('does not navigate when button is disabled and clicked', () => {
    render(
      <ToggleableList entityKey="test" items={['React', 'Vue']} label="Tags" isDisabled={true} />
    )
    const button = screen.getByText('React')
    fireEvent.click(button)
    expect(mockPush).not.toHaveBeenCalled()
  })

  it('does not navigate when pressing Enter key on disabled item button', () => {
    render(
      <ToggleableList
        entityKey="test"
        items={['React', 'Next.js', 'FastAPI']}
        label="Tags"
        limit={2}
        isDisabled={true}
      />
    )
    const button = screen.getByText('React')
    fireEvent.keyDown(button, { key: 'Enter' })
    expect(mockPush).not.toHaveBeenCalled()
  })

  it('does not navigate when button is disabled and Enter key is pressed', () => {
    render(<ToggleableList entityKey="test" items={['React']} label="Tags" isDisabled={true} />)
    const button = screen.getByText('React')
    fireEvent.keyDown(button, { key: 'Enter' })
    expect(mockPush).not.toHaveBeenCalled()
  })

  it('applies correct CSS classes when isDisabled is true', () => {
    render(
      <ToggleableList
        entityKey="test"
        items={['React', 'Vue', 'Angular']}
        label="Disabled Buttons"
        isDisabled={true}
      />
    )
    const button = screen.getByText('React')
    expect(button).toHaveClass('cursor-default')
    expect(button).not.toHaveClass('cursor-pointer')
    expect(button).toBeDisabled()
  })

  it('does not navigate when button is disabled and Space key is pressed', () => {
    render(<ToggleableList entityKey="test" items={['Vue']} label="Tags" isDisabled={true} />)
    const button = screen.getByText('Vue')
    fireEvent.keyDown(button, { key: ' ' })
    expect(mockPush).not.toHaveBeenCalled()
  })

  it('has disabled attribute when isDisabled is true', () => {
    render(<ToggleableList entityKey="test" items={['React']} label="Tags" isDisabled={true} />)
    const button = screen.getByText('React')
    expect(button).toBeDisabled()
  })

  it('does not have disabled attribute when isDisabled is false', () => {
    render(<ToggleableList entityKey="test" items={['React']} label="Tags" isDisabled={false} />)
    const button = screen.getByText('React')
    expect(button).not.toBeDisabled()
  })

  it('applies cursor-default class when isDisabled is true', () => {
    render(<ToggleableList entityKey="test" items={['React']} label="Tags" isDisabled={true} />)
    const button = screen.getByText('React')
    expect(button).toHaveClass('cursor-default')
  })

  it('applies cursor-pointer class when isDisabled is false', () => {
    render(<ToggleableList entityKey="test" items={['React']} label="Tags" isDisabled={false} />)
    const button = screen.getByText('React')
    expect(button).toHaveClass('cursor-pointer')
  })
})
