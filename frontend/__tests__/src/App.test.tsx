import { render, screen } from '@testing-library/react'
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

describe('App Component', () => {
  test('renders Home page by default', () => {
    render(
      <MemoryRouter initialEntries={['/']}>
        <App />
      </MemoryRouter>
    )

    const homePage = screen.getByTestId('home-page')
    expect(homePage).toBeInTheDocument()
  })

  test('renders Projects page when navigating to /projects', () => {
    render(
      <MemoryRouter initialEntries={['/projects']}>
        <App />
      </MemoryRouter>
    )

    const projectsPage = screen.getByTestId('projects-page')
    expect(projectsPage).toBeInTheDocument()
  })
})
