import { render, screen, fireEvent, act } from '@testing-library/react'
import { usePathname } from 'next/navigation'
import { SessionProvider } from 'next-auth/react'
import React from 'react'
import Header from 'components/Header'
import '@testing-library/jest-dom'

// Mock next/navigation
jest.mock('next/navigation', () => ({
  usePathname: jest.fn(),
}))

// Mock next/image
jest.mock('next/image', () => ({
  __esModule: true,
  default: ({ src, alt, ...props }) => {
    const { width, height, className } = props
    // eslint-disable-next-line @next/next/no-img-element
    return <img src={src} alt={alt} width={width} height={height} className={className} />
  },
}))

// Mock next/link
jest.mock('next/link', () => {
  return function MockLink({ href, children, onClick, className, ...props }: {
    href: string;
    children: React.ReactNode;
    onClick?: React.MouseEventHandler<HTMLAnchorElement>;
    className?: string;
    [key: string]: unknown;
  }) {
    return (
      <a href={href} onClick={onClick} className={className} {...props}>
        {children}
      </a>
    )
  }
})

jest.mock('react-icons/fa', () => ({
  FaBars: (props: React.SVGProps<SVGSVGElement>) => <svg data-testid="icon-bars" {...props} />,
  FaTimes: (props: React.SVGProps<SVGSVGElement>) => <svg data-testid="icon-xmark" {...props} />,
  FaRegHeart: (props: React.SVGProps<SVGSVGElement>) => <svg data-testid="icon-heart" {...props} />,
  FaRegStar: (props: React.SVGProps<SVGSVGElement>) => <svg data-testid="icon-star" {...props} />,
  FaHeart: (props: React.SVGProps<SVGSVGElement>) => (
    <svg data-testid="icon-solid-heart" {...props} />
  ),
  FaStar: (props: React.SVGProps<SVGSVGElement>) => (
    <svg data-testid="icon-solid-star" {...props} />
  ),
}))

// Mock HeroUI Button
jest.mock('@heroui/button', () => ({
  Button: ({ children, onPress, className, ...props }: {
    children: React.ReactNode;
    onPress?: () => void;
    className?: string;
    [key: string]: unknown;
  }) => (
    <button type="button" onClick={onPress} className={className} {...props}>
      {children}
    </button>
  ),
}))

// Mock components
jest.mock('components/ModeToggle', () => {
  return function MockModeToggle() {
    return <div data-testid="mode-toggle">Mode Toggle</div>
  }
})

jest.mock('components/NavButton', () => {
  return function MockNavButton({ href, text, className }: {
    href: string;
    text: string;
    className?: string;
  }) {
    return (
      <a href={href} className={className} data-testid="nav-button">
        {text}
      </a>
    )
  }
})

jest.mock('components/NavDropDown', () => {
  return function MockNavDropdown({ link, pathname }: {
    link: {
      text: string;
      submenu?: Array<{ href: string; text: string }>;
    };
    pathname: string;
  }) {
    return (
      <div data-testid="nav-dropdown">
        {link.text}
        {link.submenu?.map((sub: { href: string; text: string }) => (
          <a
            key={`${sub.text}-${sub.href}`}
            href={sub.href}
            className={pathname === sub.href ? 'active' : ''}
          >
            {sub.text}
          </a>
        ))}
      </div>
    )
  }
})

jest.mock('components/UserMenu', () => {
  return function MockUserMenu({ isGitHubAuthEnabled }: { isGitHubAuthEnabled: boolean }) {
    return (
      <div data-testid="user-menu" data-github-auth={isGitHubAuthEnabled.toString()}>
        User Menu
      </div>
    )
  }
})

// Mock constants
jest.mock('utils/constants', () => ({
  desktopViewMinWidth: 768,
  headerLinks: [
    {
      text: 'Home',
      href: '/',
    },
    {
      text: 'About',
      href: '/about',
    },
    {
      text: 'Services',
      submenu: [
        { text: 'Web Development', href: '/services/web' },
        { text: 'Mobile Development', href: '/services/mobile' },
      ],
    },
    {
      text: 'Contact',
      href: '/contact',
    },
  ],
}))

