import '@testing-library/jest-dom'
import { render, screen, waitFor, act } from '@testing-library/react'
import axios from 'axios'
import React from 'react'

import Projects from '../../../src/pages/Projects'
import logger from '../../../src/utils/logger'
import mockProjectData from '../data/mockProjectData'

jest.mock('axios')
const mockedAxios = axios as jest.Mocked<typeof axios>

const mockWindowOpen = jest.fn()
Object.defineProperty(window, 'open', {
  value: mockWindowOpen,
  writable: true,
})

describe('Projects Component', () => {
  beforeEach(() => {
    jest.clearAllMocks()

    document.title = ''

    mockedAxios.get.mockResolvedValue({
      data: mockProjectData,
    })

    delete (window as Partial<Window>).location
    window.location = {
      search: '',
      href: 'http://localhost',
    } as Location
  })

  test('sets document title on component mount', async () => {
    await act(async () => {
      render(<Projects />)
    })

    await waitFor(() => {
      expect(document.title).toBe('OWASP Projects')
    })
  })

  test('handles URL query parameter correctly', async () => {
    window.location = {
      search: '?q=test-query',
      href: 'http://localhost?q=test-query',
    } as Location

    await act(async () => {
      render(<Projects />)
    })

    await waitFor(() => {
      expect(mockedAxios.get).toHaveBeenCalledWith(
        `${process.env.VITE_NEST_API_URL}/owasp/search/project`,
        { params: { q: 'test-query' } }
      )
    })
  })

  test('fetches and sets project data correctly', async () => {
    await act(async () => {
      render(<Projects />)
    })

    await waitFor(() => {
      expect(screen.getByText(mockProjectData.projects[0].idx_name)).toBeInTheDocument()
      expect(screen.getByText(mockProjectData.projects[0].idx_summary)).toBeInTheDocument()
    })
  })

  test('renders search bar', async () => {
    await act(async () => {
      render(<Projects />)
    })

    expect(screen.getByPlaceholderText('Search for OWASP projects...')).toBeInTheDocument()
  })

  test('contribute button opens correct URL in new tab', async () => {
    await act(async () => {
      render(<Projects />)
    })

    await waitFor(() => {
      const contributeButtons = screen.getAllByText('Contribute')
      expect(contributeButtons.length).toBeGreaterThan(0)

      const firstContributeButton = contributeButtons[0]
      firstContributeButton.closest('button')?.click()

      expect(mockWindowOpen).toHaveBeenCalledWith(
        `/projects/contribute?q=${mockProjectData.projects[0].idx_name}`,
        '_blank'
      )
    })
  })

  test('handles API fetch error gracefully', async () => {
    mockedAxios.get.mockRejectedValue(new Error('Fetch failed'))

    const consoleSpy = jest.spyOn(logger, 'error').mockImplementation(() => {})

    await act(async () => {
      render(<Projects />)
    })

    await waitFor(() => {
      expect(consoleSpy).toHaveBeenCalled()
    })

    consoleSpy.mockRestore()
  })

  test('renders project details', async () => {
    await act(async () => {
      render(<Projects />)
    })

    await waitFor(() => {
      const firstProject = mockProjectData.projects[0]

      expect(screen.getByText(firstProject.idx_name)).toBeInTheDocument()
      expect(screen.getByText(firstProject.idx_summary)).toBeInTheDocument()

      firstProject.idx_topics.forEach((topic) => {
        expect(screen.getByText(topic)).toBeInTheDocument()
      })
    })
  })
})
