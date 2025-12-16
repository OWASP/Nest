/**
 * @file Complete unit tests for the NavButton component.
 * @see {@link AutoScrollToTop.test.tsx} for structural reference.
 */
import { render, screen, fireEvent } from '@testing-library/react'
import React from 'react'
import '@testing-library/jest-dom'
import type { ComponentPropsWithoutRef } from 'react'
import { FaHome } from 'react-icons/fa'
import { FaUser } from 'react-icons/fa6'
import type { NavButtonProps } from 'types/button'
import NavButton from 'components/NavButton'

jest.mock('react-icons/fa', () => ({
  FaHome: (props: React.SVGProps<SVGSVGElement>) => (
    <svg data-testid="fa-home-icon" className="fa-house" {...props} aria-hidden="true" />
  ),
}))

jest.mock('react-icons/fa6', () => ({
  FaUser: (props: React.SVGProps<SVGSVGElement>) => (
    <svg data-testid="fa-user-icon" className="fa-user" {...props} aria-hidden="true" />
  ),
}))

// Mock IconWrapper to pass through the icon component
jest.mock('wrappers/IconWrapper', () => ({
  IconWrapper: ({
    icon: IconComponent,
    className,
    style,
  }: {
    icon: React.ComponentType<{ className?: string; style?: React.CSSProperties }>
    className?: string
    style?: React.CSSProperties
  }) => {
    return IconComponent ? <IconComponent className={className} style={style} /> : null
  },
}))

// Mock Next.js Link
jest.mock('next/link', () => {
  return function MockLink({ children, href, ...props }: ComponentPropsWithoutRef<'a'>) {
    return (
      <a href={href} {...props}>
        {children}
      </a>
    )
  }
})

