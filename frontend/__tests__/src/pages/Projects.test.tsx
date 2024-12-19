import React, { act } from 'react'
import { render, screen, waitFor } from '@testing-library/react'
import '@testing-library/jest-dom'
import { ProjectsPage } from '../../../src/pages'
import { loadData } from '../../../src/lib/api'
import mockProjectData from '../data/mockProjectData'

jest.mock('../../../src/lib/api', () => ({
  loadData: jest.fn(),
}))

jest.mock('../../../src/utils/credentials', () => ({
  API_URL: 'https://mock-api.com',
}))

describe('ProjectPage Component', () => {
  beforeEach(() => {
    ;(loadData as jest.Mock).mockResolvedValue(mockProjectData)
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  it('renders loading spinner initially', () => {
    act(() => {
      render(<ProjectsPage />)
    })
    const loadingSpinner = screen.getAllByAltText('Loading indicator')
    expect(loadingSpinner.length).toBeGreaterThan(0)
  })

  it('renders project data correctly', async () => {
    await act(async () => {
      render(<ProjectsPage />)
    })

    expect(screen.getByText('Project 1')).toBeInTheDocument()

    expect(screen.getByText('This is a summary of Project 1.')).toBeInTheDocument()

    expect(screen.getByText('Leader 1')).toBeInTheDocument()

    const viewButton = screen.getByText('Contribute')
    expect(viewButton).toBeInTheDocument()
  })

  it('displays "No projects found" when there are no projects', async () => {
    ;(loadData as jest.Mock).mockResolvedValue({ ...mockProjectData, projects: [], total_pages: 0 })

    await act(async () => {
      render(<ProjectsPage />)
    })

    await waitFor(() => {
      expect(screen.getByText('No projects found')).toBeInTheDocument()
    })
  })
})
