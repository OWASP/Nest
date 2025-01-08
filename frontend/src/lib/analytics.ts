import axios from 'axios'
import { API_URL } from 'utils/credentials'
import logger from 'utils/logger'

export interface AnalyticsPayload {
  query: string
  source: string
  category: string
}

export const sendAnalyticsData = async ({ query, category }) => {
  const source = 'frontend'
  const payload: AnalyticsPayload = {
    query,
    source,
    category,
  }
  const response = await axios.post(`${API_URL}/analytics/search/`, payload)
  return response.data
}

export interface UserSearchQuery {
  query: string
  source: string
  category: string
  timestamp: string
}

export const fetchAnalyticsData = async (): Promise<UserSearchQuery[]> => {
  try {
    const response = await axios.get(`${API_URL}/analytics/search/`)
    return response.data.results
  } catch (error) {
    logger.error('Error fetching data from Algolia', error)
  }
}
