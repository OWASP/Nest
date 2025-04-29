import { MockedProvider } from '@apollo/client/testing'
import { render, screen } from '@testing-library/react'
import { usePathname, useParams } from 'next/navigation'
import BreadCrumbs from 'components/BreadCrumbs'
import '@testing-library/jest-dom'

jest.mock('next/navigation', () => ({
  usePathname: jest.fn(),
  useParams: jest.fn(),
}))

describe('BreadCrumbs', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    ;(usePathname as jest.Mock).mockReturnValue('/')
    ;(useParams as jest.Mock).mockReturnValue({})
  })

  test('does not render on root path "/"', () => {
    render(
      <MockedProvider>
        <BreadCrumbs />
      </MockedProvider>
    )
    expect(screen.queryByText('Home')).not.toBeInTheDocument()
  })

  test('renders breadcrumb with multiple segments', () => {
    ;(usePathname as jest.Mock).mockReturnValue('/dashboard/users/profile')
    render(
      <MockedProvider>
        <BreadCrumbs />
      </MockedProvider>
    )

    expect(screen.getByText('Home')).toBeInTheDocument()
    expect(screen.getByText('Dashboard')).toBeInTheDocument()
    expect(screen.getByText('Users')).toBeInTheDocument()
    expect(screen.getByText('Profile')).toBeInTheDocument()
  })

  test('disables the last segment (non-clickable)', () => {
    ;(usePathname as jest.Mock).mockReturnValue('/settings/account')
    render(
      <MockedProvider>
        <BreadCrumbs />
      </MockedProvider>
    )

    const lastSegment = screen.getByText('Account')
    expect(lastSegment).toBeInTheDocument()
    expect(lastSegment).not.toHaveAttribute('href')
  })

  test('links have correct href attributes', () => {
    ;(usePathname as jest.Mock).mockReturnValue('/dashboard/users/profile')

    render(
      <MockedProvider>
        <BreadCrumbs />
      </MockedProvider>
    )

    const homeLink = screen.getByText('Home').closest('a')
    const dashboardLink = screen.getByText('Dashboard').closest('a')
    const usersLink = screen.getByText('Users').closest('a')

    expect(homeLink).toHaveAttribute('href', '/')
    expect(dashboardLink).toHaveAttribute('href', '/dashboard')
    expect(usersLink).toHaveAttribute('href', '/dashboard/users')
  })

  test('links have hover styles', () => {
    ;(usePathname as jest.Mock).mockReturnValue('/dashboard/users')

    render(
      <MockedProvider>
        <BreadCrumbs />
      </MockedProvider>
    )

    const homeLink = screen.getByText('Home').closest('a')
    const dashboardLink = screen.getByText('Dashboard').closest('a')

    expect(homeLink).toHaveClass('hover:text-blue-700', 'hover:underline')
    expect(dashboardLink).toHaveClass('hover:text-blue-700', 'hover:underline')
  })
})
