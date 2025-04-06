import { waitFor, screen, fireEvent } from '@testing-library/react'
import mockProjectData from '@unit/data/mockProjectData'
import { useRouter } from 'next/navigation'
import { fetchAlgoliaData } from 'server/fetchAlgoliaData'
import { render } from 'wrappers/testUtil'
import ProjectsPage from 'app/projects/page'

const mockRouter = {
  push: jest.fn(),
}

jest.mock('next/navigation', () => ({
  ...jest.requireActual('next/navigation'),
  useRouter: jest.fn(() => mockRouter),
  useParams: () => ({ userKey: 'test-user' }),
  useSearchParams: () => new URLSearchParams(),
}))

jest.mock('server/fetchAlgoliaData', () => ({
  fetchAlgoliaData: jest.fn(),
}))

jest.mock('components/Pagination', () =>
  jest.fn(({ currentPage, onPageChange }) => (
    <div>
      <button onClick={() => onPageChange(currentPage + 1)}>Next Page</button>
    </div>
  ))
)
jest.mock('wrappers/FontAwesomeIconWrapper', () => ({
  __esModule: true,
  default: () => <span data-testid="mock-icon" />,
}))

jest.mock('@/components/MarkdownWrapper', () => {
  return ({ content, className }: { content: string; className?: string }) => (
    <div
      className={`md-wrapper ${className || ''}`}
      dangerouslySetInnerHTML={{ __html: content }}
    />
  )
})

describe('ProjectPage Component', () => {
  let mockRouter: { push: jest.Mock }
  beforeEach(() => {
    ;(fetchAlgoliaData as jest.Mock).mockResolvedValue({
      hits: mockProjectData.projects,
      totalPages: 2,
    })
    mockRouter = { push: jest.fn() }
    ;(useRouter as jest.Mock).mockReturnValue(mockRouter)
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  test('renders skeleton initially', async () => {
    render(<ProjectsPage />)
    await waitFor(() => {
      const skeletonLoaders = screen.getAllByRole('status')
      expect(skeletonLoaders.length).toBeGreaterThan(0)
    })
  })

  test('renders SearchBar, data, and pagination component concurrently after data is loaded', async () => {
    window.scrollTo = jest.fn()
    ;(fetchAlgoliaData as jest.Mock).mockResolvedValue({
      hits: mockProjectData.projects,
      totalPages: 2,
    })

    render(<ProjectsPage />)

    const skeletonLoaders = screen.getAllByRole('status')
    await waitFor(() => {
      expect(skeletonLoaders.length).toBeGreaterThan(0)
      expect(screen.queryByText('Next Page')).not.toBeInTheDocument()
    })
    await waitFor(() => {
      expect(screen.getByPlaceholderText('Search for OWASP projects...')).toBeInTheDocument()
      expect(screen.getByText('Project 1')).toBeInTheDocument()
      expect(screen.getByText('Next Page')).toBeInTheDocument()
    })

    expect(screen.queryByTestId('status')).not.toBeInTheDocument()
  })

  test('renders project data correctly', async () => {
    render(<ProjectsPage />)
    await waitFor(() => {
      expect(screen.getByText('Project 1')).toBeInTheDocument()
    })

    expect(screen.getByText('This is a summary of Project 1.')).toBeInTheDocument()

    const viewButton = screen.getByText('View Details')
    expect(viewButton).toBeInTheDocument()
  })

  test('displays "No projects found" when there are no projects', async () => {
    ;(fetchAlgoliaData as jest.Mock).mockResolvedValue({
      hits: [],
      totalPages: 0,
    })
    render(<ProjectsPage />)
    await waitFor(() => {
      expect(screen.getByText('No projects found')).toBeInTheDocument()
    })
  })

  test('handles page change correctly', async () => {
    window.scrollTo = jest.fn()
    ;(fetchAlgoliaData as jest.Mock).mockResolvedValue({
      hits: mockProjectData.projects,
      totalPages: 2,
    })
    render(<ProjectsPage />)
    await waitFor(() => {
      const nextPageButton = screen.getByText('Next Page')
      fireEvent.click(nextPageButton)
    })
    expect(window.scrollTo).toHaveBeenCalledWith({
      top: 0,
      behavior: 'auto',
    })
  })

  test('opens  window on View Details button click', async () => {
    render(<ProjectsPage />)

    await waitFor(() => {
      const contributeButton = screen.getByRole('button', { name: 'View Details' })
      expect(contributeButton).toBeInTheDocument()
      fireEvent.click(contributeButton)
    })
    //suppose index_key is project_1
    expect(mockRouter.push).toHaveBeenCalledWith('/projects/project_1')

    // Clean up the mock
    jest.restoreAllMocks()
  })
})
