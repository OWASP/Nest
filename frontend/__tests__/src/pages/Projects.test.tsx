import { render, screen, waitFor } from '@testing-library/react'
import React from 'react'

import '@testing-library/jest-dom'
import { loadData } from '../../../src/lib/api'
import { ProjectsPage } from '../../../src/pages'
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

  test('renders loading spinner initially', async () => {
    render(<ProjectsPage />)
    const loadingSpinner = screen.getAllByAltText('Loading indicator')
    await waitFor(() => {
      expect(loadingSpinner.length).toBeGreaterThan(0)
    })
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
})
