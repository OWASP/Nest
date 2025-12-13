import { gql } from '@apollo/client'

export const GET_PROJECT_DATA = gql`
  query GetProject($key: String!) {
    project(key: $key) {
      id
      contributorsCount
      entityLeaders {
        id
        description
        memberName
        member {
          id
          login
          name
          avatarUrl
        }
      }
      forksCount
      issuesCount
      isActive
      key
      languages
      leaders
      level
      name
      socialUrls
      healthMetricsList(limit: 30) {
        id
        createdAt
        forksCount
        lastCommitDays
        lastCommitDaysRequirement
        lastReleaseDays
        lastReleaseDaysRequirement
        openIssuesCount
        openPullRequestsCount
        score
        starsCount
        unassignedIssuesCount
        unansweredIssuesCount
      }
      recentIssues {
        author {
          id
          avatarUrl
          login
          name
          url
        }
        createdAt
        organizationName
        repositoryName
        title
        url
      }
      recentReleases {
        author {
          id
          avatarUrl
          login
          name
        }
        name
        organizationName
        publishedAt
        repositoryName
        tagName
        url
      }
      repositories {
        id
        contributorsCount
        forksCount
        isArchived
        key
        name
        openIssuesCount
        organization {
          login
        }
        starsCount
        subscribersCount
        url
      }
      repositoriesCount
      starsCount
      summary
      topics
      type
      updatedAt
      url
      recentMilestones(limit: 5) {
        author {
          id
          avatarUrl
          login
          name
        }
        title
        openIssuesCount
        closedIssuesCount
        repositoryName
        organizationName
        createdAt
        url
      }
      recentPullRequests {
        author {
          id
          avatarUrl
          login
          name
        }
        createdAt
        organizationName
        repositoryName
        title
        url
      }
    }
    topContributors(project: $key) {
      id
      avatarUrl
      login
      name
    }
  }
`

export const GET_PROJECT_METADATA = gql`
  query GetProjectMetadata($key: String!) {
    project(key: $key) {
      id
      contributorsCount
      forksCount
      issuesCount
      name
      starsCount
      summary
      recentMilestones(limit: 25) {
        id
        title
        url
        body
        progress
        state
      }
    }
  }
`

export const GET_TOP_CONTRIBUTORS = gql`
  query GetTopContributors(
    $excludedUsernames: [String!]
    $hasFullName: Boolean = false
    $key: String!
    $limit: Int = 20
  ) {
    topContributors(
      excludedUsernames: $excludedUsernames
      hasFullName: $hasFullName
      limit: $limit
      project: $key
    ) {
      id
      avatarUrl
      login
      name
    }
  }
`

export const SEARCH_PROJECTS = gql`
  query SearchProjectNames($query: String!) {
    searchProjects(query: $query) {
      id
      name
    }
  }
`
