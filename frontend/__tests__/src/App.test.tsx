import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import App from 'App'
import { useToast } from 'hooks/useToast'
import { MemoryRouter } from 'react-router-dom'
import '@testing-library/jest-dom'
import { Toaster } from 'components/ui/Toaster'

jest.mock('pages', () => ({
  Home: () => <div data-testid="home-page">Home Page</div>,
  ProjectsPage: () => <div data-testid="projects-page">Projects Page</div>,
  CommitteesPage: () => <div data-testid="committees-page">Committees Page</div>,
  ChaptersPage: () => <div data-testid="chapters-page">Chapters Page</div>,
  ContributePage: () => <div data-testid="contribute-page">Contribute Page</div>,
  ChapterDetailsPage: () => <div data-testid="chapter-details-page">ChapterDetailsPage Page</div>,
  CommitteeDetailsPage: () => <div data-testid="committee-details-page">CommitteeDetails Page</div>,
  ProjectDetailsPage: () => <div data-testid="project-details-page">ProjectDetails Page</div>,
  RepositoryDetailsPage: () => (
    <div data-testid="repository-details-page">RepositoryDetails Page</div>
  ),
  UserDetailsPage: () => <div data-testid="user-details-page">UserDetails Page</div>,
  UsersPage: () => <div data-testid="users-page">Users Page</div>,
}))
jest.mock('hooks/useToast', () => ({
  useToast: jest.fn(() => ({
    toasts: [],
    toast: jest.fn(),
    dismiss: jest.fn(),
  })),
}))

jest.mock('components/Header', () => {
  const { Link } = require('react-router-dom')
  return function MockHeader() {
    return (
      <header data-testid="header" className="fixed top-0 w-full">
        <nav>
          <Link to="/projects" data-testid="projects-link">
            Projects
          </Link>
          <Link to="/committees" data-testid="committees-link">
            Committees
          </Link>
          <Link to="/chapters" data-testid="chapters-link">
            Chapters
          </Link>
        </nav>
      </header>
    )
  }
})

jest.mock('components/Footer', () => {
  return function MockFooter() {
    return <footer data-testid="footer">Footer</footer>
  }
})

describe('App Component', () => {
  beforeEach(() => {
    window.scrollTo = jest.fn()
    ;(useToast as jest.Mock).mockImplementation(() => ({
      toasts: [],
      toast: jest.fn(),
      dismiss: jest.fn(),
    }))
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  test('renders main layout elements', () => {
    render(
      <MemoryRouter>
        <App />
      </MemoryRouter>
    )

    expect(screen.getByTestId('header')).toBeInTheDocument()
    expect(screen.getByTestId('footer')).toBeInTheDocument()
    expect(screen.getByRole('main')).toHaveClass('flex', 'min-h-screen', 'w-full', 'flex-col')
  })

  test('navigates and scrolls to top when changing routes', async () => {
    render(
      <MemoryRouter initialEntries={['/projects']}>
        <App />
      </MemoryRouter>
    )

    expect(screen.getByTestId('projects-page')).toBeInTheDocument()
    expect(window.scrollTo).toHaveBeenCalledWith(0, 0)

    const committeesLink = screen.getByTestId('committees-link')
    fireEvent.click(committeesLink)

    await waitFor(() => {
      expect(screen.getByTestId('committees-page')).toBeInTheDocument()
    })
    expect(window.scrollTo).toHaveBeenCalledWith(0, 0)

    const chaptersLink = screen.getByTestId('chapters-link')
    fireEvent.click(chaptersLink)

    await waitFor(() => {
      expect(screen.getByTestId('chapters-page')).toBeInTheDocument()
    })
    expect(window.scrollTo).toHaveBeenCalledWith(0, 0)
  })

  test('renders different pages for different routes', () => {
    const routes = [
      { path: '/projects', testId: 'projects-page' },
      { path: '/committees', testId: 'committees-page' },
      { path: '/chapters', testId: 'chapters-page' },
    ]

    routes.forEach((route) => {
      const { unmount } = render(
        <MemoryRouter initialEntries={[route.path]}>
          <App />
        </MemoryRouter>
      )

      expect(screen.getByTestId(route.testId)).toBeInTheDocument()
      unmount()
    })
  })

  test('scrolls to top when navigating from a scrolled position', async () => {
    render(
      <MemoryRouter initialEntries={['/projects']}>
        <App />
      </MemoryRouter>
    )

    expect(window.scrollTo).toHaveBeenCalledWith(0, 0)

    window.scrollTo(0, 500)
    expect(window.scrollTo).toHaveBeenCalledWith(0, 500)

    const committeesLink = screen.getByTestId('committees-link')
    fireEvent.click(committeesLink)

    await waitFor(() => {
      expect(screen.getByTestId('committees-page')).toBeInTheDocument()

      expect(window.scrollTo).toHaveBeenLastCalledWith(0, 0)
    })

    window.scrollTo(0, 800)
    expect(window.scrollTo).toHaveBeenCalledWith(0, 800)

    const chaptersLink = screen.getByTestId('chapters-link')
    fireEvent.click(chaptersLink)

    await waitFor(() => {
      expect(screen.getByTestId('chapters-page')).toBeInTheDocument()

      expect(window.scrollTo).toHaveBeenLastCalledWith(0, 0)
    })
  })
})
describe('Toaster Component', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('renders toast with title and description', () => {
    const mockToast = {
      id: '1',
      title: 'Test Title',
      description: 'Test Description',
      open: true,
    }

    ;(useToast as jest.Mock).mockReturnValue({
      toasts: [mockToast],
    })

    render(<Toaster />)

    expect(screen.getByText('Test Title')).toBeInTheDocument()
    expect(screen.getByText('Test Description')).toBeInTheDocument()
  })
})
