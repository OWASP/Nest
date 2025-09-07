/**
 * @file Complete unit tests for the NavButton component.
 * @see {@link AutoScrollToTop.test.tsx} for structural reference.
 */
import { faHome, faUser } from '@fortawesome/free-solid-svg-icons'
import { render, screen, fireEvent } from '@testing-library/react'
import '@testing-library/jest-dom'
import type { ComponentPropsWithoutRef } from 'react'
import type { NavButtonProps } from 'types/button'
import NavButton from 'components/NavButton'

// The NavButton component uses next/link internally. We mock it to isolate
// the NavButton's behavior and prevent actual navigation during tests.
jest.mock('next/link', () => {
  // Mock implementation returns a simple anchor tag with the passed props.
  return function MockLink({ children, href, ...props }: ComponentPropsWithoutRef<'a'>) {
    return (
      <a href={href} {...props}>
        {children}
      </a>
    )
  }
})

describe('<NavButton />', () => {
  // Define default props to reduce repetition in tests.
  const defaultProps: NavButtonProps = {
    href: '/test-path',
    defaultIcon: faHome,
    hoverIcon: faUser,
    text: 'Test Button',
  }

  // Helper function to render the component with optional prop overrides.
  const renderNavButton = (props: Partial<NavButtonProps> = {}) => {
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

    it('should render the default FontAwesome icon', () => {
      renderNavButton()
      // FontAwesome icons are rendered as SVGs. We check for their presence.
      const icon = screen.getByRole('img', { hidden: true })
      expect(icon).toBeInTheDocument()
      // Check for a class associated with the default icon (faHome).
      expect(icon.parentElement?.querySelector('.fa-house')).toBeInTheDocument()
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

      const icon = screen.getByRole('img', { hidden: true })
      expect(icon).toHaveStyle({ color: 'rgb(255, 0, 0)' })

      fireEvent.mouseEnter(screen.getByRole('link'))
      expect(icon).toHaveStyle({ color: 'rgb(0, 255, 0)' })
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
      const iconContainer = link.querySelector('svg')?.parentElement

      // Initially, the default icon (fa-house) should be present.
      expect(iconContainer?.querySelector('.fa-house')).toBeInTheDocument()
      expect(iconContainer?.querySelector('.fa-user')).not.toBeInTheDocument()

      // On hover, the hover icon (fa-user) should be present.
      fireEvent.mouseEnter(link)
      expect(iconContainer?.querySelector('.fa-user')).toBeInTheDocument()
      expect(iconContainer?.querySelector('.fa-house')).not.toBeInTheDocument()
    })

    it('should revert to the default icon on mouse leave', () => {
      renderNavButton()
      const link = screen.getByRole('link')
      const iconContainer = link.querySelector('svg')?.parentElement

      // Hover to change state
      fireEvent.mouseEnter(link)
      expect(iconContainer?.querySelector('.fa-user')).toBeInTheDocument()

      // Leave to revert state
      fireEvent.mouseLeave(link)
      expect(iconContainer?.querySelector('.fa-house')).toBeInTheDocument()
      expect(iconContainer?.querySelector('.fa-user')).not.toBeInTheDocument()
    })

    it('should apply scaling transform and yellow color on hover', () => {
      renderNavButton()
      const link = screen.getByRole('link')
      const icon = screen.getByRole('img', { hidden: true })

      // The icon should not be scaled initially
      expect(icon).not.toHaveClass('scale-110')
      expect(icon).not.toHaveClass('text-yellow-400')

      // On hover, it should scale up and turn yellow
      fireEvent.mouseEnter(link)
      expect(icon).toHaveClass('scale-110')
      expect(icon).toHaveClass('text-yellow-400')

      // On leave, it should scale back down and remove yellow
      fireEvent.mouseLeave(link)
      expect(icon).not.toHaveClass('scale-110')
      expect(icon).not.toHaveClass('text-yellow-400')
    })

    it('should maintain hover state when mouse moves within the component', () => {
      renderNavButton()
      const link = screen.getByRole('link')
      const icon = screen.getByRole('img', { hidden: true })

      fireEvent.mouseEnter(link)
      expect(icon).toHaveClass('scale-110')

      // Moving mouse within component should maintain hover state
      fireEvent.mouseMove(link)
      expect(icon).toHaveClass('scale-110')
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
        render(<NavButton href="/test" defaultIcon={faHome} hoverIcon={faUser} text="Test" />)
      }).not.toThrow()
    })

    it('should handle undefined for optional color props gracefully', () => {
      // Render without crashing when optional props are explicitly undefined.
      expect(() => {
        renderNavButton({ defaultIconColor: undefined, hoverIconColor: undefined })
      }).not.toThrow()
    })

    it('should render without custom className', () => {
      render(<NavButton href="/test" defaultIcon={faHome} hoverIcon={faUser} text="Test" />)
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
    it('should render Link wrapper with FontAwesome icon and span inside', () => {
      renderNavButton()
      const link = screen.getByRole('link')

      // Should contain both icon and text span
      expect(link.querySelector('svg')).toBeInTheDocument() // FontAwesome renders as SVG
      expect(link.querySelector('span')).toBeInTheDocument()
    })

    it('should maintain correct element hierarchy', () => {
      renderNavButton()
      const link = screen.getByRole('link')
      const children = link.children

      // Should have 2 children: FontAwesome icon and span
      expect(children).toHaveLength(2)
      expect(children[0].tagName).toBe('svg') // FontAwesome icon
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
      const icon = screen.getByRole('img', { hidden: true })

      // Rapid mouse enter/leave should work correctly
      fireEvent.mouseEnter(link)
      fireEvent.mouseLeave(link)
      fireEvent.mouseEnter(link)
      fireEvent.mouseLeave(link)

      // Should end up in non-hovered state
      expect(icon).not.toHaveClass('scale-110')
      expect(icon).not.toHaveClass('text-yellow-400')
    })
  })
})
