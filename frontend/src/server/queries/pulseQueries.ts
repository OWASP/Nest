import { gql } from '@apollo/client'

export const GET_RECENT_ACTIVITY_EVENTS = gql`
  query GetRecentActivityEvents($limit: Int) {
    recentActivityEvents(limit: $limit) {
      id
      activityType
      occurredAt
      title
      url
      number
      githubUser {
        id
        login
        name
        avatarUrl
      }
      githubRepository {
        id
        key
        name
        url
      }
    }
  }
`

export const GET_ACTIVITY_EVENT_STATS = gql`
  query GetActivityEventStats {
    activityEventStats {
      totalActivities
      pullRequests
      issues
      contributors
      releases
      activeRepos
    }
  }
`

export const GET_ACTIVITY_EVENTS = gql`
  query GetActivityEvents(
    $activityType: String
    $githubUserLogin: String
    $projectKey: String
    $chapterKey: String
    $timeRange: String
    $includeBots: Boolean
    $order: String
    $page: Int
    $limit: Int
  ) {
    activityEvents(
      activityType: $activityType
      githubUserLogin: $githubUserLogin
      projectKey: $projectKey
      chapterKey: $chapterKey
      timeRange: $timeRange
      includeBots: $includeBots
      order: $order
      page: $page
      limit: $limit
    ) {
      currentPage
      totalPages
      totalCount
      events {
        id
        activityType
        occurredAt
        title
        url
        number
        githubUser {
          id
          login
          name
          avatarUrl
        }
        githubRepository {
          id
          key
          name
          url
        }
      }
    }
  }
`
