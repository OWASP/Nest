import { render } from '@testing-library/react'
import React from 'react'
import { BrowserRouter } from 'react-router-dom'
import '@testing-library/jest-dom'
import Home from 'pages/Home'

jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: jest.fn(),
}))

describe('Home Component', () => {
  it('redirects to /projects on load', () => {
    const mockNavigate = jest.fn()

    ;(require('react-router-dom').useNavigate as jest.Mock).mockReturnValue(mockNavigate)

    render(
      <BrowserRouter>
        <Home />
      </BrowserRouter>
    )
    expect(mockNavigate).toHaveBeenCalledWith('/projects', { replace: true })
    expect(mockNavigate).toHaveBeenCalledTimes(1)
  })
})
