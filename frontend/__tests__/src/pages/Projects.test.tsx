import { fireEvent, screen, waitFor } from '@testing-library/react'
import React from 'react'

import '@testing-library/jest-dom'
import { loadData } from '../../../src/lib/api'
import { render } from '../../../src/lib/test-util'
import { ProjectsPage } from '../../../src/pages'
import mockProjectData from '../data/mockProjectData'

jest.mock('../../../src/lib/api', () => ({
  loadData: jest.fn(),
}))

jest.mock('../../../src/utils/credentials', () => ({
  API_URL: 'https://mock-api.com',
}))
jest.mock('../../../src/components/Pagination', () =>
  jest.fn(({ currentPage, onPageChange }) => (
    <div>
      <button onClick={() => onPageChange(currentPage + 1)}>Next Page</button>
    </div>
  ))
)

describe('ProjectPage Component', () => {
  beforeEach(() => {
    ;(loadData as jest.Mock).mockResolvedValue(mockProjectData)
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  test('renders loading spinner initially', async () => {
    render(<ProjectsPage />)
    const loadingSpinner = screen.getAllByAltText('Loading indicator')
    await waitFor(() => {
      expect(loadingSpinner.length).toBeGreaterThan(0)
    })
  })

  test('renders SearchBar, data, and pagination component concurrently after data is loaded', async () => {
    window.scrollTo = jest.fn()
    ;(loadData as jest.Mock).mockResolvedValue({
      ...mockProjectData,
      total_pages: 2,
    })

    render(<ProjectsPage />)

    const loadingSpinner = screen.getAllByAltText('Loading indicator')
    await waitFor(() => {
      expect(loadingSpinner.length).toBeGreaterThan(0)
      expect(screen.queryByPlaceholderText('Search for OWASP projects...')).not.toBeInTheDocument()
      expect(screen.queryByText('Next Page')).not.toBeInTheDocument()
    })
    await waitFor(() => {
      expect(screen.getByPlaceholderText('Search for OWASP projects...')).toBeInTheDocument()
      expect(screen.getByText('Project 1')).toBeInTheDocument()
      expect(screen.getByText('Next Page')).toBeInTheDocument()
    })

    expect(screen.queryByAltText('Loading indicator')).not.toBeInTheDocument()
  })

  test('renders project data correctly', async () => {
    render(<ProjectsPage />)
    await waitFor(() => {
      expect(screen.getByText('Project 1')).toBeInTheDocument()
    })

    expect(screen.getByText('This is a summary of Project 1.')).toBeInTheDocument()

    expect(screen.getByText('Leader 1')).toBeInTheDocument()

    const viewButton = screen.getByText('Contribute')
    expect(viewButton).toBeInTheDocument()
  })

  test('displays "No projects found" when there are no projects', async () => {
    ;(loadData as jest.Mock).mockResolvedValue({ ...mockProjectData, projects: [], total_pages: 0 })
    render(<ProjectsPage />)
    await waitFor(() => {
      expect(screen.getByText('No projects found')).toBeInTheDocument()
    })
  })

  test('handles page change correctly', async () => {
    window.scrollTo = jest.fn()
    ;(loadData as jest.Mock).mockResolvedValue({
      ...mockProjectData,
      total_pages: 2,
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

  // Test window.open functionality on Contribute button click
  test('opens new window on Contribute button click', async () => {
    // Mock window.open to track if it's called correctly
    const openSpy = jest.spyOn(window, 'open').mockImplementation(() => null)

    render(<ProjectsPage />)

    await waitFor(() => {
      const contributeButton = screen.getByText('Contribute')
      fireEvent.click(contributeButton)
    })

    // Assuming 'Project 1' is the project in the mock data
    expect(openSpy).toHaveBeenCalledWith('/projects/contribute?q=Project 1', '_blank')

    // Clean up the mock
    openSpy.mockRestore()
  })
})