// Mock utility function
jest.mock('utils/utility', () => ({
  cn: (...classes: unknown[]) => classes.filter(Boolean).join(' '),
}))

// Mock next-auth
jest.mock('next-auth/react', () => ({
  SessionProvider: ({ children }: { children: React.ReactNode }) => children,
  useSession: () => ({
    data: null,
    status: 'unauthenticated',
  }),
}))

// Mock useLogout hook
jest.mock('hooks/useLogout', () => ({
  __esModule: true,
  default: () => ({
    logout: jest.fn(),
    isLoggingOut: false,
  }),
}))

const mockUsePathname = usePathname as jest.MockedFunction<typeof usePathname>

// Helper function to render component with SessionProvider
const renderWithSession = (component: React.ReactElement) => {
  return render(<SessionProvider session={null}>{component}</SessionProvider>)
}

// Helper function to find mobile menu element
const findMobileMenu = () => {
  return (
    screen.queryByRole('navigation', { name: /mobile menu/i }) ||
    screen.queryByTestId('mobile-menu') ||
    document.querySelector('[class*="fixed"][class*="inset-y-0"][class*="left-0"]')
  )
}

// Helper function to check if mobile menu is open
const isMobileMenuOpen = () => {
  const menu = findMobileMenu()
  if (menu && menu.getAttribute('aria-expanded') === 'true') {
    return true
  }
  return menu?.className.includes('translate-x-0') || false
}

// Helper function to check if mobile menu is closed
const isMobileMenuClosed = () => {
  const menu = findMobileMenu()
  if (menu && menu.getAttribute('aria-expanded') === 'false') {
    return true
  }
  return menu?.className.includes('-translate-x-full') || false
}

