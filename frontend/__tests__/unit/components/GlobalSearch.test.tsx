import { screen, render, waitFor, fireEvent } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { useRouter } from 'next/navigation'
import React from 'react'
import { fetchAlgoliaData } from 'server/fetchAlgoliaData'
import GlobalSearch from 'components/GlobalSearch'

jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
}))

jest.mock('@next/third-parties/google', () => ({
  sendGAEvent: jest.fn(),
}))

jest.mock('next/link', () => {
  return ({ href, children, ...props }: { href: string; children: React.ReactNode }) => (
    <a href={href} {...props}>{children}</a>
  )
})

jest.mock('server/fetchAlgoliaData', () => ({
  fetchAlgoliaData: jest.fn(),
}))

jest.mock('lodash', () => ({
  debounce: jest.fn((fn: (...args: unknown[]) => unknown) => {
    const debouncedFn = (...args: unknown[]) => fn(...args)
    debouncedFn.cancel = jest.fn()
    return debouncedFn
  }),
}))

jest.mock('react-icons/fa', () => ({
  FaSearch: (props: React.SVGProps<SVGSVGElement>) => (
    <svg data-testid="fa-search-icon" {...props} />
  ),
  FaTimes: (props: React.SVGProps<SVGSVGElement>) => <svg data-testid="fa-times-icon" {...props} />,
  FaArrowRight: (props: React.SVGProps<SVGSVGElement>) => <svg data-testid="fa-arrow-right-icon" {...props} />,
}))

jest.mock('react-icons/fa6', () => ({
  FaUser: (props: React.SVGProps<SVGSVGElement>) => <svg data-testid="fa-user-icon" {...props} />,
  FaCalendar: (props: React.SVGProps<SVGSVGElement>) => (
    <svg data-testid="fa-calendar-icon" {...props} />
  ),
  FaFolder: (props: React.SVGProps<SVGSVGElement>) => (
    <svg data-testid="fa-folder-icon" {...props} />
  ),
  FaBuilding: (props: React.SVGProps<SVGSVGElement>) => (
    <svg data-testid="fa-building-icon" {...props} />
  ),
  FaLocationDot: (props: React.SVGProps<SVGSVGElement>) => (
    <svg data-testid="fa-location-icon" {...props} />
  ),
}))


jest.mock('react-icons/si', () => ({
  SiAlgolia: (props: React.SVGProps<SVGSVGElement>) => (
    <svg data-testid="si-algolia-icon" {...props} />
  ),
}))

const mockRouter = { push: jest.fn() }
const mockWindowOpen = jest.fn()

