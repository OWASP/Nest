import { render, screen, waitFor } from '@testing-library/react'

import { UserSearchQuery, fetchAnalyticsData } from 'lib/analytics'

import AnalyticsDashboard from 'pages/Analytics_dashboard'

jest.mock('lib/analytics', () => ({
  fetchAnalyticsData: jest.fn(),
}))

const mockData: UserSearchQuery[] = [
  {
    query: 'Nest',
    source: 'frontend',
    category: 'projects',
    timestamp: '2023-10-01T12:00:00Z',
  },
  {
    query: 'Nettacker',
    source: 'nestbot',
    category: 'projects',
    timestamp: '2023-10-02T12:00:00Z',
  },
]

describe('AnalyticsDashboard', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('renders loading state initially', () => {
    ;(fetchAnalyticsData as jest.Mock).mockImplementation(() => new Promise(() => {}))

    render(<AnalyticsDashboard />)
    expect(screen.getByText('Loading...')).toBeInTheDocument()
  })

  it('renders the dashboard with data after fetching', async () => {
    ;(fetchAnalyticsData as jest.Mock).mockResolvedValue(mockData)

    render(<AnalyticsDashboard />)

    await waitFor(() => expect(screen.queryByText('Loading...')).not.toBeInTheDocument())

    expect(screen.getByText('User Search Analytics')).toBeInTheDocument()

    expect(screen.getByText('Queries by Category')).toBeInTheDocument()
    expect(
      screen.getByRole('img', { name: /bar chart showing queries by category/i })
    ).toBeInTheDocument()

    expect(screen.getByText('Queries by Source')).toBeInTheDocument()
    expect(
      screen.getByRole('img', { name: /pie chart showing queries by source/i })
    ).toBeInTheDocument()

    expect(screen.getByRole('table')).toBeInTheDocument()
    expect(screen.getByText('Nest')).toBeInTheDocument()
    expect(screen.getByText('Nettacker')).toBeInTheDocument()
  })

  it('renders "No data available" when there is no data', async () => {
    ;(fetchAnalyticsData as jest.Mock).mockResolvedValue([])

    render(<AnalyticsDashboard />)

    await waitFor(() => expect(screen.queryByText('Loading...')).not.toBeInTheDocument())

    expect(screen.getByText('No data available')).toBeInTheDocument()
  })

  it('handles fetch error gracefully', async () => {
    ;(fetchAnalyticsData as jest.Mock).mockRejectedValue(new Error('Failed to fetch data'))

    jest.spyOn(console, 'error').mockImplementation(() => {})

    render(<AnalyticsDashboard />)
    await waitFor(() => expect(screen.queryByText('Loading...')).not.toBeInTheDocument())

    expect(screen.getByText('No data available')).toBeInTheDocument()
  })
})
