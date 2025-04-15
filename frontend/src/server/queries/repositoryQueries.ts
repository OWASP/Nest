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
  }
`
