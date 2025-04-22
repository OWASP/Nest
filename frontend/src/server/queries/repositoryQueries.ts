import { gql } from '@apollo/client'

export const GET_REPOSITORY_DATA = gql`
  query GetRepository($repositoryKey: String!, $organizationKey: String!) {
    repository(repositoryKey: $repositoryKey, organizationKey: $organizationKey) {
      commitsCount
      contributorsCount
      createdAt
      description
      forksCount
      key
      issues {
        author {
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
        login
      }
      releases {
        author {
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
      topContributors {
        avatarUrl
        contributionsCount
        login
        name
      }
      topics
      updatedAt
      url
    }
    recentPullRequests(limit: 5, organization: $organizationKey, repository: $repositoryKey) {
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
  }
`
