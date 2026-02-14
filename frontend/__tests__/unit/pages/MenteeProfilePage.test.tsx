import { useQuery } from '@apollo/client/react'
import { render, screen, fireEvent, within } from '@testing-library/react'
import { useParams } from 'next/navigation'
import React from 'react'
import { handleAppError } from 'app/global-error'
import MenteeProfilePage from 'app/my/mentorship/programs/[programKey]/modules/[moduleKey]/mentees/[menteeKey]/page'

// Mock dependencies
jest.mock('@apollo/client/react', () => ({
  ...jest.requireActual('@apollo/client/react'),
  useQuery: jest.fn(),
}))

jest.mock('next/navigation', () => ({
  useParams: jest.fn(),
  useRouter: () => ({
    push: jest.fn(),
  }),
}))

jest.mock('app/global-error', () => ({
  handleAppError: jest.fn(),
  ErrorDisplay: ({ title }: { title: string }) => <div>{title}</div>,
}))

// Mock components
jest.mock('components/LabelList', () => ({
  LabelList: ({ labels, entityKey: _entityKey }: { labels: string[]; entityKey: string }) => (
    <div data-testid="label-list">{labels.join(', ')}</div>
  ),
}))

jest.mock('next/image', () => ({
  __esModule: true,
  default: (props: Record<string, unknown>) => {
    // eslint-disable-next-line @next/next/no-img-element
    return <img {...props} alt={(props.alt as string) || ''} />
  },
}))

jest.mock('@heroui/tooltip', () => ({
  Tooltip: ({
    children,
    content,
    isDisabled,
  }: {
    children: React.ReactNode
    content: string
    isDisabled?: boolean
  }) => {
    if (isDisabled) {
      return <>{children}</>
    }
    return (
      <div data-testid="tooltip" data-content={content}>
        {children}
      </div>
    )
  },
}))

jest.mock('@heroui/select', () => {
  return {
    Select: ({
      children,
      selectedKeys,
      onSelectionChange,
      'aria-label': ariaLabel,
      classNames: _classNames,
      size: _size,
      ...props
    }: {
      children: React.ReactNode
      selectedKeys: Set<string>
      onSelectionChange?: (keys: Set<string>) => void
      'aria-label'?: string
      classNames?: Record<string, string>
      size?: string
    }) => {
      const [isOpen, setIsOpen] = React.useState(false)
      const selectedKey = Array.from(selectedKeys)[0] || 'all'

      const handleItemClick = (key: string) => {
        if (onSelectionChange) {
          onSelectionChange(new Set([key]))
        }
        setIsOpen(false)
      }

      return (
        <div data-testid="select-wrapper" {...props}>
          <button
            type="button"
            aria-label={ariaLabel}
            aria-expanded={isOpen}
            aria-controls="select-popover"
            onClick={() => setIsOpen(!isOpen)}
            data-testid="select-trigger"
          >
            {selectedKey}
          </button>
          <button
            type="button"
            data-testid="select-trigger-empty"
            onClick={() => onSelectionChange?.(new Set())}
            style={{ display: 'none' }}
          >
            Trigger Empty Selection
          </button>
          {isOpen && (
            <div id="select-popover" data-testid="select-popover" aria-label="Options">
              {React.Children.map(children, (child: React.ReactElement) => {
                const itemKey = String(child.key ?? '')
                return React.cloneElement(child, {
                  'data-key': itemKey,
                  onClick: () => handleItemClick(itemKey),
                } as Partial<unknown>)
              })}
            </div>
          )}
        </div>
      )
    },
    SelectItem: ({
      children,
      onClick,
      'data-key': dataKey,
      classNames: _classNames,
      ...props
    }: {
      children: React.ReactNode
      onClick?: () => void
      'data-key'?: string
      classNames?: Record<string, string>
    }) => (
      <button
        type="button"
        data-testid="select-item"
        data-key={dataKey}
        onClick={onClick}
        {...props}
      >
        {children}
      </button>
    ),
  }
})

const mockUseQuery = useQuery as unknown as jest.Mock
const mockUseParams = useParams as jest.Mock
const mockHandleAppError = handleAppError as jest.Mock

