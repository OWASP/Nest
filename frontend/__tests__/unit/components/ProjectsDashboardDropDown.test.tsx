import { render, screen, fireEvent } from '@testing-library/react'
import React from 'react'
import { FaFilter, FaSort } from 'react-icons/fa6'
import ProjectsDashboardDropDown from 'components/ProjectsDashboardDropDown'

jest.mock('react-icons/fa6', () => ({
  FaArrowDownWideShort: (props: React.SVGProps<SVGSVGElement>) => (
    <svg data-testid="font-awesome-icon" data-icon="arrow-down-wide-short" {...props} />
  ),
  FaArrowUpShortWide: (props: React.SVGProps<SVGSVGElement>) => (
    <svg data-testid="font-awesome-icon" data-icon="arrow-up-short-wide" {...props} />
  ),
  FaFilter: (props: React.SVGProps<SVGSVGElement>) => (
    <svg data-testid="font-awesome-icon" data-icon="filter" {...props} />
  ),
  FaSort: (props: React.SVGProps<SVGSVGElement>) => (
    <svg data-testid="font-awesome-icon" data-icon="sort" {...props} />
  ),
}))

// Mock IconWrapper to handle react-icons properly
jest.mock('wrappers/IconWrapper', () => ({
  IconWrapper: ({ icon: IconComponent }: { icon?: React.ComponentType }) => {
    return IconComponent ? (
      <IconComponent />
    ) : (
      <svg data-testid="font-awesome-icon" data-icon="arrow-down-wide-short" />
    )
  },
}))

// Mock HeroUI components
jest.mock('@heroui/react', () => ({
  Dropdown: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="dropdown">{children}</div>
  ),
  DropdownTrigger: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="dropdown-trigger">{children}</div>
  ),
  DropdownMenu: ({
    children,
    onAction,
    selectedKeys,
    selectionMode,
  }: {
    children: React.ReactNode
    onAction: (key: string) => void
    selectedKeys?: string[]
    selectionMode: string
  }) => (
    <div
      data-testid="dropdown-menu"
      data-selection-mode={selectionMode}
      data-selected-keys={selectedKeys?.join(',')}
      onClick={(e) => {
        const target = e.target as HTMLElement
        const key = target.dataset.key
        if (key && onAction) {
          onAction(key)
        }
      }}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          const target = e.target as HTMLElement
          const key = target.dataset.key
          if (key && onAction) {
            onAction(key)
          }
        }
      }}
      role="menu"
      tabIndex={0}
    >
      {children}
    </div>
  ),
  DropdownSection: ({ children, title }: { children: React.ReactNode; title: string }) => (
    <fieldset data-testid="dropdown-section" data-title={title}>
      <legend id={`section-${title}`} className="section-title">
        {title}
      </legend>
      {children}
    </fieldset>
  ),
  DropdownItem: (props: { children: React.ReactNode }) => {
    const itemText = typeof props.children === 'string' ? props.children : 'item'

    return (
      <div
        data-testid="dropdown-item"
        data-key={itemText}
        style={{ cursor: 'pointer' }}
        role="menuitem"
        tabIndex={0}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault()
            const clickEvent = new MouseEvent('click', { bubbles: true })
            e.currentTarget.dispatchEvent(clickEvent)
          }
        }}
      >
        {props.children}
      </div>
    )
  },
  Button: ({
    children,
    variant,
    ...props
  }: {
    children: React.ReactNode
    variant?: string
    [key: string]: unknown
  }) => (
    <button data-testid="dropdown-button" data-variant={variant} {...props}>
      {children}
    </button>
  ),
}))

