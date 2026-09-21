import { render, screen, fireEvent, act } from '@testing-library/react'
import type { ButtonHTMLAttributes, ReactNode } from 'react'
import type { PulseFiltersProps } from 'types/pulse'
import PulseFilters, { ACTIVITY_TYPES, TIME_RANGES } from 'components/pulse/PulseFilters'

jest.mock('@heroui/button', () => {
  const MockButton = ({
    children,
    onPress,
    isIconOnly: _isIconOnly,
    isPressable: _isPressable,
    variant: _variant,
    radius: _radius,
    size: _size,
    color: _color,
    fullWidth: _fullWidth,
    isDisabled: _isDisabled,
    isLoading: _isLoading,
    disableRipple: _disableRipple,
    disableAnimation: _disableAnimation,
    ...props
  }: {
    children: ReactNode
    onPress?: () => void
    [key: string]: unknown
  }) => (
    <button onClick={onPress} {...(props as ButtonHTMLAttributes<HTMLButtonElement>)}>
      {children}
    </button>
  )
  MockButton.displayName = 'MockButton'
  return {
    __esModule: true,
    // eslint-disable-next-line @typescript-eslint/naming-convention
    Button: MockButton,
  }
})

jest.mock('components/SortBy', () => {
  const MockSortBy = ({
    id,
    sortOptions,
    selectedSortOption,
    onSortChange,
    onOrderChange,
  }: {
    id: string
    sortOptions: Array<{ key: string; label: string }>
    selectedSortOption: string
    onSortChange: (value: string) => void
    onOrderChange?: (value: string) => void
  }) => (
    <div>
      <select
        data-testid={id}
        value={selectedSortOption}
        onChange={(e) => onSortChange(e.target.value)}
      >
        {sortOptions.map((opt) => (
          <option key={opt.key} value={opt.key}>
            {opt.label}
          </option>
        ))}
      </select>
      <button
        data-testid={`${id}-order-toggle`}
        onClick={() => onOrderChange?.(selectedSortOption === 'asc' ? 'desc' : 'asc')}
      />
    </div>
  )
  MockSortBy.displayName = 'MockSortBy'
  return { __esModule: true, default: MockSortBy }
})

jest.mock('utils/sortingOptions', () => ({
  sortOptionsPulse: [
    { key: 'desc', label: 'Newest First' },
    { key: 'asc', label: 'Oldest First' },
  ],
}))

const defaultProps: PulseFiltersProps = {
  activityType: '',
  chapterKey: '',
  chapterSearchInput: '',
  chapterSuggestions: [],
  clearAllFilters: jest.fn(),
  handleSelectChapter: jest.fn(),
  handleSelectProject: jest.fn(),
  isSearchingChapters: false,
  isSearchingProjects: false,
  order: 'desc',
  projectKey: '',
  projectSearchInput: '',
  projectSuggestions: [],
  searchQuery: '',
  setActivityType: jest.fn(),
  setChapterKey: jest.fn(),
  setChapterSearchInput: jest.fn(),
  setOrder: jest.fn(),
  setPage: jest.fn(),
  setProjectKey: jest.fn(),
  setProjectSearchInput: jest.fn(),
  setSearchQuery: jest.fn(),
  setShowChapterSuggestions: jest.fn(),
  setShowProjectSuggestions: jest.fn(),
  setTimeRange: jest.fn(),
  showChapterSuggestions: false,
  showProjectSuggestions: false,
  timeRange: '',
}

afterEach(() => {
  jest.clearAllMocks()
  jest.useRealTimers()
})

