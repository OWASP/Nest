import { gql } from '@apollo/client'

export const GET_REPOSITORY_DATA = gql`
  query GetRepository($repositoryKey: String!, $organizationKey: String!) {
    repository(repositoryKey: $repositoryKey, organizationKey: $organizationKey) {
      id
      commitsCount
      contributorsCount
      createdAt
      description
      forksCount
      key
      issues {
        id
        author {
          id
          avatarUrl
          login
          name
        }
        organizationName
        repositoryName
        createdAt
        title
      }
      languages
      license
      name
      openIssuesCount
      organization {
        id
        login
      }
      project {
        id
        key
        name
      }
      releases {
        id
        author {
          id
          avatarUrl
          name
          login
        }
        isPreRelease
        name
        organizationName
        publishedAt
        repositoryName
        tagName
      }
      size
      starsCount
      topics
      updatedAt
      url
      recentMilestones(limit: 5) {
        id
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
    }
    topContributors(organization: $organizationKey, repository: $repositoryKey) {
      id
      avatarUrl
      login
      name
    }
    recentPullRequests(limit: 5, organization: $organizationKey, repository: $repositoryKey) {
      id
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
`

export const GET_REPOSITORY_METADATA = gql`
  query GetRepository($repositoryKey: String!, $organizationKey: String!) {
    repository(repositoryKey: $repositoryKey, organizationKey: $organizationKey) {
      id
      description
      name
    }
  }
`