describe('ProjectsDashboardDropDown Component', () => {
  const defaultProps = {
    buttonDisplayName: 'Filter',
    onAction: jest.fn(),
    selectedKeys: ['Active'],
    selectedLabels: ['Selected Item'],
    selectionMode: 'single' as 'single' | 'multiple',
    sections: [
      {
        title: 'Status',
        items: [
          { key: 'Active', label: 'Active' },
          { key: 'Inactive', label: 'Inactive' },
        ],
      },
      {
        title: 'Priority',
        items: [
          { key: 'High Priority', label: 'High Priority' },
          { key: 'Low Priority', label: 'Low Priority' },
        ],
      },
    ],
    icon: FaFilter,
    isOrdering: false,
  }

  let mockOnAction: jest.Mock

  beforeEach(() => {
    mockOnAction = jest.fn()
    jest.clearAllMocks()

    jest.spyOn(console, 'error').mockImplementation((...args) => {
      const message = typeof args[0] === 'string' ? args[0] : String(args[0] || '')
      if (
        message.includes('Warning: ReactDOM.render is no longer supported') ||
        message.includes('Warning: You are importing createRoot') ||
        message.includes('Warning: React.createFactory')
      ) {
        return
      }
      return
    })
  })

  afterEach(() => {
    jest.restoreAllMocks()
  })

  describe('Renders successfully with minimal required props', () => {
    it('renders with minimal required props', () => {
      expect(() => {
        render(<ProjectsDashboardDropDown {...defaultProps} onAction={mockOnAction} />)
      }).not.toThrow()

      expect(screen.getByTestId('dropdown')).toBeInTheDocument()
      expect(screen.getByTestId('dropdown-button')).toBeInTheDocument()
      expect(screen.getByText('Filter')).toBeInTheDocument()
    })

    it('renders with icon when provided', () => {
      render(
        <ProjectsDashboardDropDown {...defaultProps} onAction={mockOnAction} icon={FaFilter} />
      )

      expect(screen.getByTestId('font-awesome-icon')).toBeInTheDocument()
    })

    it('renders without icon when not provided', () => {
      render(
        <ProjectsDashboardDropDown {...defaultProps} onAction={mockOnAction} icon={undefined} />
      )

      const icon = screen.getByTestId('font-awesome-icon')
      expect(icon).toHaveAttribute('data-icon', 'arrow-down-wide-short') // Default fallback
    })
  })

  describe('Conditional rendering logic', () => {
    it('shows ordering icon when isOrdering is true', () => {
      render(
        <ProjectsDashboardDropDown
          {...defaultProps}
          onAction={mockOnAction}
          isOrdering={true}
          selectedKeys={['desc']}
        />
      )

      const icon = screen.getByTestId('font-awesome-icon')
      expect(icon).toHaveAttribute('data-icon', 'arrow-down-wide-short')
    })

    it('shows regular icon when isOrdering is false', () => {
      render(
        <ProjectsDashboardDropDown
          {...defaultProps}
          onAction={mockOnAction}
          isOrdering={false}
          icon={FaSort}
        />
      )

      const icon = screen.getByTestId('font-awesome-icon')
      expect(icon).toHaveAttribute('data-icon', 'sort')
    })

    it('shows selected labels when provided', () => {
      render(
        <ProjectsDashboardDropDown
          {...defaultProps}
          onAction={mockOnAction}
          selectedLabels={['Custom', 'Labels']}
        />
      )

      expect(screen.getByText('Custom, Labels')).toBeInTheDocument()
    })

    it('hides selected labels when not provided', () => {
      render(
        <ProjectsDashboardDropDown
          {...defaultProps}
          onAction={mockOnAction}
          selectedLabels={undefined}
        />
      )

      expect(screen.queryByText('Selected Item')).not.toBeInTheDocument()
    })
  })

  describe('Prop-based behavior', () => {
    it('renders different button text based on buttonDisplayName', () => {
      render(
        <ProjectsDashboardDropDown
          {...defaultProps}
          onAction={mockOnAction}
          buttonDisplayName="Sort Options"
        />
      )

      expect(screen.getByText('Sort Options')).toBeInTheDocument()
    })

    it('applies single selection mode', () => {
      render(
        <ProjectsDashboardDropDown
          {...defaultProps}
          onAction={mockOnAction}
          selectionMode="single"
        />
      )

      const menu = screen.getByTestId('dropdown-menu')
      expect(menu).toHaveAttribute('data-selection-mode', 'single')
    })

    it('applies multiple selection mode', () => {
      render(
        <ProjectsDashboardDropDown
          {...defaultProps}
          onAction={mockOnAction}
          selectionMode="multiple"
        />
      )

      const menu = screen.getByTestId('dropdown-menu')
      expect(menu).toHaveAttribute('data-selection-mode', 'multiple')
    })
  })

  describe('Event handling', () => {
    it('calls onAction when dropdown item is clicked', () => {
      render(
        <ProjectsDashboardDropDown {...defaultProps} onAction={mockOnAction} selectedLabels={[]} />
      )

      const items = screen.getAllByTestId('dropdown-item')
      const activeItem = items.find((item) => item.textContent === 'Active')

      expect(activeItem).toBeDefined()

      fireEvent.click(activeItem)
      expect(mockOnAction).toHaveBeenCalledWith('Active')
    })

    it('calls onAction when dropdown item is activated with keyboard', () => {
      render(
        <ProjectsDashboardDropDown {...defaultProps} onAction={mockOnAction} selectedLabels={[]} />
      )

      const items = screen.getAllByTestId('dropdown-item')
      const activeItem = items.find((item) => item.textContent === 'Active')

      expect(activeItem).toBeDefined()

      fireEvent.keyDown(activeItem, { key: 'Enter' })
      expect(mockOnAction).toHaveBeenCalledWith('Active')
    })

    it('handles multiple clicks correctly', () => {
      render(
        <ProjectsDashboardDropDown {...defaultProps} onAction={mockOnAction} selectedLabels={[]} />
      )

      const items = screen.getAllByTestId('dropdown-item')
      const activeItem = items.find((item) => item.textContent === 'Active')
      const inactiveItem = items.find((item) => item.textContent === 'Inactive')

      expect(activeItem).toBeDefined()
      expect(inactiveItem).toBeDefined()

      fireEvent.click(activeItem)
      fireEvent.click(inactiveItem)

      expect(mockOnAction).toHaveBeenCalledTimes(2)
      expect(mockOnAction).toHaveBeenCalledWith('Active')
      expect(mockOnAction).toHaveBeenCalledWith('Inactive')
    })
  })

  describe('State changes / internal logic', () => {
    it('updates ordering icon based on selectedKeys', () => {
      const { rerender } = render(
        <ProjectsDashboardDropDown
          {...defaultProps}
          onAction={mockOnAction}
          isOrdering={true}
          selectedKeys={['desc']}
        />
      )

      let icon = screen.getByTestId('font-awesome-icon')
      expect(icon).toHaveAttribute('data-icon', 'arrow-down-wide-short')

      rerender(
        <ProjectsDashboardDropDown
          {...defaultProps}
          onAction={mockOnAction}
          isOrdering={true}
          selectedKeys={['asc']}
        />
      )

      icon = screen.getByTestId('font-awesome-icon')
      expect(icon).toHaveAttribute('data-icon', 'arrow-up-short-wide')
    })
  })

  describe('Default values and fallbacks', () => {
    it('handles empty selectedKeys array', () => {
      expect(() => {
        render(
          <ProjectsDashboardDropDown
            {...defaultProps}
            selectedKeys={[]}
            selectedLabels={[]}
            onAction={mockOnAction}
          />
        )
      }).not.toThrow()
    })

    it('handles undefined selectedKeys', () => {
      expect(() => {
        render(
          <ProjectsDashboardDropDown
            {...defaultProps}
            selectedKeys={undefined}
            selectedLabels={undefined}
            onAction={mockOnAction}
          />
        )
      }).not.toThrow()
    })

    it('handles empty selectedLabels array', () => {
      render(
        <ProjectsDashboardDropDown
          {...defaultProps}
          selectedKeys={['Active']}
          selectedLabels={[]}
          onAction={mockOnAction}
        />
      )

      const labelsContainer = screen.queryByText(/,/)
      expect(labelsContainer).not.toBeInTheDocument()
    })
  })

  describe('Text and content rendering', () => {
    it('renders all section titles correctly', () => {
      render(<ProjectsDashboardDropDown {...defaultProps} onAction={mockOnAction} />)

      expect(screen.getByText('Status')).toBeInTheDocument()
      expect(screen.getByText('Priority')).toBeInTheDocument()
    })

    it('renders all dropdown items correctly', () => {
      render(
        <ProjectsDashboardDropDown {...defaultProps} onAction={mockOnAction} selectedLabels={[]} />
      )

      const items = screen.getAllByTestId('dropdown-item')
      expect(items).toHaveLength(4)

      const itemTexts = items.map((item) => item.textContent)
      expect(itemTexts).toContain('Active')
      expect(itemTexts).toContain('Inactive')
      expect(itemTexts).toContain('High Priority')
      expect(itemTexts).toContain('Low Priority')
    })

    it('renders button display name correctly', () => {
      render(
        <ProjectsDashboardDropDown
          {...defaultProps}
          onAction={mockOnAction}
          buttonDisplayName="Custom Filter"
        />
      )

      expect(screen.getByText('Custom Filter')).toBeInTheDocument()
    })
  })

  describe('Handles edge cases and invalid inputs', () => {
    it('handles null/undefined props gracefully', () => {
      expect(() => {
        render(
          <ProjectsDashboardDropDown
            buttonDisplayName="Filter"
            onAction={mockOnAction}
            selectedKeys={[]}
            selectedLabels={[]}
            selectionMode="single"
            sections={defaultProps.sections}
            icon={undefined}
          />
        )
      }).not.toThrow()
    })

    it('handles empty strings in buttonDisplayName', () => {
      expect(() => {
        render(
          <ProjectsDashboardDropDown
            {...defaultProps}
            buttonDisplayName=""
            onAction={mockOnAction}
          />
        )
      }).not.toThrow()
    })

    it('handles invalid selectedKeys for ordering', () => {
      expect(() => {
        render(
          <ProjectsDashboardDropDown
            {...defaultProps}
            selectedKeys={['NonexistentKey']}
            selectedLabels={['NonexistentKey']}
            onAction={mockOnAction}
            isOrdering={true}
          />
        )
      }).not.toThrow()
    })

    it('handles empty sections array', () => {
      expect(() => {
        render(
          <ProjectsDashboardDropDown {...defaultProps} sections={[]} onAction={mockOnAction} />
        )
      }).not.toThrow()
    })
  })

  describe('Accessibility roles and labels', () => {
    it('renders button with proper structure for accessibility', () => {
      render(<ProjectsDashboardDropDown {...defaultProps} onAction={mockOnAction} />)

      const button = screen.getByTestId('dropdown-button')
      expect(button).toBeInTheDocument()
      expect(button.tagName.toLowerCase()).toBe('button')
    })

    it('maintains proper structure for screen readers', () => {
      render(
        <ProjectsDashboardDropDown
          {...defaultProps}
          onAction={mockOnAction}
          selectedLabels={['Selected']}
        />
      )

      expect(screen.getByText('Filter')).toBeInTheDocument()
      expect(screen.getByText('Selected')).toBeInTheDocument()
    })

    it('renders dropdown menu with proper ARIA roles', () => {
      render(<ProjectsDashboardDropDown {...defaultProps} onAction={mockOnAction} />)

      const menu = screen.getByTestId('dropdown-menu')
      expect(menu).toHaveAttribute('role', 'menu')
      expect(menu).toHaveAttribute('tabIndex', '0')
    })

    it('renders dropdown items with proper ARIA roles', () => {
      render(
        <ProjectsDashboardDropDown {...defaultProps} onAction={mockOnAction} selectedLabels={[]} />
      )

      const items = screen.getAllByTestId('dropdown-item')
      for (const item of items) {
        expect(item).toHaveAttribute('role', 'menuitem')
        expect(item).toHaveAttribute('tabIndex', '0')
      }
    })
  })

  describe('DOM structure / classNames / styles', () => {
    it('renders sections with correct data attributes', () => {
      render(<ProjectsDashboardDropDown {...defaultProps} onAction={mockOnAction} />)

      const sections = screen.getAllByTestId('dropdown-section')
      expect(sections).toHaveLength(2)
      expect(sections[0]).toHaveAttribute('data-title', 'Status')
      expect(sections[1]).toHaveAttribute('data-title', 'Priority')
    })

    it('renders dropdown items correctly', () => {
      render(
        <ProjectsDashboardDropDown {...defaultProps} onAction={mockOnAction} selectedLabels={[]} />
      )

      const items = screen.getAllByTestId('dropdown-item')
      expect(items).toHaveLength(4)

      const itemTexts = items.map((item) => item.textContent)
      expect(itemTexts).toContain('Active')
      expect(itemTexts).toContain('Inactive')
      expect(itemTexts).toContain('High Priority')
      expect(itemTexts).toContain('Low Priority')
    })

    it('applies correct attributes to dropdown menu', () => {
      render(
        <ProjectsDashboardDropDown
          {...defaultProps}
          selectedKeys={['TestKey']}
          selectedLabels={['TestLabel']}
          onAction={mockOnAction}
        />
      )

      const menu = screen.getByTestId('dropdown-menu')
      expect(menu).toHaveAttribute('data-selection-mode', 'single')
      expect(menu).toHaveAttribute('data-selected-keys', 'TestKey')
    })

    it('applies correct variant to button', () => {
      render(<ProjectsDashboardDropDown {...defaultProps} onAction={mockOnAction} />)

      const button = screen.getByTestId('dropdown-button')
      expect(button).toHaveAttribute('data-variant', 'solid')
    })

    it('renders proper flex layout structure', () => {
      render(
        <ProjectsDashboardDropDown
          {...defaultProps}
          onAction={mockOnAction}
          selectedLabels={['Test Label']}
        />
      )

      const flexContainer = screen.getByText('Filter').parentElement
      expect(flexContainer).toHaveClass('flex', 'flex-col', 'items-center')
    })
  })
})
