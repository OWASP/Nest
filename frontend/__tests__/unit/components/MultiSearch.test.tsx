import { sendGAEvent } from '@next/third-parties/google'
import { screen, render, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { useRouter } from 'next/navigation'
import React from 'react'
import { fetchAlgoliaData } from 'server/fetchAlgoliaData'
import { Chapter } from 'types/chapter'
import { Event } from 'types/event'
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
const mockSendGAEvent = sendGAEvent as jest.MockedFunction<typeof sendGAEvent>
const mockUseRouter = useRouter as jest.MockedFunction<typeof useRouter>

// Sample test data
const mockChapter: Chapter = {
  key: 'test-chapter',
  name: 'Test Chapter',
} as Chapter

const mockEvent: Event = {
  name: 'Test Event',
  url: 'https://example.com/event',
} as Event

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

const expectSuggestionsToExist = () => {
  const suggestionButtons = screen.getAllByRole('button')
  expect(suggestionButtons.length).toBeGreaterThan(0)
}

const expectFirstListItemHighlighted = () => {
  const listItems = screen.getAllByRole('listitem')
  expect(listItems[0]).toHaveClass('bg-gray-100')
}

const expectSecondListItemHighlighted = () => {
  const listItems = screen.getAllByRole('listitem')
  expect(listItems[1]).toHaveClass('bg-gray-100')
}

const expectListItemsNotHighlighted = () => {
  const listItems = screen.getAllByRole('listitem')
  expect(listItems[0]).not.toHaveClass('bg-gray-100')
}

const expectListItemsExist = () => {
  const listItems = screen.getAllByRole('listitem')
  expect(listItems.length).toBeGreaterThan(0)
}

const expectNoListItems = () => {
  const listItems = screen.queryAllByRole('listitem')
  expect(listItems).toHaveLength(0)
}

const expectTestChaptersExist = () => {
  const testChapters = screen.getAllByText('Test Chapter')
  expect(testChapters.length).toBeGreaterThan(0)
}

const expectChaptersCountEquals = (count: number) => {
  expect(screen.getAllByText('Test Chapter')).toHaveLength(count)
}

const expectOrgVisible = () => {
  expect(screen.getByText('Test Organization')).toBeInTheDocument()
}

const expectProjectVisible = () => {
  expect(screen.getByText('Test Project')).toBeInTheDocument()
}

const expectUserVisible = () => {
  expect(screen.getByText('Test User')).toBeInTheDocument()
}

const expectNoListToExist = () => {
  expect(screen.queryByRole('list')).not.toBeInTheDocument()
}

const expectOrgWithoutLoginVisible = () => {
  expect(screen.getByText('Org Without Login')).toBeInTheDocument()
}

const expectTestLoginVisible = () => {
  expect(screen.getByText('test-login')).toBeInTheDocument()
}

const expectChaptersCountEqualsThree = () => {
  expectChaptersCountEquals(3)
}

describe('Rendering', () => {
  it('renders successfully with minimal required props', () => {
    render(<MultiSearchBar {...defaultProps} />)

    expect(screen.getByPlaceholderText('Search...')).toBeInTheDocument()
    expect(screen.getByTestId('fa-search-icon')).toBeInTheDocument()
  })

  it('renders loading state when not loaded', () => {
    render(<MultiSearchBar {...defaultProps} isLoaded={false} />)

    const loadingSkeleton = document.querySelector(
      '.animate-pulse.h-12.w-full.rounded-lg.bg-gray-200'
    )
    expect(loadingSkeleton).toBeInTheDocument()
    expect(loadingSkeleton).toHaveClass(
      'animate-pulse',
      'bg-gray-200',
      'h-12',
      'w-full',
      'rounded-lg'
    )
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
      'border-1',
      'border-gray-300',
      'pl-10',
      'pr-10',
      'text-lg',
      'text-black'
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

    it('focuses input on mount', () => {
      render(<MultiSearchBar {...defaultProps} />)
      const input = screen.getByPlaceholderText('Search...')
      expect(input).toHaveFocus()
    })
  })

  describe('Search Functionality', () => {
    it('calls fetchAlgoliaData when search query is entered', async () => {
      const user = userEvent.setup()
      render(<MultiSearchBar {...defaultProps} />)

      const input = screen.getByPlaceholderText('Search...')
      await user.type(input, 'test')

      await waitFor(() => {
        expect(mockFetchAlgoliaData).toHaveBeenCalledWith('chapters', 'test', 1, 3)
        expect(mockFetchAlgoliaData).toHaveBeenCalledWith('users', 'test', 1, 3)
        expect(mockFetchAlgoliaData).toHaveBeenCalledWith('projects', 'test', 1, 3)
      })
    })

    it('sends Google Analytics event on search', async () => {
      const user = userEvent.setup()
      render(<MultiSearchBar {...defaultProps} />)
      const input = screen.getByPlaceholderText('Search...')
      await user.type(input, 'test query')
      await waitFor(() => {
        expect(mockSendGAEvent).toHaveBeenCalledWith({
          event: 'homepageSearch',
          path: globalThis.location.pathname,
          value: 'test query',
        })
      })
    })

    it('does not send GA event for empty queries', async () => {
      const user = userEvent.setup()
      render(<MultiSearchBar {...defaultProps} />)
      const input = screen.getByPlaceholderText('Search...')
      await user.type(input, ' ')

      await waitFor(() => {
        expect(mockSendGAEvent).not.toHaveBeenCalled()
      })
    })

    it('filters event data based on query', async () => {
      const eventData: Event[] = [
        {
          id: 'event-1',
          name: 'JavaScript Conference',
          url: 'https://example.com/js',
          objectID: 'event-1',
          key: 'js-conf',
          category: 'other',
          startDate: 1704067200, // 2024-01-01
        },
        {
          id: 'event-2',
          name: 'Python Workshop',
          url: 'https://example.com/py',
          objectID: 'event-2',
          key: 'py-workshop',
          category: 'other',
          startDate: 1706745600, // 2024-02-01
        },
        {
          id: 'event-3',
          name: 'React Meetup',
          url: 'https://example.com/react',
          objectID: 'event-3',
          key: 'react-meetup',
          category: 'other',
          startDate: 1709251200, // 2024-03-01
        },
      ]

      const user = userEvent.setup()
      render(<MultiSearchBar {...defaultProps} eventData={eventData} />)

      const input = screen.getByPlaceholderText('Search...')

      await user.type(input, 'JavaScript')

      await waitFor(() => {
        expect(screen.getByText('JavaScript Conference')).toBeInTheDocument()
        expect(screen.queryByText('Python Workshop')).not.toBeInTheDocument()
        expect(screen.queryByText('React Meetup')).not.toBeInTheDocument()
      })

      await user.clear(input)
      await user.type(input, 'Python')

      await waitFor(() => {
        expect(screen.getByText('Python Workshop')).toBeInTheDocument()
        expect(screen.queryByText('JavaScript Conference')).not.toBeInTheDocument()
        expect(screen.queryByText('React Meetup')).not.toBeInTheDocument()
      })
    })
  })

  describe('Suggestions Display', () => {
    beforeEach(() => {
      mockFetchAlgoliaData.mockResolvedValue({
        hits: [mockChapter],
        totalPages: 1,
      })
    })

    it('shows suggestions when search results are available', async () => {
      const user = userEvent.setup()

      render(<MultiSearchBar {...defaultProps} />)

      const input = screen.getByPlaceholderText('Search...')
      await user.type(input, 'test')

      await waitFor(() => {
        const suggestions = screen.getAllByText('Test Chapter')
        expect(suggestions.length).toBeGreaterThan(0)
        expect(suggestions[0]).toBeInTheDocument()
      })
    })

    it('displays correct icons for different index types', async () => {
      mockFetchAlgoliaData
        .mockResolvedValueOnce({ hits: [mockChapter], totalPages: 1 })
        .mockResolvedValueOnce({ hits: [mockUser], totalPages: 1 })
        .mockResolvedValueOnce({ hits: [mockProject], totalPages: 1 })

      const user = userEvent.setup()
      render(<MultiSearchBar {...defaultProps} />)

      const input = screen.getByPlaceholderText('Search...')
      await user.type(input, 'test')

      await waitFor(() => {
        expect(screen.getByTestId('fa-location-dot-icon')).toBeInTheDocument() // chapters
        expect(screen.getByTestId('fa-user-icon')).toBeInTheDocument() // users
        expect(screen.getByTestId('fa-folder-icon')).toBeInTheDocument() // projects
      })
    })

    it('shows Algolia branding icon', async () => {
      const user = userEvent.setup()
      render(<MultiSearchBar {...defaultProps} />)

      const input = screen.getByPlaceholderText('Search...')
      await user.type(input, 'test')

      await waitFor(() => {
        expect(screen.getByTestId('si-algolia-icon')).toBeInTheDocument()
      })
    })

    it('hides suggestions when clicking outside', async () => {
      const user = userEvent.setup()
      render(<MultiSearchBar {...defaultProps} />)

      const input = screen.getByPlaceholderText('Search...')
      await user.type(input, 'test')

      await waitFor(() => {
        const suggestions = screen.getAllByText('Test Chapter')
        expect(suggestions.length).toBeGreaterThan(0)

        for (const suggestion of suggestions) {
          expect(suggestion).toBeInTheDocument()
        }
      })

      await user.click(document.body)

      await waitFor(() => {
        expect(screen.queryAllByText('Test Chapter')).toHaveLength(0)
      })
    })

    it('handles input focus and blur correctly', async () => {
      const user = userEvent.setup()
      render(<MultiSearchBar {...defaultProps} />)

      const input = screen.getByPlaceholderText('Search...')
      await user.click(input)
      expect(input).toHaveFocus()
    })

    describe('Keyboard Navigation', () => {
      beforeEach(() => {
        mockFetchAlgoliaData.mockResolvedValue({
          hits: [mockChapter, mockUser],
          totalPages: 1,
        })
      })

      it('highlights first suggestion on arrow down', async () => {
        const user = userEvent.setup()
        render(<MultiSearchBar {...defaultProps} />)

        const input = screen.getByPlaceholderText('Search...')
        await user.type(input, 'test')
        await waitFor(expectSuggestionsToExist)
        await user.keyboard('{ArrowDown}')
        await waitFor(expectFirstListItemHighlighted)

        expect(true).toBe(true)
      })

      it('moves highlight down on subsequent arrow down presses', async () => {
        const user = userEvent.setup()
        render(<MultiSearchBar {...defaultProps} />)

        const input = screen.getByPlaceholderText('Search...')
        await user.type(input, 'test')
        await waitFor(expectTestChaptersExist)
        await user.keyboard('{ArrowDown}')
        await user.keyboard('{ArrowDown}')
        await waitFor(expectSecondListItemHighlighted)

        expect(true).toBe(true)
      })

      it('moves highlight up on arrow up', async () => {
        const user = userEvent.setup()
        render(<MultiSearchBar {...defaultProps} />)

        const input = screen.getByPlaceholderText('Search...')
        await user.type(input, 'test')
        await waitFor(expectTestChaptersExist)
        await user.keyboard('{ArrowDown}')
        await user.keyboard('{ArrowDown}')
        await waitFor(expectSecondListItemHighlighted)
        await user.keyboard('{ArrowUp}')
        await waitFor(expectFirstListItemHighlighted)

        expect(true).toBe(true)
      })

      it('closes suggestions on Escape key', async () => {
        const user = userEvent.setup()
        render(<MultiSearchBar {...defaultProps} />)

        const input = screen.getByPlaceholderText('Search...')
        await user.type(input, 'test')

        await waitFor(expectListItemsExist)
        await user.keyboard('{Escape}')
        await waitFor(expectNoListItems)

        expect(true).toBe(true)
      })

      it('selects highlighted suggestion on Enter', async () => {
        const user = userEvent.setup()
        render(<MultiSearchBar {...defaultProps} />)

        const input = screen.getByPlaceholderText('Search...')
        await user.type(input, 'test')
        await waitFor(expectListItemsExist)
        await user.keyboard('{ArrowDown}')
        await user.keyboard('{Enter}')

        expect(mockPush).toHaveBeenCalledWith('/chapters/test-chapter')
      })
    })
  })
  describe('Navigation Handling', () => {
    it('navigates to chapter page when chapter is clicked', async () => {
      mockFetchAlgoliaData.mockResolvedValue({
        hits: [mockChapter],
        totalPages: 1,
      })

      const user = userEvent.setup()
      render(<MultiSearchBar {...defaultProps} />)

      const input = screen.getByPlaceholderText('Search...')
      await user.type(input, 'test')
      await waitFor(expectChaptersCountEqualsThree)

      const chapterElements = screen.getAllByText('Test Chapter')
      await user.click(chapterElements[0])

      expect(mockPush).toHaveBeenCalledWith('/chapters/test-chapter')
    })

    it('opens event URL in new tab when event is clicked', async () => {
      const eventData = [mockEvent]
      const user = userEvent.setup()
      render(<MultiSearchBar {...defaultProps} eventData={eventData} />)

      const input = screen.getByPlaceholderText('Search...')
      await user.type(input, 'Test Event')

      await waitFor(() => {
        expect(screen.getByText('Test Event')).toBeInTheDocument()
      })

      await user.click(screen.getByText('Test Event'))

      expect(mockWindowOpen).toHaveBeenCalledWith(
        'https://example.com/event',
        '_blank',
        'noopener,noreferrer'
      )
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
      await waitFor(expectOrgVisible)

      const organizationButton = screen.getByRole('button', { name: /Test Organization/i })
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
      await waitFor(expectProjectVisible)

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
      await waitFor(expectUserVisible)

      await user.click(screen.getByText('Test User'))

      expect(mockPush).toHaveBeenCalledWith('/members/test-user')

      expect(true).toBe(true)
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

      await waitFor(expectNoListToExist)

      expect(true).toBe(true)
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
      await waitFor(expectOrgWithoutLoginVisible)

      await user.click(screen.getByText('Org Without Login'))

      expect(mockPush).not.toHaveBeenCalled()

      expect(true).toBe(true)
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
      await waitFor(expectTestLoginVisible)

      expect(true).toBe(true)
    })

    it('does not send GA events for whitespace-only queries', async () => {
      const user = userEvent.setup()
      render(<MultiSearchBar {...defaultProps} />)

      const input = screen.getByPlaceholderText('Search...')
      await user.type(input, '   ')

      await waitFor(() => {
        expect(mockFetchAlgoliaData).toHaveBeenCalled()
      })

      expect(mockSendGAEvent).not.toHaveBeenCalled()
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
      await user.keyboard('{Escape}')
      expect(input).not.toHaveFocus()
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
    it('resets highlighted index when search query changes', async () => {
      mockFetchAlgoliaData.mockResolvedValue({
        hits: [mockChapter, mockUser],
        totalPages: 1,
      })

      const user = userEvent.setup()
      render(<MultiSearchBar {...defaultProps} />)

      const input = screen.getByPlaceholderText('Search...')
      await user.type(input, 'test')

      await waitFor(expectTestChaptersExist)
      await user.keyboard('{ArrowDown}')
      await waitFor(expectFirstListItemHighlighted)

      await user.clear(input)
      await user.type(input, 'new query')

      await waitFor(() =>
        expect(mockFetchAlgoliaData).toHaveBeenCalledWith('chapters', 'new query', 1, 3)
      )

      await waitFor(expectListItemsNotHighlighted)
    })

    it('clears all state when clear button is clicked', async () => {
      const user = userEvent.setup()
      render(<MultiSearchBar {...defaultProps} />)

      const input = screen.getByPlaceholderText('Search...')
      await user.type(input, 'test')

      const clearButton = screen.getByLabelText('Clear search')
      await user.click(clearButton)

      expect(input).toHaveValue('')
      expect(screen.queryByRole('list')).not.toBeInTheDocument()
    })
  })

  describe('Component Cleanup', () => {
    it('cancels debounced search on unmount', () => {
      const removeEventListenerSpy = jest.spyOn(document, 'removeEventListener')
      const { debounce } = jest.requireMock('lodash')
      const { unmount } = render(<MultiSearchBar {...defaultProps} />)

      unmount()

      expect(removeEventListenerSpy).toHaveBeenCalledWith('keydown', expect.any(Function))
      expect(removeEventListenerSpy).toHaveBeenCalledWith('mousedown', expect.any(Function))

      const debouncedFn = debounce.mock.results[0]?.value
      expect(debouncedFn?.cancel).toHaveBeenCalled()

      removeEventListenerSpy.mockRestore()
    })
  })
})
