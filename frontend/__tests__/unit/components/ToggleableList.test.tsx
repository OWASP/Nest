import { render, screen, fireEvent } from '@testing-library/react'
import React from 'react'
import { FaUser } from 'react-icons/fa'
import ToggleableList from 'components/ToggleableList'

/* -------------------- mocks -------------------- */

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
  }: {
    icon: React.ComponentType<{ className?: string }>
    className?: string
  }) => <Icon className={className} data-testid="react-icon" {...props} />,
}))

/* -------------------- tests -------------------- */

describe('ToggleableList', () => {
  const mockItems = Array.from({ length: 15 }, (_, i) => `Item ${i + 1}`)

  const renderItem = (item: string) => <span>{item}</span>

  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('renders with limited items initially', () => {
    render(
      <ToggleableList
        items={mockItems}
        label="test-label"
        renderItem={renderItem}
      />
    )

    for (const item of mockItems.slice(0, 10)) {
      expect(screen.getByText(item)).toBeInTheDocument()
    }

    for (const item of mockItems.slice(10)) {
      expect(screen.queryByText(item)).not.toBeInTheDocument()
    }
  })

  it('renders with an icon', () => {
    render(
      <ToggleableList
        items={mockItems}
        label="test-label"
        icon={FaUser}
        renderItem={renderItem}
      />
    )

    const iconElement = screen.getByTestId('react-icon')
    expect(iconElement).toBeInTheDocument()
    expect(iconElement).toHaveClass('mr-2', 'h-5', 'w-5')
  })

  it('respects custom limit prop', () => {
    render(
      <ToggleableList
        items={mockItems}
        label="test-label"
        limit={3}
        renderItem={renderItem}
      />
    )

    expect(screen.getByText('Item 1')).toBeInTheDocument()
    expect(screen.getByText('Item 2')).toBeInTheDocument()
    expect(screen.getByText('Item 3')).toBeInTheDocument()
    expect(screen.queryByText('Item 4')).not.toBeInTheDocument()
  })

  it('does not show Show More button when item count is less than limit', () => {
    const limitedItems = mockItems.slice(0, 5)

    render(
      <ToggleableList
        items={limitedItems}
        label="test-label"
        renderItem={renderItem}
      />
    )

    expect(
      screen.queryByTestId('show-more-button')
    ).not.toBeInTheDocument()
  })

  it('shows Show More button when items exceed limit', () => {
    render(
      <ToggleableList
        items={mockItems}
        label="test-label"
        limit={5}
        renderItem={renderItem}
      />
    )

    expect(screen.getByTestId('show-more-button')).toBeInTheDocument()
  })

  it('expands to show all items when Show More is clicked', () => {
    render(
      <ToggleableList
        items={mockItems}
        label="Expandable Items"
        limit={5}
        renderItem={renderItem}
      />
    )

    expect(screen.queryByText('Item 6')).not.toBeInTheDocument()

    fireEvent.click(screen.getByTestId('show-more-button'))

    expect(screen.getByText('Item 6')).toBeInTheDocument()
    expect(screen.getByText('Item 15')).toBeInTheDocument()
  })

  it('collapses back when Show More is clicked again', () => {
    render(
      <ToggleableList
        items={mockItems}
        label="Collapsible Items"
        limit={5}
        renderItem={renderItem}
      />
    )

    fireEvent.click(screen.getByTestId('show-more-button'))
    expect(screen.getByText('Item 10')).toBeInTheDocument()

    fireEvent.click(screen.getByTestId('show-more-button'))
    expect(screen.queryByText('Item 6')).not.toBeInTheDocument()
  })

  it('handles empty items array', () => {
    render(
      <ToggleableList
        items={[]}
        label="Empty List"
        renderItem={renderItem}
      />
    )

    expect(screen.getByText('Empty List')).toBeInTheDocument()
    expect(
      screen.queryByTestId('show-more-button')
    ).not.toBeInTheDocument()
  })

  it('handles items exactly equal to limit', () => {
    const exactItems = Array.from({ length: 5 }, (_, i) => `Item ${i + 1}`)

    render(
      <ToggleableList
        items={exactItems}
        label="Exact Items"
        limit={5}
        renderItem={renderItem}
      />
    )

    expect(screen.getByText('Item 5')).toBeInTheDocument()
    expect(
      screen.queryByTestId('show-more-button')
    ).not.toBeInTheDocument()
  })

  it('properly encodes special characters in navigation', () => {
    const itemsWithSpecialChars = ['C++', 'C#']

    render(
      <ToggleableList
        items={itemsWithSpecialChars}
        label="Special Items"
        renderItem={renderItem}
      />
    )

    fireEvent.click(screen.getByText('C++'))
    expect(mockPush).toHaveBeenCalledWith('/projects?q=C%2B%2B')
  })
})