describe('GlobalSearch', () => {
  beforeEach(() => {
    ; (useRouter as jest.Mock).mockReturnValue(mockRouter)
      ; (fetchAlgoliaData as jest.Mock).mockResolvedValue({ hits: [], totalPages: 0 })
    jest.clearAllMocks()
    Object.defineProperty(globalThis, 'open', { value: mockWindowOpen, writable: true })
  })

  test('renders search trigger button', () => {
    render(<GlobalSearch />)
    expect(screen.getByLabelText('Open search')).toBeInTheDocument()
  })

  test('opens search overlay when trigger button is clicked', async () => {
    render(<GlobalSearch />)
    fireEvent.click(screen.getByLabelText('Open search'))

    await waitFor(() => {
      expect(screen.getByRole('dialog')).toBeInTheDocument()
      expect(screen.getByPlaceholderText('Search the OWASP community...')).toBeInTheDocument()
    })
  })

  test('opens search overlay with / keyboard shortcut', async () => {
    render(<GlobalSearch />)
    fireEvent.keyDown(document.body, { key: '/' })

    await waitFor(() => {
      expect(screen.getByRole('dialog')).toBeInTheDocument()
    })
  })

  test('closes search overlay with Escape key', async () => {
    render(<GlobalSearch />)
    fireEvent.click(screen.getByLabelText('Open search'))

    await waitFor(() => {
      expect(screen.getByRole('dialog')).toBeInTheDocument()
    })

    fireEvent.keyDown(document, { key: 'Escape' })

    await waitFor(() => {
      expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
    })
  })

  test('closes search overlay when clicking on backdrop', async () => {
    render(<GlobalSearch />)
    fireEvent.click(screen.getByLabelText('Open search'))

    await waitFor(() => {
      expect(screen.getByRole('dialog')).toBeInTheDocument()
    })

    fireEvent.click(screen.getByLabelText('Close search'))

    await waitFor(() => {
      expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
    })
  })

  test('shows placeholder text when no search query', async () => {
    render(<GlobalSearch />)
    fireEvent.click(screen.getByLabelText('Open search'))

    await waitFor(() => {
      expect(
        screen.getByText(/Start typing to search across projects, chapters, events, organizations, and members./)
      ).toBeInTheDocument()
    })
  })

  test('shows starter query buttons in empty state', async () => {
    render(<GlobalSearch />)
    fireEvent.click(screen.getByLabelText('Open search'))

    await waitFor(() => {
      expect(screen.getByText('Cheat Sheet Series')).toBeInTheDocument()
      expect(screen.getByText('London')).toBeInTheDocument()
      expect(screen.getByText('OWASP')).toBeInTheDocument()
    })
  })

  test('shows explore community link in empty state', async () => {
    render(<GlobalSearch />)
    fireEvent.click(screen.getByLabelText('Open search'))

    await waitFor(() => {
      const link = screen.getByRole('link', { name: 'Explore the community for more info' })
      expect(link).toBeInTheDocument()
      expect(link).toHaveAttribute('href', '/community')
    })

    fireEvent.click(screen.getByRole('link', { name: 'Explore the community for more info' }))

    await waitFor(() => {
      expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
    })
  })

  test('clicking a starter query button populates the search input', async () => {
    ; (fetchAlgoliaData as jest.Mock).mockResolvedValue({
      hits: [{ key: 'nest', name: 'Nest' }],
      totalPages: 1,
    })

    render(<GlobalSearch />)
    fireEvent.click(screen.getByLabelText('Open search'))

    await waitFor(() => {
      expect(screen.getByText('Nest')).toBeInTheDocument() // starter button
    })

    fireEvent.click(screen.getByText('Nest'))

    const input = screen.getByPlaceholderText('Search the OWASP community...')
    expect(input).toHaveValue('nest')
  })

  test('navigates to organization page when clicking an organization suggestion', async () => {
    ; (fetchAlgoliaData as jest.Mock).mockImplementation((index: string) => {
      if (index === 'organizations') {
        return Promise.resolve({
          hits: [{ login: 'owasp', name: 'OWASP' }],
          totalPages: 1,
        })
      }
      return Promise.resolve({ hits: [], totalPages: 0 })
    })

    render(<GlobalSearch />)
    fireEvent.click(screen.getByLabelText('Open search'))

    const input = screen.getByPlaceholderText('Search the OWASP community...')
    await userEvent.type(input, 'owasp')

    await waitFor(() => {
      expect(screen.getByText('Search by Algolia')).toBeInTheDocument()
    })

    fireEvent.click(screen.getByRole('button', { name: 'OWASP' }))

    expect(mockRouter.push).toHaveBeenCalledWith('/organizations/owasp')
  })


  test('shows search results when typing', async () => {
    ; (fetchAlgoliaData as jest.Mock).mockImplementation((index: string) => {
      if (index === 'projects') {
        return Promise.resolve({
          hits: [{ key: 'test-project', name: 'Test Project' }],
          totalPages: 1,
        })
      }
      return Promise.resolve({ hits: [], totalPages: 0 })
    })

    render(<GlobalSearch />)
    fireEvent.click(screen.getByLabelText('Open search'))

    const input = screen.getByPlaceholderText('Search the OWASP community...')
    await userEvent.type(input, 'test')

    await waitFor(() => {
      expect(screen.getByText('Test Project')).toBeInTheDocument()
    })
  })

  test('shows no results message for empty search results', async () => {
    ; (fetchAlgoliaData as jest.Mock).mockResolvedValue({
      hits: [],
      totalPages: 0,
    })

    render(<GlobalSearch />)
    fireEvent.click(screen.getByLabelText('Open search'))

    const input = screen.getByPlaceholderText('Search the OWASP community...')
    await userEvent.type(input, 'nonexistent')

    await waitFor(() => {
      expect(screen.getByText(/No results found/)).toBeInTheDocument()
    })
  })

  test('clears search when clear button is clicked', async () => {
    ; (fetchAlgoliaData as jest.Mock).mockImplementation((index: string) => {
      if (index === 'projects') {
        return Promise.resolve({
          hits: [{ key: 'test-project', name: 'Test Project' }],
          totalPages: 1,
        })
      }
      return Promise.resolve({ hits: [], totalPages: 0 })
    })

    render(<GlobalSearch />)
    fireEvent.click(screen.getByLabelText('Open search'))

    const input = screen.getByPlaceholderText('Search the OWASP community...')
    await userEvent.type(input, 'test')

    await waitFor(() => {
      expect(screen.getByText('Test Project')).toBeInTheDocument()
    })

    fireEvent.click(screen.getByLabelText('Clear search'))

    await waitFor(() => {
      expect(input).toHaveValue('')
    })
  })

  test('navigates to project page when clicking a project suggestion', async () => {
    ; (fetchAlgoliaData as jest.Mock).mockImplementation((index: string) => {
      if (index === 'projects') {
        return Promise.resolve({
          hits: [{ key: 'test-project', name: 'Test Project' }],
          totalPages: 1,
        })
      }
      return Promise.resolve({ hits: [], totalPages: 0 })
    })

    render(<GlobalSearch />)
    fireEvent.click(screen.getByLabelText('Open search'))

    const input = screen.getByPlaceholderText('Search the OWASP community...')
    await userEvent.type(input, 'test')

    await waitFor(() => {
      expect(screen.getByText('Test Project')).toBeInTheDocument()
    })

    fireEvent.click(screen.getByText('Test Project'))

    expect(mockRouter.push).toHaveBeenCalledWith('/projects/test-project')
  })

  test('navigates to chapter page when clicking a chapter suggestion', async () => {
    ; (fetchAlgoliaData as jest.Mock).mockImplementation((index: string) => {
      if (index === 'chapters') {
        return Promise.resolve({
          hits: [{ key: 'test-chapter', name: 'Test Chapter' }],
          totalPages: 1,
        })
      }
      return Promise.resolve({ hits: [], totalPages: 0 })
    })

    render(<GlobalSearch />)
    fireEvent.click(screen.getByLabelText('Open search'))

    const input = screen.getByPlaceholderText('Search the OWASP community...')
    await userEvent.type(input, 'test')

    await waitFor(() => {
      expect(screen.getByText('Test Chapter')).toBeInTheDocument()
    })

    fireEvent.click(screen.getByText('Test Chapter'))

    expect(mockRouter.push).toHaveBeenCalledWith('/chapters/test-chapter')
  })

  test('navigates to member page when clicking a user suggestion', async () => {
    ; (fetchAlgoliaData as jest.Mock).mockImplementation((index: string) => {
      if (index === 'users') {
        return Promise.resolve({
          hits: [{ key: 'test-user', name: 'Test User' }],
          totalPages: 1,
        })
      }
      return Promise.resolve({ hits: [], totalPages: 0 })
    })

    render(<GlobalSearch />)
    fireEvent.click(screen.getByLabelText('Open search'))

    const input = screen.getByPlaceholderText('Search the OWASP community...')
    await userEvent.type(input, 'test')

    await waitFor(() => {
      expect(screen.getByText('Test User')).toBeInTheDocument()
    })

    fireEvent.click(screen.getByText('Test User'))

    expect(mockRouter.push).toHaveBeenCalledWith('/members/test-user')
  })

  test('resets state when overlay is closed', async () => {
    ; (fetchAlgoliaData as jest.Mock).mockImplementation((index: string) => {
      if (index === 'projects') {
        return Promise.resolve({
          hits: [{ key: 'test-project', name: 'Test Project' }],
          totalPages: 1,
        })
      }
      return Promise.resolve({ hits: [], totalPages: 0 })
    })

    render(<GlobalSearch />)
    fireEvent.click(screen.getByLabelText('Open search'))

    const input = screen.getByPlaceholderText('Search the OWASP community...')
    await userEvent.type(input, 'test')

    await waitFor(() => {
      expect(screen.getByText('Test Project')).toBeInTheDocument()
    })

    fireEvent.keyDown(document, { key: 'Escape' })

    await waitFor(() => {
      expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
    })

    // Reopen - should be clean
    fireEvent.click(screen.getByLabelText('Open search'))

    await waitFor(() => {
      const newInput = screen.getByPlaceholderText('Search the OWASP community...')
      expect(newInput).toHaveValue('')
      expect(
        screen.getByText(/Start typing to search across projects, chapters, events, organizations, and members./)
      ).toBeInTheDocument()
    })
  })

  test('shows Algolia attribution link in results', async () => {
    ; (fetchAlgoliaData as jest.Mock).mockImplementation((index: string) => {
      if (index === 'projects') {
        return Promise.resolve({
          hits: [{ key: 'test-project', name: 'Test Project' }],
          totalPages: 1,
        })
      }
      return Promise.resolve({ hits: [], totalPages: 0 })
    })

    render(<GlobalSearch />)
    fireEvent.click(screen.getByLabelText('Open search'))

    const input = screen.getByPlaceholderText('Search the OWASP community...')
    await userEvent.type(input, 'test')

    await waitFor(() => {
      expect(screen.getByText('Search by Algolia')).toBeInTheDocument()
    })
  })

  test('shows error message when search fails', async () => {
    ; (fetchAlgoliaData as jest.Mock).mockRejectedValue(new Error('Search service error'))

    render(<GlobalSearch />)
    fireEvent.click(screen.getByLabelText('Open search'))

    const input = screen.getByPlaceholderText('Search the OWASP community...')
    await userEvent.type(input, 'test')

    await waitFor(() => {
      expect(
        screen.getByText('Search service is temporarily unavailable. Please try again later.')
      ).toBeInTheDocument()
    })
  })

  test('opens event URL when clicking an event suggestion', async () => {
    ; (fetchAlgoliaData as jest.Mock).mockImplementation((index: string) => {
      if (index === 'events') {
        return Promise.resolve({
          hits: [{ key: 'test-event', name: 'Test Event', url: 'https://example.com/event' }],
          totalPages: 1,
        })
      }
      return Promise.resolve({ hits: [], totalPages: 0 })
    })

    render(<GlobalSearch />)
    fireEvent.click(screen.getByLabelText('Open search'))

    const input = screen.getByPlaceholderText('Search the OWASP community...')
    await userEvent.type(input, 'test')

    await waitFor(() => {
      expect(screen.getByText('Test Event')).toBeInTheDocument()
    })

    fireEvent.click(screen.getByText('Test Event'))

    expect(mockWindowOpen).toHaveBeenCalledWith(
      'https://example.com/event',
      '_blank',
      'noopener,noreferrer'
    )
  })

  test('ignores stale search responses', async () => {
    let resolveFirst: (value: { hits: { key: string; name: string }[]; totalPages: number }) => void
    const firstPromise = new Promise<{ hits: { key: string; name: string }[]; totalPages: number }>(
      (resolve) => {
        resolveFirst = resolve
      }
    )

    let callCount = 0
      ; (fetchAlgoliaData as jest.Mock).mockImplementation((index: string) => {
        callCount++
        // First batch of calls (first keystroke) returns a slow, pending promise
        if (callCount <= 5) {
          return firstPromise
        }
        // Second batch (second keystroke) resolves immediately
        if (index === 'projects') {
          return Promise.resolve({
            hits: [{ key: 'second-result', name: 'Second Result' }],
            totalPages: 1,
          })
        }
        return Promise.resolve({ hits: [], totalPages: 0 })
      })

    render(<GlobalSearch />)
    fireEvent.click(screen.getByLabelText('Open search'))

    const input = screen.getByPlaceholderText('Search the OWASP community...')

    // Type first query (triggers slow request)
    await userEvent.type(input, 'a')

    // Type second query (triggers fast request that resolves first)
    await userEvent.type(input, 'b')

    await waitFor(() => {
      expect(screen.getByText('Second Result')).toBeInTheDocument()
    })

    // Now resolve the stale first request
    resolveFirst!({ hits: [{ key: 'stale-result', name: 'Stale Result' }], totalPages: 1 })

    // Wait a tick and verify stale result did NOT overwrite
    await waitFor(() => {
      expect(screen.getByText('Second Result')).toBeInTheDocument()
      expect(screen.queryByText('Stale Result')).not.toBeInTheDocument()
    })
  })
})
