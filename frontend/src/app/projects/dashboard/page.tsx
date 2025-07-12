'use client'
import { useQuery } from '@apollo/client'
import { GET_PROJECT_HEALTH_STATS } from 'server/queries/projectsHealthDashboardQueries'

export default function ProjectsDashboardPage() {
  const { data, loading, error } = useQuery(GET_PROJECT_HEALTH_STATS)

  if (loading) return <p>Loading...</p>
  if (error) return <p>Error: {error.message}</p>

  const stats = data.projectHealthStats

  return (
    <div>
      <h1>Projects Dashboard</h1>
      <div>
        <h2>Overall Statistics</h2>
        <p>
          Total Projects:{' '}
          {stats.projectsCountHealthy +
            stats.projectsCountNeedAttention +
            stats.projectsCountUnhealthy}
        </p>
        <p>
          Healthy Projects: {stats.projectsCountHealthy} ({stats.projectsPercentageHealthy}%)
        </p>
        <p>
          Projects Needing Attention: {stats.projectsCountNeedAttention} (
          {stats.projectsPercentageNeedAttention}%)
        </p>
        <p>
          Unhealthy Projects: {stats.projectsCountUnhealthy} ({stats.projectsPercentageUnhealthy}%)
        </p>
        <p>Total Stars: {stats.totalStars}</p>
        <p>Total Forks: {stats.totalForks}</p>
        <p>Total Contributors: {stats.totalContributors}</p>
      </div>
    </div>
  )
}
