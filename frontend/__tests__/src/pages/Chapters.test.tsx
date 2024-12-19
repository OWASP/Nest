import React, { act } from 'react'
import { render, screen, waitFor } from '@testing-library/react'
import '@testing-library/jest-dom'
import { ChaptersPage } from '../../../src/pages'
import { loadData } from '../../../src/lib/api'
import { mockChapterData } from '../data/mockChapterData'

jest.mock('../../../src/lib/api', () => ({
  loadData: jest.fn(),
}))

jest.mock('../../../src/utils/credentials', () => ({
  API_URL: 'https://mock-api.com',
}))

describe('ChaptersPage Component', () => {
  beforeEach(() => {
    ;(loadData as jest.Mock).mockResolvedValue(mockChapterData)
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  it('renders loading spinner initially', () => {
    act(() => {
      render(<ChaptersPage />)
    })
    const loadingSpinner = screen.getAllByAltText('Loading indicator')
    expect(loadingSpinner.length).toBeGreaterThan(0)
  })

  it('renders chapter data correctly', async () => {
    await act(async () => {
      render(<ChaptersPage />)
    })
    expect(screen.getByText('Chapter 1')).toBeInTheDocument()
    expect(screen.getByText('This is a summary of Chapter 1.')).toBeInTheDocument()
    expect(screen.getByText('Isanori Sakanashi,')).toBeInTheDocument()
    expect(screen.getByText('Takeshi Murai,')).toBeInTheDocument()
    expect(screen.getByText('Yukiharu Niwa')).toBeInTheDocument()
    const viewButton = screen.getByText('Join')
    expect(viewButton).toBeInTheDocument()
  })

  it('displays "No chapters found" when there are no chapters', async () => {
    ;(loadData as jest.Mock).mockResolvedValue({ ...mockChapterData, chapters: [], total_pages: 0 })

    await act(async () => {
      render(<ChaptersPage />)
    })

    await waitFor(() => {
      expect(screen.getByText('No chapters found')).toBeInTheDocument()
    })
  })
})