describe('<PulseFilters />', () => {
  it('renders filters, active filter chips, dropdowns, and handles user interactions', () => {
    jest.useFakeTimers()
    const activeProps: PulseFiltersProps = {
      ...defaultProps,
      searchQuery: 'strawberry',
      activityType: 'pr_opened',
      projectKey: 'www-project-nest',
      chapterKey: 'www-chapter-london',
      timeRange: '7d',
    }

    const { rerender } = render(<PulseFilters {...activeProps} />)

    expect(screen.getByRole('textbox', { name: 'Search activity' })).toBeInTheDocument()
    expect(ACTIVITY_TYPES.length).toBeGreaterThan(0)
    expect(TIME_RANGES.length).toBeGreaterThan(0)
    expect(screen.getByRole('textbox', { name: 'Filter by project' })).toBeInTheDocument()
    expect(screen.getByRole('textbox', { name: 'Filter by chapter' })).toBeInTheDocument()
    expect(screen.getByTestId('pulse-activity-type-select')).toBeInTheDocument()
    expect(screen.getByTestId('pulse-time-range-select')).toBeInTheDocument()
    expect(screen.getByTestId('pulse-sort-order-select')).toBeInTheDocument()

    expect(screen.getByText('Active filters:')).toBeInTheDocument()
    expect(screen.getByText(/Search: strawberry/)).toBeInTheDocument()
    expect(screen.getByText(/Type: PR Opened/)).toBeInTheDocument()
    expect(screen.getByText(/Project: www-project-nest/)).toBeInTheDocument()
    expect(screen.getByText(/Chapter: www-chapter-london/)).toBeInTheDocument()
    expect(screen.getByText(/Time: Last 7 Days/)).toBeInTheDocument()

    fireEvent.click(screen.getByLabelText('Clear search filter'))
    expect(defaultProps.setSearchQuery).toHaveBeenCalledWith('')
    expect(defaultProps.setPage).toHaveBeenCalledWith(1)

    fireEvent.click(screen.getByLabelText('Clear activity type filter'))
    expect(defaultProps.setActivityType).toHaveBeenCalledWith('')

    fireEvent.click(screen.getByLabelText('Clear project filter'))
    expect(defaultProps.setProjectKey).toHaveBeenCalledWith('')
    expect(defaultProps.setProjectSearchInput).toHaveBeenCalledWith('')

    fireEvent.click(screen.getByLabelText('Clear chapter filter'))
    expect(defaultProps.setChapterKey).toHaveBeenCalledWith('')
    expect(defaultProps.setChapterSearchInput).toHaveBeenCalledWith('')

    fireEvent.click(screen.getByLabelText('Clear time range filter'))
    expect(defaultProps.setTimeRange).toHaveBeenCalledWith('')

    fireEvent.click(screen.getByText('Clear all'))
    expect(defaultProps.clearAllFilters).toHaveBeenCalledTimes(1)

    rerender(
      <PulseFilters {...defaultProps} activityType="custom_event" timeRange="custom_range" />
    )
    expect(screen.getByText(/Type: custom_event/)).toBeInTheDocument()
    expect(screen.getByText(/Time: custom_range/)).toBeInTheDocument()

    rerender(<PulseFilters {...defaultProps} />)
    expect(screen.queryByText('Active filters:')).not.toBeInTheDocument()

    fireEvent.change(screen.getByRole('textbox', { name: 'Search activity' }), {
      target: { value: 'owasp' },
    })
    expect(defaultProps.setSearchQuery).toHaveBeenCalledWith('owasp')

    fireEvent.change(screen.getByTestId('pulse-activity-type-select'), {
      target: { value: 'pr_opened' },
    })
    expect(defaultProps.setActivityType).toHaveBeenCalledWith('pr_opened')
    fireEvent.click(screen.getByTestId('pulse-activity-type-select-order-toggle'))

    fireEvent.change(screen.getByTestId('pulse-time-range-select'), {
      target: { value: '30d' },
    })
    expect(defaultProps.setTimeRange).toHaveBeenCalledWith('30d')
    fireEvent.click(screen.getByTestId('pulse-time-range-select-order-toggle'))

    fireEvent.change(screen.getByTestId('pulse-sort-order-select'), {
      target: { value: 'asc' },
    })
    expect(defaultProps.setOrder).toHaveBeenCalledWith('asc')
    fireEvent.click(screen.getByTestId('pulse-sort-order-select-order-toggle'))

    const projInput = screen.getByRole('textbox', { name: 'Filter by project' })
    fireEvent.focus(projInput)
    expect(defaultProps.setShowProjectSuggestions).toHaveBeenCalledWith(true)

    fireEvent.change(projInput, { target: { value: 'nest' } })
    expect(defaultProps.setProjectSearchInput).toHaveBeenCalledWith('nest')
    expect(defaultProps.setProjectKey).toHaveBeenCalledWith('')

    fireEvent.blur(projInput)
    act(() => {
      jest.advanceTimersByTime(250)
    })
    expect(defaultProps.setShowProjectSuggestions).toHaveBeenCalledWith(false)

    const chapInput = screen.getByRole('textbox', { name: 'Filter by chapter' })
    fireEvent.focus(chapInput)
    expect(defaultProps.setShowChapterSuggestions).toHaveBeenCalledWith(true)

    fireEvent.change(chapInput, { target: { value: 'london' } })
    expect(defaultProps.setChapterSearchInput).toHaveBeenCalledWith('london')
    expect(defaultProps.setChapterKey).toHaveBeenCalledWith('')

    fireEvent.blur(chapInput)
    act(() => {
      jest.advanceTimersByTime(250)
    })
    expect(defaultProps.setShowChapterSuggestions).toHaveBeenCalledWith(false)

    rerender(
      <PulseFilters
        {...defaultProps}
        showProjectSuggestions
        isSearchingProjects
        showChapterSuggestions
        isSearchingChapters
      />
    )
    expect(screen.getByText('Searching projects...')).toBeInTheDocument()
    expect(screen.getByText('Searching chapters...')).toBeInTheDocument()

    const projectSuggestions = [
      { id: 'p1', name: 'OWASP Nest' },
      { id: '', name: 'OWASP Top Ten' },
    ]
    const chapterSuggestions = [
      { id: 'c1', name: 'London Chapter' },
      { id: '', name: 'NYC Chapter' },
    ]

    rerender(
      <PulseFilters
        {...defaultProps}
        showProjectSuggestions
        projectSuggestions={[]}
        showChapterSuggestions
        chapterSuggestions={[]}
      />
    )
    expect(screen.getByText('No project suggestions found')).toBeInTheDocument()
    expect(screen.getByText('No chapter suggestions found')).toBeInTheDocument()

    rerender(
      <PulseFilters
        {...defaultProps}
        showProjectSuggestions
        projectSuggestions={projectSuggestions}
        showChapterSuggestions
        chapterSuggestions={chapterSuggestions}
      />
    )

    const nestBtn = screen.getByText('OWASP Nest')
    fireEvent.mouseDown(nestBtn)
    fireEvent.click(nestBtn)
    expect(defaultProps.handleSelectProject).toHaveBeenCalledWith(projectSuggestions[0])

    const topTenBtn = screen.getByText('OWASP Top Ten')
    fireEvent.mouseDown(topTenBtn)
    fireEvent.click(topTenBtn)
    expect(defaultProps.handleSelectProject).toHaveBeenCalledWith(projectSuggestions[1])

    const londonBtn = screen.getByText('London Chapter')
    fireEvent.mouseDown(londonBtn)
    fireEvent.click(londonBtn)
    expect(defaultProps.handleSelectChapter).toHaveBeenCalledWith(chapterSuggestions[0])

    const nycBtn = screen.getByText('NYC Chapter')
    fireEvent.mouseDown(nycBtn)
    fireEvent.click(nycBtn)
    expect(defaultProps.handleSelectChapter).toHaveBeenCalledWith(chapterSuggestions[1])
  })
})
