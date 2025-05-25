import { render, screen } from '@testing-library/react'
import BreadCrumbs from 'components/BreadCrumbs'
import '@testing-library/jest-dom'

describe('BreadCrumbs', () => {
  test('does not render when bcItems is empty', () => {
    render(<BreadCrumbs bcItems={[]} />)
    expect(screen.queryByText('Home')).not.toBeInTheDocument()
  })

  test('renders breadcrumb with multiple segments', () => {
    render(
      <BreadCrumbs
        bcItems={[
          { title: 'Dashboard', href: '/dashboard' },
          { title: 'Users', href: '/dashboard/users' },
          { title: 'Profile', href: '/dashboard/users/profile' },
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
        bcItems={[
          { title: 'Settings', href: '/settings' },
          { title: 'Account', href: '/settings/account' },
        ]}
      />
    )

    const lastSegment = screen.getByText('Account')
    expect(lastSegment).toBeInTheDocument()
    expect(lastSegment.closest('a')).toBeNull()
  })

  test('links have correct href attributes', () => {
    render(
      <BreadCrumbs
        bcItems={[
          { title: 'Dashboard', href: '/dashboard' },
          { title: 'Users', href: '/dashboard/users' },
          { title: 'Profile', href: '/dashboard/users/profile' },
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
        bcItems={[
          { title: 'Dashboard', href: '/dashboard' },
          { title: 'Users', href: '/dashboard/users' },
        ]}
      />
    )

    const homeLink = screen.getByText('Home').closest('a')
    const dashboardLink = screen.getByText('Dashboard').closest('a')

    expect(homeLink).toHaveClass('hover:text-blue-700', 'hover:underline')
    expect(dashboardLink).toHaveClass('hover:text-blue-700', 'hover:underline')
  })
})
