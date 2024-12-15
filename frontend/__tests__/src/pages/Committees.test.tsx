import { render, screen, waitFor } from '@testing-library/react'
import React from 'react'

import '@testing-library/jest-dom'
import { Committees } from '../../../src/pages'
import { mockCommitteeData } from '../data/mockCommitteeData'
process.env.VITE_NEST_API_URL = 'https://mock-api.com'

global.fetch = jest.fn()

describe('Committees Component', () => {
  beforeEach(() => {
    ;(fetch as jest.Mock).mockResolvedValueOnce({
      json: async () => mockCommitteeData,
    })
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  test('renders committee data correctly', async () => {
    render(<Committees />)

    await waitFor(() => {
      expect(screen.getByText('Committee 1')).toBeInTheDocument()
    })

    expect(screen.getByText('This is a summary of Committee 1.')).toBeInTheDocument()

    const viewButton = screen.getByText('Learn More')
    expect(viewButton).toBeInTheDocument()
  })
})
