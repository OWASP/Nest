import { render, screen, act } from '@testing-library/react'
import BarChart from 'components/BarChart'
import '@testing-library/jest-dom'
import { ThemeProvider } from 'next-themes'
import { library } from '@fortawesome/fontawesome-svg-core'
import { faFire } from '@fortawesome/free-solid-svg-icons'
import React from 'react'

// Add fontawesome icon to the library
library.add(faFire)

// Mock ApexCharts to avoid dynamic import issues
jest.mock('react-apexcharts', () => () => <div data-testid="mock-chart" />)

// Silence the "not wrapped in act(...)" error logs
jest.spyOn(console, 'error').mockImplementation((...args) => {
  if (typeof args[0] === 'string' && args[0].includes('act(...)')) return
  console.warn(...args)
})

const renderWithTheme = async (ui: React.ReactElement, theme: 'light' | 'dark' = 'light') => {
  await act(() =>
    Promise.resolve(
      render(
        <ThemeProvider attribute="class" forcedTheme={theme}>
          {ui}
        </ThemeProvider>
      )
    )
  )
}

const mockProps = {
  title: 'Calories Burned',
  labels: ['Mon', 'Tue', 'Wed'],
  days: [200, 150, 100],
  requirements: [180, 170, 90],
}

describe('<BarChart />', () => {
  it('renders without crashing (minimal props)', async () => {
    await renderWithTheme(<BarChart {...mockProps} />)
    expect(screen.getByText('Calories Burned')).toBeInTheDocument()
    expect(screen.getByTestId('mock-chart')).toBeInTheDocument()
  })

  it('renders with icon if provided', async () => {
    await renderWithTheme(<BarChart {...mockProps} icon={['fas', 'fire']} />)
    expect(screen.getByText('Calories Burned')).toBeInTheDocument()
  })

  it('renders correctly in dark mode', async () => {
    await renderWithTheme(<BarChart {...mockProps} />, 'dark')
    expect(screen.getByText('Calories Burned')).toBeInTheDocument()
  })

  it('handles empty data arrays without crashing', async () => {
    const emptyProps = { title: 'Empty Chart', labels: [], days: [], requirements: [] }
    await renderWithTheme(<BarChart {...emptyProps} />)
    expect(screen.getByText('Empty Chart')).toBeInTheDocument()
    expect(screen.getByTestId('mock-chart')).toBeInTheDocument()
  })

  it('handles reverseColors logic correctly', async () => {
    const customProps = { ...mockProps, reverseColors: [true, false, true] }
    await renderWithTheme(<BarChart {...customProps} />)
    expect(screen.getByTestId('mock-chart')).toBeInTheDocument()
  })
})
