import { render, screen } from '@testing-library/react'
import { usePathname } from 'next/navigation'
import BreadCrumbsWrapper from 'components/BreadCrumbsWrapper'
import '@testing-library/jest-dom'

jest.mock('next/navigation', () => ({
  usePathname: jest.fn(),
}))

describe('BreadCrumbsWrapper', () => {
  afterEach(() => {
    jest.clearAllMocks()
  })

  describe('Route Detection - Should Hide', () => {
    test('returns null on home page', () => {
      ;(usePathname as jest.Mock).mockReturnValue('/')

      const { container } = render(<BreadCrumbsWrapper />)
      expect(container.firstChild).toBeNull()
    })

    test('returns null for project detail pages', () => {
      ;(usePathname as jest.Mock).mockReturnValue('/projects/zap')

      const { container } = render(<BreadCrumbsWrapper />)
      expect(container.firstChild).toBeNull()
    })

    test('returns null for member detail pages', () => {
      ;(usePathname as jest.Mock).mockReturnValue('/members/bjornkimminich')

      const { container } = render(<BreadCrumbsWrapper />)
      expect(container.firstChild).toBeNull()
    })

    test('returns null for chapter detail pages', () => {
      ;(usePathname as jest.Mock).mockReturnValue('/chapters/bangalore')

      const { container } = render(<BreadCrumbsWrapper />)
      expect(container.firstChild).toBeNull()
    })

    test('returns null for committee detail pages', () => {
      ;(usePathname as jest.Mock).mockReturnValue('/committees/outreach')

      const { container } = render(<BreadCrumbsWrapper />)
      expect(container.firstChild).toBeNull()
    })

    test('returns null for organization detail pages', () => {
      ;(usePathname as jest.Mock).mockReturnValue('/organizations/cyclonedx')

      const { container } = render(<BreadCrumbsWrapper />)
      expect(container.firstChild).toBeNull()
    })

    test('returns null for nested repository pages', () => {
      ;(usePathname as jest.Mock).mockReturnValue(
        '/organizations/cyclonedx/repositories/cyclonedx-python'
      )

      const { container } = render(<BreadCrumbsWrapper />)
      expect(container.firstChild).toBeNull()
    })
  })

  describe('Route Detection - Should Render', () => {
    test('renders for projects list page', () => {
      ;(usePathname as jest.Mock).mockReturnValue('/projects')

      render(<BreadCrumbsWrapper />)
      expect(screen.getByText('Home')).toBeInTheDocument()
      expect(screen.getByText('Projects')).toBeInTheDocument()
    })

    test('renders for members list page', () => {
      ;(usePathname as jest.Mock).mockReturnValue('/members')

      render(<BreadCrumbsWrapper />)
      expect(screen.getByText('Home')).toBeInTheDocument()
      expect(screen.getByText('Members')).toBeInTheDocument()
    })

    test('renders for chapters list page', () => {
      ;(usePathname as jest.Mock).mockReturnValue('/chapters')

      render(<BreadCrumbsWrapper />)
      expect(screen.getByText('Home')).toBeInTheDocument()
      expect(screen.getByText('Chapters')).toBeInTheDocument()
    })
  })

  describe('Auto-Generation Logic', () => {
    test('capitalizes single-word segments', () => {
      ;(usePathname as jest.Mock).mockReturnValue('/about')

      render(<BreadCrumbsWrapper />)
      expect(screen.getByText('About')).toBeInTheDocument()
    })

    test('replaces dashes with spaces and capitalizes', () => {
      ;(usePathname as jest.Mock).mockReturnValue('/some-page')

      render(<BreadCrumbsWrapper />)
      expect(screen.getByText('Some page')).toBeInTheDocument()
    })

    test('handles multi-segment paths correctly', () => {
      ;(usePathname as jest.Mock).mockReturnValue('/community/events')

      render(<BreadCrumbsWrapper />)
      expect(screen.getByText('Home')).toBeInTheDocument()
      expect(screen.getByText('Community')).toBeInTheDocument()
      expect(screen.getByText('Events')).toBeInTheDocument()
    })

    test('builds progressive paths for links', () => {
      ;(usePathname as jest.Mock).mockReturnValue('/community/events/conferences')

      render(<BreadCrumbsWrapper />)

      const homeLink = screen.getByText('Home').closest('a')
      const communityLink = screen.getByText('Community').closest('a')
      const eventsLink = screen.getByText('Events').closest('a')

      expect(homeLink).toHaveAttribute('href', '/')
      expect(communityLink).toHaveAttribute('href', '/community')
      expect(eventsLink).toHaveAttribute('href', '/community/events')
    })
  })

  describe('Edge Cases', () => {
    test('handles trailing slashes', () => {
      ;(usePathname as jest.Mock).mockReturnValue('/projects/')

      render(<BreadCrumbsWrapper />)
      expect(screen.getByText('Projects')).toBeInTheDocument()
    })

    test('handles paths with special characters in segment names', () => {
      ;(usePathname as jest.Mock).mockReturnValue('/test-page-name')

      render(<BreadCrumbsWrapper />)
      expect(screen.getByText('Test page name')).toBeInTheDocument()
    })
  })
})
