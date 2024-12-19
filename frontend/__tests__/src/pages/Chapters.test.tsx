import { render, screen, waitFor } from '@testing-library/react'
import axios from 'axios'
import React from 'react'

import '@testing-library/jest-dom'
import Chapters from '../../../src/pages/Chapters'
import logger from '../../../src/utils/logger'
import { mockChapterData } from '../data/mockChapterData'

jest.mock('axios')
const mockedAxios = axios as jest.Mocked<typeof axios>

describe('Chapters Component', () => {
  beforeEach(() => {
    jest.clearAllMocks()

    mockedAxios.get.mockResolvedValue({
      data: mockChapterData,
    })

    delete (window as Partial<Window>).location
    window.location = {
      search: '',
      href: 'http://localhost',
    } as Location
  })

  test('sets document title on component mount', async () => {
    render(<Chapters />)
    await waitFor(() => {
      expect(document.title).toBe('OWASP Chapters')
    })
  })

  test('handles URL query parameter correctly', async () => {
    window.location = {
      search: '?q=test-query',
      href: 'http://localhost?q=test-query',
    } as Location

    render(<Chapters />)

    await waitFor(() => {
      expect(mockedAxios.get).toHaveBeenCalledWith(
        expect.stringContaining('/owasp/search/chapter'),
        { params: { q: 'test-query' } }
      )
    })
  })

  test('fetches and sets chapter data correctly', async () => {
    render(<Chapters />)

    await waitFor(() => {
      expect(screen.getByText(mockChapterData.chapters[0].idx_name)).toBeInTheDocument()
      expect(screen.getByText(mockChapterData.chapters[0].idx_summary)).toBeInTheDocument()
    })
  })

  test('renders search bar', () => {
    render(<Chapters />)
    expect(screen.getByPlaceholderText('Search for OWASP chapters...')).toBeInTheDocument()
  })

  test('Join button links to correct URL', async () => {
    render(<Chapters />)

    await waitFor(() => {
      const joinButtons = screen.getAllByText('Join')
      expect(joinButtons.length).toBeGreaterThan(0)

      const firstChapter = mockChapterData.chapters[0]
      const firstJoinButton = joinButtons[0].closest('a')
      expect(firstJoinButton).toHaveAttribute('href', firstChapter.idx_url)
    })
  })

  test('handles API fetch error gracefully', async () => {
    mockedAxios.get.mockRejectedValue(new Error('Fetch failed'))

    const consoleSpy = jest.spyOn(logger, 'error').mockImplementation(() => {})

    render(<Chapters />)

    await waitFor(() => {
      expect(consoleSpy).toHaveBeenCalled()
    })

    consoleSpy.mockRestore()
  })
})
