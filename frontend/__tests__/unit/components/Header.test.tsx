import { render, screen } from '@testing-library/react'
import type { ImgHTMLAttributes } from 'react'
import type { Link } from 'types/link'
import Header from 'components/Header'

jest.mock('next/navigation', () => ({
  usePathname: () => '/',
  useRouter: () => ({ push: jest.fn() }),
}))

jest.mock('next/image', () => ({
  __esModule: true,
  default: (props: ImgHTMLAttributes<HTMLImageElement> & { priority?: boolean }) => (
    <span role="img" aria-label={props.alt ?? ''} />
  ),
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
  default: ({ link }: { link: Link }) => (
    <div data-testid={`nav-dropdown-${link.text}`}>{link.text} (Dropdown)</div>
  ),
}))

jest.mock('components/UserMenu', () => ({
  __esModule: true,
  default: () => <div data-testid="user-menu">User Menu</div>,
}))

jest.mock('components/GlobalSearch', () => ({
  __esModule: true,
  default: () => <div data-testid="global-search">Global Search</div>,
}))

describe('Header Navigation', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  test('renders Community link without dropdown', () => {
    render(<Header isGitHubAuthEnabled={false} />)

    const communityLinks = screen.getAllByRole('link', { name: /Community/i })
    expect(communityLinks[0]).toHaveAttribute('href', '/community')

    const dropdown = screen.queryByTestId('nav-dropdown-Community')
    expect(dropdown).not.toBeInTheDocument()
  })

  test('renders header with all main navigation links', () => {
    render(<Header isGitHubAuthEnabled={false} />)

    expect(screen.getAllByRole('link', { name: /Community/i })[0]).toHaveAttribute(
      'href',
      '/community'
    )
    expect(screen.getAllByRole('link', { name: /Projects/i })[0]).toHaveAttribute(
      'href',
      '/projects'
    )
    expect(screen.getAllByRole('link', { name: /Contribute/i })[0]).toHaveAttribute(
      'href',
      '/contribute'
    )
    expect(screen.getAllByRole('link', { name: /About/i })[0]).toHaveAttribute('href', '/about')
  })

  test('renders logo with correct href', () => {
    render(<Header isGitHubAuthEnabled={false} />)

    const logoLink = screen.getAllByRole('img', { name: 'OWASP Logo' })[0].closest('a')
    expect(logoLink).toHaveAttribute('href', '/')
  })
})
