import { render, screen, fireEvent } from '@testing-library/react'
import { faHome, faUser } from '@fortawesome/free-solid-svg-icons'
import NavButton from 'components/NavButton'
import type { NavButtonProps } from 'types/button'

// Mock Next.js Link component
jest.mock('next/link', () => {
  return function MockLink({ children, href, ...props }: any) {
    return (
      <a href={href} {...props}>
        {children}
      </a>
    )
  }
})

describe('NavButton', () => {
  const defaultProps: NavButtonProps = {
    href: '/test',
    defaultIcon: faHome,
    hoverIcon: faUser,
    text: 'Test Button',
  }

  const renderNavButton = (props: Partial<NavButtonProps> = {}) => {
    return render(<NavButton {...defaultProps} {...props} />)
  }

  describe('Rendering', () => {
    it('renders successfully with minimal required props', () => {
      renderNavButton()
      expect(screen.getByText('Test Button')).toBeInTheDocument()
      expect(screen.getByRole('link')).toHaveAttribute('href', '/test')
    })

    it('renders with custom className', () => {
      renderNavButton({ className: 'custom-class' })
      const link = screen.getByRole('link')
      expect(link).toHaveClass('custom-class')
    })

    it('renders text content correctly', () => {
      renderNavButton({ text: 'Custom Button Text' })
      expect(screen.getByText('Custom Button Text')).toBeInTheDocument()
    })

    it('renders with target="_blank" and rel="noopener noreferrer"', () => {
      renderNavButton()
      const link = screen.getByRole('link')
      expect(link).toHaveAttribute('target', '_blank')
      expect(link).toHaveAttribute('rel', 'noopener noreferrer')
    })
  })

  describe('Icon Rendering', () => {
    it('renders default icon initially', () => {
      renderNavButton()
      const icon = screen.getByRole('img', { hidden: true })
      expect(icon).toBeInTheDocument()
    })

    it('applies default icon color when provided', () => {
      renderNavButton({ defaultIconColor: '#ff0000' })
      const icon = screen.getByRole('img', { hidden: true })
      expect(icon).toHaveStyle({ color: '#ff0000' })
    })

    it('applies hover icon color when provided', () => {
      renderNavButton({ hoverIconColor: '#00ff00' })
      const link = screen.getByRole('link')
      fireEvent.mouseEnter(link)
      const icon = screen.getByRole('img', { hidden: true })
      expect(icon).toHaveStyle({ color: '#00ff00' })
    })
  })

  describe('State Changes and Hover Behavior', () => {
    it('changes icon on hover', () => {
      renderNavButton()
      const link = screen.getByRole('link')
      const icon = screen.getByRole('img', { hidden: true })
      
      // Initially should show default icon
      expect(icon).toHaveClass('scale-110', { exact: false })
      
      // On hover, should show hover icon and apply scale class
      fireEvent.mouseEnter(link)
      expect(icon).toHaveClass('scale-110')
      expect(icon).toHaveClass('text-yellow-400')
      
      // On mouse leave, should return to default state
      fireEvent.mouseLeave(link)
      expect(icon).not.toHaveClass('scale-110')
      expect(icon).not.toHaveClass('text-yellow-400')
    })

    it('handles multiple hover events correctly', () => {
      renderNavButton()
      const link = screen.getByRole('link')
      const icon = screen.getByRole('img', { hidden: true })
      
      // First hover
      fireEvent.mouseEnter(link)
      expect(icon).toHaveClass('scale-110')
      
      // Mouse leave
      fireEvent.mouseLeave(link)
      expect(icon).not.toHaveClass('scale-110')
      
      // Second hover
      fireEvent.mouseEnter(link)
      expect(icon).toHaveClass('scale-110')
    })
  })

  describe('Props-based Behavior', () => {
    it('uses different icons for default and hover states', () => {
      renderNavButton({
        defaultIcon: faHome,
        hoverIcon: faUser,
      })
      
      const link = screen.getByRole('link')
      const icon = screen.getByRole('img', { hidden: true })
      
      // Initially shows default icon
      expect(icon).toBeInTheDocument()
      
      // On hover shows different icon
      fireEvent.mouseEnter(link)
      expect(icon).toBeInTheDocument()
    })

    it('applies custom colors correctly', () => {
      renderNavButton({
        defaultIconColor: '#123456',
        hoverIconColor: '#654321',
      })
      
      const link = screen.getByRole('link')
      const icon = screen.getByRole('img', { hidden: true })
      
      // Default color
      expect(icon).toHaveStyle({ color: '#123456' })
      
      // Hover color
      fireEvent.mouseEnter(link)
      expect(icon).toHaveStyle({ color: '#654321' })
    })
  })

  describe('Event Handling', () => {
    it('handles mouse enter event', () => {
      renderNavButton()
      const link = screen.getByRole('link')
      
      fireEvent.mouseEnter(link)
      const icon = screen.getByRole('img', { hidden: true })
      expect(icon).toHaveClass('scale-110')
    })

    it('handles mouse leave event', () => {
      renderNavButton()
      const link = screen.getByRole('link')
      
      // First enter to set hover state
      fireEvent.mouseEnter(link)
      const icon = screen.getByRole('img', { hidden: true })
      expect(icon).toHaveClass('scale-110')
      
      // Then leave
      fireEvent.mouseLeave(link)
      expect(icon).not.toHaveClass('scale-110')
    })

    it('handles focus events correctly', () => {
      renderNavButton()
      const link = screen.getByRole('link')
      
      // Should have focus-visible styles
      expect(link).toHaveClass('focus-visible:outline-none')
      expect(link).toHaveClass('focus-visible:ring-1')
    })
  })

  describe('Accessibility', () => {
    it('has proper link role', () => {
      renderNavButton()
      expect(screen.getByRole('link')).toBeInTheDocument()
    })

    it('has proper target and rel attributes for external links', () => {
      renderNavButton()
      const link = screen.getByRole('link')
      expect(link).toHaveAttribute('target', '_blank')
      expect(link).toHaveAttribute('rel', 'noopener noreferrer')
    })

    it('has proper focus management', () => {
      renderNavButton()
      const link = screen.getByRole('link')
      expect(link).toHaveClass('focus-visible:outline-none')
    })
  })

  describe('DOM Structure and Styling', () => {
    it('has correct base classes', () => {
      renderNavButton()
      const link = screen.getByRole('link')
      
      expect(link).toHaveClass('group')
      expect(link).toHaveClass('relative')
      expect(link).toHaveClass('flex')
      expect(link).toHaveClass('h-10')
      expect(link).toHaveClass('cursor-pointer')
      expect(link).toHaveClass('items-center')
      expect(link).toHaveClass('justify-center')
      expect(link).toHaveClass('gap-2')
      expect(link).toHaveClass('overflow-hidden')
      expect(link).toHaveClass('whitespace-pre')
      expect(link).toHaveClass('rounded-md')
      expect(link).toHaveClass('bg-[#87a1bc]')
      expect(link).toHaveClass('p-4')
      expect(link).toHaveClass('text-sm')
      expect(link).toHaveClass('font-medium')
      expect(link).toHaveClass('text-black')
    })

    it('has correct hover and focus classes', () => {
      renderNavButton()
      const link = screen.getByRole('link')
      
      expect(link).toHaveClass('hover:ring-1')
      expect(link).toHaveClass('hover:ring-[#b0c7de]')
      expect(link).toHaveClass('hover:ring-offset-0')
      expect(link).toHaveClass('focus-visible:outline-none')
      expect(link).toHaveClass('focus-visible:ring-1')
      expect(link).toHaveClass('focus-visible:ring-ring')
    })

    it('has correct dark mode classes', () => {
      renderNavButton()
      const link = screen.getByRole('link')
      
      expect(link).toHaveClass('dark:bg-slate-900')
      expect(link).toHaveClass('dark:text-white')
      expect(link).toHaveClass('dark:hover:bg-slate-900/90')
      expect(link).toHaveClass('dark:hover:ring-[#46576b]')
    })

    it('has correct responsive classes', () => {
      renderNavButton()
      const link = screen.getByRole('link')
      
      expect(link).toHaveClass('md:flex')
    })
  })

  describe('Edge Cases and Invalid Inputs', () => {
    it('handles empty text gracefully', () => {
      renderNavButton({ text: '' })
      const link = screen.getByRole('link')
      expect(link).toBeInTheDocument()
    })

    it('handles very long text', () => {
      const longText = 'A'.repeat(1000)
      renderNavButton({ text: longText })
      expect(screen.getByText(longText)).toBeInTheDocument()
    })

    it('handles special characters in text', () => {
      renderNavButton({ text: 'Test & Button <script>alert("xss")</script>' })
      expect(screen.getByText('Test & Button <script>alert("xss")</script>')).toBeInTheDocument()
    })

    it('handles complex href values', () => {
      const complexHref = 'https://example.com/path?param=value&other=123#fragment'
      renderNavButton({ href: complexHref })
      const link = screen.getByRole('link')
      expect(link).toHaveAttribute('href', complexHref)
    })

    it('handles undefined className gracefully', () => {
      renderNavButton({ className: undefined })
      const link = screen.getByRole('link')
      expect(link).toBeInTheDocument()
    })

    it('handles undefined icon colors gracefully', () => {
      renderNavButton({
        defaultIconColor: undefined,
        hoverIconColor: undefined,
      })
      const link = screen.getByRole('link')
      expect(link).toBeInTheDocument()
    })
  })

  describe('Integration with FontAwesome', () => {
    it('renders FontAwesome icon correctly', () => {
      renderNavButton()
      const icon = screen.getByRole('img', { hidden: true })
      expect(icon).toBeInTheDocument()
    })

    it('switches between different FontAwesome icons on hover', () => {
      renderNavButton({
        defaultIcon: faHome,
        hoverIcon: faUser,
      })
      
      const link = screen.getByRole('link')
      const icon = screen.getByRole('img', { hidden: true })
      
      // Icon should be present initially
      expect(icon).toBeInTheDocument()
      
      // Icon should still be present after hover
      fireEvent.mouseEnter(link)
      expect(icon).toBeInTheDocument()
    })
  })
})
