import { render, screen } from '@testing-library/react'
import React from 'react'
import Header from 'components/Header'

jest.mock('next/navigation', () => ({
  usePathname: () => '/',
}))

jest.mock('next/image', () => ({
  __esModule: true,
  default: (props: any) => <img {...props} />,
}))

jest.mock('components/ModeToggle', () => ({
  __esModule: true,
  default: () => <div data-testid="mode-toggle">Mode Toggle</div>,
}))

jest.mock('components/NavButton', () => ({
  __esModule: true,
  default: ({ text, href }: { text: string; href: string }) => (
    <a href={href} data-testid={`nav-button-${text}`}>
      {text}
    </a>
  ),
}))

jest.mock('components/NavDropDown', () => ({
  __esModule: true,
  default: ({ link }: { link: any }) => (
    <div data-testid={`nav-dropdown-${link.text}`}>{link.text} (Dropdown)</div>
  ),
}))

jest.mock('components/UserMenu', () => ({
  __esModule: true,
  default: () => <div data-testid="user-menu">User Menu</div>,
}))

describe('Header Navigation', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  test('renders Community link without dropdown', () => {
    render(<Header isGitHubAuthEnabled={false} />)

    const communityLink = screen.getByRole('link', { name: /Community/i })
    expect(communityLink).toBeInTheDocument()
    expect(communityLink).toHaveAttribute('href', '/community')

    // Ensure it's not a dropdown by checking that NavDropdown is not rendered for Community
    const dropdown = screen.queryByTestId('nav-dropdown-Community')
    expect(dropdown).not.toBeInTheDocument()
  })

  test('renders header with all main navigation links', () => {
    render(<Header isGitHubAuthEnabled={false} />)

    expect(screen.getByRole('link', { name: /Community/i })).toHaveAttribute('href', '/community')
    expect(screen.getByRole('link', { name: /Projects/i })).toHaveAttribute('href', '/projects')
    expect(screen.getByRole('link', { name: /Contribute/i })).toHaveAttribute('href', '/contribute')
    expect(screen.getByRole('link', { name: /About/i })).toHaveAttribute('href', '/about')
  })

  test('renders logo with correct href', () => {
    render(<Header isGitHubAuthEnabled={false} />)

    const logoLink = screen.getByAltText('OWASP Logo').closest('a')
    expect(logoLink).toHaveAttribute('href', '/')
  })
})
