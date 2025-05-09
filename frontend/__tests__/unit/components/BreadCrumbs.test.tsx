import { render, screen } from '@testing-library/react'
import { usePathname } from 'next/navigation'
import BreadCrumbs from 'components/BreadCrumbs'
import '@testing-library/jest-dom'

jest.mock('next/navigation', () => ({
  usePathname: jest.fn(),
}))

describe('BreadCrumb', () => {
  afterEach(() => {
    jest.clearAllMocks()
  })

  test('does not render on root path "/"', () => {
    ;(usePathname as jest.Mock).mockReturnValue('/')

    render(<BreadCrumbs />)
    expect(screen.queryByText('Home')).not.toBeInTheDocument()
  })

  test('renders breadcrumb with multiple segments', () => {
    ;(usePathname as jest.Mock).mockReturnValue('/dashboard/users/profile')

    render(<BreadCrumbs />)

    expect(screen.getByText('Home')).toBeInTheDocument()
    expect(screen.getByText('Dashboard')).toBeInTheDocument()
    expect(screen.getByText('Users')).toBeInTheDocument()
    expect(screen.getByText('Profile')).toBeInTheDocument()
  })

  test('disables the last segment (non-clickable)', () => {
    ;(usePathname as jest.Mock).mockReturnValue('/settings/account')

    render(<BreadCrumbs />)

    const lastSegment = screen.getByText('Account')
    expect(lastSegment).toBeInTheDocument()
    expect(lastSegment).not.toHaveAttribute('href')
  })

  test('links have correct href attributes', () => {
    ;(usePathname as jest.Mock).mockReturnValue('/dashboard/users/profile')

    render(<BreadCrumbs />)

    const homeLink = screen.getByText('Home').closest('a')
    const dashboardLink = screen.getByText('Dashboard').closest('a')
    const usersLink = screen.getByText('Users').closest('a')

    expect(homeLink).toHaveAttribute('href', '/')
    expect(dashboardLink).toHaveAttribute('href', '/dashboard')
    expect(usersLink).toHaveAttribute('href', '/dashboard/users')
  })

  test('links have hover styles', () => {
    ;(usePathname as jest.Mock).mockReturnValue('/dashboard/users')

    render(<BreadCrumbs />)

    const homeLink = screen.getByText('Home').closest('a')
    const dashboardLink = screen.getByText('Dashboard').closest('a')

    expect(homeLink).toHaveClass('hover:text-blue-700', 'hover:underline')
    expect(dashboardLink).toHaveClass('hover:text-blue-700', 'hover:underline')
  })
})
