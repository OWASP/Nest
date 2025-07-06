import { gql } from '@apollo/client'

export const GET_PROJECT_HEALTH_STATS = gql`
  query {
    projectHealthStats {
      averageScore
      monthlyOverallScores
      monthlyOverallScoresMonths
      projectsCountHealthy
      projectsCountNeedAttention
      projectsCountUnhealthy
      projectsPercentageHealthy
      projectsPercentageNeedAttention
      projectsPercentageUnhealthy
      totalContributors
      totalForks
      totalStars
    }
  }
`
export const GET_PROJECT_HEALTH_METRICS_LIST = gql`
  query GetProjectHealthMetrics($filters: ProjectHealthMetricsFiltersInput) {
    projectHealthMetrics(filters: $filters) {
      projectName
      score
      createdAt
      openIssuesCount
      openPullRequestsCount
    }
  }
`
