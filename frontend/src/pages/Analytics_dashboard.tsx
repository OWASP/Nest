import React, { useEffect, useState } from 'react'
import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  XAxis,
  YAxis,
  CartesianGrid,
} from 'recharts'
import logger from 'utils/logger'
import { fetchAnalyticsData, UserSearchQuery } from 'lib/analytics'

const COLORS = ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF']

const AnalyticsDashboard: React.FC = () => {
  const [queries, setQueries] = useState<UserSearchQuery[]>([])
  const [loading, setLoading] = useState<boolean>(true)

  useEffect(() => {
    const getQueries = async () => {
      try {
        const data = await fetchAnalyticsData()
        setQueries(data)
      } catch (error) {
        logger.error('Error fetching search queries:', error)
      } finally {
        setLoading(false)
      }
    }
    getQueries()
  }, [])

  const categoryCounts = queries.reduce(
    (acc, query) => {
      acc[query.category] = (acc[query.category] || 0) + 1
      return acc
    },
    {} as Record<string, number>
  )

  const categoryData = Object.keys(categoryCounts).map((category) => ({
    name: category,
    count: categoryCounts[category],
  }))

  const sourceCounts = queries.reduce(
    (acc, query) => {
      acc[query.source] = (acc[query.source] || 0) + 1
      return acc
    },
    {} as Record<string, number>
  )

  const sourceData = Object.keys(sourceCounts).map((source) => ({
    name: source,
    value: sourceCounts[source],
  }))

  if (loading) {
    return <div>Loading...</div>
  }

  return (
    <div style={{ padding: '20px' }}>
      <h1>User Search Analytics</h1>

      <div style={{ marginBottom: '40px' }}>
        <h2>Queries by Category</h2>
        <BarChart
          width={600}
          height={400}
          data={categoryData}
          margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
          aria-label="Bar chart showing queries by category"
          role="img"
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Bar dataKey="count" fill="#36A2EB" />
        </BarChart>
      </div>

      <div style={{ marginBottom: '40px' }}>
        <h2>Queries by Source</h2>
        <PieChart
          width={600}
          height={400}
          aria-label="Pie chart showing queries by source"
          role="img"
        >
          <Pie
            data={sourceData}
            dataKey="value"
            nameKey="name"
            cx="50%"
            cy="50%"
            outerRadius={150}
            fill="#FF6384"
            label
          >
            {sourceData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip />
          <Legend />
        </PieChart>
      </div>

      {queries.length === 0 ? (
        <p>No data available</p>
      ) : (
        <table style={{ width: '50%', borderCollapse: 'collapse' }}>
          <thead>
            <tr>
              <th style={{ border: '1px solid #ddd', padding: '8px' }}>Query</th>
              <th style={{ border: '1px solid #ddd', padding: '8px' }}>Source</th>
              <th style={{ border: '1px solid #ddd', padding: '8px' }}>Category</th>
              <th style={{ border: '1px solid #ddd', padding: '8px' }}>Timestamp</th>
            </tr>
          </thead>
          <tbody>
            {queries.map((query) => (
              <tr key={query.timestamp}>
                <td style={{ border: '1px solid #ddd', padding: '8px' }}>{query.query}</td>
                <td style={{ border: '1px solid #ddd', padding: '8px' }}>{query.source}</td>
                <td style={{ border: '1px solid #ddd', padding: '8px' }}>{query.category}</td>
                <td style={{ border: '1px solid #ddd', padding: '8px' }}>
                  {new Date(query.timestamp).toLocaleString()}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}

export default AnalyticsDashboard
