import { render, screen } from '@testing-library/react'
import BreadCrumbs from 'components/BreadCrumbs'
import '@testing-library/jest-dom'

const renderBreadCrumbs = (items = [], ariaLabel = 'breadcrumb') =>
  render(<BreadCrumbs breadcrumbItems={items} aria-label={ariaLabel} />)

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
    expect(screen.getByText('Home').closest('a')).toHaveClass(
      'hover:text-blue-700',
      'hover:underline'
    )
    expect(screen.getByText('Dashboard').closest('a')).toHaveClass(
      'hover:text-blue-700',
      'hover:underline'
    )
  })

  test('has proper accessibility attributes', () => {
    renderBreadCrumbs(sampleItems)

    // Check nav element has proper role and aria-label
    const nav = screen.getAllByRole('navigation')[0]
    expect(nav).toHaveAttribute('aria-label', 'breadcrumb')

    // Check last item has aria-current="page"
    const lastItem = screen.getByText('Profile')
    expect(lastItem).toHaveAttribute('aria-current', 'page')

    // Check Home link has proper aria-label
    const homeLink = screen.getByText('Home').closest('a')
    expect(homeLink).toHaveAttribute('aria-label', 'Go to home page')
  })

  test('supports custom aria-label', () => {
    renderBreadCrumbs(sampleItems, 'custom breadcrumb')

    const nav = screen.getAllByRole('navigation')[0]
    expect(nav).toHaveAttribute('aria-label', 'custom breadcrumb')
  })

  test('filters out invalid breadcrumb items', () => {
    const invalidItems = [
      { title: 'Valid Item', path: '/valid' },
      { title: '', path: '/invalid' }, // Missing title
      { title: 'Another Valid', path: '' }, // Missing path
      { title: 'Valid Again', path: '/valid-again' },
    ]

    renderBreadCrumbs(invalidItems)

    // Should only render valid items
    expect(screen.getByText('Home')).toBeInTheDocument()
    expect(screen.getByText('Valid Item')).toBeInTheDocument()
    expect(screen.getByText('Valid Again')).toBeInTheDocument()
    expect(screen.queryByText('Another Valid')).not.toBeInTheDocument()
  })

  test('has focus styles for keyboard navigation', () => {
    renderBreadCrumbs(sampleItems)

    const homeLink = screen.getByText('Home').closest('a')
    const dashboardLink = screen.getByText('Dashboard').closest('a')

    expect(homeLink).toHaveClass('focus:outline-none', 'focus:ring-2', 'focus:ring-blue-500')
    expect(dashboardLink).toHaveClass('focus:outline-none', 'focus:ring-2', 'focus:ring-blue-500')
  })

  test('separator icon is hidden from screen readers', () => {
    renderBreadCrumbs(sampleItems)

    // Look for SVG elements with aria-hidden="true"
    const separators = screen.getAllByRole('img', { hidden: true })
    separators.forEach((separator) => {
      expect(separator).toHaveAttribute('aria-hidden', 'true')
    })
  })

  test('generates unique keys for breadcrumb items', () => {
    const itemsWithSamePath = [
      { title: 'First', path: '/same-path' },
      { title: 'Second', path: '/same-path' },
    ]

    renderBreadCrumbs(itemsWithSamePath)

    // Should render without React key warnings
    expect(screen.getByText('First')).toBeInTheDocument()
    expect(screen.getByText('Second')).toBeInTheDocument()
  })
})
