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
  query GetProjectHealthMetrics(
    $filters: ProjectHealthMetricsFilter!
    $pagination: OffsetPaginationInput!
    $ordering: [ProjectHealthMetricsOrder!]
  ) {
    projectHealthMetrics(filters: $filters, pagination: $pagination, ordering: $ordering) {
      createdAt
      contributorsCount
      forksCount
      id
      projectName
      score
      starsCount
    }
  }
`
