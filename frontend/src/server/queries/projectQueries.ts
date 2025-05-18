import { gql } from '@apollo/client'

export const GET_PROJECT_DATA = gql`
  query GetProject($key: String!) {
    project(key: $key) {
      contributorsCount
      forksCount
      issuesCount
      isActive
      key
      languages
      leaders
      level
      name
      recentIssues {
        author {
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
        contributorsCount
        forksCount
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
    }
    recentPullRequests(project: $key) {
      author {
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
    topContributors(project: $key) {
      avatarUrl
      contributionsCount
      login
      name
    }
  }
`

export const GET_PROJECT_METADATA = gql`
  query GetProjectMetadata($key: String!) {
    project(key: $key) {
      contributorsCount
      forksCount
      issuesCount
      name
      starsCount
      summary
    }
  }
`

export const GET_TOP_CONTRIBUTORS = gql`
  query GetTopContributors($excludedUsernames: [String!], $key: String!) {
    topContributors(excludedUsernames: $excludedUsernames, project: $key) {
      avatarUrl
      contributionsCount
      login
      name
    }
  }
`