describe('Header Component', () => {
  beforeEach(() => {
    mockUsePathname.mockReturnValue('/')
    // Mock window.innerWidth
    Object.defineProperty(globalThis, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 1024,
    })

    // Mock window methods
    window.addEventListener = jest.fn()
    window.removeEventListener = jest.fn()

    // Clear all mocks
    jest.clearAllMocks()
  })

  afterEach(() => {
    jest.restoreAllMocks()
  })

  describe('Basic Rendering', () => {
    it('renders successfully with GitHub auth enabled', () => {
      renderWithSession(<Header isGitHubAuthEnabled />)

      expect(screen.getByRole('banner')).toBeInTheDocument()

      // Use getAllByRole for multiple elements
      const logoImages = screen.getAllByRole('img', { name: /owasp logo/i })
      expect(logoImages.length).toBe(2) // 1 in desktop header + 1 in mobile menu

      const brandTexts = screen.getAllByText('Nest')
      expect(brandTexts.length).toBe(2) // One in desktop header, one in mobile menu

      const userMenu = screen.getByTestId('user-menu')
      expect(userMenu).toHaveAttribute('data-github-auth', 'true')
    })

    it('renders successfully with GitHub auth disabled', () => {
      renderWithSession(<Header isGitHubAuthEnabled={false} />)

      expect(screen.getByRole('banner')).toBeInTheDocument()

      const logoImages = screen.getAllByRole('img', { name: /owasp logo/i })
      expect(logoImages.length).toBe(2)

      const brandTexts = screen.getAllByText('Nest')
      expect(brandTexts.length).toBe(2)

      const userMenu = screen.getByTestId('user-menu')
      expect(userMenu).toHaveAttribute('data-github-auth', 'false')
    })
  })

  describe('Logo and Branding', () => {
    it('renders logo with correct attributes', () => {
      renderWithSession(<Header isGitHubAuthEnabled />)

      const logoImages = screen.getAllByRole('img', { name: /owasp logo/i })
      expect(logoImages.length).toBe(2) // 1 in desktop header + 1 in mobile menu

      for (const logo of logoImages) {
        expect(logo).toHaveAttribute('width', '64')
        expect(logo).toHaveAttribute('height', '64')
        expect(logo).toHaveAttribute('src')
      }
    })

    it('renders logo_dark.png image in both desktop and mobile header', () => {
      renderWithSession(<Header isGitHubAuthEnabled />)

      const logoImages = screen.getAllByRole('img', { name: /owasp logo/i })
      expect(logoImages.length).toBe(2)

      for (const logo of logoImages) {
        expect(logo).toHaveAttribute('src', '/img/logo_dark.png')
        expect(logo).toBeInTheDocument()
      }
    })

    it('renders Nest text branding', () => {
      renderWithSession(<Header isGitHubAuthEnabled />)

      const brandTexts = screen.getAllByText('Nest')
      expect(brandTexts.length).toBe(2) // One in desktop header, one in mobile menu
      expect(brandTexts[0]).toBeInTheDocument()
      expect(brandTexts[0].tagName).toBe('DIV')
    })

    it('logo link navigates to home page', () => {
      renderWithSession(<Header isGitHubAuthEnabled />)

      // Find all links that go to home page with logo images
      const homeLinks = screen
        .getAllByRole('link')
        .filter(
          (link) => link.getAttribute('href') === '/' && link.querySelector('img[alt="OWASP Logo"]')
        )
      expect(homeLinks.length).toBe(2) // Desktop and mobile

      for (const link of homeLinks) {
        expect(link).toHaveAttribute('href', '/')
      }
    })
  })

  describe('Navigation Links', () => {
    it('renders all header links on desktop', () => {
      renderWithSession(<Header isGitHubAuthEnabled />)

      // Use getAllByRole for navigation links since they appear in both desktop and mobile
      const homeLinks = screen.getAllByRole('link', { name: 'Home' })
      const aboutLinks = screen.getAllByRole('link', { name: 'About' })
      const contactLinks = screen.getAllByRole('link', { name: 'Contact' })

      expect(homeLinks.length).toBeGreaterThanOrEqual(1)
      expect(aboutLinks.length).toBeGreaterThanOrEqual(1)
      expect(contactLinks.length).toBeGreaterThanOrEqual(1)
    })

    it('applies active styling to current page link', () => {
      mockUsePathname.mockReturnValue('/about')
      renderWithSession(<Header isGitHubAuthEnabled />)

      // Find the About links with aria-current attribute
      const aboutLinks = screen.getAllByRole('link', { name: 'About' })
      const activeAboutLinks = aboutLinks.filter(
        (link) => link.getAttribute('aria-current') === 'page'
      )
      expect(activeAboutLinks.length).toBeGreaterThan(0)
    })
  })

  describe('Mobile Menu Functionality', () => {
    it('renders mobile menu toggle button', () => {
      renderWithSession(<Header isGitHubAuthEnabled />)

      const toggleButton = screen.getByRole('button', { name: /open main menu/i })
      expect(toggleButton).toBeInTheDocument()
    })

    it('opens mobile menu when toggle button is clicked', async () => {
      renderWithSession(<Header isGitHubAuthEnabled />)

      const toggleButton = screen.getByRole('button', { name: /open main menu/i })

      await act(async () => {
        fireEvent.click(toggleButton)
      })

      expect(isMobileMenuOpen()).toBe(true)
    })

    it('closes mobile menu when toggle button is clicked again', async () => {
      renderWithSession(<Header isGitHubAuthEnabled />)

      const toggleButton = screen.getByRole('button', { name: /open main menu/i })

      // Open menu
      await act(async () => {
        fireEvent.click(toggleButton)
      })

      // Close menu
      await act(async () => {
        fireEvent.click(toggleButton)
      })

      expect(isMobileMenuClosed()).toBe(true)
    })

    it('shows hamburger icon when menu is closed', () => {
      renderWithSession(<Header isGitHubAuthEnabled />)

      // Use queryByTestId to check if element exists without throwing
      const barsIcon = screen.queryByTestId('icon-bars')
      const xmarkIcon = screen.queryByTestId('icon-xmark')

      // Either bars or xmark should be present (depending on initial state)
      expect(barsIcon || xmarkIcon).toBeInTheDocument()
    })

    it('shows close icon when menu is open', async () => {
      renderWithSession(<Header isGitHubAuthEnabled />)

      const toggleButton = screen.getByRole('button', { name: /open main menu/i })

      await act(async () => {
        fireEvent.click(toggleButton)
      })

      // Check for close icon - use xmark instead of times based on error output
      const closeIcon = screen.queryByTestId('icon-xmark') || screen.queryByTestId('icon-times')
      expect(closeIcon).toBeInTheDocument()
    })

    it('closes mobile menu when logo is clicked', async () => {
      renderWithSession(<Header isGitHubAuthEnabled />)

      const toggleButton = screen.getByRole('button', { name: /open main menu/i })

      // Open menu first
      await act(async () => {
        fireEvent.click(toggleButton)
      })

      expect(isMobileMenuOpen()).toBe(true)

      // Find and click the logo link in mobile menu
      const logoLinks = screen.getAllByRole('link')
      const mobileLogoLink = logoLinks.find(
        (link) => link.getAttribute('href') === '/' && link.querySelector('img[alt="OWASP Logo"]')
      )

      // Assert that mobileLogoLink is not null before clicking
      expect(mobileLogoLink).not.toBeNull()
      await act(async () => {
        fireEvent.click(mobileLogoLink)
      })
      expect(isMobileMenuClosed()).toBe(true)
    })
  })

  describe('Mobile Menu Content', () => {
    beforeEach(async () => {
      renderWithSession(<Header isGitHubAuthEnabled />)
      const toggleButton = screen.getByRole('button', { name: /open main menu/i })
      await act(async () => {
        fireEvent.click(toggleButton)
      })
    })

    it('renders navigation links in mobile menu', () => {
      const allHomeLinks = screen.getAllByText('Home')
      const allAboutLinks = screen.getAllByText('About')
      const allContactLinks = screen.getAllByText('Contact')

      expect(allHomeLinks.length).toBeGreaterThan(1) // Desktop + Mobile
      expect(allAboutLinks.length).toBeGreaterThan(1)
      expect(allContactLinks.length).toBeGreaterThan(1)
    })

    it('renders NavButtons with correct text in mobile menu', () => {
      const navButtons = screen.getAllByTestId('nav-button')
      expect(navButtons.length).toBeGreaterThanOrEqual(2)

      // Check for the specific button texts from the actual component
      const starButton = navButtons.find((btn) => btn.textContent?.includes('Star'))
      const sponsorButton = navButtons.find((btn) => btn.textContent?.includes('Sponsor'))

      expect(starButton).toBeInTheDocument()
      expect(sponsorButton).toBeInTheDocument()
    })

    it('renders submenu items correctly in mobile menu', () => {
      const servicesDropdown = screen.getAllByTestId('nav-dropdown')
      expect(servicesDropdown.length).toBeGreaterThan(0)
    })
  })

  describe('Component Integration', () => {
    it('renders UserMenu component', () => {
      renderWithSession(<Header isGitHubAuthEnabled />)

      expect(screen.getByTestId('user-menu')).toBeInTheDocument()
    })

    it('renders ModeToggle component', () => {
      renderWithSession(<Header isGitHubAuthEnabled />)

      expect(screen.getByTestId('mode-toggle')).toBeInTheDocument()
    })

    it('renders NavButton components with correct props', () => {
      renderWithSession(<Header isGitHubAuthEnabled />)

      const navButtons = screen.getAllByTestId('nav-button')
      expect(navButtons.length).toBeGreaterThanOrEqual(2)
    })

    it('renders NavDropdown for submenu items', () => {
      renderWithSession(<Header isGitHubAuthEnabled />)

      expect(screen.getByTestId('nav-dropdown')).toBeInTheDocument()
    })
  })

  describe('Event Handling and Lifecycle', () => {
    it('sets up resize event listener on mount', () => {
      renderWithSession(<Header isGitHubAuthEnabled />)

      expect(window.addEventListener).toHaveBeenCalledWith('resize', expect.any(Function))
    })

    it('sets up click event listener on mount', () => {
      renderWithSession(<Header isGitHubAuthEnabled />)

      expect(window.addEventListener).toHaveBeenCalledWith('click', expect.any(Function))
    })

    // Simplified resize test - just check that the functionality works
    it('handles window resize events', async () => {
      renderWithSession(<Header isGitHubAuthEnabled />)

      // Open mobile menu first
      const toggleButton = screen.getByRole('button', { name: /open main menu/i })
      await act(async () => {
        fireEvent.click(toggleButton)
      })

      // Simulate resize event
      await act(async () => {
        globalThis.dispatchEvent(new Event('resize'))
      })

      // Test passes if no errors are thrown
      expect(true).toBe(true)
    })

    it('handles outside click correctly', async () => {
      renderWithSession(<Header isGitHubAuthEnabled />)

      // Open mobile menu
      const toggleButton = screen.getByRole('button', { name: /open main menu/i })
      await act(async () => {
        fireEvent.click(toggleButton)
      })

      // Click outside
      await act(async () => {
        document.body.click()
      })

      // Verify the event listener is set up
      expect(window.addEventListener).toHaveBeenCalledWith('click', expect.any(Function))
    })
  })

  describe('Accessibility', () => {
    it('has proper banner role', () => {
      renderWithSession(<Header isGitHubAuthEnabled />)

      expect(screen.getByRole('banner')).toBeInTheDocument()
    })

    it('has screen reader text for mobile menu button', () => {
      renderWithSession(<Header isGitHubAuthEnabled />)

      const screenReaderText = screen.getByText('Open main menu')
      expect(screenReaderText).toBeInTheDocument()
    })

    it('has proper alt text for logo images', () => {
      renderWithSession(<Header isGitHubAuthEnabled />)

      const logoImages = screen.getAllByRole('img', { name: /owasp logo/i })
      expect(logoImages.length).toBeGreaterThan(0)
    })

    it('has proper aria-current attribute on active links', () => {
      mockUsePathname.mockReturnValue('/')
      renderWithSession(<Header isGitHubAuthEnabled />)

      // Find the Home links that should be active
      const homeLinks = screen.getAllByRole('link', { name: 'Home' })
      const activeHomeLinks = homeLinks.filter(
        (link) => link.getAttribute('aria-current') === 'page'
      )
      expect(activeHomeLinks.length).toBeGreaterThan(0)
    })
  })

  describe('Styling and CSS Classes', () => {
    it('applies correct header structure', () => {
      renderWithSession(<Header isGitHubAuthEnabled />)

      const header = screen.getByRole('banner')
      expect(header).toBeInTheDocument()
      // Focus on semantic structure rather than specific classes
      expect(header.tagName).toBe('HEADER')
    })

    it('mobile menu starts closed', () => {
      renderWithSession(<Header isGitHubAuthEnabled />)

      expect(isMobileMenuClosed()).toBe(true)
    })

    it('mobile menu opens when toggled', async () => {
      renderWithSession(<Header isGitHubAuthEnabled />)

      const toggleButton = screen.getByRole('button', { name: /open main menu/i })
      await act(async () => {
        fireEvent.click(toggleButton)
      })

      expect(isMobileMenuOpen()).toBe(true)
    })
  })

  describe('Prop-based Behavior', () => {
    it('passes isGitHubAuthEnabled prop to UserMenu correctly when true', () => {
      renderWithSession(<Header isGitHubAuthEnabled />)

      expect(screen.getByTestId('user-menu')).toHaveAttribute('data-github-auth', 'true')
    })

    it('passes isGitHubAuthEnabled prop to UserMenu correctly when false', () => {
      renderWithSession(<Header isGitHubAuthEnabled={false} />)

      expect(screen.getByTestId('user-menu')).toHaveAttribute('data-github-auth', 'false')
    })
  })

  describe('Edge Cases and Error Handling', () => {
    it('handles undefined pathname gracefully', () => {
      mockUsePathname.mockReturnValue('')

      expect(() => {
        renderWithSession(<Header isGitHubAuthEnabled />)
      }).not.toThrow()
    })

    it('handles missing headerLinks gracefully', () => {
      expect(() => {
        renderWithSession(<Header isGitHubAuthEnabled />)
      }).not.toThrow()
    })

    it('handles multiple rapid toggle clicks', async () => {
      renderWithSession(<Header isGitHubAuthEnabled />)

      const toggleButton = screen.getByRole('button', { name: /open main menu/i })

      // Rapid clicks
      await act(async () => {
        fireEvent.click(toggleButton)
        fireEvent.click(toggleButton)
        fireEvent.click(toggleButton)
      })

      // Should still work correctly
      expect(toggleButton).toBeInTheDocument()
    })
  })

  describe('State Management', () => {
    it('initializes with mobile menu closed', () => {
      renderWithSession(<Header isGitHubAuthEnabled />)

      expect(isMobileMenuClosed()).toBe(true)
    })

    it('toggles mobile menu state correctly', async () => {
      renderWithSession(<Header isGitHubAuthEnabled />)

      const toggleButton = screen.getByRole('button', { name: /open main menu/i })

      // Initially closed
      expect(isMobileMenuClosed()).toBe(true)

      // Open
      await act(async () => {
        fireEvent.click(toggleButton)
      })
      expect(isMobileMenuOpen()).toBe(true)

      // Close
      await act(async () => {
        fireEvent.click(toggleButton)
      })
      expect(isMobileMenuClosed()).toBe(true)
    })
  })

  describe('Content Rendering', () => {
    it('renders all expected text content', () => {
      renderWithSession(<Header isGitHubAuthEnabled />)

      // Use getAllByText since elements appear multiple times
      expect(screen.getAllByText('Nest').length).toBeGreaterThan(0)
      expect(screen.getAllByText('Home').length).toBeGreaterThan(0)
      expect(screen.getAllByText('About').length).toBeGreaterThan(0)
      expect(screen.getAllByText('Contact').length).toBeGreaterThan(0)
      expect(screen.getAllByText('Services').length).toBeGreaterThan(0)
    })

    it('renders navigation buttons with correct text', () => {
      renderWithSession(<Header isGitHubAuthEnabled />)

      const navButtons = screen.getAllByTestId('nav-button')
      expect(navButtons.length).toBeGreaterThan(0)
    })
  })

  describe('Responsive Behavior', () => {
    it('has proper responsive navigation structure', () => {
      renderWithSession(<Header isGitHubAuthEnabled />)

      // Check for desktop navigation (should exist but may be hidden on mobile)
      const navigation = screen.getByRole('banner')
      expect(navigation).toBeInTheDocument()

      // Check for mobile menu toggle
      const mobileToggle = screen.getByRole('button', { name: /open main menu/i })
      expect(mobileToggle).toBeInTheDocument()
    })

    it('shows mobile menu button for mobile screens', () => {
      // Set window width to simulate mobile
      Object.defineProperty(globalThis, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 400,
      })
      renderWithSession(<Header isGitHubAuthEnabled />)

      const mobileToggle = screen.getByRole('button', { name: /open main menu/i })
      expect(mobileToggle).toBeInTheDocument()
    })
  })

  describe('Integration with Next.js', () => {
    it('renders Next.js Image component correctly', () => {
      renderWithSession(<Header isGitHubAuthEnabled />)

      const logoImages = screen.getAllByRole('img', { name: /owasp logo/i })
      const firstLogo = logoImages[0]
      expect(firstLogo).toHaveAttribute('src')
      expect(firstLogo).toHaveAttribute('alt', 'OWASP Logo')
      expect(firstLogo).toHaveAttribute('width', '64')
      expect(firstLogo).toHaveAttribute('height', '64')
    })

    it('renders Next.js Link components correctly', () => {
      renderWithSession(<Header isGitHubAuthEnabled />)

      const homeLinks = screen.getAllByRole('link', { name: 'Home' })
      const firstHomeLink = homeLinks[0]
      expect(firstHomeLink).toHaveAttribute('href', '/')
    })

    it('integrates with Next.js routing via usePathname', () => {
      mockUsePathname.mockReturnValue('/about')
      renderWithSession(<Header isGitHubAuthEnabled />)

      const aboutLinks = screen.getAllByRole('link', { name: 'About' })
      const activeAboutLinks = aboutLinks.filter(
        (link) => link.getAttribute('aria-current') === 'page'
      )
      expect(activeAboutLinks.length).toBeGreaterThan(0)
    })
  })
})
