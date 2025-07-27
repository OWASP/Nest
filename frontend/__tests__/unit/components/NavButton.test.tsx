import { render, screen, fireEvent } from '@testing-library/react';
import { faHome, faUser, faCog } from '@fortawesome/free-solid-svg-icons';
import NavButton from 'components/NavButton';
import type { NavButtonProps } from 'types/button';

/**
 * Mocking Next.js's Link component is crucial for unit testing.
 * This mock isolates the NavButton component from the Next.js routing system,
 * allowing us to test its own logic without external dependencies.
 * We render a simple anchor tag `<a>` to inspect props like `href`.
 */
jest.mock('next/link', () => {
  // The mock takes the same props as a real Next.js Link component.
  // It passes them down to a standard `a` element.
  return function MockLink({ children, href, ...props }: any) {
    return (
      <a href={href} {...props}>
        {children}
      </a>
    );
  };
});

// Main test suite for the NavButton component.
describe('NavButton', () => {
  // Define a set of default props to be used in most tests.
  // This reduces repetition and makes tests easier to read.
  const defaultProps: NavButtonProps = {
    href: '/home',
    defaultIcon: faHome,
    hoverIcon: faUser,
    text: 'Home',
  };

  /**
   * A helper function to render the NavButton component.
   * It merges any provided props with the default props,
   * making it easy to test different component variations.
   * @param {Partial<NavButtonProps>} props - Optional props to override defaults.
   * @returns The result of the `render` call from @testing-library/react.
   */
  const renderNavButton = (props: Partial<NavButtonProps> = {}) => {
    return render(<NavButton {...defaultProps} {...props} />);
  };

  // Group tests related to initial rendering and basic structure.
  describe('Rendering and DOM Structure', () => {
    it('renders successfully with minimal required props', () => {
      renderNavButton();
      // Check if the button text is rendered.
      expect(screen.getByText('Home')).toBeInTheDocument();
      // Verify the link has the correct href attribute.
      expect(screen.getByRole('link')).toHaveAttribute('href', '/home');
    });

    it('applies a custom className when provided', () => {
      const customClass = 'my-custom-class';
      renderNavButton({ className: customClass });
      const linkElement = screen.getByRole('link');
      expect(linkElement).toHaveClass(customClass);
    });

    it('renders the correct text content', () => {
      const buttonText = 'Profile Page';
      renderNavButton({ text: buttonText });
      expect(screen.getByText(buttonText)).toBeInTheDocument();
    });

    it('has the correct base DOM structure and essential CSS classes', () => {
        renderNavButton();
        const linkElement = screen.getByRole('link');
        // Check for essential layout and styling classes.
        expect(linkElement).toHaveClass('group', 'relative', 'flex', 'items-center', 'justify-center', 'rounded-md', 'p-4');
        // Check for typography and color classes.
        expect(linkElement).toHaveClass('text-sm', 'font-medium', 'text-black', 'dark:text-white');
    });
  });

  // Group tests related to the component's icon behavior.
  describe('Icon Rendering and State Changes', () => {
    it('renders the default icon initially', () => {
      renderNavButton();
      // The FontAwesome icon is rendered as an SVG with role="img".
      const icon = screen.getByRole('img', { hidden: true });
      expect(icon).toBeInTheDocument();
      // Check if the initial icon corresponds to the defaultIcon prop.
      expect(icon.getAttribute('data-icon')).toBe(faHome.iconName);
    });

    it('switches to the hover icon on mouse enter and back on mouse leave', () => {
      renderNavButton();
      const linkElement = screen.getByRole('link');
      
      // Initial state: default icon should be visible.
      let icon = screen.getByRole('img', { hidden: true });
      expect(icon.getAttribute('data-icon')).toBe(faHome.iconName);

      // Simulate mouse enter event.
      fireEvent.mouseEnter(linkElement);
      icon = screen.getByRole('img', { hidden: true });
      // The icon should now be the hoverIcon.
      expect(icon.getAttribute('data-icon')).toBe(faUser.iconName);

      // Simulate mouse leave event.
      fireEvent.mouseLeave(linkElement);
      icon = screen.getByRole('img', { hidden: true });
      // The icon should revert to the defaultIcon.
      expect(icon.getAttribute('data-icon')).toBe(faHome.iconName);
    });
  });

  // Group tests for behavior driven by props.
  describe('Prop-based Behavior', () => {
    it('applies default and hover icon colors correctly', () => {
      renderNavButton({
        defaultIconColor: 'rgb(0, 0, 255)', // blue
        hoverIconColor: 'rgb(255, 0, 0)',   // red
      });
      const linkElement = screen.getByRole('link');
      const icon = screen.getByRole('img', { hidden: true });

      // Check initial color.
      expect(icon).toHaveStyle({ color: 'rgb(0, 0, 255)' });

      // Check color on hover.
      fireEvent.mouseEnter(linkElement);
      expect(icon).toHaveStyle({ color: 'rgb(255, 0, 0)' });

      // Check color after hover ends.
      fireEvent.mouseLeave(linkElement);
      expect(icon).toHaveStyle({ color: 'rgb(0, 0, 255)' });
    });

    it('uses different icons for default and hover states as per props', () => {
        renderNavButton({ defaultIcon: faCog, hoverIcon: faHome });
        const linkElement = screen.getByRole('link');
        
        // Check initial icon
        let icon = screen.getByRole('img', { hidden: true });
        expect(icon.getAttribute('data-icon')).toBe(faCog.iconName);
        
        // Check hover icon
        fireEvent.mouseEnter(linkElement);
        icon = screen.getByRole('img', { hidden: true });
        expect(icon.getAttribute('data-icon')).toBe(faHome.iconName);
    });
  });

  // Group tests for event handling and accessibility.
  describe('Event Handling and Accessibility', () => {
    it('has the correct accessibility role', () => {
      renderNavButton();
      expect(screen.getByRole('link', { name: 'Home' })).toBeInTheDocument();
    });

    it('includes target="_blank" and rel="noopener noreferrer" for security', () => {
      renderNavButton();
      const linkElement = screen.getByRole('link');
      expect(linkElement).toHaveAttribute('target', '_blank');
      expect(linkElement).toHaveAttribute('rel', 'noopener noreferrer');
    });

    it('applies focus-visible styles for keyboard navigation', () => {
        renderNavButton();
        const linkElement = screen.getByRole('link');
        // These classes are critical for accessibility, showing a ring on focus.
        expect(linkElement).toHaveClass('focus-visible:outline-none', 'focus-visible:ring-1');
    });
  });

  // Group tests for edge cases and invalid inputs.
  describe('Edge Cases and Invalid Inputs', () => {
    it('handles an empty string for the text prop gracefully', () => {
      renderNavButton({ text: '' });
      // The link should still render, but the accessible name might be missing.
      const linkElement = screen.getByRole('link');
      expect(linkElement).toBeInTheDocument();
      // The text span should not be present.
      expect(screen.queryByText(/.+/)).not.toBeInTheDocument();
    });

    it('handles very long text without breaking', () => {
      const longText = 'a'.repeat(500);
      renderNavButton({ text: longText });
      expect(screen.getByText(longText)).toBeInTheDocument();
      // The component uses `whitespace-pre`, so long text should be handled by CSS.
      expect(screen.getByText(longText)).toHaveClass('truncate');
    });

    it('handles undefined for optional props without crashing', () => {
      // Render with only the required props to ensure no crashes.
      const { unmount } = render(
        <NavButton
          href="/test"
          defaultIcon={faHome}
          hoverIcon={faUser}
          text="Test"
          className={undefined}
          defaultIconColor={undefined}
          hoverIconColor={undefined}
        />
      );
      expect(screen.getByRole('link')).toBeInTheDocument();
      // Clean up the rendered component.
      unmount();
    });

    it('handles complex href values correctly', () => {
        const complexHref = 'https://example.com/path?query=value&another=true#section-id';
        renderNavButton({ href: complexHref });
        expect(screen.getByRole('link')).toHaveAttribute('href', complexHref);
    });
  });
});
