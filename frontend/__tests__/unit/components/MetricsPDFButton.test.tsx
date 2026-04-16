import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import React from 'react'
import { fetchMetricsPDF } from 'server/fetchMetricsPDF'
import MetricsPDFButton from 'components/MetricsPDFButton'

jest.mock('server/fetchMetricsPDF', () => ({
  fetchMetricsPDF: jest.fn(),
}))

jest.mock('@heroui/tooltip', () => ({
  Tooltip: ({ children, content }: { children: React.ReactNode; content: string }) => (
    <div data-testid="tooltip" title={content}>
      {children}
    </div>
  ),
}))

describe('MetricsPDFButton', () => {
  const mockFetchMetricsPDF = fetchMetricsPDF as jest.Mock

  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('renders the download icon with tooltip', () => {
    render(<MetricsPDFButton path="/api/metrics" fileName="metrics.pdf" />)

    const tooltip = screen.getByTestId('tooltip')
    expect(tooltip).toBeInTheDocument()
    expect(tooltip).toHaveAttribute('title', 'Download as PDF')
  })

  it('calls fetchMetricsPDF when icon is clicked', async () => {
    mockFetchMetricsPDF.mockResolvedValueOnce(undefined)

    render(<MetricsPDFButton path="/api/metrics" fileName="metrics.pdf" />)

    const icon = screen.getByTestId('tooltip').querySelector('svg')
    expect(icon).toBeInTheDocument()

    fireEvent.click(icon!)

    await waitFor(() => {
      expect(mockFetchMetricsPDF).toHaveBeenCalledWith('/api/metrics', 'metrics.pdf')
    })
  })

  it('passes correct path and fileName props', async () => {
    mockFetchMetricsPDF.mockResolvedValueOnce(undefined)

    render(<MetricsPDFButton path="/custom/path" fileName="custom-file.pdf" />)

    const icon = screen.getByTestId('tooltip').querySelector('svg')
    fireEvent.click(icon!)

    await waitFor(() => {
      expect(mockFetchMetricsPDF).toHaveBeenCalledWith('/custom/path', 'custom-file.pdf')
    })
  })
})
