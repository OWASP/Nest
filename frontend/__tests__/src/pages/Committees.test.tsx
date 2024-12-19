import React, { act } from 'react'
import { render, screen, waitFor } from '@testing-library/react'
import '@testing-library/jest-dom'
import { CommitteesPage } from '../../../src/pages'
import { loadData } from '../../../src/lib/api'
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

  it('renders loading spinner initially', () => {
    act(() => {
      render(<CommitteesPage />)
    })
    const loadingSpinner = screen.getAllByAltText('Loading indicator')
    expect(loadingSpinner.length).toBeGreaterThan(0)
  })

  it('renders committee data correctly', async () => {
    await act(async () => {
      render(<CommitteesPage />)
    })

    expect(screen.getByText('Committee 1')).toBeInTheDocument()

    expect(screen.getByText('This is a summary of Committee 1.')).toBeInTheDocument()

    expect(screen.getByText('Edmond Momartin,')).toBeInTheDocument()
    expect(screen.getByText('Garth Boyd,')).toBeInTheDocument()
    expect(screen.getByText('Kyle Smith')).toBeInTheDocument()

    const viewButton = screen.getByText('Learn More')
    expect(viewButton).toBeInTheDocument()
  })

  it('displays "No committees found" when there are no committees', async () => {
    ;(loadData as jest.Mock).mockResolvedValue({
      ...mockCommitteeData,
      committees: [],
      total_pages: 0,
    })

    await act(async () => {
      render(<CommitteesPage />)
    })

    await waitFor(() => {
      expect(screen.getByText('No committees found')).toBeInTheDocument()
    })
  })
})
