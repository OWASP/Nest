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
  query GetProject($key: String!) {
    project(key: $key) {
      name
      summary
    }
  }
`
