import React from 'react'
import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'
import Home from '../../../src/pages/Home'

describe('Home Component', () => {
  test('renders the Home component with the correct content', () => {
    render(<Home />)
    const helloText = screen.getByText(/hello!/i)
    expect(helloText).toBeInTheDocument()
  })
})
