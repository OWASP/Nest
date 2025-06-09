import { render, screen } from '@testing-library/react'
import BreadCrumbs from 'components/BreadCrumbs'
import '@testing-library/jest-dom'

const renderBreadCrumbs = (items = []) =>
  render(<BreadCrumbs breadcrumbItems={items} />)

const sampleItems = [
  { title: 'Dashboard', path: '/dashboard' },
  { title: 'Users', path: '/dashboard/users' },
  { title: 'Profile', path: '/dashboard/users/profile' },
]

describe('BreadCrumbs', () => {
  test('does not render when breadcrumb item is empty', () => {
    renderBreadCrumbs()
    expect(screen.queryByText('Home')).not.toBeInTheDocument()
  })

  test('renders breadcrumb with multiple segments', () => {
    renderBreadCrumbs(sampleItems)
    expect(screen.getByText('Home')).toBeInTheDocument()
    expect(screen.getByText('Dashboard')).toBeInTheDocument()
    expect(screen.getByText('Users')).toBeInTheDocument()
    expect(screen.getByText('Profile')).toBeInTheDocument()
  })

  test('disables the last segment (non-clickable)', () => {
    const items = [
      { title: 'Settings', path: '/settings' },
      { title: 'Account', path: '/settings/account' },
    ]
    renderBreadCrumbs(items)
    const lastSegment = screen.getByText('Account')
    expect(lastSegment).toBeInTheDocument()
    expect(lastSegment.closest('a')).toBeNull()
  })

  test('links have correct path attributes', () => {
    renderBreadCrumbs(sampleItems)
    expect(screen.getByText('Home').closest('a')).toHaveAttribute('href', '/')
    expect(screen.getByText('Dashboard').closest('a')).toHaveAttribute('href', '/dashboard')
    expect(screen.getByText('Users').closest('a')).toHaveAttribute('href', '/dashboard/users')
  })

  test('links have hover styles', () => {
    const items = [
      { title: 'Dashboard', path: '/dashboard' },
      { title: 'Users', path: '/dashboard/users' },
    ]
    renderBreadCrumbs(items)
    expect(screen.getByText('Home').closest('a')).toHaveClass('hover:text-blue-700', 'hover:underline')
    expect(screen.getByText('Dashboard').closest('a')).toHaveClass('hover:text-blue-700', 'hover:underline')
  })
})
