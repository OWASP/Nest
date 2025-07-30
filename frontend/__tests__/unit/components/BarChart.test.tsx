import { library } from '@fortawesome/fontawesome-svg-core'
import { faFire } from '@fortawesome/free-solid-svg-icons'
import { act, render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'
import { ThemeProvider } from 'next-themes'
import React from 'react'

import BarChart from 'components/BarChart'

// Register FontAwesome icon
library.add(faFire)

// Mock ApexCharts
jest.mock('react-apexcharts', () => {
  const MockChart = () => <div data-testid="mock-chart" />
  return {
    __esModule: true,
    default: MockChart,
  }
})

// Silence known warnings
const originalError = console.error
beforeAll(() => {
  jest.spyOn(console, 'error').mockImplementation((...args) => {
    const [message] = args
    if (
      typeof message === 'string' &&
      (message.includes('act(...)') ||
        message.includes('not wrapped in act') ||
        message.includes('LoadableComponent') ||
        message.includes('useLayoutEffect'))
    ) {
      return
    }
    originalError(...args)
  })
})

// Utility to render with act + theme
const renderWithTheme = async (
  ui: React.ReactElement,
  theme: 'light' | 'dark' = 'light'
) => {
  let result: ReturnType<typeof render> | undefined
  await act(async () => {
    result = render(
      <ThemeProvider attribute="class" forcedTheme={theme}>
        {ui}
      </ThemeProvider>
    )
  })
  return result!
}

// Common test props
const mockProps = {
  title: 'Calories Burned',
  labels: ['Mon', 'Tue', 'Wed'],
  days: [200, 150, 100],
  requirements: [180, 170, 90],
}

describe('<BarChart />', () => {
  it('renders without crashing with minimal props', async () => {
    await renderWithTheme(<BarChart {...mockProps} />)
    expect(screen.getByText('Calories Burned')).toBeInTheDocument()
    expect(screen.getByTestId('mock-chart')).toBeInTheDocument()
  })

  it('renders with icon when provided', async () => {
    // cspell:ignore fas
    await renderWithTheme(<BarChart {...mockProps} icon={['fas', 'fire']} />)
    expect(screen.getByText('Calories Burned')).toBeInTheDocument()
    expect(document.querySelector('[data-icon="fire"]')).toBeInTheDocument()
  })

  it('renders correctly in dark mode', async () => {
    await renderWithTheme(<BarChart {...mockProps} />, 'dark')
    expect(screen.getByText('Calories Burned')).toBeInTheDocument()
    expect(screen.getByTestId('mock-chart')).toBeInTheDocument()
  })

  it('handles empty data arrays without crashing', async () => {
    const emptyProps = {
      title: 'Empty Chart',
      labels: [],
      days: [],
      requirements: [],
    }
    await renderWithTheme(<BarChart {...emptyProps} />)
    expect(screen.getByText('Empty Chart')).toBeInTheDocument()
    expect(screen.getByTestId('mock-chart')).toBeInTheDocument()
  })

  it('handles reverseColors logic correctly', async () => {
    const customProps = {
      ...mockProps,
      reverseColors: [true, false, true],
    }
    await renderWithTheme(<BarChart {...customProps} />)
    expect(screen.getByTestId('mock-chart')).toBeInTheDocument()
  })

  it('renders chart container with proper structure', async () => {
    await renderWithTheme(<BarChart {...mockProps} />)
    const chartElement = screen.getByTestId('mock-chart')
    expect(chartElement).toBeInTheDocument()
  })

  it('handles mismatched array lengths gracefully', async () => {
    const mismatchedProps = {
      ...mockProps,
      days: [200, 150], // Only 2 entries instead of 3
    }
    await renderWithTheme(<BarChart {...mismatchedProps} />)
    expect(screen.getByText('Calories Burned')).toBeInTheDocument()
    expect(screen.getByTestId('mock-chart')).toBeInTheDocument()
  })

  it('renders title correctly', async () => {
    await renderWithTheme(<BarChart {...mockProps} />)
    expect(screen.getByText('Calories Burned')).toBeInTheDocument()
  })

  it('renders chart component when data is provided', async () => {
    await renderWithTheme(<BarChart {...mockProps} />)
    expect(screen.getByTestId('mock-chart')).toBeInTheDocument()
  })
})
