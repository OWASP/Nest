import { useQuery } from '@apollo/client/react'
import { render, screen, fireEvent, within } from '@testing-library/react'
import { useParams } from 'next/navigation'
import { handleAppError } from 'app/global-error'
import MenteeProfilePage from 'app/my/mentorship/programs/[programKey]/modules/[moduleKey]/mentees/[menteeKey]/page'

// Mock dependencies
jest.mock('@apollo/client/react', () => ({
  ...jest.requireActual('@apollo/client/react'),
  useQuery: jest.fn(),
}))

jest.mock('next/navigation', () => ({
  useParams: jest.fn(),
}))

jest.mock('app/global-error', () => ({
  handleAppError: jest.fn(),
  ErrorDisplay: ({ title }: { title: string }) => <div>{title}</div>,
}))

// Mock components
jest.mock('components/LabelList', () => ({
  LabelList: ({ labels }: { labels: string[] }) => (
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

    // Check stats
    expect(screen.getByText('Total Issues')).toBeInTheDocument()
    expect(screen.getByText('3')).toBeInTheDocument()
    expect(screen.getByText('Open Issues')).toBeInTheDocument()
    expect(screen.getByText('2')).toBeInTheDocument()
    expect(screen.getByText('Closed Issues')).toBeInTheDocument()
    expect(screen.getByText('1')).toBeInTheDocument()

    // Check domains and skills
    const domainsHeading = screen.getByRole('heading', { name: /Domains/i })
    const domainsContainer = domainsHeading.parentElement
    expect(domainsContainer).not.toBeNull()
    expect(within(domainsContainer as HTMLElement).getByTestId('label-list')).toHaveTextContent(
      'frontend, backend'
    )

    const skillsHeading = screen.getByRole('heading', { name: /Skills & Technologies/i })
    const skillsContainer = skillsHeading.parentElement
    expect(skillsContainer).not.toBeNull()
    expect(within(skillsContainer as HTMLElement).getByTestId('label-list')).toHaveTextContent(
      'react, nodejs'
    )

    // Check issues
    expect(screen.getByText('Open Issue 1')).toBeInTheDocument()
    expect(screen.getByText('Closed Issue 1')).toBeInTheDocument()
    expect(screen.getByText('Open Issue 2')).toBeInTheDocument()
  })

  it('filters issues correctly when the dropdown is used', () => {
    mockUseQuery.mockReturnValue({ data: mockMenteeData, loading: false, error: undefined })
    render(<MenteeProfilePage />)

    const filterSelect = screen.getByRole('combobox')

    // Filter for open issues
    fireEvent.change(filterSelect, { target: { value: 'open' } })
    expect(screen.getByText('Open Issue 1')).toBeInTheDocument()
    expect(screen.getByText('Open Issue 2')).toBeInTheDocument()
    expect(screen.queryByText('Closed Issue 1')).not.toBeInTheDocument()

    // Filter for closed issues
    fireEvent.change(filterSelect, { target: { value: 'closed' } })
    expect(screen.getByText('Closed Issue 1')).toBeInTheDocument()
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
    expect(screen.getByText('No issues assigned to this mentee in this module')).toBeInTheDocument()
  })
})
