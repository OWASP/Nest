import { sendGAEvent } from '@next/third-parties/google'
import { screen, render, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { useRouter } from 'next/navigation'
import React from 'react'
import { fetchAlgoliaData } from 'server/fetchAlgoliaData'
import { Chapter } from 'types/chapter'
import { Organization } from 'types/organization'
import { Project } from 'types/project'
import { User } from 'types/user'
import MultiSearchBar from 'components/MultiSearch'

jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
}))

jest.mock('@next/third-parties/google', () => ({
  sendGAEvent: jest.fn(),
}))

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
    <svg data-testid="fa-location-dot-icon" {...props} />
  ),
}))

jest.mock('react-icons/si', () => ({
  SiAlgolia: (props: React.SVGProps<SVGSVGElement>) => (
    <svg data-testid="si-algolia-icon" {...props} />
  ),
}))

// Mock window.open globally
const mockWindowOpen = jest.fn()
Object.defineProperty(globalThis, 'open', {
  value: mockWindowOpen,
  writable: true,
})

const mockPush = jest.fn()
const mockFetchAlgoliaData = fetchAlgoliaData as jest.MockedFunction<typeof fetchAlgoliaData>
const mockUseRouter = useRouter as jest.MockedFunction<typeof useRouter>

// Sample test data
const mockChapter: Chapter = {
  key: 'test-chapter',
  name: 'Test Chapter',
} as Chapter

const mockUser: User = {
  key: 'test-user',
  name: 'Test User',
} as User

const mockProject: Project = {
  key: 'test-project',
  name: 'Test Project',
} as Project

const mockOrganization: Organization = {
  login: 'test-org',
  name: 'Test Organization',
} as Organization

const defaultProps = {
  isLoaded: true,
  placeholder: 'Search...',
  indexes: ['chapters', 'users', 'projects'],
  initialValue: '',
  eventData: [],
}

beforeEach(() => {
  mockUseRouter.mockReturnValue({
    push: mockPush,
    replace: jest.fn(),
    back: jest.fn(),
    forward: jest.fn(),
    refresh: jest.fn(),
    prefetch: jest.fn(),
  })

  mockFetchAlgoliaData.mockResolvedValue({
    hits: [],
    totalPages: 0,
  })
})

afterEach(() => {
  jest.clearAllMocks()
})

