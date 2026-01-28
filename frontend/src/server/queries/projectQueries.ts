import { gql } from '@apollo/client'

export const GET_PROJECT_DATA = gql`
  query GetProject($key: String!) {
    project(key: $key) {
      contributionData
      contributionStats
      contributorsCount
      entityLeaders {
        description
        id
        memberName
        member {
          avatarUrl
          id
          login
          name
        }
      }
      forksCount
      id
      isActive
      issuesCount
      key
      languages
      leaders
      level
      name
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
        id
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

export const GET_ABOUT_PAGE_DATA = gql`
  query GetAboutPageData(
    $key: String!
    $excludedUsernames: [String!]
    $hasFullName: Boolean = false
    $limit: Int = 20
    $leader1: String!
    $leader2: String!
    $leader3: String!
  ) {
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
    leader1: user(login: $leader1) {
      id
      avatarUrl
      login
      name
      badgeCount
      badges {
        cssClass
        description
        id
        name
        weight
      }
    }
    leader2: user(login: $leader2) {
      id
      avatarUrl
      login
      name
      badgeCount
      badges {
        cssClass
        description
        id
        name
        weight
      }
    }
    leader3: user(login: $leader3) {
      id
      avatarUrl
      login
      name
      badgeCount
      badges {
        cssClass
        description
        id
        name
        weight
      }
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
