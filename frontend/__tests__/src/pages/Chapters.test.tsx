import { render, screen, waitFor } from '@testing-library/react'
import React from 'react'

import '@testing-library/jest-dom'
import { Chapters } from '../../../src/pages'
import { mockChapterData } from '../data/mockChapterData'
process.env.VITE_NEST_API_URL = 'https://mock-api.com'

global.fetch = jest.fn()

describe('Chapters Component', () => {
  beforeEach(() => {
    ;(fetch as jest.Mock).mockResolvedValueOnce({
      json: async () => mockChapterData,
    })
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  test('renders chapter data correctly', async () => {
    render(<Chapters />)

    await waitFor(() => {
      expect(screen.getByText('Chapter 1')).toBeInTheDocument()
    })

    expect(screen.getByText('This is a summary of Chapter 1.')).toBeInTheDocument()

    const exploreButton = screen.getByText('Join')
    expect(exploreButton).toBeInTheDocument()
  })
})
