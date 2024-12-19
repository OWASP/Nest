import { render, screen, waitFor } from '@testing-library/react'
import React from 'react'

import '@testing-library/jest-dom'
import { loadData } from '../../../src/lib/api'
import { CommitteesPage } from '../../../src/pages'
import { mockCommitteeData } from '../data/mockCommitteeData'

jest.mock('../../../src/lib/api', () => ({
  loadData: jest.fn(),
}))

jest.mock('../../../src/utils/credentials', () => ({
  API_URL: 'https://mock-api.com',
}))

describe('Committees Component', () => {
  beforeEach(() => {
    ;(loadData as jest.Mock).mockResolvedValue(mockCommitteeData)
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  test('renders loading spinner initially', async () => {
    render(<CommitteesPage />)
    const loadingSpinner = screen.getAllByAltText('Loading indicator')
    await waitFor(() => {
      expect(loadingSpinner.length).toBeGreaterThan(0)
    })
  })

  test('renders committee data correctly', async () => {
    render(<CommitteesPage />)

    await waitFor(() => {
      expect(screen.getByText('Committee 1')).toBeInTheDocument()
    })
    expect(screen.getByText('This is a summary of Committee 1.')).toBeInTheDocument()
    expect(screen.getByText('Edmond Momartin,')).toBeInTheDocument()
    expect(screen.getByText('Garth Boyd,')).toBeInTheDocument()
    expect(screen.getByText('Kyle Smith')).toBeInTheDocument()
    const viewButton = screen.getByText('Learn More')
    expect(viewButton).toBeInTheDocument()
  })

  test('displays "No committees found" when there are no committees', async () => {
    ;(loadData as jest.Mock).mockResolvedValue({
      ...mockCommitteeData,
      committees: [],
      total_pages: 0,
    })
    render(<CommitteesPage />)
    await waitFor(() => {
      expect(screen.getByText('No committees found')).toBeInTheDocument()
    })
  })
})
