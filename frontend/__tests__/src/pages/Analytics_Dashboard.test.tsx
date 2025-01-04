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
    // Reset the mock implementation before each test
    jest.clearAllMocks()
  })

  it('renders loading state initially', () => {
    // Mock the fetchAnalyticsData to return a promise that hasn't resolved yet
    ;(fetchAnalyticsData as jest.Mock).mockImplementation(() => new Promise(() => {}))

    render(<AnalyticsDashboard />)
    expect(screen.getByText('Loading...')).toBeInTheDocument()
  })

  it('renders the dashboard with data after fetching', async () => {
    // Mock the fetchAnalyticsData to return mock data
    ;(fetchAnalyticsData as jest.Mock).mockResolvedValue(mockData)

    render(<AnalyticsDashboard />)

    // Wait for the loading state to disappear
    await waitFor(() => expect(screen.queryByText('Loading...')).not.toBeInTheDocument())

    // Check if the dashboard title is rendered
    expect(screen.getByText('User Search Analytics')).toBeInTheDocument()

    // Check if the bar chart for queries by category is rendered
    expect(screen.getByText('Queries by Category')).toBeInTheDocument()
    expect(
      screen.getByRole('img', { name: /bar chart showing queries by category/i })
    ).toBeInTheDocument()

    // Check if the pie chart for queries by source is rendered
    expect(screen.getByText('Queries by Source')).toBeInTheDocument()
    expect(
      screen.getByRole('img', { name: /pie chart showing queries by source/i })
    ).toBeInTheDocument()

    // Check if the table with query data is rendered
    expect(screen.getByRole('table')).toBeInTheDocument()
    expect(screen.getByText('Nest')).toBeInTheDocument()
    expect(screen.getByText('Nettacker')).toBeInTheDocument()
  })

  it('renders "No data available" when there is no data', async () => {
    // Mock the fetchAnalyticsData to return an empty array
    ;(fetchAnalyticsData as jest.Mock).mockResolvedValue([])

    render(<AnalyticsDashboard />)

    // Wait for the loading state to disappear
    await waitFor(() => expect(screen.queryByText('Loading...')).not.toBeInTheDocument())

    // Check if the "No data available" message is rendered
    expect(screen.getByText('No data available')).toBeInTheDocument()
  })

  it('handles fetch error gracefully', async () => {
    // Mock the fetchAnalyticsData to throw an error
    ;(fetchAnalyticsData as jest.Mock).mockRejectedValue(new Error('Failed to fetch data'))

    // Mock console.error to avoid logging the error in the test output
    jest.spyOn(console, 'error').mockImplementation(() => {})

    render(<AnalyticsDashboard />)

    // Wait for the loading state to disappear
    await waitFor(() => expect(screen.queryByText('Loading...')).not.toBeInTheDocument())

    // Check if the "No data available" message is rendered
    expect(screen.getByText('No data available')).toBeInTheDocument()
  })
})
