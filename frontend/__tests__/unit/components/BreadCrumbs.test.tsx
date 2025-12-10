import { render, screen } from '@testing-library/react'
import BreadCrumbRenderer from 'components/BreadCrumbs'
import '@testing-library/jest-dom'

describe('BreadCrumbRenderer', () => {
  const mockItems = [
    { title: 'Home', path: '/' },
    { title: 'Projects', path: '/projects' },
    { title: 'OWASP ZAP', path: '/projects/zap' },
  ]

  test('renders all breadcrumb items', () => {
    render(<BreadCrumbRenderer items={mockItems} />)

    expect(screen.getByText('Home')).toBeInTheDocument()
    expect(screen.getByText('Projects')).toBeInTheDocument()
    expect(screen.getByText('OWASP ZAP')).toBeInTheDocument()
  })

  test('renders navigation element with correct aria-label', () => {
    render(<BreadCrumbRenderer items={mockItems} />)

    const nav = screen.getByRole('navigation')
    expect(nav).toHaveAttribute('aria-label', 'breadcrumb')
  })

  test('renders clickable links for non-last items', () => {
    render(<BreadCrumbRenderer items={mockItems} />)

    const homeLink = screen.getByText('Home').closest('a')
    const projectsLink = screen.getByText('Projects').closest('a')

    expect(homeLink).toHaveAttribute('href', '/')
    expect(projectsLink).toHaveAttribute('href', '/projects')
  })

  test('disables the last item (non-clickable)', () => {
    render(<BreadCrumbRenderer items={mockItems} />)

    const lastItem = screen.getByText('OWASP ZAP')
    expect(lastItem).not.toHaveAttribute('href')
    expect(lastItem.tagName).toBe('SPAN')
  })

  test('applies hover styles to clickable links', () => {
    render(<BreadCrumbRenderer items={mockItems} />)

    const homeLink = screen.getByText('Home').closest('a')
    expect(homeLink).toHaveClass('hover:text-blue-700', 'hover:underline')
  })

  test('applies disabled styling to last breadcrumb', () => {
    render(<BreadCrumbRenderer items={mockItems} />)

    const lastItem = screen.getByText('OWASP ZAP')
    expect(lastItem).toHaveClass('cursor-default', 'font-semibold')
  })

  test('renders chevron separators between items', () => {
    const { container } = render(<BreadCrumbRenderer items={mockItems} />)

    const separators = container.querySelectorAll('[data-slot="separator"]')
    expect(separators).toHaveLength(2)
  })

  test('handles single item (home only)', () => {
    const singleItem = [{ title: 'Home', path: '/' }]
    render(<BreadCrumbRenderer items={singleItem} />)

    expect(screen.getByText('Home')).toBeInTheDocument()
    const separators = screen.queryByRole('separator')
    expect(separators).not.toBeInTheDocument()
  })

  test('handles empty items array', () => {
    const { container } = render(<BreadCrumbRenderer items={[]} />)

    const breadcrumbList = container.querySelector('[data-slot="list"]')
    expect(breadcrumbList?.children).toHaveLength(0)
  })

  test('applies correct wrapper styling', () => {
    const { container } = render(<BreadCrumbRenderer items={mockItems} />)

    const wrapper = container.querySelector('.mt-16')
    expect(wrapper).toHaveClass('w-full', 'pt-4')
  })

  test('links have correct href attributes', () => {
    render(<BreadCrumbRenderer items={mockItems} />)

    const homeLink = screen.getByText('Home').closest('a')
    const projectsLink = screen.getByText('Projects').closest('a')

    expect(homeLink).toHaveAttribute('href', '/')
    expect(projectsLink).toHaveAttribute('href', '/projects')
  })
})
