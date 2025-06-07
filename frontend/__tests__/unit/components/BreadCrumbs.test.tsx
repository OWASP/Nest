import { render, screen } from '@testing-library/react'
import BreadCrumbs from 'components/BreadCrumbs'
import '@testing-library/jest-dom'

describe('BreadCrumbs', () => {
  test('does not render when breadcrumb item is empty', () => {
    render(<BreadCrumbs breadcrumbItems={[]} />)
    expect(screen.queryByText('Home')).not.toBeInTheDocument()
  })

  test('renders breadcrumb with multiple segments', () => {
    render(
      <BreadCrumbs
        breadcrumbItems={[
          { title: 'Dashboard', path: '/dashboard' },
          { title: 'Users', path: '/dashboard/users' },
          { title: 'Profile', path: '/dashboard/users/profile' },
        ]}
      />
    )

    expect(screen.getByText('Home')).toBeInTheDocument()
    expect(screen.getByText('Dashboard')).toBeInTheDocument()
    expect(screen.getByText('Users')).toBeInTheDocument()
    expect(screen.getByText('Profile')).toBeInTheDocument()
  })

  test('disables the last segment (non-clickable)', () => {
    render(
      <BreadCrumbs
        breadcrumbItems={[
          { title: 'Settings', path: '/settings' },
          { title: 'Account', path: '/settings/account' },
        ]}
      />
    )

    const lastSegment = screen.getByText('Account')
    expect(lastSegment).toBeInTheDocument()
    expect(lastSegment.closest('a')).toBeNull()
  })

  test('links have correct path attributes', () => {
    render(
      <BreadCrumbs
        breadcrumbItems={[
          { title: 'Dashboard', path: '/dashboard' },
          { title: 'Users', path: '/dashboard/users' },
          { title: 'Profile', path: '/dashboard/users/profile' },
        ]}
      />
    )

    const homeLink = screen.getByText('Home').closest('a')
    const dashboardLink = screen.getByText('Dashboard').closest('a')
    const usersLink = screen.getByText('Users').closest('a')

    expect(homeLink).toHaveAttribute('href', '/')
    expect(dashboardLink).toHaveAttribute('href', '/dashboard')
    expect(usersLink).toHaveAttribute('href', '/dashboard/users')
  })

  test('links have hover styles', () => {
    render(
      <BreadCrumbs
        breadcrumbItems={[
          { title: 'Dashboard', path: '/dashboard' },
          { title: 'Users', path: '/dashboard/users' },
        ]}
      />
    )

    const homeLink = screen.getByText('Home').closest('a')
    const dashboardLink = screen.getByText('Dashboard').closest('a')

    expect(homeLink).toHaveClass('hover:text-blue-700', 'hover:underline')
    expect(dashboardLink).toHaveClass('hover:text-blue-700', 'hover:underline')
  })
})
