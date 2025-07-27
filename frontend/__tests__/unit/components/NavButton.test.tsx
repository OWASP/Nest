/**
 * @file Unit tests for the NavButton component.
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
  })

  describe('Prop-based Behavior', () => {
    it('should render as a link with the correct href attribute', () => {
      const href = '/custom-path'
      renderNavButton({ href })
      expect(screen.getByRole('link')).toHaveAttribute('href', href)
    })

    it('should open in a new tab with correct security attributes', () => {
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

    it('should apply scaling transform on hover', () => {
      renderNavButton()
      const link = screen.getByRole('link')
      const icon = screen.getByRole('img', { hidden: true })

      // The icon should not be scaled initially
      expect(icon).not.toHaveClass('scale-110')

      // On hover, it should scale up
      fireEvent.mouseEnter(link)
      expect(icon).toHaveClass('scale-110')

      // On leave, it should scale back down
      fireEvent.mouseLeave(link)
      expect(icon).not.toHaveClass('scale-110')
    })
  })

  describe('DOM Structure & Styling', () => {
    it('should have the correct base layout and style classes', () => {
      renderNavButton()
      const link = screen.getByRole('link')
      // Check for a few key classes to ensure structure is correct.
      expect(link).toHaveClass('group', 'relative', 'flex', 'items-center', 'justify-center')
    })

    it('should apply a custom className without removing default classes', () => {
      const customClass = 'my-custom-class'
      renderNavButton({ className: customClass })
      const link = screen.getByRole('link')
      expect(link).toHaveClass('group') // A default class
      expect(link).toHaveClass(customClass) // The custom class
    })

    it('should have correct hover and focus-visible utility classes for accessibility', () => {
      renderNavButton()
      const link = screen.getByRole('link')
      expect(link).toHaveClass('hover:ring-1')
      expect(link).toHaveClass('focus-visible:ring-1')
    })
  })

  describe('Edge Cases & Invalid Inputs', () => {
    it('should render correctly even if text is an empty string', () => {
      renderNavButton({ text: '' })
      // The link should still render, even without visible text.
      expect(screen.getByRole('link')).toBeInTheDocument()
    })

    it('should handle long text without breaking', () => {
      const longText = 'This is an extremely long text string to test wrapping and overflow'.repeat(
        10
      )
      renderNavButton({ text: longText })
      expect(screen.getByText(longText)).toBeInTheDocument()
    })

    it('should handle undefined for optional color props gracefully', () => {
      // Render without crashing when optional props are explicitly undefined.
      expect(() => {
        renderNavButton({ defaultIconColor: undefined, hoverIconColor: undefined })
      }).not.toThrow()
    })
  })
})
