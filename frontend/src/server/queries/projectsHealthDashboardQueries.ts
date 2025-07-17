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
export const GET_PROJECT_HEALTH_METRICS_DETAILS = gql`
  query Project($projectKey: String!) {
    project(key: $projectKey) {
      healthMetricsLatest {
        createdAt
        contributorsCount
        forksCount
        isFundingRequirementsCompliant
        isLeaderRequirementsCompliant
        lastCommitDays
        lastCommitDaysRequirement
        lastReleaseDays
        lastReleaseDaysRequirement
        openIssuesCount
        openPullRequestsCount
        owaspPageLastUpdateDays
        projectName
        recentReleasesCount
        score
        starsCount
        totalIssuesCount
        totalReleasesCount
        unassignedIssuesCount
        unansweredIssuesCount
      }
    }
  }
`