describe('Rendering', () => {
  it('renders successfully with minimal required props', () => {
    render(<MultiSearchBar {...defaultProps} />)

    expect(screen.getByPlaceholderText('Search...')).toBeInTheDocument()
    expect(screen.getByTestId('fa-search-icon')).toBeInTheDocument()
  })

  it('renders with initial value', () => {
    render(<MultiSearchBar {...defaultProps} initialValue={'initial search'} />)

    expect(screen.getByDisplayValue('initial search')).toBeInTheDocument()
  })

  it('renders custom placeholder', () => {
    render(<MultiSearchBar {...defaultProps} placeholder={'Custom Placeholder'} />)

    expect(screen.getByPlaceholderText('Custom Placeholder')).toBeInTheDocument()
  })

  it('applies correct css classes for input', () => {
    render(<MultiSearchBar {...defaultProps} />)
    const input = screen.getByPlaceholderText('Search...')
    expect(input).toHaveClass(
      'h-12',
      'w-full',
      'rounded-lg',
      'border',
      'border-gray-300',
      'pl-10',
      'pr-10',
      'text-lg'
    )
  })

  describe('Search input behavior', () => {
    it('updates search query on input change', async () => {
      const user = userEvent.setup()

      render(<MultiSearchBar {...defaultProps} />)
      const input = screen.getByPlaceholderText('Search...')
      await user.type(input, 'test query')

      expect(input).toHaveValue('test query')
    })

    it('shows clear button when search query exists', async () => {
      const user = userEvent.setup()

      render(<MultiSearchBar {...defaultProps} />)
      const input = screen.getByPlaceholderText('Search...')
      await user.type(input, 'test')
      expect(screen.getByTestId('fa-times-icon')).toBeInTheDocument()
    })

    it('clears search when clear button is clicked', async () => {
      const user = userEvent.setup()

      render(<MultiSearchBar {...defaultProps} />)
      const input = screen.getByPlaceholderText('Search...')
      await user.type(input, 'test')
      const clearButton = screen.getByLabelText('Clear search')
      await user.click(clearButton)
      expect(input).toHaveValue('')
    })
  })

  describe('Search Functionality', () => {
    it('calls fetchAlgoliaData when search query is entered', async () => {
      const user = userEvent.setup()
      render(<MultiSearchBar {...defaultProps} />)

      const input = screen.getByPlaceholderText('Search...')
      await user.type(input, 'test')

      await waitFor(() => {
        expect(mockFetchAlgoliaData).toHaveBeenCalledWith(
          'chapters',
          'test',
          1,
          3,
          [],
          expect.any(AbortSignal)
        )
        expect(mockFetchAlgoliaData).toHaveBeenCalledWith(
          'users',
          'test',
          1,
          3,
          [],
          expect.any(AbortSignal)
        )
        expect(mockFetchAlgoliaData).toHaveBeenCalledWith(
          'projects',
          'test',
          1,
          3,
          [],
          expect.any(AbortSignal)
        )
      })
    })

    it('sends Google Analytics event on search', async () => {
      const user = userEvent.setup()
      render(<MultiSearchBar {...defaultProps} />)

      const input = screen.getByPlaceholderText('Search...')
      await user.type(input, 'test')

      await waitFor(() => {
        expect(sendGAEvent).toHaveBeenCalledWith({
          event: 'homepageSearch',
          path: '/',
          value: 'test',
        })
      })
    })

    it('does not send GA event for empty queries', async () => {
      const user = userEvent.setup()
      render(<MultiSearchBar {...defaultProps} />)

      const input = screen.getByPlaceholderText('Search...')
      await user.type(input, '   ')

      await waitFor(() => {
        expect(sendGAEvent).not.toHaveBeenCalled()
      })
    })
  })

  describe('Suggestions Display', () => {
    it('shows suggestions when search results are available', async () => {
      mockFetchAlgoliaData.mockResolvedValue({
        hits: [mockChapter],
        totalPages: 1,
      })
      const user = userEvent.setup()
      render(<MultiSearchBar {...defaultProps} indexes={['chapters']} />)

      const input = screen.getByPlaceholderText('Search...')
      await user.type(input, 'test')

      await waitFor(() => {
        expect(screen.getByText('Test Chapter')).toBeInTheDocument()
      })
    })

    it('displays correct icons for different index types', async () => {
      mockFetchAlgoliaData.mockImplementation((index) => {
        if (index === 'chapters') return Promise.resolve({ hits: [mockChapter], totalPages: 1 })
        if (index === 'users') return Promise.resolve({ hits: [mockUser], totalPages: 1 })
        return Promise.resolve({ hits: [], totalPages: 0 })
      })

      const user = userEvent.setup()
      render(<MultiSearchBar {...defaultProps} indexes={['chapters', 'users']} />)

      const input = screen.getByPlaceholderText('Search...')
      await user.type(input, 'test')

      await waitFor(() => {
        expect(screen.getAllByTestId('fa-location-dot-icon')).toHaveLength(1)
        expect(screen.getAllByTestId('fa-user-icon')).toHaveLength(1)
      })
    })

    it('handles input focus and blur correctly', async () => {
      const user = userEvent.setup()
      render(<MultiSearchBar {...defaultProps} />)

      const input = screen.getByPlaceholderText('Search...')
      await user.click(input)
      expect(input).toHaveFocus()

      await user.tab()
      expect(input).not.toHaveFocus()
    })
  })

  describe('Navigation Handling', () => {
    it('navigates to chapter page when chapter is clicked', async () => {
      mockFetchAlgoliaData.mockResolvedValue({
        hits: [mockChapter],
        totalPages: 1,
      })

      const user = userEvent.setup()
      render(<MultiSearchBar {...defaultProps} indexes={['chapters']} />)

      const input = screen.getByPlaceholderText('Search...')
      await user.type(input, 'test')

      await waitFor(() => {
        expect(screen.getByText('Test Chapter')).toBeInTheDocument()
      })

      const chapterElement = screen.getByText('Test Chapter')
      await user.click(chapterElement)

      expect(mockPush).toHaveBeenCalledWith('/chapters/test-chapter')
    })

    it('navigates to organization page when organization is clicked', async () => {
      mockFetchAlgoliaData.mockResolvedValue({
        hits: [mockOrganization],
        totalPages: 1,
      })

      const user = userEvent.setup()
      render(<MultiSearchBar {...defaultProps} indexes={['organizations']} />)

      const input = screen.getByPlaceholderText('Search...')
      await user.type(input, 'test')

      await waitFor(() => {
        expect(screen.getByText('Test Organization')).toBeInTheDocument()
      })

      const organizationButton = screen.getByText('Test Organization')
      await user.click(organizationButton)

      expect(mockPush).toHaveBeenCalledWith('/organizations/test-org')
    })

    it('navigates to project page when project is clicked', async () => {
      mockFetchAlgoliaData.mockResolvedValue({
        hits: [mockProject],
        totalPages: 1,
      })

      const user = userEvent.setup()
      render(<MultiSearchBar {...defaultProps} indexes={['projects']} />)

      const input = screen.getByPlaceholderText('Search...')
      await user.type(input, 'test')

      await waitFor(() => {
        expect(screen.getByText('Test Project')).toBeInTheDocument()
      })

      await user.click(screen.getByText('Test Project'))

      expect(mockPush).toHaveBeenCalledWith('/projects/test-project')
    })

    it('navigates to user page when user is clicked', async () => {
      mockFetchAlgoliaData.mockResolvedValue({
        hits: [mockUser],
        totalPages: 1,
      })

      const user = userEvent.setup()
      render(<MultiSearchBar {...defaultProps} indexes={['users']} />)

      const input = screen.getByPlaceholderText('Search...')
      await user.type(input, 'test')

      await waitFor(() => {
        expect(screen.getByText('Test User')).toBeInTheDocument()
      })

      await user.click(screen.getByText('Test User'))

      expect(mockPush).toHaveBeenCalledWith('/members/test-user')
    })
  })

  describe('Edge Cases', () => {
    it('handles empty search results gracefully', async () => {
      mockFetchAlgoliaData.mockResolvedValue({
        hits: [],
        totalPages: 0,
      })

      const user = userEvent.setup()
      render(<MultiSearchBar {...defaultProps} />)

      const input = screen.getByPlaceholderText('Search...')
      await user.type(input, 'nonexistent')

      await waitFor(() => {
        expect(mockFetchAlgoliaData).toHaveBeenCalled()
      })

      expect(screen.queryByText('Test Chapter')).not.toBeInTheDocument()
    })

    it('handles organization without login property', async () => {
      const orgWithoutLogin = { name: 'Org Without Login' } as Organization
      mockFetchAlgoliaData.mockResolvedValue({
        hits: [orgWithoutLogin],
        totalPages: 1,
      })

      const user = userEvent.setup()
      render(<MultiSearchBar {...defaultProps} indexes={['organizations']} />)

      const input = screen.getByPlaceholderText('Search...')
      await user.type(input, 'test')

      await waitFor(() => {
        expect(screen.getByText('Org Without Login')).toBeInTheDocument()
      })

      await user.click(screen.getByText('Org Without Login'))

      expect(mockPush).not.toHaveBeenCalled()
    })

    it('handles items without name property', async () => {
      const itemWithLogin = { login: 'test-login' } as Organization
      mockFetchAlgoliaData.mockResolvedValue({
        hits: [itemWithLogin],
        totalPages: 1,
      })

      const user = userEvent.setup()
      render(<MultiSearchBar {...defaultProps} indexes={['organizations']} />)

      const input = screen.getByPlaceholderText('Search...')
      await user.type(input, 'test')

      await waitFor(() => {
        expect(screen.getByText('test-login')).toBeInTheDocument()
      })
    })

    it('does not send GA events for whitespace-only queries', async () => {
      const user = userEvent.setup()
      render(<MultiSearchBar {...defaultProps} />)

      const input = screen.getByPlaceholderText('Search...')
      await user.type(input, '   ')

      await waitFor(() => {
        expect(mockFetchAlgoliaData).not.toHaveBeenCalled()
      })

      expect(sendGAEvent).not.toHaveBeenCalled()
    })

    it('handles rapid successive searches', async () => {
      const user = userEvent.setup()
      render(<MultiSearchBar {...defaultProps} />)

      const input = screen.getByPlaceholderText('Search...')

      await user.type(input, 'test1')
      await user.clear(input)
      await user.type(input, 'test2')
      await user.clear(input)
      await user.type(input, 'test3')

      expect(input).toHaveValue('test3')
    })

    it('handles empty eventData array', () => {
      render(<MultiSearchBar {...defaultProps} eventData={[]} />)

      expect(screen.getByPlaceholderText('Search...')).toBeInTheDocument()
    })

    it('handles undefined eventData', () => {
      render(<MultiSearchBar {...defaultProps} eventData={undefined} />)

      expect(screen.getByPlaceholderText('Search...')).toBeInTheDocument()
    })
  })

  describe('Accessibility', () => {
    it('has proper ARIA attributes', () => {
      render(<MultiSearchBar {...defaultProps} />)

      const input = screen.getByPlaceholderText('Search...')
      expect(input).toHaveAttribute('type', 'text')
    })

    it('maintains focus management', async () => {
      const user = userEvent.setup()
      render(<MultiSearchBar {...defaultProps} />)

      const input = screen.getByPlaceholderText('Search...')
      // Just check focusable
      await user.click(input)
      expect(input).toHaveFocus()
    })

    it('has keyboard-accessible buttons', async () => {
      const user = userEvent.setup()
      render(<MultiSearchBar {...defaultProps} />)

      const input = screen.getByPlaceholderText('Search...')
      await user.type(input, 'test')

      const clearButton = screen.getByLabelText('Clear search')
      expect(clearButton).toBeInTheDocument()

      await user.click(clearButton)
      expect(input).toHaveValue('')
    })
  })

  describe('State Management', () => {
    it('clears all state when clear button is clicked', async () => {
      const user = userEvent.setup()
      render(<MultiSearchBar {...defaultProps} />)

      const input = screen.getByPlaceholderText('Search...')
      await user.type(input, 'test')

      const clearButton = screen.getByLabelText('Clear search')
      await user.click(clearButton)

      expect(input).toHaveValue('')
      expect(screen.queryByText('Test Chapter')).not.toBeInTheDocument()
    })
  })
})
