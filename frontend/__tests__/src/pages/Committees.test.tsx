import '@testing-library/jest-dom'
import { render, screen, waitFor } from '@testing-library/react'
import axios from 'axios'
import React from 'react'

import { Committees } from '../../../src/pages'
import logger from '../../../src/utils/logger'
import { mockCommitteeData } from '../data/mockCommitteeData'

jest.mock('axios')
const mockedAxios = axios as jest.Mocked<typeof axios>

describe('Committees Component', () => {
  beforeEach(() => {
    jest.clearAllMocks()

    mockedAxios.get.mockResolvedValue({
      data: mockCommitteeData,
    })

    delete (window as Partial<Window>).location
    window.location = {
      search: '',
      href: 'http://localhost',
    } as Location
  })

  test('sets document title on component mount', async () => {
    render(<Committees />)
    await waitFor(() => {
      expect(document.title).toBe('OWASP Committees')
    })
  })

  test('handles URL query parameter correctly', async () => {
    window.location = {
      search: '?q=test-query',
      href: 'http://localhost?q=test-query',
    } as Location

    render(<Committees />)

    await waitFor(() => {
      expect(mockedAxios.get).toHaveBeenCalledWith(
        expect.stringContaining('/owasp/search/committee'),
        { params: { q: 'test-query' } }
      )
    })
  })

  test('fetches and sets committee data correctly', async () => {
    render(<Committees />)

    await waitFor(() => {
      expect(screen.getByText(mockCommitteeData.committees[0].idx_name)).toBeInTheDocument()
      expect(screen.getByText(mockCommitteeData.committees[0].idx_summary)).toBeInTheDocument()
    })
  })

  test('renders search bar', () => {
    render(<Committees />)
    expect(screen.getByPlaceholderText('Search for OWASP committees...')).toBeInTheDocument()
  })

  test('Learn More button links to correct URL', async () => {
    render(<Committees />)

    await waitFor(() => {
      const learnMoreButtons = screen.getAllByText('Learn More')
      expect(learnMoreButtons.length).toBeGreaterThan(0)
      const firstCommittee = mockCommitteeData.committees[0]
      expect(learnMoreButtons[0]).toHaveAttribute('href', firstCommittee.idx_url)
    })
  })

  test('handles API fetch error gracefully', async () => {
    mockedAxios.get.mockRejectedValue(new Error('Fetch failed'))

    const consoleSpy = jest.spyOn(logger, 'error').mockImplementation(() => {})

    render(<Committees />)

    await waitFor(() => {
      expect(consoleSpy).toHaveBeenCalled()
    })

    consoleSpy.mockRestore()
  })
})
