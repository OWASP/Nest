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
