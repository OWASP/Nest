import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import '@testing-library/jest-dom'
import type { Link as LinkType } from 'types/link'
import NavDropdown from 'components/NavDropDown'

// Mock Next.js Link component
jest.mock('next/link', () => {
  return ({ href, children, ...props }) => {
    return (
      <a
        href={href}
        {...props}
        onClick={(e) => {
          e.preventDefault()
          props.onClick?.(e)
        }}
      >
        {children}
      </a>
    )
  }
})

// Mock FontAwesome icons
jest.mock('@fortawesome/react-fontawesome', () => ({
  FontAwesomeIcon: ({ className }) => <span data-testid="chevron-icon" className={className} />,
}))

// Mock utility function
jest.mock('utils/utility', () => ({
  cn: (...classes) => classes.filter(Boolean).join(' '),
}))

describe('NavDropdown Component', () => {
  // Test data matching your component's expected structure
  const mockLink: LinkType = {
    text: 'Documentation',
    href: '/docs',
    submenu: [
      { text: 'Getting Started', href: '/docs/getting-started' },
      { text: 'API Reference', href: '/docs/api' },
      { text: 'Examples', href: '/docs/examples' },
    ],
  }

  const defaultProps = {
    pathname: '/current-page',
    link: mockLink,
  }

  beforeEach(() => {
    jest.clearAllMocks()
  })

  describe('Basic Rendering', () => {
    it('renders successfully with required props', () => {
      render(<NavDropdown {...defaultProps} />)

      expect(screen.getByRole('button')).toBeInTheDocument()
      expect(screen.getByText('Documentation')).toBeInTheDocument()
      expect(screen.getByTestId('chevron-icon')).toBeInTheDocument()
    })

    it('renders dropdown button with correct text', () => {
      render(<NavDropdown {...defaultProps} />)

      const button = screen.getByRole('button')
      expect(button).toHaveTextContent('Documentation')
    })

    it('initially does not show submenu items', () => {
      render(<NavDropdown {...defaultProps} />)

      expect(screen.queryByText('Getting Started')).not.toBeInTheDocument()
      expect(screen.queryByText('API Reference')).not.toBeInTheDocument()
      expect(screen.queryByText('Examples')).not.toBeInTheDocument()
    })
  })

  describe('Conditional Rendering Logic', () => {
    it('shows submenu items when dropdown is opened', async () => {
      const user = userEvent.setup()
      render(<NavDropdown {...defaultProps} />)

      const button = screen.getByRole('button')
      await user.click(button)

      await waitFor(() => {
        expect(screen.getByText('Getting Started')).toBeInTheDocument()
        expect(screen.getByText('API Reference')).toBeInTheDocument()
        expect(screen.getByText('Examples')).toBeInTheDocument()
      })
    })

    it('hides submenu items when dropdown is closed', async () => {
      const user = userEvent.setup()
      render(<NavDropdown {...defaultProps} />)

      const button = screen.getByRole('button')

      // Open dropdown
      await user.click(button)
      expect(screen.getByText('Getting Started')).toBeInTheDocument()

      // Close dropdown
      await user.click(button)
      await waitFor(() => {
        expect(screen.queryByText('Getting Started')).not.toBeInTheDocument()
      })
    })

    it('applies active styling when current pathname matches submenu item', () => {
      const propsWithActiveSubmenu = {
        pathname: '/docs/getting-started',
        link: mockLink,
      }

      render(<NavDropdown {...propsWithActiveSubmenu} />)

      const dropdown = screen.getByRole('button').parentElement
      expect(dropdown).toHaveClass('font-bold', 'text-blue-800', 'dark:text-white')
    })

    it('does not apply active styling when pathname does not match any submenu', () => {
      render(<NavDropdown {...defaultProps} />)

      const dropdown = screen.getByRole('button').parentElement
      expect(dropdown).not.toHaveClass('font-bold', 'text-blue-800')
    })

    it('applies active styling to submenu item when pathname matches', async () => {
      const propsWithActiveSubmenu = {
        pathname: '/docs/getting-started',
        link: mockLink,
      }

      const user = userEvent.setup()
      render(<NavDropdown {...propsWithActiveSubmenu} />)

      const button = screen.getByRole('button')
      await user.click(button)

      //active
      const gettingStartedLink = screen.getByRole('link', { name: /getting started/i })

      expect(gettingStartedLink).toHaveClass('font-bold', 'text-white')
    })

    it('does not apply active styling to other submenu items when one is active', async () => {
      const propsWithActiveSubmenu = {
        pathname: '/docs/getting-started',
        link: mockLink,
      }

      const user = userEvent.setup()
      render(<NavDropdown {...propsWithActiveSubmenu} />)

      const button = screen.getByRole('button')
      await user.click(button)

      //inactive
      const apiReferenceLink = screen.getByRole('link', { name: /api reference/i })
      const examplesLink = screen.getByRole('link', { name: /examples/i })

      expect(apiReferenceLink).toHaveClass('font-medium', 'text-slate-600')
      expect(examplesLink).toHaveClass('font-medium', 'text-slate-600')
    })
  })

  describe('Prop-based Behavior', () => {
    it('renders different link text based on props', () => {
      const customLink: LinkType = {
        text: 'Custom Menu',
        href: '/custom',
        submenu: [{ text: 'Sub Item', href: '/custom/sub' }],
      }

      render(<NavDropdown pathname="/test" link={customLink} />)

      expect(screen.getByText('Custom Menu')).toBeInTheDocument()
    })

    it('renders correct number of submenu items', async () => {
      const linkWithManyItems: LinkType = {
        text: 'Menu',
        href: '/menu',
        submenu: [
          { text: 'Item 1', href: '/item1' },
          { text: 'Item 2', href: '/item2' },
          { text: 'Item 3', href: '/item3' },
          { text: 'Item 4', href: '/item4' },
        ],
      }

      const user = userEvent.setup()
      render(<NavDropdown pathname="/test" link={linkWithManyItems} />)

      const button = screen.getByRole('button')
      await user.click(button)

      const links = screen.getAllByRole('link')
      expect(links).toHaveLength(4)
    })

    it('handles submenu items with different href values', async () => {
      const user = userEvent.setup()
      render(<NavDropdown {...defaultProps} />)

      const button = screen.getByRole('button')
      await user.click(button)

      const gettingStartedLink = screen.getByText('Getting Started').closest('a')
      const apiLink = screen.getByText('API Reference').closest('a')

      expect(gettingStartedLink).toHaveAttribute('href', '/docs/getting-started')
      expect(apiLink).toHaveAttribute('href', '/docs/api')
    })
  })

  describe('Event Handling', () => {
    it('toggles dropdown when button is clicked', async () => {
      const user = userEvent.setup()
      render(<NavDropdown {...defaultProps} />)

      const button = screen.getByRole('button')

      // Initially closed
      expect(screen.queryByText('Getting Started')).not.toBeInTheDocument()

      // Click to open
      await user.click(button)
      expect(screen.getByText('Getting Started')).toBeInTheDocument()

      // Click to close
      await user.click(button)
      await waitFor(() => {
        expect(screen.queryByText('Getting Started')).not.toBeInTheDocument()
      })
    })

    it('closes dropdown when submenu item is clicked', async () => {
      const user = userEvent.setup()
      render(<NavDropdown {...defaultProps} />)

      const button = screen.getByRole('button')
      await user.click(button)

      const submenuItem = screen.getByText('Getting Started')
      await user.click(submenuItem)
      await waitFor(() => {
        expect(screen.queryByText('Getting Started')).not.toBeInTheDocument()
      })
    })

    it('closes dropdown when clicking outside', async () => {
      const user = userEvent.setup()
      render(
        <div>
          <NavDropdown {...defaultProps} />
          <button>Outside Button</button>
        </div>
      )

      const dropdownButton = screen.getByRole('button', { name: /documentation/i })
      await user.click(dropdownButton)

      expect(screen.getByText('Getting Started')).toBeInTheDocument()

      const outsideButton = screen.getByRole('button', { name: /outside button/i })
      await user.click(outsideButton)

      await waitFor(() => {
        expect(screen.queryByText('Getting Started')).not.toBeInTheDocument()
      })
    })

    it('handles keyboard events on dropdown button', async () => {
      const user = userEvent.setup()
      render(<NavDropdown {...defaultProps} />)

      const button = screen.getByRole('button')
      button.focus()

      // Open with Enter key
      await user.keyboard('{Enter}')
      expect(screen.getByText('Getting Started')).toBeInTheDocument()

      // Close with Escape key
      await user.keyboard('{Escape}')
      await waitFor(() => {
        expect(screen.queryByText('Getting Started')).not.toBeInTheDocument()
      })
    })

    it('handles keyboard events on submenu items', async () => {
      const user = userEvent.setup()
      render(<NavDropdown {...defaultProps} />)

      const button = screen.getByRole('button')
      await user.click(button)

      const submenuItem = screen.getByText('Getting Started')
      submenuItem.focus()

      // Close with Enter key on submenu item
      await user.keyboard('{Enter}')
      await waitFor(() => {
        expect(screen.queryByText('Getting Started')).not.toBeInTheDocument()
      })
    })

    it('handles space key to toggle dropdown', async () => {
      const user = userEvent.setup()
      render(<NavDropdown {...defaultProps} />)

      const button = screen.getByRole('button')
      button.focus()

      // Open with Space key
      await user.keyboard(' ')
      expect(screen.getByText('Getting Started')).toBeInTheDocument()
    })
  })

  describe('State Changes and Internal Logic', () => {
    it('rotates chevron icon when dropdown opens and closes', async () => {
      const user = userEvent.setup()
      render(<NavDropdown {...defaultProps} />)

      const button = screen.getByRole('button')
      const chevronContainer = button.querySelector('span[style]')

      // Initially not rotated
      expect(chevronContainer).toHaveStyle('transform: rotate(0deg)')

      // Open dropdown - should rotate
      await user.click(button)
      expect(chevronContainer).toHaveStyle('transform: rotate(180deg)')

      // Close dropdown - should rotate back
      await user.click(button)
      expect(chevronContainer).toHaveStyle('transform: rotate(0deg)')
    })
  })

  describe('Default Values and Fallbacks', () => {
    it('handles empty submenu array', async () => {
      const linkWithEmptySubmenu: LinkType = {
        text: 'Empty Menu',
        href: '/empty',
        submenu: [],
      }

      const user = userEvent.setup()
      render(<NavDropdown pathname="/test" link={linkWithEmptySubmenu} />)

      const button = screen.getByRole('button')
      await user.click(button)

      // Should render dropdown container but no items
      const dropdownContainer = screen.getByRole('button').parentElement?.querySelector('[id]')
      expect(dropdownContainer).toBeInTheDocument()
      expect(screen.queryByRole('link')).not.toBeInTheDocument()
    })

    it('handles submenu items without href', async () => {
      const linkWithMissingHref: LinkType = {
        text: 'Menu',
        href: '/menu',
        submenu: [
          { text: 'Valid Item', href: '/valid' },
          { text: 'Invalid Item' }, // Missing href
        ],
      }

      const user = userEvent.setup()
      render(<NavDropdown pathname="/test" link={linkWithMissingHref} />)

      const button = screen.getByRole('button')
      await user.click(button)

      const validLink = screen.getByText('Valid Item').closest('a')
      const invalidLink = screen.getByText('Invalid Item').closest('a')

      expect(validLink).toHaveAttribute('href', '/valid')
      expect(invalidLink).toHaveAttribute('href', '/') // Fallback to '/'
    })
  })

  describe('Text and Content Rendering', () => {
    it('renders link text correctly', () => {
      render(<NavDropdown {...defaultProps} />)

      expect(screen.getByText('Documentation')).toBeInTheDocument()
    })

    it('renders all submenu item texts', async () => {
      const user = userEvent.setup()
      render(<NavDropdown {...defaultProps} />)

      const button = screen.getByRole('button')
      await user.click(button)

      expect(screen.getByText('Getting Started')).toBeInTheDocument()
      expect(screen.getByText('API Reference')).toBeInTheDocument()
      expect(screen.getByText('Examples')).toBeInTheDocument()
    })

    it('handles special characters in text', async () => {
      const specialLink: LinkType = {
        text: 'Special & <Characters>',
        href: '/special',
        submenu: [
          { text: 'Item with & symbol', href: '/item1' },
          { text: 'Item with <tags>', href: '/item2' },
        ],
      }

      const user = userEvent.setup()
      render(<NavDropdown pathname="/test" link={specialLink} />)

      expect(screen.getByText('Special & <Characters>')).toBeInTheDocument()

      const button = screen.getByRole('button')
      await user.click(button)

      expect(screen.getByText('Item with & symbol')).toBeInTheDocument()
      expect(screen.getByText('Item with <tags>')).toBeInTheDocument()
    })
  })

  describe('Edge Cases and Invalid Inputs', () => {
    it('handles very long menu text', () => {
      const longTextLink: LinkType = {
        text: 'A'.repeat(100),
        href: '/long',
        submenu: [{ text: 'B'.repeat(50), href: '/long-sub' }],
      }

      render(<NavDropdown pathname="/test" link={longTextLink} />)

      const button = screen.getByRole('button')
      expect(button).toHaveTextContent('A'.repeat(100))
    })

    it('handles large number of submenu items', async () => {
      const manySubmenuItems = Array.from({ length: 50 }, (_, i) => ({
        text: `Item ${i + 1}`,
        href: `/item${i + 1}`,
      }))

      const linkWithManyItems: LinkType = {
        text: 'Many Items',
        href: '/many',
        submenu: manySubmenuItems,
      }

      const user = userEvent.setup()
      render(<NavDropdown pathname="/test" link={linkWithManyItems} />)

      const button = screen.getByRole('button')
      await user.click(button)

      expect(screen.getByText('Item 1')).toBeInTheDocument()
      expect(screen.getByText('Item 50')).toBeInTheDocument()

      const links = screen.getAllByRole('link')
      expect(links).toHaveLength(50)
    })
  })

  describe('Accessibility', () => {
    it('has proper ARIA attributes on button', () => {
      render(<NavDropdown {...defaultProps} />)

      const button = screen.getByRole('button')
      expect(button).toHaveAttribute('aria-expanded', 'false')
      expect(button).toHaveAttribute('aria-haspopup', 'true')
      expect(button).toHaveAttribute('aria-controls')
    })

    it('updates aria-expanded when dropdown state changes', async () => {
      const user = userEvent.setup()
      render(<NavDropdown {...defaultProps} />)

      const button = screen.getByRole('button')
      expect(button).toHaveAttribute('aria-expanded', 'false')

      await user.click(button)
      expect(button).toHaveAttribute('aria-expanded', 'true')

      await user.click(button)
      expect(button).toHaveAttribute('aria-expanded', 'false')
    })

    it('has proper id relationship between button and dropdown', async () => {
      const user = userEvent.setup()
      render(<NavDropdown {...defaultProps} />)

      const button = screen.getByRole('button')
      const ariaControls = button.getAttribute('aria-controls')

      await user.click(button)

      const dropdown = screen.getByRole('button').parentElement?.querySelector('[id]')
      expect(dropdown).toHaveAttribute('id', ariaControls)
    })

    it('marks chevron icon as decorative', () => {
      render(<NavDropdown {...defaultProps} />)

      const chevronContainer = screen.getByRole('button').querySelector('span[aria-hidden="true"]')
      expect(chevronContainer).toHaveAttribute('aria-hidden', 'true')
    })

    it('supports keyboard navigation', async () => {
      const user = userEvent.setup()
      render(<NavDropdown {...defaultProps} />)

      // Focus button with tab
      await user.tab()
      const button = screen.getByRole('button')
      expect(button).toHaveFocus()
    })
  })

  describe('DOM Structure and Styling', () => {
    it('applies correct CSS classes to dropdown container', () => {
      render(<NavDropdown {...defaultProps} />)

      const container = screen.getByRole('button').parentElement
      expect(container).toHaveClass('dropdown', 'navlink', 'relative', 'px-3', 'py-2')
    })

    it('applies correct classes to dropdown button', () => {
      render(<NavDropdown {...defaultProps} />)

      const button = screen.getByRole('button')
      expect(button).toHaveClass('flex', 'items-center', 'gap-2', 'whitespace-nowrap')
    })

    it('applies correct classes to dropdown menu when open', async () => {
      const user = userEvent.setup()
      render(<NavDropdown {...defaultProps} />)

      const button = screen.getByRole('button')
      await user.click(button)

      const menu = screen.getByRole('button').parentElement?.querySelector('[id]')
      expect(menu).toHaveClass(
        'absolute',
        'left-0',
        'top-full',
        'z-10',
        'mt-1',
        'w-48',
        'overflow-hidden',
        'rounded-md',
        'bg-white',
        'shadow-lg'
      )
    })

    it('applies hover styling to inactive submenu items', async () => {
      const user = userEvent.setup()
      render(<NavDropdown {...defaultProps} />)

      const button = screen.getByRole('button')
      await user.click(button)

      const submenuItem = screen.getByRole('link', { name: 'API Reference' })
      expect(submenuItem).toHaveClass('text-slate-600', 'hover:bg-gray-200', 'hover:text-slate-900')
    })
  })

  describe('Integration Tests', () => {
    it('works with Next.js Link component', async () => {
      const user = userEvent.setup()
      render(<NavDropdown {...defaultProps} />)

      const button = screen.getByRole('button')
      await user.click(button)

      const gettingStartedLink = screen.getByText('Getting Started').closest('a')
      expect(gettingStartedLink).toHaveAttribute('href', '/docs/getting-started')
    })

    it('maintains dropdown state across re-renders', async () => {
      const user = userEvent.setup()
      const { rerender } = render(<NavDropdown {...defaultProps} />)

      const button = screen.getByRole('button')
      await user.click(button)

      expect(screen.getByText('Getting Started')).toBeInTheDocument()

      // Re-render with same props
      rerender(<NavDropdown {...defaultProps} />)

      // Dropdown should still be open
      expect(screen.getByText('Getting Started')).toBeInTheDocument()
    })

    it('cleans up event listeners on unmount', () => {
      const addEventListenerSpy = jest.spyOn(document, 'addEventListener')
      const removeEventListenerSpy = jest.spyOn(document, 'removeEventListener')

      const { unmount } = render(<NavDropdown {...defaultProps} />)

      expect(addEventListenerSpy).toHaveBeenCalledWith('mousedown', expect.any(Function))

      unmount()

      expect(removeEventListenerSpy).toHaveBeenCalledWith('mousedown', expect.any(Function))

      addEventListenerSpy.mockRestore()
      removeEventListenerSpy.mockRestore()
    })
  })
})
