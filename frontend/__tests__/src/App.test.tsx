import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import React from 'react'
import { MemoryRouter } from 'react-router-dom'

import App from '../../src/App'

import '@testing-library/jest-dom'

jest.mock('../../src/pages', () => ({
  Home: jest.fn(() => <div data-testid="home-page">Home Page</div>),
  ProjectsPage: jest.fn(() => <div data-testid="projects-page">Projects Page</div>),
  CommitteesPage: jest.fn(() => <div data-testid="committees-page">Committees Page</div>),
  ChaptersPage: jest.fn(() => <div data-testid="chapters-page">Chapters Page</div>),
  ContributePage: jest.fn(() => <div data-testid="contribute-page">Contribute Page</div>),
}))

jest.mock('../../src/components/Header', () => {
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

jest.mock('../../src/components/Footer', () => {
  return function MockFooter() {
    return <footer data-testid="footer">Footer</footer>
  }
})

describe('App Component', () => {
  beforeEach(() => {
    window.scrollTo = jest.fn()
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