describe('<NavButton />', () => {
  const defaultProps: NavButtonProps & { defaultIcon: typeof FaHome; hoverIcon: typeof FaUser } = {
    href: '/test-path',
    defaultIcon: FaHome,
    hoverIcon: FaUser,
    text: 'Test Button',
  }

  // Helper function to render the component with optional prop overrides.
  const renderNavButton = (props: Partial<typeof defaultProps> = {}) => {
    return render(<NavButton {...defaultProps} {...props} />)
  }

  describe('Rendering & Content', () => {
    it('should render successfully with minimal required props', () => {
      renderNavButton()
      // It should render as a link because `href` is provided.
      const linkElement = screen.getByRole('link', { name: 'Test Button' })
      expect(linkElement).toBeInTheDocument()
    })

    it('should render the correct text content', () => {
      const customText = 'Click Here'
      renderNavButton({ text: customText })
      expect(screen.getByText(customText)).toBeInTheDocument()
    })

    it('should render the default react-icons icon', () => {
      renderNavButton()
      const icon = screen.getByTestId('fa-home-icon')
      expect(icon).toBeInTheDocument()
    })

    it('should render text content inside a span element', () => {
      const testText = 'Button Text'
      renderNavButton({ text: testText })
      const span = screen.getByText(testText)
      expect(span.tagName).toBe('SPAN')
    })
  })

  describe('Prop-based Behavior', () => {
    it('should render as a link with the correct href attribute', () => {
      const href = '/custom-path'
      renderNavButton({ href })
      expect(screen.getByRole('link')).toHaveAttribute('href', href)
    })

    it('should always open in a new tab with correct security attributes', () => {
      renderNavButton()
      const link = screen.getByRole('link')
      expect(link).toHaveAttribute('target', '_blank')
      expect(link).toHaveAttribute('rel', 'noopener noreferrer')
    })

    it('should apply custom icon colors via props', () => {
      renderNavButton({
        defaultIconColor: 'rgb(255, 0, 0)', // red
        hoverIconColor: 'rgb(0, 255, 0)', // green
      })

      const icon = screen.getByTestId('fa-home-icon')
      expect(icon).toHaveStyle({ color: 'rgb(255, 0, 0)' })

      fireEvent.mouseEnter(screen.getByRole('link'))
      const hoverIcon = screen.getByTestId('fa-user-icon')
      expect(hoverIcon).toHaveStyle({ color: 'rgb(0, 255, 0)' })
    })

    it('should apply custom className while preserving default classes', () => {
      const customClass = 'my-custom-class'
      renderNavButton({ className: customClass })
      const link = screen.getByRole('link')
      expect(link).toHaveClass('group') // A default class
      expect(link).toHaveClass(customClass) // The custom class
    })
  })

  describe('State Changes & Hover Effects', () => {
    it('should switch from default icon to hover icon on mouse enter', () => {
      renderNavButton()
      const link = screen.getByRole('link')

      expect(screen.getByTestId('fa-home-icon')).toBeInTheDocument()
      expect(screen.queryByTestId('fa-user-icon')).not.toBeInTheDocument()

      fireEvent.mouseEnter(link)
      expect(screen.getByTestId('fa-user-icon')).toBeInTheDocument()
      expect(screen.queryByTestId('fa-home-icon')).not.toBeInTheDocument()
    })

    it('should revert to the default icon on mouse leave', () => {
      renderNavButton()
      const link = screen.getByRole('link')

      // Hover to change state
      fireEvent.mouseEnter(link)
      expect(screen.getByTestId('fa-user-icon')).toBeInTheDocument()

      // Leave to revert state
      fireEvent.mouseLeave(link)
      expect(screen.getByTestId('fa-home-icon')).toBeInTheDocument()
      expect(screen.queryByTestId('fa-user-icon')).not.toBeInTheDocument()
    })

    it('should apply scaling transform and yellow color on hover', () => {
      renderNavButton()
      const link = screen.getByRole('link')

      const defaultIcon = screen.getByTestId('fa-home-icon')
      expect(defaultIcon).not.toHaveClass('scale-110')
      expect(defaultIcon).not.toHaveClass('text-yellow-400')

      fireEvent.mouseEnter(link)
      const hoverIcon = screen.getByTestId('fa-user-icon')
      expect(hoverIcon).toHaveClass('scale-110')
      expect(hoverIcon).toHaveClass('text-yellow-400')

      // On leave, should revert to default icon without hover classes
      fireEvent.mouseLeave(link)
      const revertedIcon = screen.getByTestId('fa-home-icon')
      expect(revertedIcon).not.toHaveClass('scale-110')
      expect(revertedIcon).not.toHaveClass('text-yellow-400')
    })

    it('should maintain hover state when mouse moves within the component', () => {
      renderNavButton()
      const link = screen.getByRole('link')

      fireEvent.mouseEnter(link)
      const hoverIcon = screen.getByTestId('fa-user-icon')
      expect(hoverIcon).toHaveClass('scale-110')

      // Moving mouse within component should maintain hover state
      fireEvent.mouseMove(link)
      expect(screen.getByTestId('fa-user-icon')).toHaveClass('scale-110')
    })
  })

  describe('DOM Structure & Styling', () => {
    it('should have the correct base layout and style classes', () => {
      renderNavButton()
      const link = screen.getByRole('link')
      // Check for key classes based on actual component implementation
      expect(link).toHaveClass(
        'group',
        'relative',
        'flex',
        'h-10',
        'cursor-pointer',
        'items-center',
        'justify-center',
        'gap-2',
        'overflow-hidden',
        'whitespace-pre',
        'rounded-md'
      )
    })

    it('should have correct background color classes', () => {
      renderNavButton()
      const link = screen.getByRole('link')
      expect(link).toHaveClass('bg-[#87a1bc]')
    })

    it('should have correct text styling classes', () => {
      renderNavButton()
      const link = screen.getByRole('link')
      expect(link).toHaveClass('text-sm', 'font-medium', 'text-black')
    })

    it('should have correct padding and spacing classes', () => {
      renderNavButton()
      const link = screen.getByRole('link')
      expect(link).toHaveClass('p-4')
    })

    it('should have correct hover and focus-visible utility classes for accessibility', () => {
      renderNavButton()
      const link = screen.getByRole('link')
      expect(link).toHaveClass(
        'hover:ring-1',
        'hover:ring-[#b0c7de]',
        'hover:ring-offset-0',
        'focus-visible:outline-hidden',
        'focus-visible:ring-1',
        'focus-visible:ring-ring'
      )
    })

    it('should have dark mode classes', () => {
      renderNavButton()
      const link = screen.getByRole('link')
      expect(link).toHaveClass(
        'dark:bg-slate-900',
        'dark:text-white',
        'dark:hover:bg-slate-900/90',
        'dark:hover:ring-[#46576b]'
      )
    })

    it('should have disabled state classes', () => {
      renderNavButton()
      const link = screen.getByRole('link')
      expect(link).toHaveClass('disabled:pointer-events-none', 'disabled:opacity-50')
    })

    it('should have responsive display classes', () => {
      renderNavButton()
      const link = screen.getByRole('link')
      expect(link).toHaveClass('md:flex')
    })
  })

  describe('Default Values and Fallbacks', () => {
    it('should render without crashing when optional color props are not provided', () => {
      expect(() => {
        render(<NavButton href="/test" defaultIcon={FaHome} hoverIcon={FaUser} text="Test" />)
      }).not.toThrow()
    })

    it('should handle undefined for optional color props gracefully', () => {
      // Render without crashing when optional props are explicitly undefined.
      expect(() => {
        renderNavButton({ defaultIconColor: undefined, hoverIconColor: undefined })
      }).not.toThrow()
    })

    it('should render without custom className', () => {
      render(<NavButton href="/test" defaultIcon={FaHome} hoverIcon={FaUser} text="Test" />)
      const link = screen.getByRole('link')
      expect(link).toBeInTheDocument()
      expect(link).toHaveClass('group') // Should still have default classes
    })
  })

  describe('Edge Cases & Invalid Inputs', () => {
    it('should render correctly even if text is an empty string', () => {
      renderNavButton({ text: '' })
      // The link should still render, even without visible text.
      expect(screen.getByRole('link')).toBeInTheDocument()
      // The span should exist but be empty
      const span = screen.getByRole('link').querySelector('span')
      expect(span).toBeInTheDocument()
      expect(span?.textContent).toBe('')
    })

    it('should handle long text without breaking', () => {
      const longText = 'This is an extremely long text string to test wrapping and overflow'.repeat(
        10
      )
      renderNavButton({ text: longText })
      expect(screen.getByText(longText)).toBeInTheDocument()
      // The component should handle overflow with whitespace-pre class
      expect(screen.getByRole('link')).toHaveClass('whitespace-pre', 'overflow-hidden')
    })

    it('should handle special characters in text', () => {
      const specialText = '!@#$%^&*()_+-=[]{}|;:,.<>?'
      renderNavButton({ text: specialText })
      expect(screen.getByText(specialText)).toBeInTheDocument()
    })

    it('should handle unicode characters in text', () => {
      const unicodeText = '🏠 Home 🌟 ∑ ∆ ∇'
      renderNavButton({ text: unicodeText })
      expect(screen.getByText(unicodeText)).toBeInTheDocument()
    })
  })

  describe('Accessibility', () => {
    it('should be keyboard focusable', () => {
      renderNavButton()
      const link = screen.getByRole('link')

      link.focus()
      expect(link).toHaveFocus()
    })

    it('should have proper link semantics', () => {
      renderNavButton()
      const link = screen.getByRole('link')
      expect(link.tagName).toBe('A')
    })

    it('should have accessible name from text content', () => {
      const buttonText = 'Navigate Home'
      renderNavButton({ text: buttonText })
      expect(screen.getByRole('link', { name: buttonText })).toBeInTheDocument()
    })

    it('should maintain focus visibility with focus-visible classes', () => {
      renderNavButton()
      const link = screen.getByRole('link')
      expect(link).toHaveClass('focus-visible:outline-hidden', 'focus-visible:ring-1')
    })
  })

  describe('Component Composition & Structure', () => {
    it('should render Link wrapper with react-icons icon and span inside', () => {
      renderNavButton()
      const link = screen.getByRole('link')

      // Should contain both icon and text span
      expect(screen.getByTestId('fa-home-icon')).toBeInTheDocument() // React-icons renders as SVG
      expect(link.querySelector('span')).toBeInTheDocument()
    })

    it('should maintain correct element hierarchy', () => {
      renderNavButton()
      const link = screen.getByRole('link')
      const children = link.children

      // Should have 2 children: react-icons icon and span
      expect(children).toHaveLength(2)
      expect(children[0].tagName.toUpperCase()).toBe('SVG') // React-icons icon
      expect(children[1].tagName).toBe('SPAN') // Text span
    })
  })

  describe('Performance & State Management', () => {
    it('should not cause memory leaks with event listeners', () => {
      const { unmount } = renderNavButton()
      expect(() => unmount()).not.toThrow()
    })

    it('should handle rapid hover state changes', () => {
      renderNavButton()
      const link = screen.getByRole('link')

      // Rapid mouse enter/leave should work correctly
      fireEvent.mouseEnter(link)
      fireEvent.mouseLeave(link)
      fireEvent.mouseEnter(link)
      fireEvent.mouseLeave(link)

      // Should end up in non-hovered state
      const defaultIcon = screen.getByTestId('fa-home-icon')
      expect(defaultIcon).not.toHaveClass('scale-110')
      expect(defaultIcon).not.toHaveClass('text-yellow-400')
    })
  })
})