const mockMenteeData = {
  getMenteeDetails: {
    id: 'mentee1',
    login: 'test-mentee',
    name: 'Test Mentee',
    avatarUrl: 'http://example.com/avatar.png',
    bio: 'A test bio.',
    domains: ['frontend', 'backend'],
    tags: ['react', 'nodejs'],
  },
  getMenteeModuleIssues: [
    {
      id: 'issue1',
      number: 101,
      title: 'Open Issue 1',
      state: 'open',
      url: 'http://example.com/issue1',
      labels: ['bug'],
    },
    {
      id: 'issue2',
      number: 102,
      title: 'Closed Issue 1',
      state: 'closed',
      url: 'http://example.com/issue2',
      labels: ['feature'],
    },
    {
      id: 'issue3',
      number: 103,
      title: 'Open Issue 2',
      state: 'open',
      url: 'http://example.com/issue3',
      labels: ['docs'],
    },
  ],
}

describe('MenteeProfilePage', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    mockUseParams.mockReturnValue({
      programKey: 'prog1',
      moduleKey: 'mod1',
      menteeKey: 'test-mentee',
    })
  })

  it('renders a loading spinner while data is being fetched', () => {
    mockUseQuery.mockReturnValue({ data: undefined, loading: true, error: undefined })
    render(<MenteeProfilePage />)
    expect(screen.getAllByAltText('Loading indicator')[0]).toBeInTheDocument()
  })

  it('calls handleAppError on query error', () => {
    const error = new Error('Test error')
    mockUseQuery.mockReturnValue({ data: undefined, loading: false, error })
    render(<MenteeProfilePage />)
    expect(mockHandleAppError).toHaveBeenCalledWith(error)
  })

  it('renders a 404 error if the mentee is not found', () => {
    mockUseQuery.mockReturnValue({
      data: { getMenteeDetails: null },
      loading: false,
      error: undefined,
    })
    render(<MenteeProfilePage />)
    expect(screen.getByText('Mentee Not Found')).toBeInTheDocument()
  })

  it('renders the mentee profile and issues successfully', () => {
    mockUseQuery.mockReturnValue({ data: mockMenteeData, loading: false, error: undefined })
    render(<MenteeProfilePage />)

    // Check header
    expect(screen.getByText('Test Mentee')).toBeInTheDocument()
    expect(screen.getByText('@test-mentee')).toBeInTheDocument()
    expect(screen.getByText('A test bio.')).toBeInTheDocument()

    // Check domains and skills
    const domainsHeading = screen.getByRole('heading', { name: /Domains/i })
    const domainsContainer = domainsHeading.parentElement
    if (!domainsContainer) {
      throw new Error('Domains container not found')
    }
    expect(within(domainsContainer).getByTestId('label-list')).toHaveTextContent(
      'frontend, backend'
    )

    const skillsHeading = screen.getByRole('heading', { name: /Skills & Technologies/i })
    const skillsContainer = skillsHeading.parentElement
    if (!skillsContainer) {
      throw new Error('Skills container not found')
    }
    expect(within(skillsContainer).getByTestId('label-list')).toHaveTextContent('react, nodejs')

    // Check issues (appear in both desktop and mobile views)
    const openIssue1Elements = screen.getAllByText('Open Issue 1')
    const closedIssue1Elements = screen.getAllByText('Closed Issue 1')
    const openIssue2Elements = screen.getAllByText('Open Issue 2')
    expect(openIssue1Elements.length).toBeGreaterThan(0)
    expect(closedIssue1Elements.length).toBeGreaterThan(0)
    expect(openIssue2Elements.length).toBeGreaterThan(0)
  })

  it('filters issues correctly when the dropdown is used', () => {
    mockUseQuery.mockReturnValue({ data: mockMenteeData, loading: false, error: undefined })
    render(<MenteeProfilePage />)

    const filterSelect = screen.getByTestId('select-trigger')

    // Filter for open issues
    fireEvent.click(filterSelect)
    const openOption = screen.getByText('Open (2)')
    fireEvent.click(openOption)
    const openIssue1Elements = screen.getAllByText('Open Issue 1')
    const openIssue2Elements = screen.getAllByText('Open Issue 2')
    expect(openIssue1Elements.length).toBeGreaterThan(0)
    expect(openIssue2Elements.length).toBeGreaterThan(0)
    expect(screen.queryByText('Closed Issue 1')).not.toBeInTheDocument()

    // Filter for closed issues
    fireEvent.click(filterSelect)
    const closedOption = screen.getByText('Closed (1)')
    fireEvent.click(closedOption)
    const closedIssue1Elements = screen.getAllByText('Closed Issue 1')
    expect(closedIssue1Elements.length).toBeGreaterThan(0)
    expect(screen.queryByText('Open Issue 1')).not.toBeInTheDocument()
    expect(screen.queryByText('Open Issue 2')).not.toBeInTheDocument()
  })

  it('shows a message when no issues are assigned', () => {
    const noIssuesData = {
      ...mockMenteeData,
      getMenteeModuleIssues: [],
    }
    mockUseQuery.mockReturnValue({ data: noIssuesData, loading: false, error: undefined })
    render(<MenteeProfilePage />)
    const emptyMessages = screen.getAllByText('No issues found for the selected filter.')
    expect(emptyMessages.length).toBeGreaterThan(0)
  })

  describe('handleIssueClick', () => {
    beforeEach(() => {
      jest.spyOn(globalThis, 'open').mockImplementation(() => null)
    })

    afterEach(() => {
      jest.restoreAllMocks()
    })

    it('opens the issue URL in a new tab when clicking on an issue with a URL', () => {
      mockUseQuery.mockReturnValue({ data: mockMenteeData, loading: false, error: undefined })
      render(<MenteeProfilePage />)

      // The IssuesTable component renders the title as a button - click on it
      const issueButton = screen.getAllByRole('button', { name: 'Open Issue 1' })[0]
      fireEvent.click(issueButton)
      expect(window.open).toHaveBeenCalledWith(
        'http://example.com/issue1',
        '_blank',
        'noopener,noreferrer'
      )
    })

    it('does not call window.open when issue has no URL', () => {
      const dataWithNoUrl = {
        ...mockMenteeData,
        getMenteeModuleIssues: [
          {
            id: 'issue1',
            number: 101,
            title: 'Issue without URL',
            state: 'open',
            url: '',
            labels: ['bug'],
          },
        ],
      }
      mockUseQuery.mockReturnValue({ data: dataWithNoUrl, loading: false, error: undefined })
      render(<MenteeProfilePage />)

      const issueButton = screen.getAllByRole('button', { name: 'Issue without URL' })[0]
      fireEvent.click(issueButton)
      // window.open should not be called for empty URL
      expect(window.open).not.toHaveBeenCalled()
    })

    it('does not call window.open when issue URL is undefined', () => {
      const dataWithUndefinedUrl = {
        ...mockMenteeData,
        getMenteeModuleIssues: [
          {
            id: 'issue1',
            number: 101,
            title: 'Issue with undefined URL',
            state: 'open',
            url: undefined,
            labels: ['bug'],
          },
        ],
      }
      mockUseQuery.mockReturnValue({ data: dataWithUndefinedUrl, loading: false, error: undefined })
      render(<MenteeProfilePage />)

      const issueButton = screen.getAllByRole('button', { name: 'Issue with undefined URL' })[0]
      fireEvent.click(issueButton)
      // window.open should not be called for undefined URL
      expect(window.open).not.toHaveBeenCalled()
    })
  })

  it('renders mentee name from login when name is not provided', () => {
    const dataWithoutName = {
      ...mockMenteeData,
      getMenteeDetails: {
        ...mockMenteeData.getMenteeDetails,
        name: null,
      },
    }
    mockUseQuery.mockReturnValue({ data: dataWithoutName, loading: false, error: undefined })
    render(<MenteeProfilePage />)

    // Should show login as the heading when name is null
    const headings = screen.getAllByRole('heading')
    const nameHeading = headings.find((h) => h.textContent === 'test-mentee')
    expect(nameHeading).toBeInTheDocument()
  })

  it('does not render bio section when bio is not provided', () => {
    const dataWithoutBio = {
      ...mockMenteeData,
      getMenteeDetails: {
        ...mockMenteeData.getMenteeDetails,
        bio: null,
      },
    }
    mockUseQuery.mockReturnValue({ data: dataWithoutBio, loading: false, error: undefined })
    render(<MenteeProfilePage />)

    expect(screen.queryByText('A test bio.')).not.toBeInTheDocument()
  })

  it('does not render domains/skills section when both are empty', () => {
    const dataWithoutDomainsAndTags = {
      ...mockMenteeData,
      getMenteeDetails: {
        ...mockMenteeData.getMenteeDetails,
        domains: [],
        tags: [],
      },
    }
    mockUseQuery.mockReturnValue({
      data: dataWithoutDomainsAndTags,
      loading: false,
      error: undefined,
    })
    render(<MenteeProfilePage />)

    expect(screen.queryByRole('heading', { name: /Domains/i })).not.toBeInTheDocument()
    expect(
      screen.queryByRole('heading', { name: /Skills & Technologies/i })
    ).not.toBeInTheDocument()
  })

  it('renders only domains section when tags are empty', () => {
    const dataWithOnlyDomains = {
      ...mockMenteeData,
      getMenteeDetails: {
        ...mockMenteeData.getMenteeDetails,
        domains: ['frontend'],
        tags: [],
      },
    }
    mockUseQuery.mockReturnValue({ data: dataWithOnlyDomains, loading: false, error: undefined })
    render(<MenteeProfilePage />)

    expect(screen.getByRole('heading', { name: /Domains/i })).toBeInTheDocument()
    expect(
      screen.queryByRole('heading', { name: /Skills & Technologies/i })
    ).not.toBeInTheDocument()
  })

  it('renders only skills section when domains are empty', () => {
    const dataWithOnlyTags = {
      ...mockMenteeData,
      getMenteeDetails: {
        ...mockMenteeData.getMenteeDetails,
        domains: [],
        tags: ['react'],
      },
    }
    mockUseQuery.mockReturnValue({ data: dataWithOnlyTags, loading: false, error: undefined })
    render(<MenteeProfilePage />)

    expect(screen.queryByRole('heading', { name: /Domains/i })).not.toBeInTheDocument()
    expect(screen.getByRole('heading', { name: /Skills & Technologies/i })).toBeInTheDocument()
  })

  it('handles issues with null labels using fallback', () => {
    const dataWithNullLabels = {
      ...mockMenteeData,
      getMenteeModuleIssues: [
        {
          id: 'issue1',
          number: 101,
          title: 'Issue with null labels',
          state: 'open',
          url: 'http://example.com/issue1',
          labels: null,
        },
      ],
    }
    mockUseQuery.mockReturnValue({ data: dataWithNullLabels, loading: false, error: undefined })
    render(<MenteeProfilePage />)

    expect(screen.getAllByText('Issue with null labels').length).toBeGreaterThan(0)
  })

  it('handles issues with undefined labels using fallback', () => {
    const dataWithUndefinedLabels = {
      ...mockMenteeData,
      getMenteeModuleIssues: [
        {
          id: 'issue1',
          number: 101,
          title: 'Issue with undefined labels',
          state: 'open',
          url: 'http://example.com/issue1',
          labels: undefined,
        },
      ],
    }
    mockUseQuery.mockReturnValue({
      data: dataWithUndefinedLabels,
      loading: false,
      error: undefined,
    })
    render(<MenteeProfilePage />)

    expect(screen.getAllByText('Issue with undefined labels').length).toBeGreaterThan(0)
  })

  it('handles null domains with nullish coalescing', () => {
    const dataWithNullDomains = {
      ...mockMenteeData,
      getMenteeDetails: {
        ...mockMenteeData.getMenteeDetails,
        domains: null,
        tags: ['react'],
      },
    }
    mockUseQuery.mockReturnValue({ data: dataWithNullDomains, loading: false, error: undefined })
    render(<MenteeProfilePage />)

    expect(screen.queryByRole('heading', { name: /Domains/i })).not.toBeInTheDocument()
    expect(screen.getByRole('heading', { name: /Skills & Technologies/i })).toBeInTheDocument()
  })

  it('handles null tags with nullish coalescing', () => {
    const dataWithNullTags = {
      ...mockMenteeData,
      getMenteeDetails: {
        ...mockMenteeData.getMenteeDetails,
        domains: ['frontend'],
        tags: null,
      },
    }
    mockUseQuery.mockReturnValue({ data: dataWithNullTags, loading: false, error: undefined })
    render(<MenteeProfilePage />)

    expect(screen.getByRole('heading', { name: /Domains/i })).toBeInTheDocument()
    expect(
      screen.queryByRole('heading', { name: /Skills & Technologies/i })
    ).not.toBeInTheDocument()
  })

  it('does not change filter when selection is empty', () => {
    mockUseQuery.mockReturnValue({ data: mockMenteeData, loading: false, error: undefined })
    render(<MenteeProfilePage />)

    expect(screen.getAllByText('Open Issue 1').length).toBeGreaterThan(0)
    expect(screen.getAllByText('Closed Issue 1').length).toBeGreaterThan(0)

    const emptyTrigger = screen.getByTestId('select-trigger-empty')
    fireEvent.click(emptyTrigger)

    expect(screen.getAllByText('Open Issue 1').length).toBeGreaterThan(0)
    expect(screen.getAllByText('Closed Issue 1').length).toBeGreaterThan(0)
  })
})
