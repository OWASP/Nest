import React from 'react'
import { render, screen, waitFor } from '@testing-library/react'
import '@testing-library/jest-dom'
import { Projects } from '../../../src/pages'
import mockProjectData from '../../../__mocks__/data/mockProjectData'

process.env.VITE_NEST_API_URL = 'https://mock-api.com'
global.fetch = jest.fn()

describe('Projects Component', () => {
  beforeEach(() => {
    ;(fetch as jest.Mock).mockResolvedValueOnce({
      json: async () => mockProjectData,
    })
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  test('renders project data correctly', async () => {
    render(<Projects />)

    await waitFor(() => {
      expect(screen.getByText('Project 1')).toBeInTheDocument()
    })

    expect(screen.getByText('This is a summary of Project 1.')).toBeInTheDocument()

    const contributeButton = screen.getByText('Contribute')
    expect(contributeButton).toBeInTheDocument()
  })
})
