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
      projectKey
      projectName
      score
      starsCount
    }
    projectHealthMetricsDistinctLength(filters: $filters)
  }
`
export const GET_PROJECT_HEALTH_METRICS_DETAILS = gql`
  query Project($projectKey: String!) {
    project(key: $projectKey) {
      healthMetricsLatest {
        ageDays
        ageDaysRequirement
        isFundingRequirementsCompliant
        isLeaderRequirementsCompliant
        lastCommitDays
        lastCommitDaysRequirement
        lastPullRequestDays
        lastPullRequestDaysRequirement
        lastReleaseDays
        lastReleaseDaysRequirement
        owaspPageLastUpdateDays
        owaspPageLastUpdateDaysRequirement
        projectName
        score
      }
      healthMetricsList(limit: 30) {
        contributorsCount
        createdAt
        forksCount
        openIssuesCount
        openPullRequestsCount
        recentReleasesCount
        starsCount
        totalIssuesCount
        totalReleasesCount
        unassignedIssuesCount
        unansweredIssuesCount
      }
    }
  }
`
